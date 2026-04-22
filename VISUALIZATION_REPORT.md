F1 Visualization & Governance Report

Overview

This report documents the visualization design, implementation artifacts, and governance recommendations for the F1 dataset in this repository. The visualization deliverable is a Streamlit prototype in `visualization/app.py` that consumes the cleaned dataset `df_master-2.csv`.

What I implemented

1. Visualization scaffold
- `visualization/app.py`: Streamlit dashboard prototype with KPI cards, Championship Leaderboard, Cumulative Points timeline, Race Results Explorer, and Circuit Map.
- `visualization/queries.py`: pandas-based helper functions that reproduce the analytical queries in `Amira_sql.ipynb` (top drivers, cumulative points, DNF rate, positions gained).
- `visualization/README.md`: instructions to run the prototype.

2. Governance artifacts
- `data/README.md`: provenance notes and file descriptions.
- `data/manifest.csv`: SHA256 checksums for key files (`df_master-2.csv`, `Formula1_2023season_raceResults.csv`, `JSON-F1-full (1).json`, `f1_circuits.xml`).
- `metadata.yaml`: basic schema and notes (explicitly documents `length_km` scaling concern and missing `circuitId` values).

3. Non-invasive notebook fixes
- Updated `Carmen_F1notebook.ipynb` and `Amira_sql.ipynb` to avoid Colab-only mounts by introducing a `DATA_ROOT` fallback. No content-level cleaning or ETL was added; source data was not modified.

Data assumptions & known issues

- The cleaned dataset is `df_master-2.csv` and is used by the visualization prototype. Row counts match raw sources (440 rows).
- The cleaned dataset is missing `race_name` in the schema; the dashboard will fall back to `track` when `race_name` is absent.
- `f1_circuits.xml` `length_km` values appear scaled (e.g., 5278 likely represents 5.278 km). I documented this in `metadata.yaml` and `data/README.md`.
- No ETL/canonical data layer or provenance automation (DVC) was added per request.

How the visualization fits the pipeline

- The dashboard reads the cleaned CSV directly (file-based artifact). For a production pipeline, convert cleaned CSV to a versioned Parquet and run a deterministic ETL producing that artifact; schedule the ETL and trigger dashboard refresh.
- Implement validation checks (row counts, required columns) in CI for each PR to prevent regressions. The earlier `validate_cleaned_vs_raw.py` served as an ad-hoc validator for peer review and should not be used by the dashboard.

Using existing SQL in visualizations (without DuckDB)

- I converted core SQL logic into pandas functions (`visualization/queries.py`). The notebook `Amira_sql.ipynb` can continue to run SQL-like queries using its in-memory SQLite approach if needed. Alternatively, call the pandas functions directly for reproducible results.

Files added (summary)

- data/manifest.csv
- data/README.md
- metadata.yaml
- visualization/app.py
- visualization/queries.py
- visualization/README.md
- VISUALIZATION_REPORT.md

Running the prototype (quick steps)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd visualization
streamlit run app.py
```

Governance next steps (recommended)

1. Add `data/manifest.csv` maintenance: append new artifact rows on each data refresh with `run_ts` and source URL.
2. Add CI job (GitHub Actions) to run validation checks (row parity, required columns, basic null thresholds) on PRs.
3. Implement a small ETL (`etl.py`) to produce `data/df_master.parquet` and write `manifest` entries programmatically.
4. Consider DVC for dataset versioning if dataset size or team workflow requires it.

Appendix: Quick developer notes

- `visualization/app.py` uses pandas for computations and Plotly for charts. It's designed for small-medium datasets; pre-aggregate if dataset grows.
- I intentionally avoided DuckDB per request and used pandas/SQLite patterns from `Amira_sql.ipynb` where appropriate.

Contact & ownership

Data owner: Team (please name a person and contact email to include here)

End of report
