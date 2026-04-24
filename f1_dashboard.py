"""
F1 2023 Season Analytics - Premium Interactive Dashboard
PRODUCTION VERSION - Thread-Safe SQL with Absolute Paths
"""

import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import sqlite3
from threading import Lock
import os

# ============================================================================
# CONFIGURATION
# ============================================================================

# Find the CSV file - try multiple locations
CSV_PATHS = [
    'df_master.csv',  # Same directory as script
    '../df_master.csv',  # Parent directory
    '../../df_master.csv',  # Two levels up
    os.path.expanduser('~/df_master.csv'),  # Home directory
]

def find_csv():
    """Find the CSV file"""
    for path in CSV_PATHS:
        if os.path.exists(path):
            print(f"✓ Found CSV: {path}")
            return path
    raise FileNotFoundError(
        f"Cannot find df_master.csv. Please run this script from your project directory.\n"
        f"Tried: {CSV_PATHS}"
    )

CSV_FILE = find_csv()

# ============================================================================
# DATA LOADING - THREAD-SAFE
# ============================================================================

df = None
df_lock = Lock()

def load_data():
    """Load F1 data"""
    df = pd.read_csv(CSV_FILE)
    df.columns = [c.strip() for c in df.columns]
    
    # Type conversions
    for col in ['finish_position', 'grid_position', 'laps']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    if 'points' in df.columns:
        df['points'] = pd.to_numeric(df['points'], errors='coerce')
    if 'race_date' in df.columns:
        df['race_date'] = pd.to_datetime(df['race_date'], errors='coerce')
    
    return df

def sql_query(query):
    """Execute SQL query - thread-safe"""
    global df
    
    conn = sqlite3.connect(':memory:')
    
    with df_lock:
        df.to_sql('f1_races', conn, index=False, if_exists='replace')
    
    try:
        result = pd.read_sql_query(query, conn)
    finally:
        conn.close()
    
    return result

# Initialize
print("\n" + "="*70)
print("🏎️  F1 2023 ANALYTICS DASHBOARD - INITIALIZING")
print("="*70)
print(f"\n📂 Loading data from: {CSV_FILE}")
df = load_data()
print(f"✓ Loaded {len(df)} race entries")
print(f"✓ Columns: {', '.join(df.columns.tolist()[:8])}...")

# Test SQL
test_result = sql_query("SELECT COUNT(*) as cnt FROM f1_races")
print(f"✓ SQL engine ready ({test_result.iloc[0,0]} rows accessible)")

# Pre-calculate stats
leader_points = sql_query("""
    SELECT SUM(points) as total_points 
    FROM f1_races 
    GROUP BY driver_name 
    ORDER BY total_points DESC 
    LIMIT 1
""").iloc[0, 0]
print(f"✓ Pre-calculated stats (Leader: {leader_points} points)")

# ============================================================================
# F1 THEME
# ============================================================================

F1_COLORS = {
    'red': '#E10600',
    'dark': '#15151E',
    'white': '#FFFFFF',
    'silver': '#C0C0C0',
    'gold': '#FFD700',
    'background': '#0A0A0F',
    'card_bg': '#1A1A24',
    'text_light': '#E0E0E0',
    'accent_green': '#00FF41',
}

TEAM_COLORS = {
    'Red Bull Racing Honda RBPT': '#0600EF',
    'Mercedes': '#00D2BE',
    'Ferrari': '#DC0000',
    'McLaren Mercedes': '#FF8700',
    'Aston Martin Aramco Mercedes': '#006F62',
    'Alpine F1 Team': '#0090FF',
    'Williams Mercedes': '#005AFF',
    'AlphaTauri Honda RBPT': '#2B4562',
    'Alfa Romeo Ferrari': '#900000',
    'Haas Ferrari': '#FFFFFF',
}

# ============================================================================
# DASH APP
# ============================================================================

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
app.title = "F1 2023 Analytics"

# Custom CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                font-family: 'Arial', sans-serif;
                background: linear-gradient(135deg, #0A0A0F 0%, #1A0000 100%);
                background-attachment: fixed;
            }
            .f1-header {
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 3px;
                background: linear-gradient(90deg, #E10600 0%, #FF4444 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                animation: glow 2s ease-in-out infinite;
            }
            @keyframes glow {
                0%, 100% { filter: drop-shadow(0 0 10px rgba(225, 6, 0, 0.5)); }
                50% { filter: drop-shadow(0 0 20px rgba(225, 6, 0, 0.8)); }
            }
            .racing-stripe {
                height: 4px;
                background: linear-gradient(90deg, #E10600 0%, #FFD700 50%, #E10600 100%);
                background-size: 200% 100%;
                animation: stripe-move 3s linear infinite;
            }
            @keyframes stripe-move {
                0% { background-position: 0% 50%; }
                100% { background-position: 100% 50%; }
            }
            .stat-card {
                background: rgba(26, 26, 36, 0.9);
                border: 2px solid rgba(225, 6, 0, 0.3);
                border-radius: 12px;
                padding: 20px;
                transition: all 0.3s ease;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
            }
            .stat-card:hover {
                border-color: #E10600;
                transform: translateY(-5px);
                box-shadow: 0 8px 30px rgba(225, 6, 0, 0.4);
            }
            .metric-value {
                font-size: 3rem;
                font-weight: 700;
                color: #E10600;
                text-shadow: 0 0 20px rgba(225, 6, 0, 0.5);
            }
            .metric-label {
                font-size: 0.9rem;
                color: #C0C0C0;
                text-transform: uppercase;
                letter-spacing: 2px;
                margin-top: 10px;
            }
            .section-header {
                font-size: 2rem;
                font-weight: 700;
                color: #FFFFFF;
                text-transform: uppercase;
                letter-spacing: 2px;
                margin: 30px 0 20px 0;
                padding-bottom: 10px;
                border-bottom: 3px solid #E10600;
            }
            .graph-container {
                background: rgba(26, 26, 36, 0.6);
                border-radius: 12px;
                padding: 20px;
                margin: 20px 0;
                border: 1px solid rgba(225, 6, 0, 0.2);
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_kpi_card(title, value, subtitle, icon):
    return html.Div([
        html.Div([
            html.Div(icon, style={'fontSize': '2rem', 'marginBottom': '10px'}),
            html.Div(str(value), className='metric-value'),
            html.Div(title, className='metric-label'),
            html.Div(subtitle, style={'fontSize': '0.85rem', 'color': F1_COLORS['accent_green'], 'marginTop': '5px'})
        ], style={'textAlign': 'center'})
    ], className='stat-card')

# ============================================================================
# LAYOUT
# ============================================================================

app.layout = html.Div([
    # Header
    html.Div([
        html.Div(className='racing-stripe'),
        html.Div([
            html.H1("🏎️ FORMULA 1 2023 SEASON ANALYTICS", className='f1-header',
                   style={'textAlign': 'center', 'padding': '30px 0', 'margin': '0'}),
        ], style={'background': F1_COLORS['card_bg'], 'padding': '20px'}),
        html.Div(className='racing-stripe'),
    ]),
    
    dbc.Container([
        # KPIs
        html.Div([
            html.H2("CHAMPIONSHIP OVERVIEW", className='section-header'),
            dbc.Row([
                dbc.Col(html.Div(id='kpi-races'), width=12, lg=2),
                dbc.Col(html.Div(id='kpi-drivers'), width=12, lg=2),
                dbc.Col(html.Div(id='kpi-champion'), width=12, lg=3),
                dbc.Col(html.Div(id='kpi-margin'), width=12, lg=2),
                dbc.Col(html.Div(id='kpi-dnf'), width=12, lg=3),
            ], className='mb-4')
        ]),
        
        # Driver Championship
        html.Div([
            html.H2("DRIVER CHAMPIONSHIP", className='section-header'),
            html.Div(className='graph-container', children=[
                dcc.Graph(id='driver-championship', config={'displayModeBar': False})
            ])
        ]),
        
        # Season Progression
        html.Div([
            html.H2("SEASON PROGRESSION", className='section-header'),
            dcc.Dropdown(id='driver-selector', multi=True,
                        placeholder="Select drivers to compare...",
                        style={'backgroundColor': F1_COLORS['card_bg'], 'marginBottom': '20px'}),
            html.Div(className='graph-container', children=[
                dcc.Graph(id='season-progression', config={'displayModeBar': False})
            ])
        ]),
        
        # Grid vs Finish
        html.Div([
            html.H2("QUALIFYING IMPACT", className='section-header'),
            html.Div(className='graph-container', children=[
                dcc.Graph(id='grid-finish', config={'displayModeBar': False})
            ])
        ]),
        
        # DNF Analysis
        html.Div([
            html.H2("RELIABILITY ANALYSIS", className='section-header'),
            dbc.Row([
                dbc.Col([
                    html.Div(className='graph-container', children=[
                        dcc.Graph(id='dnf-rates', config={'displayModeBar': False})
                    ])
                ], width=12, lg=6),
                dbc.Col([
                    html.Div(className='graph-container', children=[
                        dcc.Graph(id='dnf-causes', config={'displayModeBar': False})
                    ])
                ], width=12, lg=6),
            ])
        ]),
        
        # Circuit Competitiveness
        html.Div([
            html.H2("CIRCUIT COMPETITIVENESS", className='section-header'),
            html.Div(className='graph-container', children=[
                dcc.Graph(id='circuit-comp', config={'displayModeBar': False})
            ])
        ]),
        
    ], fluid=True, style={'maxWidth': '1400px', 'padding': '20px'})
], style={'minHeight': '100vh'})

# ============================================================================
# CALLBACKS
# ============================================================================

@app.callback(
    [Output('kpi-races', 'children'), Output('kpi-drivers', 'children'),
     Output('kpi-champion', 'children'), Output('kpi-margin', 'children'),
     Output('kpi-dnf', 'children')],
    [Input('driver-championship', 'id')]
)
def update_kpis(_):
    try:
        total_races = sql_query("SELECT COUNT(DISTINCT track) FROM f1_races").iloc[0, 0]
        total_drivers = sql_query("SELECT COUNT(DISTINCT driver_name) FROM f1_races").iloc[0, 0]
        
        champion = sql_query("""
            SELECT driver_name, SUM(points) as total_points 
            FROM f1_races GROUP BY driver_name ORDER BY total_points DESC LIMIT 1
        """)
        champion_name = champion.iloc[0, 0]
        champion_points = int(champion.iloc[0, 1])
        
        avg_gap = sql_query("""
            SELECT AVG(CAST(REPLACE(time_retired, '+', '') AS REAL))
            FROM f1_races WHERE finish_position = 2 AND time_retired LIKE '+%' AND time_retired NOT LIKE '%lap%'
        """).iloc[0, 0]
        
        dnf_stats = sql_query("""
            SELECT COUNT(*) as total, SUM(CASE WHEN status != 'Finished' THEN 1 ELSE 0 END) as dnfs
            FROM f1_races
        """)
        dnf_rate = (dnf_stats.iloc[0, 1] / dnf_stats.iloc[0, 0] * 100)
        
        return (
            create_kpi_card("Races", total_races, "Complete Season", "🏁"),
            create_kpi_card("Drivers", total_drivers, "Full Grid", "👨‍✈️"),
            create_kpi_card("Champion", champion_name, f"{champion_points} pts", "🏆"),
            create_kpi_card("Avg Gap", f"{avg_gap:.2f}s", "P1 to P2", "⚡"),
            create_kpi_card("DNF Rate", f"{dnf_rate:.1f}%", f"{int(dnf_stats.iloc[0, 1])} DNFs", "⚠️")
        )
    except Exception as e:
        print(f"❌ KPI Error: {e}")
        return [create_kpi_card("Error", "N/A", str(e)[:20], "❌")] * 5

@app.callback(
    Output('driver-championship', 'figure'),
    [Input('driver-championship', 'id')]
)
def update_driver_championship(_):
    try:
        data = sql_query("""
            SELECT driver_name, team, SUM(points) as total_points
            FROM f1_races GROUP BY driver_name, team ORDER BY total_points DESC LIMIT 15
        """)
        
        colors = [TEAM_COLORS.get(team, F1_COLORS['silver']) for team in data['team']]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=data['total_points'], y=data['driver_name'], orientation='h',
            marker=dict(color=colors, line=dict(color=F1_COLORS['white'], width=2)),
            text=data['total_points'], textposition='outside',
            hovertemplate='<b>%{y}</b><br>Points: %{x}<extra></extra>'
        ))
        
        fig.update_layout(
            title='Driver Championship Standings',
            xaxis=dict(title='Points', gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(categoryorder='total ascending'),
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color=F1_COLORS['white']), height=600
        )
        return fig
    except Exception as e:
        print(f"❌ Championship Error: {e}")
        return go.Figure()

@app.callback(
    [Output('driver-selector', 'options'), Output('driver-selector', 'value')],
    [Input('driver-selector', 'id')]
)
def update_driver_dropdown(_):
    try:
        drivers = sql_query("SELECT DISTINCT driver_name FROM f1_races ORDER BY driver_name")['driver_name'].tolist()
        top_5 = sql_query("""
            SELECT driver_name FROM f1_races GROUP BY driver_name ORDER BY SUM(points) DESC LIMIT 5
        """)['driver_name'].tolist()
        
        return [{'label': d, 'value': d} for d in drivers], top_5
    except Exception as e:
        print(f"❌ Dropdown Error: {e}")
        return [], []

@app.callback(
    Output('season-progression', 'figure'),
    [Input('driver-selector', 'value')]
)
def update_season_progression(selected_drivers):
    try:
        if not selected_drivers:
            selected_drivers = sql_query("""
                SELECT driver_name FROM f1_races GROUP BY driver_name ORDER BY SUM(points) DESC LIMIT 5
            """)['driver_name'].tolist()
        
        drivers_str = "','".join(selected_drivers)
        data = sql_query(f"""
            SELECT driver_name, race_date, points,
                   SUM(points) OVER (PARTITION BY driver_name ORDER BY race_date) as cumulative_points
            FROM f1_races WHERE driver_name IN ('{drivers_str}') ORDER BY race_date
        """)
        
        fig = go.Figure()
        for driver in selected_drivers:
            driver_data = data[data['driver_name'] == driver]
            fig.add_trace(go.Scatter(
                x=driver_data['race_date'], y=driver_data['cumulative_points'],
                mode='lines+markers', name=driver, line=dict(width=3),
                hovertemplate='<b>%{fullData.name}</b><br>Points: %{y}<extra></extra>'
            ))
        
        fig.update_layout(
            title='Championship Points Progression',
            xaxis=dict(title='Race Date', gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(title='Cumulative Points', gridcolor='rgba(255,255,255,0.1)'),
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            height=550, hovermode='x unified'
        )
        return fig
    except Exception as e:
        print(f"❌ Progression Error: {e}")
        return go.Figure()

@app.callback(
    Output('grid-finish', 'figure'),
    [Input('grid-finish', 'id')]
)
def update_grid_finish(_):
    try:
        data = sql_query("""
            SELECT driver_name, grid_position, finish_position, points
            FROM f1_races WHERE status = 'Finished' AND finish_position IS NOT NULL
        """)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data['grid_position'], y=data['finish_position'], mode='markers',
            marker=dict(size=10, color=data['points'], colorscale='Reds',
                       showscale=True, colorbar=dict(title='Points')),
            text=data['driver_name'],
            hovertemplate='<b>%{text}</b><br>Grid: P%{x}<br>Finish: P%{y}<extra></extra>'
        ))
        
        fig.update_layout(
            title='Grid Position vs Finish Position',
            xaxis=dict(title='Grid Position', range=[0, 21]),
            yaxis=dict(title='Finish Position', range=[0, 21]),
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=600
        )
        return fig
    except Exception as e:
        print(f"❌ Grid-Finish Error: {e}")
        return go.Figure()

@app.callback(
    Output('dnf-rates', 'figure'),
    [Input('dnf-rates', 'id')]
)
def update_dnf_rates(_):
    try:
        data = sql_query("""
            SELECT team, COUNT(*) as total,
                   ROUND(100.0 * SUM(CASE WHEN status != 'Finished' THEN 1 ELSE 0 END) / COUNT(*), 1) as dnf_pct
            FROM f1_races GROUP BY team ORDER BY dnf_pct DESC
        """)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=data['dnf_pct'], y=data['team'], orientation='h',
            marker=dict(color=data['dnf_pct'], colorscale='Reds'),
            text=data['dnf_pct'], texttemplate='%{text:.1f}%',
            hovertemplate='<b>%{y}</b><br>DNF: %{x:.1f}%<extra></extra>'
        ))
        
        fig.update_layout(
            title='DNF Rate by Team',
            xaxis=dict(title='DNF Rate (%)'),
            yaxis=dict(categoryorder='total ascending'),
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=500
        )
        return fig
    except Exception as e:
        print(f"❌ DNF Rates Error: {e}")
        return go.Figure()

@app.callback(
    Output('dnf-causes', 'figure'),
    [Input('dnf-causes', 'id')]
)
def update_dnf_causes(_):
    try:
        data = sql_query("""
            SELECT status, COUNT(*) as count FROM f1_races 
            WHERE status != 'Finished' GROUP BY status ORDER BY count DESC LIMIT 8
        """)
        
        fig = go.Figure()
        fig.add_trace(go.Pie(
            labels=data['status'], values=data['count'], hole=0.4,
            marker=dict(colors=px.colors.sequential.Reds),
            hovertemplate='<b>%{label}</b><br>Count: %{value}<extra></extra>'
        ))
        
        fig.update_layout(
            title='DNF Causes Distribution',
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=500
        )
        return fig
    except Exception as e:
        print(f"❌ DNF Causes Error: {e}")
        return go.Figure()

@app.callback(
    Output('circuit-comp', 'figure'),
    [Input('circuit-comp', 'id')]
)
def update_circuit_competitiveness(_):
    try:
        data = sql_query("""
            SELECT track, AVG(CAST(REPLACE(time_retired, '+', '') AS REAL)) as avg_gap
            FROM f1_races WHERE finish_position = 2 AND time_retired LIKE '+%' AND time_retired NOT LIKE '%lap%'
            GROUP BY track ORDER BY avg_gap ASC
        """)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=data['avg_gap'], y=data['track'], orientation='h',
            marker=dict(color=data['avg_gap'], colorscale='RdYlGn_r'),
            text=data['avg_gap'], texttemplate='%{text:.2f}s',
            hovertemplate='<b>%{y}</b><br>Gap: %{x:.2f}s<extra></extra>'
        ))
        
        fig.update_layout(
            title='Circuit Competitiveness (P1-P2 Gap)',
            xaxis=dict(title='Average Gap (seconds)'),
            yaxis=dict(categoryorder='total ascending'),
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=650
        )
        return fig
    except Exception as e:
        print(f"❌ Circuit Comp Error: {e}")
        return go.Figure()

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))
    debug = os.environ.get("DASH_DEBUG", "false").lower() == "true"
    app.run(debug=debug, host='0.0.0.0', port=port)