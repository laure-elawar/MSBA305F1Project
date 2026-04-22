Project: MSBA305 F1 analysis

This repository contains F1 race data and notebooks for exploratory analysis.

What I changed for local execution:
- Notebooks updated to use a `DATA_ROOT` fallback. They will try Colab Drive if available, otherwise use the repository root (`./`).
- Hard-coded Colab paths replaced with safe path checks; notebooks now try local filenames when Colab paths are not found.
- `Amira_sql.ipynb` will prefer `df_master-2.csv` if `df_master.csv` is not present.

How to set up (local):
1. Create and activate a Python environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Run notebooks with Jupyter Lab / Notebook, or open in VS Code.

Notes and caveats:
- I did NOT add an ETL/canonical dataset or provenance files as requested.
- I did NOT modify dataset contents; cleaning steps remain in the notebooks.
- `f1_circuits.xml` and other dataset metadata issues were intentionally left for later (unit ambiguity, missing IDs).

Next recommended steps:
- (Optional) Create a small ETL script to produce a canonical dataset for dashboards.
- (Optional) Add `data/manifest.csv` and `metadata.yaml` for provenance.