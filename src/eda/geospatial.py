"""Geospatial analysis of the EV charging stations (geopandas + folium).

Run from the project root:  python -m src.eda.geospatial
Outputs are saved to outputs/geospatial/ (interactive map, GeoJSON and station table).
"""
import os

import folium
import geopandas as gpd
import numpy as np
import pandas as pd
from branca.colormap import LinearColormap
from folium.plugins import HeatMap

from src import clean_data

OUT_DIR = "outputs/geospatial"
IDLE_THRESHOLD_H = 20 / 60  # a session counts as "long idle" above 20 minutes
CRS_LATLON = "EPSG:4326"
CRS_METRIC = "EPSG:32610"  # UTM zone 10N (Palo Alto), distances in metres


def load_data() -> pd.DataFrame:
    """Load the cleaned dataset (re-creating it from the raw data if it is missing)."""
    if os.path.exists(clean_data.CLEAN_PATH):
        return pd.read_csv(clean_data.CLEAN_PATH, low_memory=False)
    return clean_data.clean(pd.read_csv(clean_data.RAW_PATH, low_memory=False))


def build_station_gdf(df: pd.DataFrame) -> gpd.GeoDataFrame:
    """One row per station: point geometry (median of reported coordinates) and usage metrics."""
    df = df.assign(long_idle=df["idle_hours"] > IDLE_THRESHOLD_H)
    stations = (
        df.groupby("Station Name")
        .agg(
            lat=("Latitude", "median"),
            lon=("Longitude", "median"),
            address=("Address 1", "first"),
            n_events=("Station Name", "size"),
            n_ports=("EVSE ID", "nunique"),
            avg_total_hours=("total_duration_hours", "mean"),
            avg_charging_hours=("charging_duration_hours", "mean"),
            avg_idle_hours=("idle_hours", "mean"),
            pct_long_idle=("long_idle", "mean"),
            total_energy_kwh=("Energy (kWh)", "sum"),
            avg_energy_kwh=("Energy (kWh)", "mean"),
        )
        .reset_index()
    )
    stations["pct_long_idle"] *= 100
    stations["short_name"] = stations["Station Name"].str.replace("PALO ALTO CA / ", "", regex=False)
    return gpd.GeoDataFrame(
        stations, geometry=gpd.points_from_xy(stations["lon"], stations["lat"]), crs=CRS_LATLON
    )


def add_spatial_features(stations: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Add nearest-neighbour distance, stations within 250 m and distance to the usage-weighted centre."""
    stations = stations.copy()
    metric = stations.to_crs(CRS_METRIC)

    dist = np.vstack([metric.distance(geom).to_numpy() for geom in metric.geometry])
    np.fill_diagonal(dist, np.inf)
    stations["nearest_station_m"] = dist.min(axis=1)
    stations["n_within_250m"] = (dist <= 250).sum(axis=1)

    xy = np.column_stack([metric.geometry.x, metric.geometry.y])
    centre = np.average(xy, axis=0, weights=stations["n_events"])
    stations["dist_to_center_m"] = np.hypot(*(xy - centre).T)
    stations.attrs["center_latlon"] = (
        gpd.GeoSeries(gpd.points_from_xy([centre[0]], [centre[1]]), crs=CRS_METRIC)
        .to_crs(CRS_LATLON)
        .iloc[0]
    )
    return stations


def _radius(n_events, max_events, r_min=5, r_max=28):
    return r_min + (r_max - r_min) * np.sqrt(n_events / max_events)


def _tooltip(row):
    return (
        f"<b>{row['short_name']}</b><br>{row['address']}<br>"
        f"Events: {row['n_events']:,}<br>Ports: {row['n_ports']}<br>"
        f"Avg total / charging / idle: {row['avg_total_hours']:.2f} / "
        f"{row['avg_charging_hours']:.2f} / {row['avg_idle_hours']:.2f} h<br>"
        f"Idle > 20 min: {row['pct_long_idle']:.1f}%<br>"
        f"Avg energy: {row['avg_energy_kwh']:.1f} kWh"
    )


def add_metric_layer(m, stations, column, caption, colors, show=False):
    """Circle markers: size = number of events, colour = `column`."""
    cmap = LinearColormap(colors, vmin=stations[column].min(), vmax=stations[column].max(), caption=caption)
    layer = folium.FeatureGroup(name=caption, show=show)
    max_events = stations["n_events"].max()
    for _, row in stations.sort_values("n_events", ascending=False).iterrows():
        folium.CircleMarker(
            location=(row.geometry.y, row.geometry.x),
            radius=_radius(row["n_events"], max_events),
            color="black", weight=1, fill=True,
            fill_color=cmap(row[column]), fill_opacity=0.8,
            tooltip=folium.Tooltip(_tooltip(row)),
        ).add_to(layer)
    layer.add_to(m)
    cmap.add_to(m)


def add_heatmap_layer(m, stations):
    """Density of charging events (stations weighted by number of events)."""
    HeatMap(
        stations[["lat", "lon", "n_events"]].values.tolist(), name="Heatmap of charging events",
        radius=25, blur=20, show=False,
    ).add_to(m)


def add_yearly_layers(m, df, stations):
    """One toggleable layer per year with events per station."""
    counts = df.groupby(["year", "Station Name"]).size().rename("n").reset_index()
    counts = counts.merge(stations[["Station Name", "short_name", "lat", "lon"]], on="Station Name")
    max_n = counts["n"].max()
    for year, sub in counts.groupby("year"):
        layer = folium.FeatureGroup(name=f"Events in {year}", show=False)
        for _, row in sub.iterrows():
            folium.CircleMarker(
                location=(row["lat"], row["lon"]), radius=_radius(row["n"], max_n),
                color="steelblue", weight=1, fill=True, fill_opacity=0.6,
                tooltip=f"{row['short_name']}: {row['n']:,} events in {year}",
            ).add_to(layer)
        layer.add_to(m)


def build_map(df, stations) -> folium.Map:
    centre = stations.attrs["center_latlon"]
    m = folium.Map(location=(centre.y, centre.x), zoom_start=14, tiles="OpenStreetMap")

    add_metric_layer(m, stations, "n_events", "Number of events", ["#fee8c8", "#e34a33", "#7f0000"], show=True)
    add_metric_layer(m, stations, "pct_long_idle", "Sessions with idle > 20 min [%]", ["#ffffb2", "#fd8d3c", "#bd0026"])
    add_metric_layer(m, stations, "avg_energy_kwh", "Average energy per session [kWh]", ["#f7fcb9", "#31a354", "#006837"])
    add_heatmap_layer(m, stations)
    add_yearly_layers(m, df, stations)

    folium.Marker(
        (centre.y, centre.x), tooltip="Usage-weighted centre of stations",
        icon=folium.Icon(color="blue", icon="star"),
    ).add_to(m)
    folium.LayerControl(collapsed=False).add_to(m)
    return m


def main():
    df = load_data()
    stations = add_spatial_features(build_station_gdf(df))

    print(f"{len(stations)} stations, {len(df):,} sessions")
    cols = ["short_name", "n_events", "n_ports", "pct_long_idle", "avg_energy_kwh",
            "nearest_station_m", "n_within_250m", "dist_to_center_m"]
    print(stations.sort_values("n_events", ascending=False)[cols].head(10).round(1).to_string(index=False))
    for col in ["dist_to_center_m", "nearest_station_m"]:
        rho = stations[[col, "n_events"]].corr(method="spearman").iloc[0, 1]
        print(f"Spearman correlation of n_events with {col}: {rho:.2f}")

    os.makedirs(OUT_DIR, exist_ok=True)
    stations.drop(columns="geometry").to_csv(os.path.join(OUT_DIR, "station_summary.csv"), index=False)
    stations.to_file(os.path.join(OUT_DIR, "stations.geojson"), driver="GeoJSON")
    build_map(df, stations).save(os.path.join(OUT_DIR, "station_map.html"))
    print(f"Saved outputs to {OUT_DIR}/")


if __name__ == "__main__":
    main()
