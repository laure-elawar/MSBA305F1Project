import os
import sys
# Ensure repo root is on sys.path so `from visualization...` imports work
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import streamlit as st
import plotly.express as px
import pandas as pd
try:
    from visualization.queries import (
        load_cleaned,
        top_drivers,
        cumulative_points,
        constructors_leaderboard,
        parse_time_to_seconds,
        circuit_competitiveness,
        avg_fastest_lap_by_circuit,
        team_performance_by_circuit_type,
    )
except ImportError:
    # Fallback: import the module and grab attributes (works around weird import/path issues)
    import importlib
    _q = importlib.import_module('visualization.queries')
    load_cleaned = getattr(_q, 'load_cleaned')
    top_drivers = getattr(_q, 'top_drivers')
    cumulative_points = getattr(_q, 'cumulative_points')
    constructors_leaderboard = getattr(_q, 'constructors_leaderboard')
    parse_time_to_seconds = getattr(_q, 'parse_time_to_seconds')
    circuit_competitiveness = getattr(_q, 'circuit_competitiveness')
    avg_fastest_lap_by_circuit = getattr(_q, 'avg_fastest_lap_by_circuit')
    team_performance_by_circuit_type = getattr(_q, 'team_performance_by_circuit_type')

st.set_page_config(layout='wide', page_title='F1 Season Dashboard')

@st.cache_data
def load_data(path='df_master-2.csv'):
    return load_cleaned(path)

df = load_data()

# Top KPIs
st.title('F1 Season Dashboard')
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric('Races', value=df['round'].nunique() if 'round' in df.columns else df['race_date'].nunique())
with col2:
    st.metric('Drivers', value=df['driver_name'].nunique())
with col3:
    top = top_drivers(df, limit=1)
    st.metric('Top Driver', value=top.iloc[0]['driver_name'] if not top.empty else 'n/a', delta=str(int(top.iloc[0]['points'])) if not top.empty else '')
with col4:
    st.metric('Total Points', value=int(df['points'].sum()))

# Leaderboard
st.header('Championship Leaderboard')
limit = st.slider('Top N drivers', 5, 25, 10)
drivers_df = top_drivers(df, limit=limit)
fig = px.bar(drivers_df, x='points', y='driver_name', orientation='h', color='points', color_continuous_scale='Viridis')
st.plotly_chart(fig, use_container_width=True)

# Cumulative points
st.header('Cumulative Points Progression')
drivers_select = st.multiselect('Select drivers (empty = top 5)', options=df['driver_name'].unique().tolist(), default=list(df['driver_name'].value_counts().head(5).index))
cp = cumulative_points(df, drivers=drivers_select)
if not cp.empty:
    fig2 = px.line(cp, x='race_date', y='cumulative_points', color='driver_name', markers=True)
    st.plotly_chart(fig2, use_container_width=True)

# Race Results Explorer
st.header('Race Results Explorer')
if 'race_name' in df.columns:
    races = df['race_name'].unique()
else:
    races = df['track'].unique()
race = st.selectbox('Select race', options=sorted(races))
if 'race_name' in df.columns:
    df_race = df[df['race_name']==race]
else:
    df_race = df[df['track']==race]
st.dataframe(df_race.sort_values('finish_position'))

# Map of circuits
if 'latitude' in df.columns and 'longitude' in df.columns:
    st.header('Circuit Map')
    map_df = df[['track','latitude','longitude']].drop_duplicates().dropna()
    st.map(map_df.rename(columns={'latitude':'lat','longitude':'lon'}))

# Constructor leaderboard
st.header('Constructor Leaderboard')
cons_df = constructors_leaderboard(df, limit=10)
figc = px.bar(cons_df, x='points', y='team', orientation='h', color='points', color_continuous_scale='Plasma')
st.plotly_chart(figc, width='stretch')

# Grid vs Finish analysis
st.header('Grid vs Finish')
if 'grid_position' in df.columns and 'finish_position' in df.columns:
    scatter = px.scatter(df, x='grid_position', y='finish_position', color='driver_name', hover_data=['track','race_date'], opacity=0.7)
    st.plotly_chart(scatter, width='stretch')
    # show pole-to-win stats
    pole_wins = df[(df['grid_position']==1) & (pd.to_numeric(df['finish_position'], errors='coerce')==1)].shape[0]
    total_races = df['race_date'].nunique() if 'race_date' in df.columns else df['round'].nunique()
    st.metric('Pole-to-win conversions', value=f"{pole_wins}/{total_races}")

# Circuit competitiveness
st.header('Circuit Competitiveness')
comp = circuit_competitiveness(df)
if not comp.empty:
    st.dataframe(comp.sort_values('competitiveness_metric').head(10))

# Circuit characteristics vs fastest lap
st.header('Circuit length vs average fastest lap')
fastest = avg_fastest_lap_by_circuit(df)
if not fastest.empty:
    fig3 = px.scatter(fastest, x='length_km', y='avg_fastest_sec', hover_data=['track'])
    st.plotly_chart(fig3, width='stretch')

# Team performance by circuit type (requires data/circuit_types.csv)
st.header('Team performance by circuit type')
tp = team_performance_by_circuit_type(df)
if tp.empty:
    st.info('No circuit type mapping found at data/circuit_types.csv — provide a mapping to enable this view.')
else:
    st.dataframe(tp.sort_values(['circuit_type','points'], ascending=[True,False]))

st.markdown('---')
st.caption('Data source: df_master-2.csv. Visualizations powered by pandas + Plotly + Streamlit.')


if __name__ == '__main__':
    print("This module is a Streamlit app. Start it using the Streamlit CLI:")
    print("Run from the repository root:\n  source .venv/bin/activate\n  .venv/bin/streamlit run visualization/app.py\n")
    # Exit without trying to bootstrap Streamlit programmatically to avoid Runtime conflicts
    import sys
    sys.exit(0)
