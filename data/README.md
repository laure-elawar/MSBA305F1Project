Data directory and provenance

Files included:
- `df_master-2.csv`: cleaned dataset produced by team (canonical input for visualizations).
- `Formula1_2023season_raceResults.csv`: raw race results CSV.
- `JSON-F1-full (1).json`: raw JSON API dump.
- `f1_circuits.xml`: circuits metadata (lat/long, length_km, opened).

Provenance:
- See `data/manifest.csv` for SHA256 checksums and download dates.

Notes:
- `length_km` in `f1_circuits.xml` appears scaled (e.g., 5278 represents 5.278 km). Treat as raw and document scaling in `metadata.yaml`.
- The canonical cleaned dataset used by visualizations is `df_master-2.csv`. No ETL or further canonicalization is provided in this commit.
