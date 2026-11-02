# Data Dictionary: EV Charging Station Usage (raw)

Source: `datasets/EVChargingStationUsage.csv`, as loaded with `pd.read_csv(..., low_memory=False)` and before any cleaning. For the cleaned version, see [`data_dictionary.md`](data_dictionary.md).

- **Raw data:** 259,415 rows × 33 columns
- **Exact duplicate rows:** 4
- **Granularity:** one row per charging session (plug-in event) at a City of Palo Alto public charging station, July 2011 to December 2020.

Each charging session is one row. *Missing* counts real empty cells (`NaN`). Nothing has been imputed yet.

## Columns

| # | Column | Description | Type (as read) | Range / distinct values | Missing | Example values |
|---|---|---|---|---|---|---|
| 1 | `Station Name` | Name of the charging station (city / street / station number) | string | 47 distinct stations (one name is spelled differently: `BRYANT # 1` vs `BRYANT #1`) | 0 | `PALO ALTO CA / HAMILTON #2`, `PALO ALTO CA / WEBSTER #1`, `PALO ALTO CA / BRYANT # 1` |
| 2 | `MAC Address` | Hardware MAC address of the charger's network module | string | 83 distinct; two formats: with colons (222,067 rows) and without (37,348 rows) | 0 | `000D:6F00:015A:9D76`, `0024:B100:0002:1329`, `000D6F0000A2108E` |
| 3 | `Org Name` | Organisation that owns or operates the station | string | 2 distinct: `City of Palo Alto ` with a trailing space (236,865) and `City of Palo Alto` (22,550) | 0 | `City of Palo Alto ` |
| 4 | `Start Date` | Local date and time when the session started | string (`M/D/YYYY H:MM`) | 2011-07-29 20:17 → 2020-12-31 18:19; all values parse | 0 | `10/20/2011 14:41`, `1/29/2016 10:47`, `5/10/2019 18:26` |
| 5 | `Start Time Zone` | Time zone of `Start Date` | string (categorical) | `PDT` (166,763), `PST` (92,621), `UTC` (31) | 0 | `PDT`, `PST`, `UTC` |
| 6 | `End Date` | Local date and time when the session ended (vehicle unplugged) | string (`M/D/YYYY H:MM`) | 2011-07-29 23:20 → 2021-01-04 21:01; 40 values are Excel serial numbers instead of dates | 0 | `10/20/2011 15:32`, `7/29/2020 18:17`, `42845.81041` |
| 7 | `End Time Zone` | Time zone of `End Date` | string (categorical) | `PDT` (166,791), `PST` (92,623), `UTC` (1); differs from `Start Time Zone` in 120 rows | 0 | `PDT`, `PST` |
| 8 | `Transaction Date (Pacific Time)` | Date and time the transaction was recorded, in Pacific time | string (`M/D/YYYY H:MM`) | 2011-07-29 23:20 → 2021-01-04 21:03; the same 40 rows hold Excel serial numbers | 209 | `6/26/2015 9:25`, `9/8/2018 15:46`, `42845.79442` |
| 9 | `Total Duration (hh:mm:ss)` | Total time the vehicle was plugged in | string (`h:mm:ss`) | 0:01:00 → 114:32:21; all values parse | 0 | `0:50:57`, `1:47:25`, `3:49:15` |
| 10 | `Charging Time (hh:mm:ss)` | Time the vehicle was actually drawing power | string (`h:mm:ss`) | 0:00:06 → 22:55:55; all values parse | 0 | `0:50:49`, `1:57:30`, `2:33:29` |
| 11 | `Energy (kWh)` | Energy delivered to the vehicle in the session | float | 0.01 → 97.36 (mean 8.54, median 6.87) | 0 | `3.110018`, `6.095`, `10.447` |
| 12 | `GHG Savings (kg)` | Estimated greenhouse-gas emissions avoided compared with a gasoline car | float | 0.004 → 40.891 (mean 3.59, median 2.89) | 0 | `1.306`, `2.805`, `4.388` |
| 13 | `Gasoline Savings (gallons)` | Estimated gasoline saved compared with a gasoline car | float | 0.001 → 12.219 (mean 1.07, median 0.86) | 0 | `0.39`, `0.838`, `1.311` |
| 14 | `Port Type` | Charging level of the port | string (categorical) | `Level 2` (254,727), `Level 1` (4,679) | 9 | `Level 2`, `Level 1` |
| 15 | `Port Number` | Which port of a dual-port station was used | int | 1 (105,938), 2 (153,477) | 0 | `1`, `2` |
| 16 | `Plug Type` | Connector standard | string (categorical) | `J1772` (254,734), `NEMA 5-20R` (4,681) | 0 | `J1772`, `NEMA 5-20R` |
| 17 | `EVSE ID` | ID of the Electric Vehicle Supply Equipment (charger unit) | float | 51 distinct (3,792 → 5,535,441) | 78,948 | `104427.0`, `109783.0`, `189855.0` |
| 18 | `Address 1` | Street address of the station | string | 20 distinct, including spelling variants of the same address (`528 High St`, `528 high st`, `528 High St.`) | 0 | `250 Hamilton Ave`, `445 Bryant St`, `Bryant St` |
| 19 | `City` | City of the station | string (constant) | 1 value | 0 | `Palo Alto` |
| 20 | `State/Province` | State of the station | string (constant) | 1 value | 0 | `California` |
| 21 | `Postal Code` | ZIP code of the station | int | `94301` (163,195), `94306` (49,630), `94303` (46,590) | 0 | `94301`, `94303`, `94306` |
| 22 | `Country` | Country of the station | string (constant) | 1 value | 0 | `United States` |
| 23 | `Latitude` | Station latitude (WGS84) | float | 37.422104 → 37.449375 (62 distinct) | 0 | `37.426155`, `37.443344`, `37.446583` |
| 24 | `Longitude` | Station longitude (WGS84) | float | −122.163239 → −122.11248 (64 distinct) | 0 | `-122.163231`, `-122.162109`, `-122.146065` |
| 25 | `Currency` | Currency of the fee | string (categorical) | `USD` (257,613), `EUR` (8), `MXN` (5), `CAD` (1) | 1,788 | `USD`, `EUR`, `MXN` |
| 26 | `Fee` | Amount the driver paid for the session | float | 0.00 → 84.56 (mean 1.10, median 0.00; 133,538 sessions are free) | 0 | `0.0`, `1.4`, `2.4` |
| 27 | `Ended By` | What ended the session | string (categorical) | 16 distinct, mostly `Plug Out at Vehicle` (210,721), `Customer` (41,090), `CPS Server` (7,065); the other 13 values are rare faults or events | 248 | `Plug Out at Vehicle`, `Customer`, `Door Open`, `Final GFCI Tripped` |
| 28 | `Plug In Event Id` | ID of the plug-in event (a counter per station, so it is not globally unique) | int | 1 → 1,609,436,248 (36,838 distinct) | 0 | `29`, `6728`, `13374` |
| 29 | `Driver Postal Code` | ZIP code of the driver's home or registered address | float | 985 distinct (1,013 → 99,354; 180 values below 10,000 have lost their leading zero) | 8,402 | `94301.0`, `94538.0`, `95014.0` |
| 30 | `User ID` | Anonymised ID of the driver's account | string | 21,441 distinct; 21 IDs (41 rows) have a `V` suffix | 7,677 | `3421`, `130531`, `21237641`, `263V` |
| 31 | `County` | County of the station | string (categorical) | `Santa Clara County` (147,263), `San Mateo County` (27,487) | 84,665 | `Santa Clara County`, `San Mateo County` |
| 32 | `System S/N` | Serial number of the charging system | float | 81 distinct | 78,948 | `142741000000.0`, `114710012380.0`, `170541000000.0` |
| 33 | `Model Number` | ChargePoint hardware model of the charger | string (categorical) | 10 models, top: `CT4020-HD-GW` (84,886), `CT4020-HD` (45,129), `CT2100-HD-CDMA-CCR` (11,377) | 78,948 | `CT4020-HD-GW`, `CT2000-HD-CCR`, `CTHDR-S` |

## Notes and data-quality issues

- **Dates are stored as text.** `Start Date`, `End Date` and `Transaction Date` are strings in `M/D/YYYY H:MM` format, with no seconds. They need `pd.to_datetime`.
- **40 rows have Excel serial numbers in `End Date` and `Transaction Date`** (e.g. `42845.81041`). They decode to 2017-04-20 (24 rows) and 2017-08-29 (16 rows), always the same day as their `Start Date`, so they could be recovered rather than dropped.
- **31 sessions use `UTC` as their start time zone**, while all other rows are local Pacific time (`PDT`/`PST`). In 120 rows the start and end time zones differ. Most of these (72%) start in March or November, so they are probably sessions that ran across a daylight-saving change.
- **Durations are stored as text** (`h:mm:ss`). The longest session lasted over 114 hours.
- **The same 78,948 rows are missing `EVSE ID`, `System S/N` and `Model Number`.** Hardware metadata is completely missing for 2011–2015 and partly missing for 2016. `County` follows a similar pattern (84,665 missing).
- **ID columns are read as numbers.** `EVSE ID`, `System S/N` and `Driver Postal Code` are floats, so they end in `.0`. `System S/N` lost precision in the source file itself: 96,883 values are stored in scientific notation (e.g. `1.74241E+11`, used 2018 to June 2020) and 4,938 are rounded but written out (e.g. `142741000000`, from September 2020). Only 78,646 values are exact serials. `Postal Code` is an int.
- **The same value is written in different ways:**
  - `Org Name` has a trailing-space variant.
  - `Address 1` uses mixed case and punctuation (`528 High St` / `528 high st` / `528 High St.`).
  - `MAC Address` has two formats.
  - `Station Name` has `BRYANT # 1`.
- **Columns with a single value:** `City`, `State/Province` and `Country` hold the same value in every row.
- **`Port Type` and `Plug Type` are redundant.** Level 1 always uses `NEMA 5-20R` and Level 2 always uses `J1772`, so the 9 missing `Port Type` values can be filled in from `Plug Type`.
- **`GHG Savings` and `Gasoline Savings` are almost exactly proportional to `Energy`** (about 0.42 kg/kWh and 0.1255 gal/kWh), so they add no new information.
- **`Currency`:** 1,788 values are missing, and 14 sessions are in a currency other than USD.
- **`Plug In Event Id` is not a unique key.** The value `657` alone appears 257 times.
- **`Fee` is 0 for about 51% of sessions.**
