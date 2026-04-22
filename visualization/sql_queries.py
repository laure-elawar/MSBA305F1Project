import sqlite3
import pandas as pd
from .sqlite_utils import get_connection, load_csv_to_sqlite

def run_sql(conn, query):
    try:
        return pd.read_sql_query(query, conn)
    except Exception as e:
        raise

def q1_top_drivers(conn_or_path, table='f1', limit=10):
    """Total points per driver (top N). conn_or_path can be a sqlite3.Connection or CSV path."""
    if isinstance(conn_or_path, str):
        conn = load_csv_to_sqlite(conn_or_path)
    else:
        conn = conn_or_path
    q = f"""
    SELECT driver_name, SUM(points) AS total_points, COUNT(*) AS races_entered
    FROM {table}
    GROUP BY driver_name
    ORDER BY total_points DESC
    LIMIT {limit}
    """
    return run_sql(conn, q)

def q2_dnf_rate_by_team(conn_or_path, table='f1'):
    if isinstance(conn_or_path, str):
        conn = load_csv_to_sqlite(conn_or_path)
    else:
        conn = conn_or_path
    # SQLite supports CASE WHEN
    q = f"""
    SELECT team,
           COUNT(*) AS total_entries,
           SUM(CASE WHEN status IN ('Retired','Accident','Collision damage') THEN 1 ELSE 0 END) AS dnfs,
           ROUND(100.0 * SUM(CASE WHEN status IN ('Retired','Accident','Collision damage') THEN 1 ELSE 0 END) / COUNT(*), 1) AS dnf_pct
    FROM {table}
    GROUP BY team
    ORDER BY dnf_pct DESC
    """
    return run_sql(conn, q)

def q3_pole_to_win(conn_or_path, table='f1'):
    if isinstance(conn_or_path, str):
        conn = load_csv_to_sqlite(conn_or_path)
    else:
        conn = conn_or_path
    q = f"""
    SELECT team,
           SUM(CASE WHEN grid_position = 1 THEN 1 ELSE 0 END) AS poles,
           SUM(CASE WHEN finish_position = 1 THEN 1 ELSE 0 END) AS wins,
           SUM(CASE WHEN grid_position = 1 AND finish_position = 1 THEN 1 ELSE 0 END) AS pole_to_win,
           ROUND(100.0 * SUM(CASE WHEN grid_position = 1 AND finish_position = 1 THEN 1 ELSE 0 END)
                 / NULLIF(SUM(CASE WHEN grid_position = 1 THEN 1 ELSE 0 END), 0), 1) AS conversion_pct
    FROM {table}
    GROUP BY team
    HAVING poles > 0
    ORDER BY conversion_pct DESC
    """
    return run_sql(conn, q)

def q4_avg_positions_gained(conn_or_path, table='f1', min_races=10):
    if isinstance(conn_or_path, str):
        conn = load_csv_to_sqlite(conn_or_path)
    else:
        conn = conn_or_path
    q = f"""
    SELECT driver_name,
           ROUND(AVG(grid_position), 2) AS avg_grid,
           ROUND(AVG(finish_position), 2) AS avg_finish,
           ROUND(AVG(grid_position - finish_position), 2) AS avg_positions_gained,
           COUNT(*) AS races
    FROM {table}
    WHERE status = 'Finished'
    GROUP BY driver_name
    HAVING races >= {min_races}
    ORDER BY avg_positions_gained DESC
    """
    return run_sql(conn, q)

def q5_cumulative_points(conn_or_path, table='f1', drivers=None):
    if isinstance(conn_or_path, str):
        conn = load_csv_to_sqlite(conn_or_path)
    else:
        conn = conn_or_path
    # If drivers provided, add a WHERE clause
    drivers_filter = ''
    if drivers:
        vals = ','.join([f"'{d.replace("'","''")}'" for d in drivers])
        drivers_filter = f"WHERE driver_name IN ({vals})"
    q = f"""
    WITH cumulative_points_calc AS (
        SELECT driver_name,
               race_date,
               track,
               points,
               SUM(points) OVER (PARTITION BY driver_name ORDER BY race_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_points
        FROM {table}
    )
    SELECT driver_name, track, race_date, points, cumulative_points
    FROM cumulative_points_calc
    {drivers_filter}
    ORDER BY race_date, cumulative_points
    """
    return run_sql(conn, q)
