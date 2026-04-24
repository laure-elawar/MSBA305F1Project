# F1 2023 Season Analytics — MSBA 305 Final Project

**Live Dashboard:** [msba305f1project.onrender.com](https://msba305f1project.onrender.com)

An end-to-end data pipeline and interactive analytics dashboard built on the 2023 Formula 1 season race results. Built for MSBA 305 – Data Processing Frameworks.

---

## Live Dashboard

The interactive dashboard is deployed at **[msba305f1project.onrender.com](https://msba305f1project.onrender.com)** and features:

- **Championship Overview** — constructor standings and season summary KPIs
- **Driver Championship** — points standings bar chart across all drivers
- **Season Progression** — cumulative points over the race calendar
- **Qualifying Impact** — grid position vs. finish position analysis
- **Reliability Analysis** — DNF and mechanical failure breakdown by team
- **Circuit Competitiveness** — P1–P2 gap by track to measure race tightness

---

## Repository Structure & Navigation

```
MSBA305F1Project/
│
├── dashboard/
│   └── f1_dashboard.py
│
├── data/
│   ├── df_master.csv
│   ├── Formula1_2023season_raceResults.csv
│   ├── JSON-F1-full (1).json
│   └── f1_circuits.xml
│
├── notebooks/
│   ├── F1_2023_Full_Pipeline.ipynb
│   ├── F1_2023_Analytics_Dashboard.ipynb
│   ├── Amira_sql.ipynb
│   ├── Carmen_F1notebook.ipynb
│   └── carmen-EDA.ipynb
│
├── docs/
│   ├── access_control_design.md
│   ├── MSBA 305 - Spring 2025 2026 - Course Project.pdf
│   └── MSBA305- F1 project proposal.docx
│
└── requirements.txt
```

### `dashboard/`

| File | Description |
|---|---|
| `f1_dashboard.py` | The main Dash app. Loads `df_master.csv`, runs all SQL queries via an in-memory SQLite engine, and renders the interactive dashboard. This is the file deployed to Render. Start here to understand the full visualization layer. |

### `data/`

| File | Description |
|---|---|
| `df_master.csv` | **Primary dataset.** 440 rows × 23 columns covering every driver's result across all 22 races of the 2023 season. Columns include `race_date`, `track`, `driver_name`, `team`, `grid_position`, `finish_position`, `points`, `fastest_lap_time`, `status`, and circuit metadata (length, coordinates). This is the single source of truth used by the dashboard and all notebooks. |
| `Formula1_2023season_raceResults.csv` | Raw race results as originally collected, before cleaning and enrichment into `df_master.csv`. |
| `JSON-F1-full (1).json` | Full season data in JSON format — useful for nested or document-style queries. |
| `f1_circuits.xml` | Circuit metadata in XML format, including track length, location, and year opened. |

### `notebooks/`

| File | Description |
|---|---|
| `F1_2023_Full_Pipeline.ipynb` | **Start here for the data pipeline.** Covers the full ETL flow: loading raw sources, cleaning, merging circuit metadata, and producing `df_master.csv`. |
| `F1_2023_Analytics_Dashboard.ipynb` | Prototype of the dashboard visualizations built in Jupyter before being ported to Dash. Shows the chart logic with inline outputs. |
| `Amira_sql.ipynb` | SQL-focused analysis using SQLite. Covers championship standings (points aggregation), DNF rate per team (filtering + aggregation), and other structured queries on the race data. |
| `Carmen_F1notebook.ipynb` | Exploratory analysis focused on driver and team performance trends. Originally written for Colab; adapted for local execution with path fallbacks. |
| `carmen-EDA.ipynb` | Exploratory data analysis (EDA) — distributions, missing value checks, and early descriptive statistics on the raw dataset. |

### `docs/`

| File | Description |
|---|---|
| `access_control_design.md` | Data governance document. Classifies the dataset as PUBLIC (no PII), describes what data is present, and outlines access control considerations. |
| `MSBA 305 - Spring 2025 2026 - Course Project.pdf` | Official course project brief and requirements. |
| `MSBA305- F1 project proposal.docx` | Original project proposal submitted at the start of the semester. |

### Root files

| File | Description |
|---|---|
| `requirements.txt` | Python dependencies: `pandas`, `numpy`, `plotly`, `dash`, `dash-bootstrap-components`, `gunicorn`. Install with `pip install -r requirements.txt`. |

---

## Running Locally

```bash
# 1. Set up environment
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Start the dashboard
cd dashboard
python f1_dashboard.py
```

Then open [http://localhost:8050](http://localhost:8050).

For the notebooks, open Jupyter from the repo root:

```bash
jupyter lab
```

Navigate to `notebooks/` and open any notebook — they all resolve `df_master.csv` from the `data/` folder automatically.

---

## Stack

| Layer | Technology |
|---|---|
| Data processing | Python, Pandas, NumPy |
| SQL queries | SQLite (in-memory) |
| Visualizations | Plotly |
| Dashboard framework | Dash + Dash Bootstrap Components |
| Hosting | Render.com |
