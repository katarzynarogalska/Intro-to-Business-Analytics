"""Clean the EV charging station usage data (same steps as section 1.1 of main.ipynb)."""
import sys

import numpy as np
import pandas as pd

RAW_PATH = "datasets/EVChargingStationUsage.csv"
CLEAN_PATH = "datasets/EVChargingStationUsage_cleaned.csv"

DATE_COLS = ['Start Date', 'End Date', 'Transaction Date (Pacific Time)']
CAT_COLS = ['County', 'Model Number', 'User ID', 'Currency', 'Ended By', 'Port Type',
            'EVSE ID', 'System S/N', 'Driver Postal Code', 'Postal Code']
TZ_OFFSETS = {"UTC": 0, "PST": -8, "PDT": -7}
TOL_MIN = 1.0  # tolerance (minutes) when checking Total Duration against End - Start


def clean(df: pd.DataFrame) -> pd.DataFrame:
    initial_length = len(df)

    # convert date columns to datetime and drop rows with invalid dates
    for col in DATE_COLS:
        df[col] = pd.to_datetime(df[col], errors='coerce')
    n0 = len(df)
    df = df.dropna(subset=DATE_COLS)
    print(f"Dropped {n0 - len(df)} rows with invalid or missing dates.")

    # impute missing categorical values with "missing"
    for col in CAT_COLS:
        df[col] = df[col].astype('string').str.strip().fillna('missing')

    # UTC start / end dates
    df["Start Date UTC"] = df["Start Date"] - pd.to_timedelta(df["Start Time Zone"].map(TZ_OFFSETS), unit="h")
    df["End Date UTC"] = df["End Date"] - pd.to_timedelta(df["End Time Zone"].map(TZ_OFFSETS), unit="h")

    # drop rows where start and end time zones differ
    n0 = len(df)
    df = df[df['Start Time Zone'] == df['End Time Zone']]
    print(f"Dropped {n0 - len(df)} rows where start and end time zones are different.")

    # date features
    df['year'] = df['Start Date'].dt.year
    df['month'] = df['Start Date'].dt.month
    df['day_of_week'] = df['Start Date'].dt.dayofweek  # 0 = Monday, 6 = Sunday

    # durations in seconds and hours
    df["total_duration_sec"] = pd.to_timedelta(df["Total Duration (hh:mm:ss)"], errors="coerce").dt.total_seconds()
    df['charging_duration_sec'] = pd.to_timedelta(df["Charging Time (hh:mm:ss)"], errors="coerce").dt.total_seconds()
    df['total_duration_hours'] = df['total_duration_sec'] / 3600
    df['charging_duration_hours'] = df['charging_duration_sec'] / 3600

    # idle time
    df["idle_seconds"] = df["total_duration_sec"] - df["charging_duration_sec"]
    df['idle_hours'] = df['idle_seconds'] / 3600

    # time of day
    df["start_hour"] = df["Start Date"].dt.hour
    conditions = [
        df["start_hour"].between(0, 5),
        df["start_hour"].between(6, 11),
        df["start_hour"].between(12, 17),
        df["start_hour"].between(18, 23),
    ]
    df["time_of_day"] = np.select(conditions, ["Night", "Morning", "Afternoon", "Evening"], default=None)

    # remove rows where charging time is longer than total duration
    n0 = len(df)
    df = df[df['charging_duration_sec'] <= df['total_duration_sec']].copy()
    print(f"Removed {n0 - len(df)} rows with inconsistent durations, remaining: {len(df)}")

    # remove rows where Total Duration != End Date - Start Date (within tolerance) or End Date is missing
    total = pd.to_timedelta(df['Total Duration (hh:mm:ss)'])
    df['diff_min'] = ((df['End Date UTC'] - df['Start Date UTC']) - total).dt.total_seconds() / 60
    within = df['diff_min'].abs() <= TOL_MIN
    n0 = len(df)
    df = df[within].copy()
    print(f"Removed {n0 - len(df)} rows ({(n0 - len(df)) / n0:.2%}), remaining: {len(df)}")

    dropped = initial_length - len(df)
    print(f"Final size: {len(df)}. Dropped in total: {dropped} rows ({dropped / initial_length:.2%}).")
    return df


if __name__ == "__main__":
    out_path = sys.argv[1] if len(sys.argv) > 1 else CLEAN_PATH
    clean(pd.read_csv(RAW_PATH)).to_csv(out_path, index=False)
    print(f"Saved to {out_path}")
