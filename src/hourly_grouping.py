import pandas as pd
import numpy as np

def build_session_hours(df: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    """Split every session into the clock hours it covers (one row per session and hour).

    Input: the cleaned dataframe returned by `preprocess()`.

    For every piece:
      occupied_h - part of the plug-in interval [start, start + Total Duration) in that hour
      charging_h - part of the charging interval [start, start + Charging Time) in that hour
      energy_kwh - session energy shared out in proportion to charging time (idle hours get 0)
      idle_h     - occupied_h - charging_h

    Assumption: charging starts at plug-in and runs without breaks until the charging time is used up.
    Hours are in local time.
    """


    sessions = df[["User ID", "Station Name", "Port Number", "Start Date",
                         "total_duration_sec", "charging_duration_sec", "Energy (kWh)"]].reset_index(drop=True)
    sessions["session_id"] = sessions.index

    # plug-in interval: [start, start + Total Duration)  -> exact to the second (End Date has whole minutes only)
    start = sessions["Start Date"].values
    end = start + pd.to_timedelta(sessions["total_duration_sec"], unit="s").values
    charge_end = start + pd.to_timedelta(sessions["charging_duration_sec"], unit="s").values
    first_hour = sessions["Start Date"].dt.floor("h").values

    one_hour = np.timedelta64(1, "h")
    n_hours = np.ceil((end - first_hour) / one_hour).astype(int)        # clock hours touched by each session
    row = np.repeat(np.arange(len(sessions)), n_hours)                  # session position, once per hour
    offset = np.arange(len(row)) - np.repeat(np.cumsum(n_hours) - n_hours, n_hours)  # 0, 1, 2, ... per session

    hour_start = first_hour[row] + offset * one_hour
    hour_end = hour_start + one_hour
    overlap_start = np.maximum(start[row], hour_start)
    occupied_sec = (np.minimum(end[row], hour_end) - overlap_start) / np.timedelta64(1, "s")
    charging_sec = np.clip(
        (np.minimum(charge_end[row], hour_end) - overlap_start) / np.timedelta64(1, "s"), 0, None
    )

    charging_total = sessions["charging_duration_sec"].values[row]
    energy = np.where(
        charging_total > 0,
        sessions["Energy (kWh)"].values[row] * charging_sec / np.where(charging_total > 0, charging_total, 1),
        0.0,
    )

    session_hours = pd.DataFrame({
        "session_id": sessions["session_id"].values[row],
        "User ID": sessions["User ID"].values[row],
        "Station Name": sessions["Station Name"].values[row],
        "hour": hour_start,
        "occupied_h": occupied_sec / 3600,
        "charging_h": charging_sec / 3600,
        "energy_kwh": energy,
    })
    session_hours["idle_h"] = session_hours["occupied_h"] - session_hours["charging_h"]

    # sanity checks: nothing is lost or created by the split
    assert np.isclose(session_hours["energy_kwh"].sum(), sessions["Energy (kWh)"].sum()), "energy does not match"
    assert np.isclose(session_hours["occupied_h"].sum(), sessions["total_duration_sec"].sum() / 3600), "plug-in time does not match"
    assert (session_hours["idle_h"] >= -1e-9).all(), "negative idle time"

    if verbose:
        print(f"Hourly rows: {len(session_hours):,} "
              f"(on average {len(session_hours) / len(sessions):.1f} hours per session)")
    return session_hours