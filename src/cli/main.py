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

    Args:
        filepath (str): Path to the CSV file.

    Returns:
        pd.DataFrame: Loaded data as a pandas DataFrame.
    """
    df = pd.read_csv(filepath, dtype=str)
    df = df.map(lambda x: x.strip().replace(',', '') if isinstance(x, str) else x)
    df = df.replace('', np.nan)
    # Try to convert columns to numeric where possible (except 'date')
    for col in df.columns:
        if col.lower() != 'date':
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

def forecast_future_lake_level(data: pd.DataFrame) -> None:
    """
    Forecast future lake levels based on recent trend after detecting major trajectory changes.

    Args:
        data (pd.DataFrame): DataFrame containing at least 'date' and 'lakelevel' columns.

    Returns:
        None
    """
    data = data.copy()
    data['date'] = pd.to_datetime(data['date'])
    data = data.sort_values('date')

    # Convert dates to matplotlib float format for regression
    x = mdates.date2num(data['date'])
    y = data['lakelevel'].values

    # Calculate rolling slope to detect change points
    window = max(10, len(data) // 10)  # Use a window of at least 10 or 10% of data
    slopes = pd.Series(np.polyfit(x[i:i+window], y[i:i+window], 1)[0]
                       for i in range(len(x) - window + 1))
    # Find where the slope changes significantly (e.g., by more than 2x std deviation)
    slope_diff = slopes.diff().abs()
    threshold = 2 * slope_diff.std()
    change_points = slope_diff[slope_diff > threshold].index.tolist()

    # Use the most recent segment after the last major change point
    if change_points:
        last_change_idx = change_points[-1]
        start_idx = last_change_idx
        x_recent = x[start_idx:]
        y_recent = y[start_idx:]
        data_recent = data.iloc[start_idx:]
    else:
        x_recent = x
        y_recent = y
        data_recent = data

    # Fit trend line to recent segment
    trend_line_function = np.poly1d(np.polyfit(x_recent, y_recent, 1))
    last_date = data_recent['date'].max()

    years = [1, 10, 50, 100]
    days_in_year = 365.25

    print("Forecast based on recent trend after major trajectory change detection:")
    for year in years:
        future_date = last_date + pd.Timedelta(days=year * days_in_year)
        future_numeric = mdates.date2num(future_date)
        forecast = trend_line_function(future_numeric)
        print(f"Forecast for {year} years ({future_date.date()}): {forecast:.2f}")

    slope = trend_line_function.c[0]
    if slope < 0:
        last_numeric = mdates.date2num(last_date)
        intercept = trend_line_function.c[1]
        zero_day = -intercept / slope
        days_until_dry = zero_day - last_numeric

        if days_until_dry > 0:
            years_until_dry = days_until_dry / days_in_year
            dry_date = mdates.num2date(zero_day).date()
            print(f"\nWarning: Lake is projected to dry out in {int(days_until_dry)} days "
                  f"({years_until_dry:.2f} years), around {dry_date}.")
        else:
            print("\nWarning: Trend suggests lake would already be dry based on current data.")

    print("\nThis forecast is based on the most recent trend segment after detecting major changes.")
    print("The forecast is subject to uncertainty and may not reflect actual future conditions.")

def main() -> None:
    """
    Main function to run the Lake Trend Analyzer.

    Returns:
        None
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
    # Remove rows with NaT in 'date' after conversion
    data = data.dropna(subset=['date'])

    if arguments.variables is not None:
        variables = arguments.variables
        # Check for invalid variables and suggest closest matches
        for var in variables:
            if var not in data.columns:
                close_matches = difflib.get_close_matches(var, data.columns, n=1)
                suggestion = f" Did you mean '{close_matches[0]}'?" if close_matches else ""
                raise ValueError(f"No variable '{var}' found in data.{suggestion}")
    else:
        variables = [col for col in data.columns if col != 'date']  # Use all columns except 'date'

    forecast_future_lake_level(data)

    use_months = len(data) > 1000
    use_years = len(data) > 3000

    for variable in variables:
        # Remove rows with NaN for the variable (and lakelevel if needed) before plotting
        if variable == 'lakelevel':
            plot_data = data.dropna(subset=['date', 'lakelevel'])
        else:
            if use_years:
                yearly = data.set_index('date').resample('YE')
                plot_data = yearly[variable].mean().reset_index()
                if 'lakelevel' in data.columns and variable != 'lakelevel':
                    plot_data['lakelevel'] = yearly['lakelevel'].mean().values
                year_counts = data.set_index('date').resample('YE').size().reset_index(name='count')
                complete_years = year_counts[year_counts['count'] >= 365]['date']
                plot_data = plot_data[plot_data['date'].isin(complete_years)].reset_index(drop=True)
            elif use_months:
                plot_data = data.set_index('date').resample('ME')[variable].mean().reset_index()
                if 'lakelevel' in data.columns and variable != 'lakelevel':
                    plot_data['lakelevel'] = data.set_index('date')['lakelevel'].resample('M').mean().values
            else:
                plot_data = data
            # Remove rows with NaN for variable and lakelevel if present
            subset_cols = ['date', variable]
            if 'lakelevel' in plot_data.columns:
                subset_cols.append('lakelevel')
            plot_data = plot_data.dropna(subset=subset_cols)

        if plot_data.empty:
            print(f"Skipping plot for '{variable}' due to insufficient data.")
            continue

        generate_plots.plot_trend(plot_data, variable, trend_folder_path, use_years=use_years)

        if variable != 'lakelevel':
            if use_months:
                monthly_data = data.set_index('date').resample('ME').mean().reset_index()
                monthly_data = monthly_data.dropna(subset=[variable, 'lakelevel'])
                if not monthly_data.empty:
                    generate_plots.plot_correlation(monthly_data, variable, correlation_folder_path)
                else:
                    print(f"Skipping correlation plot for '{variable}' due to insufficient data.")
            else:
                corr_data = data.dropna(subset=[variable, 'lakelevel'])
                if not corr_data.empty:
                    generate_plots.plot_correlation(corr_data, variable, correlation_folder_path)
                else:
                    print(f"Skipping correlation plot for '{variable}' due to insufficient data.")

    # For seasonal correlation, drop missing values
    seasonal_data = data.dropna(subset=['date', 'lakelevel'])
    if not seasonal_data.empty:
        generate_plots.plot_seasonal_correlation(seasonal_data, correlation_folder_path)
    else:
        print("Skipping seasonal correlation plot due to insufficient data.")

    print(f"\nGraphs saved to {trend_folder_path} and {correlation_folder_path}")

if __name__ == '__main__':
    main()
