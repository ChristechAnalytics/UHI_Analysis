# Urban Heat Island (UHI) Effect Analysis — Lagos State, Nigeria

Analysis of the **Urban Heat Island effect** in Lagos State using **real 2024 temperature data**: an urban point in Ikeja (Lagos mainland) compared against a rural point in Epe, a predominantly agrarian LGA in eastern Lagos State — cross-checked against a real weather station before drawing any conclusions.

![Urban vs rural temperature trend](images/urban_vs_rural_trend.png)

## Data sources

There is no public rural weather station near Lagos, so this project combines two real, freely available sources rather than relying on simulated data:

| Source | What it provides | Access |
|---|---|---|
| [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api) (ERA5-Land reanalysis, ECMWF) | Daily max/min/mean temperature at the urban and rural points | Free, no API key |
| [NOAA GHCN-Daily](https://www.ncei.noaa.gov/pub/data/ghcn/daily/), station `NIM00065201` | Real observations from Murtala Muhammed International Airport, Lagos | Free, public archive |

ERA5-Land is a reanalysis product — real observations, satellite data, and a physical land-surface model blended onto a ~9 km grid — used here for both points since no public ground station exists in rural Lagos State. To make sure that stand-in is trustworthy, the ERA5-Land series for the urban point is validated directly against the real NOAA station at almost the same location before it's used for anything else (see [notebook section 2](notebooks/uhi_lagos_analysis.ipynb)).

The full pipeline is reproducible with one command:

```bash
python scripts/fetch_data.py
```

which pulls both sources fresh and rebuilds `data/lagos_uhi_2024.csv` and `data/lagos_airport_station_2024.csv`.

## Key findings

| Metric | Value |
|---|---|
| Validation: ERA5-Land vs. real station (TMax) | MAE 1.36°C, r = 0.90 |
| Validation: ERA5-Land vs. real station (TMin) | MAE 1.02°C, r = 0.63 |
| Average daytime UHI effect (urban TMax − rural TMax) | +0.91°C |
| Maximum daytime UHI effect | +3.20°C |
| Average nighttime difference (urban TMin − rural TMin) | −0.21°C |
| Days urban daytime high exceeds rural | 311 / 366 (~85%) |

**The UHI effect here is a daytime signal, not a 24-hour one, and it has a strong seasonal pattern.** Daytime highs in Ikeja run about 0.9°C above Epe on average — but that effect is **2–3x stronger in the dry season (Nov–May, up to +2.3°C in December) than in the rainy season (Jun–Oct, as low as +0.2°C)**, likely because rainy-season cloud cover and evaporative cooling narrow the gap almost everywhere. Nighttime lows show no equivalent urban warming at this resolution — in fact Ikeja runs marginally *cooler* than Epe overnight on average, the opposite of the classic "city traps heat overnight" pattern, possibly reflecting a coastal moderating effect or the weaker nighttime accuracy of the reanalysis (see validation above).

<p float="left">
  <img src="images/diurnal_uhi_effect.png" width="49%" alt="UHI effect by time of day" />
  <img src="images/monthly_uhi_effect.png" width="49%" alt="Daytime UHI effect by month" />
</p>

## Why this matters more than it might look

A naive urban-vs-rural comparison could easily have reported a single flat number and moved on. Splitting the analysis by time of day and by season surfaced two findings that would otherwise have been hidden: the effect is concentrated in daytime hours, and it swings by more than 2°C across the year depending on season. That's the kind of nuance real data forces you to deal with — a synthetic dataset would never have raised these questions in the first place.

## Limitations & next steps

- **Spatial resolution**: ERA5-Land's ~9 km grid cells blend urban and surrounding land cover, diluting the true urban heat signal compared to ground-level conditions in central Lagos. Satellite land-surface temperature (MODIS MOD11A2 or Landsat 8/9 thermal bands, both accessible via Google Earth Engine) would resolve intra-city variation far better and is the natural next iteration of this project.
- **Two-point comparison**: this compares one urban and one rural point, not a full urban-vs-rural land-cover classification across Lagos State.
- **Single rural proxy**: Epe was chosen as a genuinely agrarian LGA, but its own proximity to the Lagos Lagoon may moderate its temperatures in ways that don't generalize to all rural areas of the state.
- **Nighttime validation gap**: weaker station agreement for TMin (r ≈ 0.63) means the nighttime finding should be treated as a hypothesis pending better nighttime data, not a settled result.
- **One year of data**: 2024 alone can't separate a genuine climatological pattern from one year's weather variability.

## Project structure

```
UHI_Analysis/
├── data/
│   ├── raw/                              # untouched API/station responses
│   │   ├── era5_urban_ikeja.json
│   │   ├── era5_rural_epe.json
│   │   └── lagos_airport_ghcn.csv.gz
│   ├── lagos_uhi_2024.csv                # merged, analysis-ready urban/rural dataset
│   └── lagos_airport_station_2024.csv    # real station observations, for validation
├── scripts/
│   └── fetch_data.py                     # reproducible pull from Open-Meteo + NOAA
├── notebooks/
│   └── uhi_lagos_analysis.ipynb          # full analysis notebook
├── images/                                # exported charts (used in this README)
├── requirements.txt
└── README.md
```

## How to run

```bash
git clone https://github.com/ChristechAnalytics/UHI_Analysis.git
cd UHI_Analysis
pip install -r requirements.txt
python scripts/fetch_data.py          # optional: refresh the data from source
jupyter notebook notebooks/uhi_lagos_analysis.ipynb
```

## Tech stack

Python, pandas, NumPy, Matplotlib, Seaborn, Jupyter — Open-Meteo (ERA5-Land) and NOAA GHCN-Daily as data sources.

## Author

Christopher Onyeneke — [Christech Analytics](https://github.com/ChristechAnalytics)
