import pandas as pd
import numpy as np


def generate_gallons(weeks):
    data = {
        "All Hives 2025-03-20": np.sin(np.linspace(0, 10, len(weeks))) * 4_000_000
        + 14_000_000,
        "Detlor Off": np.sin(np.linspace(0, 10, len(weeks)) + 0.5) * 3_000_000
        + 11_000_000,
        "CCC": np.sin(np.linspace(0, 10, len(weeks)) + 1.0) * 2_000_000 + 9_000_000,
        "Retail Minus": np.sin(np.linspace(0, 10, len(weeks)) + 1.5) * 1_500_000
        + 6_000_000,
        "Over/Short": np.full(len(weeks), 500_000),
        "Funded": np.full(len(weeks), 0),
    }
    return pd.DataFrame(data, index=weeks)


def generate_net_margin(weeks):
    data = {
        "All Hives": np.random.normal(8000, 300, len(weeks)),
        "Detlor Off": np.random.normal(7000, 400, len(weeks)),
        "Retail Minus": np.random.normal(6000, 500, len(weeks)),
        "CCC": np.random.normal(5000, 300, len(weeks)),
        "Funded": np.random.normal(4000, 200, len(weeks)),
    }
    return pd.DataFrame(data, index=weeks)


def generate_market_pricing(weeks):
    base = np.linspace(0, 6, len(weeks))
    return pd.DataFrame({
        "Independent Gallon-Weighted": np.sin(base) * 150 + 3400,
        "Detlor Off Gallon-Weighted": np.sin(base + 0.3) * 130 + 3350,
        "CCC Gallon-Weighted": np.sin(base + 0.6) * 110 + 3300,
        "Retail Minus Gallon-Weighted": np.sin(base + 0.9) * 90 + 3250,
        "TIA Gallon-Weighted": np.sin(base + 1.2) * 70 + 3200,
    }, index=weeks)


def generate_transactions(weeks):
    data = {
        "All Hives": np.sin(np.linspace(0, 10, len(weeks))) * 60_000 + 200_000,
        "Detlor Off": np.sin(np.linspace(0, 10, len(weeks)) + 0.5) * 50_000 + 150_000,
        "Retail Minus": np.sin(np.linspace(0, 10, len(weeks)) + 1.0) * 30_000 + 100_000,
        "CCC": np.full(len(weeks), 40_000),
        "Over/Short": np.full(len(weeks), 0),
        "Funded": np.full(len(weeks), 0),
    }
    return pd.DataFrame(data, index=weeks)


def generate_margin_impacting_components(weeks):
    data = {
        "Component A": np.random.normal(2500, 50, len(weeks)),
        "Component B": np.random.normal(2450, 40, len(weeks)),
    }
    return pd.DataFrame(data, index=weeks)


def generate_market_price_delta(weeks):
    base = np.linspace(0, 6, len(weeks))
    return pd.DataFrame({
        "Independent Delta": np.sin(base) * 50 + 9100,
        "Detlor Off Delta": np.sin(base + 0.3) * 50 + 9050,
        "Retail Minus Delta": np.sin(base + 0.6) * 50 + 9000,
        "CCC Delta": np.sin(base + 0.9) * 50 + 8950,
        "TIA Delta": np.sin(base + 1.2) * 50 + 8900,
    }, index=weeks)


if __name__ == "__main__":
    weeks = pd.date_range(start="2024-01-01", end="2025-05-31", freq="W")
    print(generate_gallons(weeks).head())
    print(generate_net_margin(weeks).head())
    print(generate_market_pricing(weeks).head())
    print(generate_transactions(weeks).head())
    print(generate_margin_impacting_components(weeks).head())
    print(generate_market_price_delta(weeks).head())
