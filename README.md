# F1 2023 Season Analytics — MSBA 305 Final Project

**Live Dashboard:** [msba305f1project.onrender.com](https://msba305f1project.onrender.com)

An end-to-end data pipeline and interactive analytics dashboard built on the 2023 Formula 1 season race results. Built for MSBA 305 – Data Processing Frameworks.

---

## Dashboard

The interactive dashboard is built with Dash + Plotly and features:

- **Championship Overview** — constructor standings and season summary KPIs
- **Driver Championship** — points standings bar chart across all drivers
- **Season Progression** — cumulative points over the race calendar
- **Qualifying Impact** — grid position vs. finish position analysis
- **Reliability Analysis** — DNF and mechanical failure breakdown by team
- **Circuit Competitiveness** — P1–P2 gap by track to measure race tightness

---

## Repository Structure

```
├── dashboard/
│   └── f1_dashboard.py        # Dash app (deployed to Render)
├── data/
│   ├── df_master.csv          # Master race results dataset
│   ├── Formula1_2023season_raceResults.csv
│   ├── JSON-F1-full (1).json
│   └── f1_circuits.xml
├── notebooks/
│   ├── F1_2023_Full_Pipeline.ipynb      # Full ETL pipeline
│   ├── F1_2023_Analytics_Dashboard.ipynb
│   ├── Amira_sql.ipynb                  # SQL-based analysis
│   ├── Carmen_F1notebook.ipynb
│   └── carmen-EDA.ipynb
├── docs/
│   ├── access_control_design.md
│   ├── MSBA 305 - Spring 2025 2026 - Course Project.pdf
│   └── MSBA305- F1 project proposal.docx
└── requirements.txt
```

---

## Running Locally

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cd dashboard
python f1_dashboard.py
```

Then open [http://localhost:8050](http://localhost:8050).

---

## Stack

| Layer | Technology |
|---|---|
| Data processing | Python, Pandas, NumPy |
| SQL queries | SQLite (in-memory) |
| Visualizations | Plotly |
| Dashboard framework | Dash + Dash Bootstrap Components |
| Hosting | Render.com |
