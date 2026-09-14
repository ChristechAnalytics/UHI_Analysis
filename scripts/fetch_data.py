"""
Pull the real data used in this project and rebuild data/lagos_uhi_2024.csv
and data/lagos_airport_station_2024.csv from source.

Sources (all public, no API key required):
  - Open-Meteo Historical Weather API (ERA5-Land reanalysis, ECMWF)
    https://open-meteo.com/en/docs/historical-weather-api
    Used for daily temperatures at an urban point (Ikeja / Lagos mainland)
    and a rural point (Epe, a predominantly agrarian LGA in eastern Lagos
    State), since no public rural ground station exists near Lagos.
  - NOAA GHCN-Daily (real station observations)
    https://www.ncei.noaa.gov/pub/data/ghcn/daily/
    Station NIM00065201 = Murtala Muhammed International Airport, Lagos.
    Used to validate the ERA5-Land urban series against real observations.

Run from the repository root:
    python scripts/fetch_data.py
"""
import csv
import gzip
import json
import shutil
from pathlib import Path
from urllib.request import urlretrieve

import pandas as pd

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

URBAN_LAT, URBAN_LON = 6.5774, 3.3210   # Ikeja / Lagos mainland (matches the airport station)
RURAL_LAT, RURAL_LON = 6.5833, 3.9833   # Epe, Lagos State
START, END = "2024-01-01", "2024-12-31"
GHCN_STATION = "NIM00065201"


def fetch_era5(lat, lon, out_path):
    url = (
        "https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={lat}&longitude={lon}&start_date={START}&end_date={END}"
        "&daily=temperature_2m_max,temperature_2m_min,temperature_2m_mean"
        "&timezone=Africa%2FLagos"
    )
    urlretrieve(url, out_path)


def fetch_ghcn_station(station_id, out_path_gz):
    url = f"https://www.ncei.noaa.gov/pub/data/ghcn/daily/by_station/{station_id}.csv.gz"
    urlretrieve(url, out_path_gz)


def build_uhi_dataset():
    with open(RAW_DIR / "era5_urban_ikeja.json") as f:
        urban_json = json.load(f)
    with open(RAW_DIR / "era5_rural_epe.json") as f:
        rural_json = json.load(f)

    urban_df = pd.DataFrame(urban_json["daily"]).rename(
        columns={
            "time": "Date",
            "temperature_2m_max": "Urban_TMax",
            "temperature_2m_min": "Urban_TMin",
            "temperature_2m_mean": "Urban_Temperature",
        }
    )
    rural_df = pd.DataFrame(rural_json["daily"]).rename(
        columns={
            "time": "Date",
            "temperature_2m_max": "Rural_TMax",
            "temperature_2m_min": "Rural_TMin",
            "temperature_2m_mean": "Rural_Temperature",
        }
    )

    merged = urban_df.merge(rural_df, on="Date")
    merged["Date"] = pd.to_datetime(merged["Date"])
    merged["Temperature_Difference"] = merged["Urban_Temperature"] - merged["Rural_Temperature"]
    merged = merged[
        [
            "Date",
            "Urban_Temperature",
            "Rural_Temperature",
            "Temperature_Difference",
            "Urban_TMax",
            "Urban_TMin",
            "Rural_TMax",
            "Rural_TMin",
        ]
    ]
    merged.to_csv("data/lagos_uhi_2024.csv", index=False)
    print(f"Saved data/lagos_uhi_2024.csv ({len(merged)} rows)")


def build_station_dataset():
    gz_path = RAW_DIR / "lagos_airport_ghcn.csv.gz"
    csv_path = RAW_DIR / "lagos_airport_ghcn.csv"
    with gzip.open(gz_path, "rb") as f_in, open(csv_path, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)

    rows = []
    with open(csv_path) as f:
        for station, date, element, value, *_ in csv.reader(f):
            if date.startswith("2024") and element in ("TMAX", "TMIN", "TAVG"):
                rows.append((date, element, int(value) / 10.0))

    station_df = pd.DataFrame(rows, columns=["Date", "Element", "Value"])
    station_df["Date"] = pd.to_datetime(station_df["Date"], format="%Y%m%d")
    station_pivot = station_df.pivot_table(index="Date", columns="Element", values="Value").reset_index()
    station_pivot.to_csv("data/lagos_airport_station_2024.csv", index=False)
    print(f"Saved data/lagos_airport_station_2024.csv ({len(station_pivot)} rows)")

    csv_path.unlink()  # keep only the compressed raw file; the full multi-decade CSV is derived


if __name__ == "__main__":
    print("Fetching ERA5-Land reanalysis (Open-Meteo)...")
    fetch_era5(URBAN_LAT, URBAN_LON, RAW_DIR / "era5_urban_ikeja.json")
    fetch_era5(RURAL_LAT, RURAL_LON, RAW_DIR / "era5_rural_epe.json")

    print("Fetching real NOAA GHCN-Daily station data (Murtala Muhammed Intl)...")
    fetch_ghcn_station(GHCN_STATION, RAW_DIR / "lagos_airport_ghcn.csv.gz")

    build_uhi_dataset()
    build_station_dataset()
