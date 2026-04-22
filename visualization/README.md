Visualization folder

Run the Streamlit prototype:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r ../requirements.txt
streamlit run app.py
```

Files:
- `app.py`: Streamlit dashboard prototype (KPIs, Leaderboard, Cumulative timeline, Race Results, Map).
- `queries.py`: pandas-based query helpers mirroring `Amira_sql.ipynb` logic.

Notes:
- The app reads `df_master-2.csv` from repo root. Ensure the file is present.
- This prototype uses pandas for computation (no DuckDB). For large datasets, consider pre-aggregating to Parquet.
