# Data Dictionary: EV Charging Station Usage (cleaned)

Source: `datasets/EVChargingStationUsage.csv`, cleaned with [`src/clean_data.py`](../src/clean_data.py).

- **Raw data:** 259,415 rows × 33 columns
- **Cleaned data:** 258,693 rows × 47 columns (722 rows dropped, 0.28%)
- **Rows removed during cleaning:**
  - 249 with invalid or missing dates
  - 120 where the start and end time zones differ
  - 45 where charging time is longer than total duration
  - 308 where `Total Duration` differs from `End Date UTC − Start Date UTC` by more than 1 minute
- **Granularity:** one row per charging session (plug-in event) at a City of Palo Alto public charging station, July 2011 to December 2020.

Each charging session is one row. In the cleaned file, missing values in the categorical columns are replaced with the string `"missing"`. The *Missing* column below counts those values.

## Original columns

| # | Column | Description | Type (after cleaning) | Range / distinct values | Missing | Example values |
|---|---|---|---|---|---|---|
| 1 | `Station Name` | Name of the charging station (city / street / station number) | string | 47 distinct stations | 0 | `PALO ALTO CA / HAMILTON #2`, `PALO ALTO CA / WEBSTER #1`, `PALO ALTO CA / TED THOMPSON #3`, `PALO ALTO CA / BRYANT # 1` |
| 2 | `MAC Address` | Hardware MAC address of the charger's network module | string | 83 distinct | 0 | `000D:6F00:015A:9D76`, `0024:B100:0002:1329`, `0024:B100:0002:4213` |
| 3 | `Org Name` | Organisation that owns or operates the station | string | 2 distinct (`City of Palo Alto` with and without a trailing space) | 0 | `City of Palo Alto` |
| 4 | `Start Date` | Local date and time when the session started | datetime | 2011-07-29 20:17 → 2020-12-31 18:19 | 0 | `2016-03-27 19:55`, `2019-01-10 14:46`, `2019-08-07 14:22` |
| 5 | `Start Time Zone` | Time zone of `Start Date` | string (categorical) | `PDT` (166,307), `PST` (92,386) | 0 | `PDT`, `PST` |
| 6 | `End Date` | Local date and time when the session ended (vehicle unplugged) | datetime | 2011-07-29 23:20 → 2021-01-01 10:56 | 0 | `2014-11-07 13:56`, `2017-07-13 12:28`, `2017-11-20 16:37` |
| 7 | `End Time Zone` | Time zone of `End Date` (after cleaning, always the same as `Start Time Zone`) | string (categorical) | `PDT`, `PST` | 0 | `PDT`, `PST` |
| 8 | `Transaction Date (Pacific Time)` | Date and time the transaction was recorded, in Pacific time | datetime | 2011-07-29 23:20 → 2021-01-01 10:57 | 0 | `2015-07-31 15:01`, `2016-12-05 12:55`, `2018-01-10 13:59` |
| 9 | `Total Duration (hh:mm:ss)` | Total time the vehicle was plugged in | string (`h:mm:ss`) | 0:01:00 → 114:32:21 | 0 | `2:09:43`, `4:44:48`, `7:03:40`, `16:43:29` |
| 10 | `Charging Time (hh:mm:ss)` | Time the vehicle was actually drawing power | string (`h:mm:ss`) | 0:00:06 → 22:55:55 | 0 | `1:31:15`, `2:18:42`, `3:36:06`, `4:49:34` |
| 11 | `Energy (kWh)` | Energy delivered to the vehicle in the session | float | 0.01 → 97.36 (mean 8.54, median 6.87) | 0 | `1.657`, `4.032`, `5.642`, `12.975` |
| 12 | `GHG Savings (kg)` | Estimated greenhouse-gas emissions avoided compared with a gasoline car | float | 0.004 → 40.89 (mean 3.59, median 2.89) | 0 | `2.66`, `6.453`, `17.224`, `28.068` |
| 13 | `Gasoline Savings (gallons)` | Estimated gasoline saved compared with a gasoline car | float | 0.001 → 12.22 (mean 1.07, median 0.86) | 0 | `0.03`, `0.862`, `2.41`, `7.739` |
| 14 | `Port Type` | Charging level of the port | string (categorical) | `Level 2` (254,069), `Level 1` (4,623) | 1 | `Level 2`, `Level 1` |
| 15 | `Port Number` | Which port of a dual-port station was used | int | 1 → 2 | 0 | `1`, `2` |
| 16 | `Plug Type` | Connector standard | string (categorical) | `J1772` (254,070), `NEMA 5-20R` (4,623) | 0 | `J1772`, `NEMA 5-20R` |
| 17 | `EVSE ID` | ID of the Electric Vehicle Supply Equipment (charger unit) | string | 52 distinct | 78,633 | `109785.0`, `104427.0`, `27313.0`, `2884001.0` |
| 18 | `Address 1` | Street address of the station | string | 20 distinct | 0 | `250 Hamilton Ave`, `528 High St`, `3700 Middlefield Rd`, `445 Bryant St` |
| 19 | `City` | City of the station | string (constant) | 1 value | 0 | `Palo Alto` |
| 20 | `State/Province` | State of the station | string (constant) | 1 value | 0 | `California` |
| 21 | `Postal Code` | ZIP code of the station | string (categorical) | `94301` (162,658), `94306` (49,553), `94303` (46,482) | 0 | `94301`, `94303`, `94306` |
| 22 | `Country` | Country of the station | string (constant) | 1 value | 0 | `United States` |
| 23 | `Latitude` | Station latitude (WGS84) | float | 37.422104 → 37.449375 (62 distinct) | 0 | `37.448284`, `37.44651`, `37.443378` |
| 24 | `Longitude` | Station longitude (WGS84) | float | −122.163239 → −122.11248 (64 distinct) | 0 | `-122.146065`, `-122.158272`, `-122.16214` |
| 25 | `Currency` | Currency of the fee | string (categorical) | `USD` (257,075), `EUR` (8), `MXN` (5), `CAD` (1) | 1,604 | `USD`, `EUR`, `MXN` |
| 26 | `Fee` | Amount the driver paid for the session | float | 0.00 → 84.56 (mean 1.10, median 0.00; 133,089 sessions are free) | 0 | `0.0`, `1.4`, `3.77`, `10.35` |
| 27 | `Ended By` | What ended the session | string (categorical) | 16 distinct, mostly `Plug Out at Vehicle` (210,352), `Customer` (41,008), `CPS Server` (7,055); the other 13 values are rare faults or events | 11 | `Plug Out at Vehicle`, `Customer`, `CPS Server`, `Door Open`, `Final GFCI Tripped` |
| 28 | `Plug In Event Id` | ID of the plug-in event (a counter per station, so it is not globally unique) | int | 1 → 1,609,436,248 (36,786 distinct) | 0 | `2293`, `9633`, `13210`, `1575752656` |
| 29 | `Driver Postal Code` | ZIP code of the driver's home or registered address | string | 985 distinct | 8,342 | `94301.0`, `94303.0`, `94025.0`, `95125.0` |
| 30 | `User ID` | Anonymised ID of the driver's account | string | 27,668 distinct | 7,631 | `283441`, `196691`, `447577`, `1798361` |
| 31 | `County` | County of the station | string (categorical) | `Santa Clara County` (146,924), `San Mateo County` (27,431) | 84,338 | `Santa Clara County`, `San Mateo County` |
| 32 | `System S/N` | Serial number of the charging system | string | 82 distinct | 78,633 | `142741000000.0`, `164041000000.0`, `170541001572.0` |
| 33 | `Model Number` | ChargePoint hardware model of the charger | string (categorical) | 10 models, top: `CT4020-HD-GW` (84,699), `CT4020-HD` (45,021), `CT2100-HD-CDMA-CCR` (11,343) | 78,633 | `CT4020-HD-GW`, `CT4020-HD`, `CTHDR`, `CT4010-HD-GW` |

## Columns added by `clean_data.py`

| # | Column | Description | Type | Range / distinct values | Missing | Example values |
|---|---|---|---|---|---|---|
| 34 | `Start Date UTC` | `Start Date` converted to UTC (PST = UTC−8, PDT = UTC−7) | datetime | 2011-07-30 03:17 → 2021-01-01 02:19 | 0 | `2016-02-04 21:18`, `2019-08-07 21:22` |
| 35 | `End Date UTC` | `End Date` converted to UTC | datetime | 2011-07-30 06:20 → 2021-01-01 18:56 | 0 | `2014-11-07 21:56`, `2017-11-21 00:37` |
| 36 | `year` | Year of `Start Date` | int | 2011 → 2020 | 0 | `2013`, `2015`, `2019`, `2020` |
| 37 | `month` | Month of `Start Date` | int | 1 → 12 | 0 | `1`, `5`, `6`, `11` |
| 38 | `day_of_week` | Day of week of `Start Date` (0 = Monday … 6 = Sunday) | int | 0 → 6 | 0 | `0`, `3`, `5`, `6` |
| 39 | `total_duration_sec` | `Total Duration` in seconds | float | 60 → 412,341 (mean 8,944, median 7,521) | 0 | `7783.0`, `17088.0`, `25420.0`, `60209.0` |
| 40 | `charging_duration_sec` | `Charging Time` in seconds | float | 6 → 82,555 (mean 7,194, median 6,538) | 0 | `5475.0`, `8322.0`, `12966.0`, `17374.0` |
| 41 | `total_duration_hours` | `Total Duration` in hours | float | 0.017 → 114.54 (mean 2.49, median 2.09) | 0 | `2.162`, `4.747`, `7.061`, `16.725` |
| 42 | `charging_duration_hours` | `Charging Time` in hours | float | 0.0017 → 22.93 (mean 2.00, median 1.82) | 0 | `1.521`, `2.312`, `3.602`, `4.826` |
| 43 | `idle_seconds` | Time plugged in but not charging (`total_duration_sec − charging_duration_sec`) | float | 0 → 405,170 (mean 1,750, median 26) | 0 | `13.0`, `4846.0`, `5176.0`, `14603.0` |
| 44 | `idle_hours` | Idle time in hours | float | 0 → 112.55 (mean 0.49, median 0.007) | 0 | `0.0036`, `1.346`, `1.438`, `4.056` |
| 45 | `start_hour` | Hour of `Start Date` (local time) | int | 0 → 23 | 0 | `5`, `9`, `13`, `23` |
| 46 | `time_of_day` | Part of the day the session started: Night 0–5, Morning 6–11, Afternoon 12–17, Evening 18–23 | string (categorical) | `Afternoon` (107,342), `Morning` (95,634), `Evening` (50,180), `Night` (5,537) | 0 | `Morning`, `Afternoon`, `Evening`, `Night` |
| 47 | `diff_min` | Helper column: `(End Date UTC − Start Date UTC) − Total Duration`, in minutes. Used only to filter rows. | float | −1.0 → 1.0 (cleaning keeps only \|diff\| ≤ 1) | 0 | `-0.167`, `0.0`, `0.533`, `0.833` |

## Notes and data-quality issues

- **Columns with a single value:** `City`, `State/Province` and `Country` hold the same value in every row and tell you nothing about individual sessions. `Org Name` has only one real value; the second variant is the same name with a trailing space.
- **The same 78,633 rows are missing `EVSE ID`, `System S/N` and `Model Number`.** These are most likely the older sessions, recorded before the hardware metadata was logged.
- **`County` is missing in 84,338 rows (about 33%).** Palo Alto is in Santa Clara County, so the `San Mateo County` values are probably taken from the location of the user's account rather than the station.
- **ID columns were read as floats, so their values end in `.0`:** `EVSE ID`, `System S/N`, `Driver Postal Code` and some `User ID` values. In `System S/N` the float conversion also lost precision: many serials end in `000000`.
- **`Total Duration` and `Charging Time`** are kept as text. Use the `*_sec` or `*_hours` columns for numeric work.
- **Idle time is right-skewed.** The median is about 26 seconds, but a few sessions stay plugged in for days, up to about 112 hours.
- **`Fee` is 0 for about 51% of sessions.** Charging at these stations was free during part of the period.
- **`Plug In Event Id` is not a unique key.** It is a counter per station, and the same value can appear for different sessions.
