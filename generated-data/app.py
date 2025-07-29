import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objs as go
import pandas as pd
import requests
from urllib.parse import urlencode, parse_qs
from datetime import datetime, date
from data import (
    generate_gallons,
    generate_net_margin,
    generate_market_pricing,
    generate_transactions,
    generate_margin_impacting_components,
    generate_market_price_delta,
)

# Initial setup with default dates
default_start = "2024-01-01"
default_end = "2025-05-31"

# Helper for making graphs
def make_graph(df, title):
    if df.empty:
        return dcc.Graph(
            figure=go.Figure(
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
            ),
            config={"displayModeBar": False},
            style={"height": "350px"}
        )
    
    return dcc.Graph(
        figure=go.Figure(
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
        ),
        config={"displayModeBar": False},
        style={"height": "350px"}
    )

# App Layout
app = dash.Dash(__name__)
app.title = "Fuel Margin Dashboard"

app.layout = html.Div(
    style={"backgroundColor": "black", "padding": "10px"},
    children=[
        # URL location component for query params
        dcc.Location(id="url", refresh=False),

        # Interval triggers once on load
        """ 
        dcc.Interval(id="dog-refresh", interval=1, n_intervals=0, max_intervals=1),
        """
        # Placeholder for dog image
        html.Div(
            html.Img(id="dog-img", style={"maxWidth": "300px", "display": "block", "margin": "auto"}),
            style={"textAlign": "center", "paddingBottom": "20px"}
        ),

        # Date selection controls
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
            )
        ], style={"textAlign": "center", "marginBottom": "30px", "padding": "20px"}),

        # Graphs container
        html.Div(id="graphs-container")
    ]
)

# Update date pickers from URL params
@app.callback(
    [Output("start-date-picker", "date"),
     Output("end-date-picker", "date")],
    Input("url", "search")
)
def sync_dates_from_url(search):
    if not search:
        return default_start, default_end
    params = parse_qs(search.lstrip("?"))
    start_date = params.get("start", [default_start])[0]
    end_date = params.get("end", [default_end])[0]
    return start_date, end_date

# Update URL query params when button clicked
@app.callback(
    Output("url", "search"),
    Input("update-button", "n_clicks"),
    State("start-date-picker", "date"),
    State("end-date-picker", "date"),
    prevent_initial_call=True
)
def update_url_params(n_clicks, start_date, end_date):
    params = {"start": start_date, "end": end_date}
    return "?" + urlencode(params)

# Update graphs
@app.callback(
    Output("graphs-container", "children"),
    [Input("start-date-picker", "date"),
     Input("end-date-picker", "date")]
)
def update_graphs(start_date, end_date):
    if start_date is None or end_date is None:
        start_date = default_start
        end_date = default_end
    
    try:
        weeks = pd.date_range(start=start_date, end=end_date, freq="2W")
        
        if len(weeks) == 0:
            empty_df = pd.DataFrame()
            return html.Div([
                html.Div([
                    html.Div(make_graph(empty_df, "Liters"), style={"width": "33%", "display": "inline-block", "padding": "5px"}),
                    html.Div(make_graph(empty_df, "Net Margin"), style={"width": "33%", "display": "inline-block", "padding": "5px"}),
                    html.Div(make_graph(empty_df, "Market Pricing"), style={"width": "33%", "display": "inline-block", "padding": "5px"}),
                ], style={"display": "flex", "flex-wrap": "nowrap"}),

                html.Div([
                    html.Div(make_graph(empty_df, "Transactions"), style={"width": "33%", "display": "inline-block", "padding": "5px"}),
                    html.Div(make_graph(empty_df, "Margin Impacting Components"), style={"width": "33%", "display": "inline-block", "padding": "5px"}),
                    html.Div(make_graph(empty_df, "Market Price Delta"), style={"width": "33%", "display": "inline-block", "padding": "5px"}),
                ], style={"display": "flex", "flex-wrap": "nowrap"}),
            ])
        
        gallons_df = generate_gallons(weeks)
        net_margin_df = generate_net_margin(weeks)
        market_pricing_df = generate_market_pricing(weeks)
        transactions_df = generate_transactions(weeks)
        margin_components_df = generate_margin_impacting_components(weeks)
        market_price_delta_df = generate_market_price_delta(weeks)

        return html.Div([
            html.Div([
                html.Div(make_graph(gallons_df, "Liters"), style={"width": "33%", "display": "inline-block", "padding": "5px"}),
                html.Div(make_graph(net_margin_df, "Net Margin"), style={"width": "33%", "display": "inline-block", "padding": "5px"}),
                html.Div(make_graph(market_pricing_df, "Market Pricing"), style={"width": "33%", "display": "inline-block", "padding": "5px"}),
            ], style={"display": "flex", "flex-wrap": "nowrap"}),

            html.Div([
                html.Div(make_graph(transactions_df, "Transactions"), style={"width": "33%", "display": "inline-block", "padding": "5px"}),
                html.Div(make_graph(margin_components_df, "Margin Impacting Components"), style={"width": "33%", "display": "inline-block", "padding": "5px"}),
                html.Div(make_graph(market_price_delta_df, "Market Price Delta"), style={"width": "33%", "display": "inline-block", "padding": "5px"}),
            ], style={"display": "flex", "flex-wrap": "nowrap"}),
        ])
        
    except Exception as e:
        return html.Div([
            html.H3(f"Error generating data: {str(e)}", style={"color": "red", "textAlign": "center"})
        ])

# Callback to update dog image
""" 
@app.callback(
    Output("dog-img", "src"),
    Input("dog-refresh", "n_intervals")
)
def load_random_dog(_):
    return requests.get("https://dog.ceo/api/breeds/image/random").json()["message"]
 """
if __name__ == "__main__":
    app.run(debug=True)