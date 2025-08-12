"""Dash app: Fuel Margin Dashboard

Provides a dark-themed dashboard backed by Databricks SQL. Users select a
date range which is reflected in the URL, and the app fetches several
timeseries tables (gallons, net_margin, pricing, etc.) filtered by
`week` to render Plotly line charts. Data auto-refreshes on an interval.
"""

import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objs as go
import pandas as pd
from urllib.parse import urlencode, parse_qs
from databricks.sdk.core import Config
import databricks.sql as dbsql
from flask import request as flask_request
from datetime import date

# Databricks config
try:
    DBX_CONFIG = Config()
except Exception:
    # Databricks config used for local development
    DBX_CONFIG = Config(profile="E2-DOGFOOD")

# TODO: Configure this via config or environment variable
# Databricks SQL Warehouse HTTP path used for connections.
SQL_HTTP_PATH = "/sql/1.0/warehouses/4fe75792cd0d304c"

# Defaults
# Default date range applied on first load or when URL lacks params.
default_start = "2024-01-01"
default_end = "2025-05-31"

def connect_to_warehouse():
    """Create a Databricks SQL connection using a bearer token.

    Tries to read a user token from the `x-forwarded-access-token` header
    (useful when running behind a reverse proxy). Falls back to the token
    resolved by `databricks.sdk.core.Config`. Raises if no token is found.
    """
    user_token = flask_request.headers.get("x-forwarded-access-token")
    if not user_token:
        user_token = DBX_CONFIG.token
    if not user_token:
        raise ValueError("No user token found")
    return dbsql.connect(
        server_hostname=DBX_CONFIG.host,
        http_path=SQL_HTTP_PATH,
        access_token=user_token,
    )

def normalize_df(df):
    """Normalize column names and index for charting.

    - Lower-cases, trims, and snake_cases columns keeping only [A-Za-z0-9_].
    - If a `week` column exists, parse it to datetime, set as index, and sort.
    Returns the mutated DataFrame for convenience.
    """
    df.columns = (
        df.columns.str.lower()
                  .str.strip()
                  .str.replace(" ", "_")
                  .str.replace(r"[^0-9a-zA-Z_]", "", regex=True)
    )
    if "week" in df.columns:
        df["week"] = pd.to_datetime(df["week"])
        df.set_index("week", inplace=True)
        df.sort_index(inplace=True)
    return df

def fetch_table(table_name, start_date, end_date):
    """Fetch a table for the given date range and return a normalized DataFrame.

    Filters rows by `week BETWEEN start AND end` and orders by `week`.
    The table is fully qualified under `reggie_pierce.apps_workshop`.
    """
    start = pd.to_datetime(start_date).strftime("%Y-%m-%d")
    end = pd.to_datetime(end_date).strftime("%Y-%m-%d")
    query = f"""
      SELECT *
      FROM reggie_pierce.apps_workshop.{table_name}
      WHERE week BETWEEN DATE('{start}') AND DATE('{end}')
      ORDER BY week
    """
    # For quick troubleshooting; consider moving to structured logging if needed.
    print(query)
    with connect_to_warehouse() as conn:
        df = pd.read_sql(query, conn)
    return normalize_df(df)

def make_graph_component(df, title):
    """Build a dark-themed Plotly line chart wrapped in a Dash `dcc.Graph`.

    - If `df` is empty, render a placeholder with a helpful message.
    - Otherwise, plot each column as a separate line against the datetime index.
    Returns the `dcc.Graph` component.
    """
    if df.empty or df.index.size == 0:
        fig = go.Figure(
            layout=go.Layout(
                title=title,
                paper_bgcolor="black",
                plot_bgcolor="black",
                font=dict(color="white"),
                xaxis=dict(gridcolor="#333"),
                yaxis=dict(gridcolor="#333"),
                annotations=[dict(text="No data for selected date range",
                                  showarrow=False,
                                  font=dict(color="white", size=16))]
            )
        )
        return dcc.Graph(figure=fig, config={"displayModeBar": False}, style={"height": "350px"})
    fig = go.Figure(
        data=[
            go.Scatter(
                x=df.index,
                y=df[col],
                mode="lines",
                name=col
            ) for col in df.columns
        ],
        layout=go.Layout(
            title=title,
            paper_bgcolor="black",
            plot_bgcolor="black",
            font=dict(color="white"),
            xaxis=dict(gridcolor="#333"),
            yaxis=dict(gridcolor="#333"),
            legend=dict(font=dict(color="white"))
        )
    )
    return dcc.Graph(figure=fig, config={"displayModeBar": False}, style={"height": "350px"})

app = dash.Dash(__name__)
app.title = "Fuel Margin Dashboard"

# Top-level layout: URL for deep-linking, date pickers, update button,
# periodic refresh, and a container where graphs are injected.
app.layout = html.Div(
    style={"backgroundColor": "black", "padding": "10px"},
    children=[
        dcc.Location(id="url", refresh=False),

        # Date range controls
        html.Div([
            html.Div([
                html.Label("Start Date:", style={"color": "white", "marginRight": "10px", "fontWeight": "bold"}),
                dcc.DatePickerSingle(
                    id="start-date-picker",
                    date=default_start,
                    display_format="YYYY-MM-DD",
                    style={"marginRight": "20px"}
                ),
            ], style={"display": "inline-block", "marginRight": "30px"}),

            html.Div([
                html.Label("End Date:", style={"color": "white", "marginRight": "10px", "fontWeight": "bold"}),
                dcc.DatePickerSingle(
                    id="end-date-picker",
                    date=default_end,
                    display_format="YYYY-MM-DD",
                    style={"marginRight": "20px"}
                ),
            ], style={"display": "inline-block", "marginRight": "30px"}),

            # Explicit update button to sync URL and trigger fetches
            html.Button(
                "Update Data",
                id="update-button",
                style={
                    "backgroundColor": "#007BFF",
                    "color": "white",
                    "border": "none",
                    "padding": "10px 20px",
                    "borderRadius": "5px",
                    "cursor": "pointer"
                }
            ),
        ], style={"textAlign": "center", "marginBottom": "30px", "padding": "20px"}),

        # Periodic refresh every 60 seconds
        dcc.Interval(id="interval-loader", interval=60*1000, n_intervals=0),

        # Graphs are populated by callback
        html.Div(id="graphs-container")
    ]
)

@app.callback(
    [Output("start-date-picker", "date"),
     Output("end-date-picker", "date")],
    Input("url", "search")
)
def sync_dates_from_url(search):
    """Set date pickers from querystring parameters on initial load or change."""
    if not search:
        return default_start, default_end
    params = parse_qs(search.lstrip("?"))
    start_date = params.get("start", [default_start])[0]
    end_date = params.get("end", [default_end])[0]
    return start_date, end_date

@app.callback(
    Output("url", "search"),
    Input("update-button", "n_clicks"),
    State("start-date-picker", "date"),
    State("end-date-picker", "date"),
    prevent_initial_call=True
)
def update_url_params(n_clicks, start_date, end_date):
    """Encode current date pickers into the URL querystring.

    This enables deep-linking and sharing the selected date range.
    """
    params = {"start": start_date, "end": end_date}
    return "?" + urlencode(params)

@app.callback(
    Output("graphs-container", "children"),
    [Input("start-date-picker", "date"),
     Input("end-date-picker", "date"),
     Input("interval-loader", "n_intervals")]
)
def update_graphs(start_date, end_date, _):
    """Fetch data for all panels and render six synchronized charts.

    Triggered when dates change or the interval ticks. Each table is
    independently loaded and plotted; failures surface as a user-visible
    error banner instead of a stack trace.
    """
    start_date = start_date or default_start
    end_date = end_date or default_end

    try:
        gallons_df = fetch_table("gallons", start_date, end_date)
        net_margin_df = fetch_table("net_margin", start_date, end_date)
        market_pricing_df = fetch_table("market_pricing", start_date, end_date)
        transactions_df = fetch_table("transactions", start_date, end_date)
        margin_components_df = fetch_table("margin_components", start_date, end_date)
        market_price_delta_df = fetch_table("market_price_delta", start_date, end_date)

        return html.Div([
            html.Div([
                html.Div(make_graph_component(gallons_df, "Gallons"), style={"width": "33%", "display": "inline-block", "padding": "5px"}),
                html.Div(make_graph_component(net_margin_df, "Net Margin"), style={"width": "33%", "display": "inline-block", "padding": "5px"}),
                html.Div(make_graph_component(market_pricing_df, "Market Pricing"), style={"width": "33%", "display": "inline-block", "padding": "5px"}),
            ], style={"display": "flex", "flex-wrap": "nowrap"}),

            html.Div([
                html.Div(make_graph_component(transactions_df, "Transactions"), style={"width": "33%", "display": "inline-block", "padding": "5px"}),
                html.Div(make_graph_component(margin_components_df, "Margin Impacting Components"), style={"width": "33%", "display": "inline-block", "padding": "5px"}),
                html.Div(make_graph_component(market_price_delta_df, "Market Price Delta"), style={"width": "33%", "display": "inline-block", "padding": "5px"}),
            ], style={"display": "flex", "flex-wrap": "nowrap"}),
        ])
    except Exception as e:
        return html.Div([
            html.H3(f"Error loading data: {str(e)}", style={"color": "red", "textAlign": "center"})
        ])

if __name__ == "__main__":
    app.run(debug=True)