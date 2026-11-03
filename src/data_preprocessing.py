"""
All steps are taken from the notebook but put here for notebook clarity.

A complete pipeline taking raw data and returning a cleaned version. 

Steps:
1. Clean IDs (348.0 -> 348 etc)
2. Clean station name - remove PALO ALTO and # 
3. Clean address 
4. COnvert date columns to dates; test if Total duration = End Date - Start Date (if not, then drop; 1 min tolerance)
5. Delete irrelevant columns 
6. Remove rows in foreign currencies 
7. MAC cleaning by removing : 
8. Evse ID and System S/N imputation from MAC
9. Missing values in categorical columns imputation with 'missing'
10. Remove rows where start date zone != end date zone 
11. Additional features such as total_duration_sec/h, charging_duration_sec/h, idle_sec/h,  time of day, day of week, etc
12. Removing failed sessions, i.e impossible plugins (only for a few seconds), no energy etc 
"""

from __future__ import annotations

import numpy as np
import pandas as pd


ID_COLS = ["User ID", "EVSE ID", "System S/N", "Driver Postal Code", "Postal Code"]
DATE_COLS = ["Start Date", "End Date", "Transaction Date (Pacific Time)"]

FOREIGN_CURRENCIES = ["MXN", "EUR", "CAD"]

# Country: same value in every row | Plug Type: duplicates Port Type |
# Org Name: one organisation (with/without trailing space) | Currency: only USD left |
# City, State/Province: constant
REDUNDANT_COLS = ["Country", "Plug Type", "Org Name", "Currency", "City", "State/Province"]

STATION_NAME_PREFIX = "PALO ALTO CA / "


CATEGORICAL_FILL_COLS = [
    "County", "Model Number", "User ID", "Ended By",
    "Port Type", "EVSE ID", "Driver Postal Code", "Postal Code",
]

# columns filled from other rows with the same MAC address
FILL_FROM_MAC_COLS = ["EVSE ID", "Model Number"]

TZ_OFFSETS_H = {"UTC": 0, "PST": -8, "PDT": -7}

# allowed difference between "Total Duration" and (End Date - Start Date), in seconds
DURATION_TOLERANCE_SEC = 60

TIME_OF_DAY_LABELS = ["Night", "Morning", "Afternoon", "Evening"]




def standardize_id(ids: pd.Series) -> pd.Series:
    """Return IDs as strings without the trailing '.0' added when pandas read them as floats.
    """
    return (
        ids
        .astype("string")
        .str.strip()
        .str.replace(r"^(-?\d+)\.0$", r"\1", regex=True)
    )


def clean_station_name(names: pd.Series) -> pd.Series:
    """Remove the 'PALO ALTO CA / ' prefix and the '#' (e.g. 'BRYANT # 1' -> 'BRYANT 1')."""
    return (
        names
        .str.removeprefix(STATION_NAME_PREFIX)
        .str.replace(r"\s*#\s*", " ", regex=True)
        .str.strip()
    )


def normalize_mac(macs: pd.Series) -> pd.Series:
    """Keep only the hex digits, in upper case: '000D:6F00:015A:9D76' -> '000D6F00015A9D76'."""
    return macs.str.replace(r"[^0-9A-Fa-f]", "", regex=True).str.upper()


def fill_from_mac(df: pd.DataFrame, col: str) -> pd.Series:
    """Fill missing values of `col` from other rows with the same MAC, if that MAC only ever has one value."""
    known = df.dropna(subset=[col])
    values_per_mac = known.groupby("MAC Address")[col].nunique()
    one_value = values_per_mac[values_per_mac == 1].index
    mapping = known[known["MAC Address"].isin(one_value)].groupby("MAC Address")[col].first()
    return df[col].fillna(df["MAC Address"].map(mapping))

# Actual functions on the dataset 

def convert_ids_to_string(df: pd.DataFrame) -> pd.DataFrame:
    """IDs and technical IDs are identifiers, not numbers -> strings."""
    df = df.copy()
    for col in ID_COLS:
        df[col] = standardize_id(df[col])
    return df


def parse_dates_and_drop_invalid(df: pd.DataFrame) -> pd.DataFrame:
    """Convert date columns to datetime and drop rows where any of them is invalid or missing."""
    df = df.copy()
    for col in DATE_COLS:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    n0 = len(df)
    df = df.dropna(subset=DATE_COLS)
    print(f"  dropped {n0 - len(df)} rows with invalid or missing dates")
    return df


def drop_redundant_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Remove non-USD sessions, then drop columns that add no information."""
    n0 = len(df)
    df = df[~df["Currency"].isin(FOREIGN_CURRENCIES)]
    print(f"  dropped {n0 - len(df)} rows with currency {', '.join(FOREIGN_CURRENCIES)}")
    df = df.drop(columns=REDUNDANT_COLS)
    print(f"  dropped columns: {REDUNDANT_COLS}")
    return df


def clean_station_names(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Station Name"] = clean_station_name(df["Station Name"])
    return df


def clean_addresses(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Address 1"] = (
        df["Address 1"]
        .str.replace(r"\s+", " ", regex=True)   # '528  High St' -> '528 High St'
        .str.title()                            # '528 high st' -> '528 High St'
        .str.rstrip(".")                        # '528 High St.' -> '528 High St'
        .str.strip()                            # leading/trailing spaces (last, so nothing is left behind)
        .replace({"Bryant St": "445 Bryant St"})
    )
    return df


def normalize_mac_addresses(df: pd.DataFrame) -> pd.DataFrame:
    """Two MAC formats ('0024:B100:0002:1329' and '000D6F0000A2108E') -> hex digits only, upper case."""
    df = df.copy()
    df["MAC Address"] = normalize_mac(df["MAC Address"])
    return df


def fill_hardware_details_from_mac(df: pd.DataFrame) -> pd.DataFrame:
    """EVSE ID and Model Number were only recorded from Aug 2016; copy them back to earlier sessions of the same MAC."""
    df = df.copy()
    for col in FILL_FROM_MAC_COLS:
        n0 = df[col].isna().sum()
        df[col] = fill_from_mac(df, col)
        print(f"  {col}: filled {n0 - df[col].isna().sum():,} of {n0:,} missing, {df[col].isna().sum():,} still missing")
    return df


def drop_system_serial(df: pd.DataFrame) -> pd.DataFrame:
    """System S/N is stored in scientific notation (rounded to 6 digits) -> unreliable, hardware is identified by MAC and EVSE ID."""
    return df.drop(columns=["System S/N"])


def fill_missing_categoricals(df: pd.DataFrame) -> pd.DataFrame:
    """Missing values of categorical features become the category 'missing'."""
    df = df.copy()
    for col in CATEGORICAL_FILL_COLS:
        df[col] = df[col].astype("string").str.strip().fillna("missing")
    return df


def add_utc_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Local time -> UTC, using the time zone reported next to each date (UTC / PST / PDT)."""
    df = df.copy()
    df["Start Date UTC"] = df["Start Date"] - pd.to_timedelta(df["Start Time Zone"].map(TZ_OFFSETS_H), unit="h")
    df["End Date UTC"] = df["End Date"] - pd.to_timedelta(df["End Time Zone"].map(TZ_OFFSETS_H), unit="h")
    return df


def drop_timezone_mismatch(df: pd.DataFrame) -> pd.DataFrame:
    """Sessions whose start and end time zones differ are most likely incorrect."""
    n0 = len(df)
    df = df[df["Start Time Zone"] == df["End Time Zone"]]
    print(f"  dropped {n0 - len(df)} rows where start and end time zones are different")
    return df


def build_duration_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    - convert the hh:mm:ss columns to seconds,
    - drop sessions where Total Duration differs from (End Date - Start Date) by more than 1 minute
      (or cannot be compared),
    - charging time can not be longer than total time,
    - add duration columns in hours and the idle time (= total - charging).
    """
    df = df.copy()
    n0 = len(df)

    df["total_duration_sec"] = pd.to_timedelta(df["Total Duration (hh:mm:ss)"], errors="coerce").dt.total_seconds()
    df["charging_duration_sec"] = pd.to_timedelta(df["Charging Time (hh:mm:ss)"], errors="coerce").dt.total_seconds()

    timestamp_duration_sec = (df["End Date"] - df["Start Date"]).dt.total_seconds()
    duration_diff_sec = (timestamp_duration_sec - df["total_duration_sec"]).abs()

    df = df[duration_diff_sec.notna() & (duration_diff_sec <= DURATION_TOLERANCE_SEC)].copy()
    print(f"  dropped {n0 - len(df)} rows with missing or inconsistent duration "
          f"(difference > {DURATION_TOLERANCE_SEC} s)")

    # Total Duration has up to 1 min error, so make sure charging is not longer than total
    df["charging_duration_sec"] = df[["charging_duration_sec", "total_duration_sec"]].min(axis=1)

    df["total_duration_hours"] = df["total_duration_sec"] / 3600
    df["charging_duration_hours"] = df["charging_duration_sec"] / 3600

    df["idle_seconds"] = df["total_duration_sec"] - df["charging_duration_sec"]
    df["idle_hours"] = df["idle_seconds"] / 3600
    return df


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """start_hour, time_of_day (Night/Morning/Afternoon/Evening), year, month, day_of_week (0 = Monday)."""
    df = df.copy()
    df["start_hour"] = df["Start Date"].dt.hour

    conditions = [
        df["start_hour"].between(0, 5),
        df["start_hour"].between(6, 11),
        df["start_hour"].between(12, 17),
        df["start_hour"].between(18, 23),
    ]
    df["time_of_day"] = np.select(conditions, TIME_OF_DAY_LABELS, default=None)

    df["year"] = df["Start Date"].dt.year
    df["month"] = df["Start Date"].dt.month
    df["day_of_week"] = df["Start Date"].dt.dayofweek
    return df


def check_start_before_end(df: pd.DataFrame) -> pd.DataFrame:
    """Consistency test"""
    n_bad = int((df["Start Date"] > df["End Date"]).sum())
    if n_bad:
        print(f"  WARNING: {n_bad} rows with Start Date later than End Date")
    else:
        print("  OK: no rows with Start Date later than End Date")
    return df


def remove_failed_sessions(df: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    """Drop failed plug-ins and physically impossible sessions (see "Outliers" in the EDA and "Step 1" of Idea 2).

    In the notebook these sessions are KEPT in `df` for the EDA and removed only before building
    the hourly tables (clustering / prediction). Call this yourself when you need that version:

        sessions = remove_failed_sessions(df)

    Removed: plugged in < 2 min, energy < 0.1 kWh, or charging power > 7.2 kW.
    Very long sessions (> 24 h) are kept on purpose (the car really occupied the charger).
    """
    failed_plugin = (df["total_duration_sec"] < 120) | (df["Energy (kWh)"] < 0.1)
    impossible_power = df["Energy (kWh)"] / (df["charging_duration_sec"] / 3600) > 7.2
    out = df.loc[~failed_plugin & ~impossible_power].reset_index(drop=True)
    if verbose:
        print(f"Sessions kept: {len(out):,} of {len(df):,} "
              f"(failed plug-ins removed: {failed_plugin.sum():,}, "
              f"impossible power removed: {(impossible_power & ~failed_plugin).sum():,})")
    return out

def drop_duplicate_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Drop duplicated sessions, keeping the first occurrence.]).
    """
    n0 = len(df)
    df = df.drop_duplicates(keep="first")
    print(f"  dropped {n0 - len(df)} duplicated rows")
    return df

# order matters
PIPELINE = [
    ("IDs -> strings", convert_ids_to_string),
    ("parse dates, drop invalid", parse_dates_and_drop_invalid),
    ("drop non-USD sessions and redundant columns", drop_redundant_columns),
    ("clean station names", clean_station_names),
    ("clean addresses", clean_addresses),
    ("normalize MAC addresses", normalize_mac_addresses),
    ("fill EVSE ID / Model Number from MAC", fill_hardware_details_from_mac),
    ("drop System S/N", drop_system_serial),
    ("fill missing categoricals with 'missing'", fill_missing_categoricals),
    ("add UTC columns", add_utc_columns),
    ("drop time zone mismatches", drop_timezone_mismatch),
    ("validate durations and build duration columns", build_duration_columns),
    ("add time features", add_time_features),
    ("check Start <= End", check_start_before_end),
    ("remove outliers", remove_failed_sessions),
    ("drop duplicate rows", drop_duplicate_rows),
]


# --------------------------------------------------------------------------- #
# Main entry point
# --------------------------------------------------------------------------- #

def preprocess(df_raw: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    """Run the whole cleaning pipeline on the raw dataframe and return the cleaned one.
    """
    df = df_raw.copy()
    initial_length = len(df)

    for name, step in PIPELINE:
        if verbose:
            print(f"[{name}]")
        df = step(df)

    if verbose:
        dropped = initial_length - len(df)
        print("-" * 70)
        print(f"Final dataset: {len(df):,} rows x {df.shape[1]} columns")
        print(f"Dropped in total: {dropped:,} rows ({dropped / initial_length:.2%} of the original dataset)")

    return df.reset_index(drop=True)



