import argparse
import numpy as np
import pandas as pd
import matplotlib.dates as mdates
import difflib
import sys
from pathlib import Path

core_path = Path(__file__).resolve().parent.parent / "core"
sys.path.append(str(core_path))

import generate_plots
import analysis

def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments for the Lake Trend Analyzer.

    Returns:
        argparse.Namespace: Parsed arguments with input file and variables.
    """
    parser = argparse.ArgumentParser(description='Lake Trend Analyzer')

    parser.add_argument('input', type=str, help='Input CSV file')
    parser.add_argument('--variables', type=str, nargs='+', help='Variables to analyze')

    return parser.parse_args()

def load_data(filepath: str) -> pd.DataFrame:
    """
    Load CSV data from the given file path, cleaning stray commas and empty values.
    Interpolates missing values for numeric columns.

    Args:
        filepath (str): Path to the CSV file.

    Returns:
        pd.DataFrame: Loaded data as a pandas DataFrame.
    """
    df = pd.read_csv(filepath, dtype=str)
    df = df.map(lambda x: x.strip().replace(',', '') if isinstance(x, str) else x)
    df = df.replace('', np.nan)
    df.columns = [col.lower() for col in df.columns]  # Standardize column names to lowercase
    # Try to convert columns to numeric where possible (except 'date')
    for col in df.columns:
        if col.lower() != 'date':
            df[col] = pd.to_numeric(df[col], errors='coerce')
    # Convert 'date' to datetime and set as index for interpolation
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.set_index('date')
    # Interpolate numeric columns
    df = df.interpolate(method='time')
    df = df.reset_index()
    # Filter out years 1970 and 2025
    df = df[~df['date'].dt.year.isin([1970, 2025])]
    return df

def load_lakelevel_data() -> pd.DataFrame:
    """
    Load lakelevel data from the dedicated CSV.
    """
    df = pd.read_csv('data/lakelevel_data.csv', dtype=str)
    df = df.map(lambda x: x.strip().replace(',', '') if isinstance(x, str) else x)
    df = df.replace('', np.nan)
    df.columns = [col.lower() for col in df.columns]
    df = df.dropna(subset=['date', 'lakelevel'])
    if not np.issubdtype(df['date'].dtype, np.datetime64):
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['lakelevel'] = pd.to_numeric(df['lakelevel'], errors='coerce')
    df = df.dropna(subset=['date', 'lakelevel'])
    return df[['date', 'lakelevel']]

def main() -> None:
    """
    Main function to execute the Lake Trend Analyzer workflow:
    1. Parse command-line arguments.
    2. Load and preprocess data.
    3. Perform analysis and generate plots.
    """
    trend_folder_path = 'output/timeseries_graphs/'
    correlation_folder_path = 'output/correlation_graphs/'

    arguments = parse_arguments()
    filepath = arguments.input

    data = load_data(filepath)
    data.columns = [col.lower() for col in data.columns]  # Standardize column names to lowercase

    # Remove rows with NaN in 'date'
    data = data.dropna(subset=['date'])

    # Convert 'date' to datetime if not already
    if not np.issubdtype(data['date'].dtype, np.datetime64):
        data['date'] = pd.to_datetime(data['date'], errors='coerce')
    data = data.dropna(subset=['date'])

    # --- Always use lakelevel from data/lakelevel_data.csv ---
    lakelevel_df = load_lakelevel_data()
    data = pd.merge(data, lakelevel_df, on='date', how='left')
    # --------------------------------------------------------

    if arguments.variables is not None:
        variables = arguments.variables
        for var in variables:
            if var not in data.columns:
                close_matches = difflib.get_close_matches(var, data.columns, n=1)
                suggestion = f" Did you mean '{close_matches[0]}'?" if close_matches else ""
                raise ValueError(f"No variable '{var}' found in data.{suggestion}")
    else:
        variables = [col for col in data.columns if col != 'date']

    # Only forecast if lakelevel data is present
    if 'lakelevel' in data.columns:
        analysis.forecast_future_lake_level(data, file_path='output/lake_level_forecast.txt')

    # Determine time scale based on date range
    date_min = data['date'].min()
    date_max = data['date'].max()
    date_range_years = (date_max - date_min).days / 365.25

    use_years = date_range_years > 10
    use_months = 2 < date_range_years <= 10
    use_days = date_range_years <= 2

    for variable in variables:
        if variable == 'lakelevel':
            plot_data = lakelevel_df.copy()
            plot_data = plot_data.dropna(subset=['date', 'lakelevel'])
        else:
            if use_years:
                plot_data = data.set_index('date').resample('YE')[variable].mean().reset_index()
                # Interpolate after resampling
                plot_data[variable] = plot_data[variable].interpolate(method='linear')
                plot_data = plot_data.dropna(subset=[variable])
            elif use_months:
                plot_data = data.set_index('date').resample('ME')[variable].mean().reset_index()
                plot_data[variable] = plot_data[variable].interpolate(method='linear')
                plot_data = plot_data.dropna(subset=[variable])
            else:  # use_days
                plot_data = data[['date', variable]].copy()
                plot_data[variable] = plot_data[variable].interpolate(method='linear')
                plot_data = plot_data.dropna(subset=[variable])
        # Always drop rows with missing date (shouldn't happen, but for safety)
        plot_data = plot_data.dropna(subset=['date'])

        if plot_data.empty:
            print(f"Skipping plot for '{variable}' due to insufficient data.")
            continue

        generate_plots.plot_trend(plot_data, variable, trend_folder_path, use_years=use_years)

        # Correlation plots (only if not lakelevel)
        if variable != 'lakelevel':
            if use_months or use_years:
                monthly_data = data.set_index('date').resample('ME')[variable].mean().reset_index()
                lakelevel_monthly = lakelevel_df.set_index('date').resample('ME')['lakelevel'].mean().reset_index()
                monthly_data = pd.merge(monthly_data, lakelevel_monthly, on='date', how='left')
                monthly_data = monthly_data.dropna(subset=[variable, 'lakelevel'])
                if not monthly_data.empty:
                    generate_plots.plot_correlation(monthly_data, variable, correlation_folder_path)
                else:
                    print(f"Skipping correlation plot for '{variable}' due to insufficient data.")
            else:
                corr_data = pd.merge(data[['date', variable]], lakelevel_df, on='date', how='left')
                corr_data = corr_data.dropna(subset=[variable, 'lakelevel'])
                if not corr_data.empty:
                    generate_plots.plot_correlation(corr_data, variable, correlation_folder_path)
                else:
                    print(f"Skipping correlation plot for '{variable}' due to insufficient data.")

    # For seasonal correlation, use only lakelevel_df
    if not lakelevel_df.empty:
        generate_plots.plot_seasonal_correlation(lakelevel_df, correlation_folder_path)
    else:
        print("Skipping seasonal correlation plot due to insufficient data.")

    print(f"Graphs saved to {trend_folder_path} and {correlation_folder_path}")

if __name__ == '__main__':
    main()
