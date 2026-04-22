import pandas as pd

def load_cleaned(path='df_master-2.csv'):
    df = pd.read_csv(path)
    # standardize column names to expected snake_case
    df.columns = [c.strip() for c in df.columns]
    # convert types
    for col in ['finish_position','grid_position','laps']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    if 'points' in df.columns:
        df['points'] = pd.to_numeric(df['points'], errors='coerce')
    if 'race_date' in df.columns:
        df['race_date'] = pd.to_datetime(df['race_date'], errors='coerce')
    return df

def top_drivers(df, limit=10):
    return df.groupby('driver_name', as_index=False)['points'].sum().sort_values('points', ascending=False).head(limit)

def dnf_rate_by_team(df):
    # consider status values containing 'Retired' or 'Accident' as DNF
    df = df.copy()
    df['is_dnf'] = df['status'].isin(['Retired', 'Accident', 'Collision damage']) if 'status' in df.columns else False
    return df.groupby('team').agg(total_entries=('driver_name','count'), dnfs=('is_dnf','sum')).assign(dnf_pct=lambda x: (x['dnfs']/x['total_entries']*100).round(1)).reset_index().sort_values('dnf_pct', ascending=False)

def cumulative_points(df, drivers=None):
    df = df.copy()
    # choose a sensible sort column
    if 'race_date' in df.columns:
        df = df.sort_values(['race_date'])
    elif 'round' in df.columns:
        df = df.sort_values(['round'])
    else:
        # fall back to existing order
        df = df
    if drivers:
        df = df[df['driver_name'].isin(drivers)]
    df['cumulative_points'] = df.groupby('driver_name')['points'].cumsum()
    cols = ['driver_name','race_date','round','track','points','cumulative_points']
    # return only columns that exist in the dataframe
    cols_to_return = [c for c in cols if c in df.columns]
    return df[cols_to_return]

def avg_positions_gained(df, min_races=10):
    df = df.copy()
    df = df[df['status']=='Finished'] if 'status' in df.columns else df
    df['positions_gained'] = df['grid_position'] - df['finish_position']
    res = df.groupby('driver_name').agg(avg_grid=('grid_position','mean'), avg_finish=('finish_position','mean'), avg_positions_gained=('positions_gained','mean'), races=('driver_name','count')).reset_index()
    return res[res['races']>=min_races].sort_values('avg_positions_gained', ascending=False)

def constructors_leaderboard(df, limit=10):
    return df.groupby('team', as_index=False)['points'].sum().sort_values('points', ascending=False).head(limit)

def parse_time_to_seconds(t):
    """Parse a time string to seconds. Supports formats like '1:23.456', '1:23:45' and '+1.234' or '+1 lap'. Returns None if unparsable."""
    if pd.isna(t):
        return None
    s = str(t).strip()
    try:
        if s.startswith('+'):
            # relative times like '+1.234' or '+1 lap'
            body = s[1:]
            if 'lap' in body:
                return None
            return float(body)
        # colon-separated mm:ss[.ms] or hh:mm:ss
        parts = s.split(':')
        parts = [p.strip() for p in parts]
        if len(parts) == 2:
            m, sec = parts
            return int(m) * 60 + float(sec)
        if len(parts) == 3:
            h, m, sec = parts
            return int(h) * 3600 + int(m) * 60 + float(sec)
        # fallback numeric
        return float(s)
    except Exception:
        return None

def circuit_competitiveness(df):
    """Compute competitiveness per circuit.
    Primary metric: average winner-to-2nd time gap when parsable.
    Fallback: mean absolute position changes per race (higher -> more position shuffling).
    Returns DataFrame with circuit, metric_value and method used.
    """
    df2 = df.copy()
    # ensure finish_position numeric
    df2['finish_position'] = pd.to_numeric(df2['finish_position'], errors='coerce')
    results = []
    for track, g in df2.groupby('track'):
        # attempt time-gap method per race
        gaps = []
        for race, rg in g.groupby(['race_date'] if 'race_date' in g.columns else ['round']):
            winners = rg[rg['finish_position'] == 1]
            seconds = rg[rg['finish_position'] == 2]
            if not winners.empty and not seconds.empty:
                t1 = parse_time_to_seconds(winners.iloc[0].get('time_retired'))
                t2 = parse_time_to_seconds(seconds.iloc[0].get('time_retired'))
                if t1 is not None and t2 is not None:
                    gaps.append(abs(t2 - t1))
        if gaps:
            metric = float(pd.Series(gaps).mean())
            method = 'time_gap_s'
        else:
            # fallback: mean abs position change per race
            pos_changes = []
            for race, rg in g.groupby(['race_date'] if 'race_date' in g.columns else ['round']):
                if 'grid_position' in rg.columns and 'finish_position' in rg.columns:
                    rg = rg.copy()
                    rg['grid_position'] = pd.to_numeric(rg['grid_position'], errors='coerce')
                    rg['finish_position'] = pd.to_numeric(rg['finish_position'], errors='coerce')
                    rg = rg.dropna(subset=['grid_position','finish_position'])
                    if not rg.empty:
                        pos_changes.append((rg['grid_position'] - rg['finish_position']).abs().mean())
            metric = float(pd.Series(pos_changes).mean()) if pos_changes else None
            method = 'avg_abs_pos_change'
        results.append({'track': track, 'competitiveness_metric': metric, 'method': method})
    return pd.DataFrame(results).sort_values('competitiveness_metric')

def avg_fastest_lap_by_circuit(df):
    df2 = df.copy()
    if 'fastest_lap_time' not in df2.columns:
        return pd.DataFrame()
    df2['ft_seconds'] = df2['fastest_lap_time'].apply(parse_time_to_seconds)
    df2['length_km'] = pd.to_numeric(df2['length_km'], errors='coerce')
    res = df2.groupby('track', as_index=False).agg(avg_fastest_sec=('ft_seconds','mean'), length_km=('length_km','mean'))
    return res.dropna()

def team_performance_by_circuit_type(df, circuit_types_path='data/circuit_types.csv'):
    """Aggregate team performance by circuit type. Expects a CSV mapping track -> circuit_type.
    If mapping not present, returns empty DataFrame.
    """
    import os
    if not os.path.exists(circuit_types_path):
        return pd.DataFrame()
    types = pd.read_csv(circuit_types_path)
    df2 = df.merge(types, left_on='track', right_on='track', how='left')
    res = df2.groupby(['team','circuit_type'], as_index=False)['points'].sum()
    return res


