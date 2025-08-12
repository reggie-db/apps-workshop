# Apps Workshop

A collection of interactive fuel margin dashboard applications demonstrating different data sources and web frameworks for analytics applications.

## Repository Structure

This repository contains two main applications showcasing different approaches to building data dashboards:

### Generated Data App (`generated-data/`)
An interactive dashboard that generates synthetic fuel margin data in real-time.

**Key Files:**
- `app.py` - Main Dash application with interactive date selection
- `app-shiny.py` - Alternative implementation using Shiny for Python
- `data.py` - Synthetic data generation functions
- `app.yaml` - Databricks Apps configuration
- `sync.sh` - Development deployment script

### SQL Data App (`sql-data/`)
A dashboard that reads fuel margin data from a Databricks SQL warehouse.

**Key Files:**
- `app.py` - Dash application with live database connectivity
- `sql-insert.py` - Data population script for Databricks tables
- `app.yaml` - Databricks Apps configuration  
- `sync.sh` - Development deployment script

## Applications Overview

### Generated Data Dashboard

**Features:**
- Interactive date range selection (start/end date pickers)
- URL query parameter support for sharing specific date ranges
- Six comprehensive chart types:
  - **Gallons/Liters**: Volume metrics across different fuel categories
  - **Net Margin**: Profit margins by fuel type
  - **Market Pricing**: Gallon-weighted pricing trends
  - **Transactions**: Transaction volume by category
  - **Margin Impacting Components**: Key cost components
  - **Market Price Delta**: Price variation analysis

**Technology Stack:**
- **Frontend**: Dash (Python web framework)
- **Visualization**: Plotly interactive charts
- **Data Generation**: NumPy mathematical functions (sine waves, normal distributions)
- **Styling**: Custom dark theme CSS

**Data Sources:**
- Synthetic data generated using mathematical functions
- Configurable date ranges from 2024-01-01 to 2025-05-31
- Real-time data generation based on selected time periods

### SQL Data Dashboard

**Features:**
- Auto-refresh every 60 seconds
- URL query parameter support for sharing specific date ranges
- Same six chart types as generated data app
- Live connection to Databricks SQL warehouse
- Consistent dark theme UI

**Technology Stack:**
- **Frontend**: Dash framework
- **Database**: Databricks SQL Warehouse
- **Data Processing**: Pandas for data manipulation
- **Authentication**: Token-based access via HTTP headers when running in Databricks Apps; falls back to local `databricks` profile or environment config when running locally

**Database Schema:**
- **Catalog**: `reggie_pierce`
- **Schema**: `apps_workshop`
- **Tables**: `gallons`, `net_margin`, `market_pricing`, `transactions`, `margin_components`, `market_price_delta`

### Alternative Implementation: Shiny

The `generated-data/app-shiny.py` provides an alternative implementation using Shiny for Python, offering:
- Same visualization capabilities as the Dash version
- Different reactive programming model
- Simplified server/UI architecture

## Quick Start

### Prerequisites
- Python 3.8+
- Databricks workspace access (for SQL data app)
- Required dependencies (see `requirements.txt` in each directory)

### Running the Generated Data App

```bash
cd generated-data
pip install -r requirements.txt
python app.py
```

Navigate to `http://localhost:8050` to view the dashboard.

**Dash Alternative:**
```bash
python app-shiny.py
```
Access at `http://localhost:8000`

### Running the SQL Data App

```bash
cd sql-data
pip install -r requirements.txt

# First, populate the database tables
python sql-insert.py

# Then run the dashboard
python app.py
```

Configuration notes:
- Set the SQL Warehouse HTTP path in `sql-data/app.py` by updating the `SQL_HTTP_PATH` constant to point to your warehouse.
- When running inside Databricks Apps, the app uses the `x-forwarded-access-token` request header for auth automatically.
- When running locally, ensure Databricks host and token are available via your `~/.databrickscfg` profile or environment variables supported by `databricks-sdk`.

### Deployment to Databricks

Both applications include deployment configurations for Databricks Apps:

1. **Configuration**: Each app has an `app.yaml` file defining the runtime environment
2. **Live Development**: Use `sync.sh` scripts for real-time development with workspace sync
3. **Environment Variables**: Databricks warehouse ID configured via environment variables

## Dependencies

### Generated Data App
- `dash` - Web framework
- `plotly` - Interactive charts
- `pandas` - Data manipulation  
- `numpy` - Mathematical operations
- `shiny` - Alternative framework option

### SQL Data App
- `dash` - Web framework
- `plotly` - Interactive charts
- `pandas` - Data manipulation
- `databricks-sql-connector` - Database connectivity
- `databricks-sdk` - Databricks API access

## Key Features

### User Interface
- **Dark Theme**: Consistent black background with white text
- **Responsive Layout**: Flexible grid system with 3 charts per row
- **Interactive Controls**: Date pickers and update buttons
- **Modern Styling**: Clean, professional appearance

### Data Visualization
- **Multiple Chart Types**: Six different analytical views
- **Time Series**: All charts show data over time periods
- **Interactive Plots**: Hover tooltips, zoom, and pan capabilities
- **Consistent Styling**: Unified color scheme and formatting

### Technical Architecture
- **Modular Design**: Separate data generation and visualization logic
- **Configurable Data Sources**: Easy switching between generated and database sources
- **Error Handling**: Graceful handling of data generation failures
- **Performance Optimized**: Efficient data processing and chart rendering

## Development

### File Structure
```
apps-workshop/
├── generated-data/
│   ├── app.py              # Main Dash application
│   ├── app-shiny.py        # Shiny alternative
│   ├── data.py             # Data generation functions
│   ├── requirements.txt    # Python dependencies
│   ├── app.yaml           # Databricks config
│   ├── sync.sh            # Deployment script
│   └── assets/
│       └── styles.css     # Custom styling
└── sql-data/
    ├── app.py              # SQL-powered Dash app
    ├── sql-insert.py       # Database population
    ├── requirements.txt    # Python dependencies
    ├── app.yaml           # Databricks config
    ├── sync.sh            # Deployment script
    └── assets/
        └── styles.css     # Custom styling
```

### Customization
- **Data Generation**: Modify functions in `data.py` to change synthetic data patterns
- **Chart Types**: Add new visualizations by extending the data generation and display logic
- **Styling**: Update `assets/styles.css` for theme customization
- **Database Schema**: Modify table structure in `sql-insert.py` as needed

## License

This project is part of a apps workshop and is intended for educational and demonstration purposes. 