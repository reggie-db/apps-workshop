import dash
from dash import dcc, html, Output, Input
import plotly.graph_objs as go
import pandas as pd
from databricks.sdk.core import Config
import databricks.sql as dbsql
from flask import request as flask_request

CFG = Config()
SQL_HTTP_PATH = "/sql/1.0/warehouses/4fe75792cd0d304c"

def connect_to_warehouse():
    user_token = flask_request.headers.get("x-forwarded-access-token")
    return dbsql.connect(
        server_hostname=CFG.host,
        http_path=SQL_HTTP_PATH,
        access_token=user_token,
    )

def fetch_table(table_name):
    with connect_to_warehouse() as conn:
        query = f"SELECT * FROM reggie_pierce.apps_workshop.{table_name} ORDER BY week"
        df = pd.read_sql(query, conn)

    df.columns = (
        df.columns.str.lower()
                  .str.strip()
                  .str.replace(" ", "_")
                  .str.replace(r"[^0-9a-zA-Z_]", "", regex=True)
    )
    if "week" in df.columns:
        df["week"] = pd.to_datetime(df["week"])
        df.set_index("week", inplace=True)
    return df

def make_graph(df, title):
    return {
        "data": [
            go.Scatter(
                x=df.index,
                y=df[col],
                mode="lines",
                name=col
            ) for col in df.columns
        ],
        "layout": go.Layout(
            title=title,
            paper_bgcolor="black",
            plot_bgcolor="black",
            font=dict(color="white"),
            xaxis=dict(gridcolor="#333"),
            yaxis=dict(gridcolor="#333"),
            legend=dict(font=dict(color="white"))
        )
    }

app = dash.Dash(__name__)
app.title = "Fuel Margin Dashboard"

# Layout with empty graphs that get filled via callback
app.layout = html.Div(
    style={"backgroundColor": "black", "padding": "10px"},
    children=[
        dcc.Interval(id="interval-loader", interval=60*1000, n_intervals=0),  # refresh every 60s
        html.Div(id="graphs-container")
    ]
)

@app.callback(
    Output("graphs-container", "children"),
    Input("interval-loader", "n_intervals")
)
def load_graphs(_):
    return html.Div([
        html.Div(dcc.Graph(figure=make_graph(fetch_table("gallons"), "Gallons")),
                 style={"width": "33%", "display": "inline-block", "padding": "5px"}),
        html.Div(dcc.Graph(figure=make_graph(fetch_table("net_margin"), "Net Margin")),
                 style={"width": "33%", "display": "inline-block", "padding": "5px"}),
        html.Div(dcc.Graph(figure=make_graph(fetch_table("market_pricing"), "Market Pricing")),
                 style={"width": "33%", "display": "inline-block", "padding": "5px"}),
        html.Div(dcc.Graph(figure=make_graph(fetch_table("transactions"), "Transactions")),
                 style={"width": "33%", "display": "inline-block", "padding": "5px"}),
        html.Div(dcc.Graph(figure=make_graph(fetch_table("margin_components"), "Margin Impacting Components")),
                 style={"width": "33%", "display": "inline-block", "padding": "5px"}),
        html.Div(dcc.Graph(figure=make_graph(fetch_table("market_price_delta"), "Market Price Delta")),
                 style={"width": "33%", "display": "inline-block", "padding": "5px"}),
    ], style={"display": "flex", "flex-wrap": "wrap"})

if __name__ == "__main__":
    app.run(debug=True)