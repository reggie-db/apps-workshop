import pandas as pd
import plotly.graph_objects as go
from shiny import App, ui, run_app
from shinywidgets import output_widget, render_plotly

from data import (
    generate_gallons,
    generate_net_margin,
    generate_market_pricing,
    generate_transactions,
    generate_margin_impacting_components,
    generate_market_price_delta,
)

# Setup
weeks = pd.date_range(start="2024-01-01", end="2025-05-31", freq="2W")
gallons_df = generate_gallons(weeks)
net_margin_df = generate_net_margin(weeks)
market_pricing_df = generate_market_pricing(weeks)
transactions_df = generate_transactions(weeks)
margin_components_df = generate_margin_impacting_components(weeks)
market_price_delta_df = generate_market_price_delta(weeks)

# Helper for making graphs
def make_graph(df, title):
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
    return fig

# UI
app_ui = ui.page_fluid(
    ui.div(
        {"style": "background-color: black; padding: 10px;"},
        ui.div(
            {"style": "display: flex; flex-wrap: nowrap;"},
            ui.div(output_widget("gallons"), style="width: 33%; padding: 5px;"),
            ui.div(output_widget("net_margin"), style="width: 33%; padding: 5px;"),
            ui.div(output_widget("market_pricing"), style="width: 33%; padding: 5px;"),
        ),
        ui.div(
            {"style": "display: flex; flex-wrap: nowrap;"},
            ui.div(output_widget("transactions"), style="width: 33%; padding: 5px;"),
            ui.div(output_widget("margin_components"), style="width: 33%; padding: 5px;"),
            ui.div(output_widget("market_price_delta"), style="width: 33%; padding: 5px;"),
        )
    )
)

# Server
def server(input, output, session):
    @output
    @render_plotly
    def gallons():
        return make_graph(gallons_df, "Gallons")

    @output
    @render_plotly
    def net_margin():
        return make_graph(net_margin_df, "Net Margin")

    @output
    @render_plotly
    def market_pricing():
        return make_graph(market_pricing_df, "Market Pricing")

    @output
    @render_plotly
    def transactions():
        return make_graph(transactions_df, "Transactions")

    @output
    @render_plotly
    def margin_components():
        return make_graph(margin_components_df, "Margin Impacting Components")

    @output
    @render_plotly
    def market_price_delta():
        return make_graph(market_price_delta_df, "Market Price Delta")

# App
app = App(app_ui, server)

if __name__ == "__main__":
    run_app(app, host="0.0.0.0", port=8000)