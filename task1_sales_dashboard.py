import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import os

# 1. DATA PREPARATION
script_dir = os.path.dirname(__file__)
file_path = os.path.join(script_dir, 'train.csv')

df = pd.read_csv(file_path)
df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True)

# 2. BUILD THE APP WITH A MODERN THEME (LUX/DARKLY)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])

# Custom Styling for Cards
card_icon_style = {"textAlign": "center", "fontSize": "30px", "color": "#2c3e50"}

app.layout = dbc.Container([
    # Header Section
    dbc.Row([
        dbc.Col(html.H2("SALES PERFORMANCE EXECUTIVE INSIGHTS", 
                        className="text-center text-primary mb-4 mt-4", 
                        style={'fontWeight': 'bold', 'letterSpacing': '2px'}), width=12)
    ]),

    # Filter Section
    dbc.Row([
        dbc.Col([
            html.Label("🌍 Filter by Region:", className="fw-bold"),
            dcc.Dropdown(
                id='region-filter',
                options=[{'label': i, 'value': i} for i in df['Region'].unique()],
                value=df['Region'].unique()[0],
                clearable=False,
                className="mb-4"
            )
        ], width=4)
    ], justify="center"),

    # KPI Value Cards Row
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H6("Total Revenue", className="card-title text-secondary"),
                html.H3(id="total-sales-text", className="text-primary")
            ])
        ], color="light", outline=True), width=4),
        
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H6("Total Orders", className="card-title text-secondary"),
                html.H3(id="total-orders-text", className="text-success")
            ])
        ], color="light", outline=True), width=4),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H6("Avg Order Value", className="card-title text-secondary"),
                html.H3(id="avg-order-text", className="text-info")
            ])
        ], color="light", outline=True), width=4),
    ], className="mb-4"),

    # Visualizations Row
    dbc.Row([
        dbc.Col(dcc.Graph(id='sales-trend-graph'), width=8),
        dbc.Col(dcc.Graph(id='category-pie-graph'), width=4),
    ]),

], fluid=True, style={'backgroundColor': '#f8f9fa', 'minHeight': '100vh'})

# 3. DASHBOARD LOGIC
@app.callback(
    [Output('total-sales-text', 'children'),
     Output('total-orders-text', 'children'),
     Output('avg-order-text', 'children'),
     Output('sales-trend-graph', 'figure'),
     Output('category-pie-graph', 'figure')],
    [Input('region-filter', 'value')]
)
def update_dashboard(selected_region):
    filtered_df = df[df['Region'] == selected_region]
    
    # KPIs
    sales = filtered_df['Sales'].sum()
    orders = filtered_df['Order ID'].nunique()
    aov = sales / orders if orders > 0 else 0
    
    # Trend Chart (Cleaned up with professional colors)
    trend_data = filtered_df.groupby('Order Date')['Sales'].sum().reset_index()
    fig_trend = px.area(trend_data, x='Order Date', y='Sales', 
                        title=f"📈 Sales Momentum: {selected_region}",
                        template="plotly_white", color_discrete_sequence=['#2c3e50'])
    
    # Category Donut Chart
    cat_data = filtered_df.groupby('Category')['Sales'].sum().reset_index()
    fig_pie = px.pie(cat_data, values='Sales', names='Category', 
                     hole=0.6, title="📦 Category Mix",
                     color_discrete_sequence=px.colors.qualitative.Pastel)
    
    return f"${sales:,.0f}", f"{orders:,}", f"${aov:,.2f}", fig_trend, fig_pie

if __name__ == '__main__':
    app.run(debug=True)