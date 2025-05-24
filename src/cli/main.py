import argparse
import numpy as np
import pandas as pd
import matplotlib.dates as mdates
import core.generate_plots as generate_plots
import difflib

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
    Load CSV data from the given file path.

    Args:
        filepath (str): Path to the CSV file.

    Returns:
        pd.DataFrame: Loaded data as a pandas DataFrame.
    """
    return pd.read_csv(filepath)

def forecast_future_lake_level(data: pd.DataFrame) -> None:
    """
    Forecast future lake levels based on historical data and print results.

    Args:
        data (pd.DataFrame): DataFrame containing at least 'date' and 'lakelevel' columns.

    Returns:
        None
    """
    data['date'] = pd.to_datetime(data['date'])  # Ensure 'date' column is datetime

    trend_line_function = generate_plots.calculate_trend(data, 'date', 'lakelevel')
    last_date = data['date'].max()  # Most recent date in the data

    years = [1, 10, 50, 100]
    days_in_year = 365.25  # Average days in a year accounting for leap years

    for year in years:
        future_date = last_date + pd.Timedelta(days=year * days_in_year)
        future_numeric = mdates.date2num(future_date)  # Convert date to matplotlib float format
        forecast = trend_line_function(future_numeric)
        print(f"Forecast for {year} years ({future_date.date()}): {forecast:.2f}")

    slope = trend_line_function.c[0]  # Slope of the trend line
    if slope < 0:
        last_numeric = mdates.date2num(last_date)
        intercept = trend_line_function.c[1]
        zero_day = -intercept / slope  # Day when lake level reaches zero
        days_until_dry = zero_day - last_numeric

        if days_until_dry > 0:
            years_until_dry = days_until_dry / days_in_year
            dry_date = mdates.num2date(zero_day).date()  # Convert numeric date back to datetime
            print(f"\nWarning: Lake is projected to dry out in {int(days_until_dry)} days "
                    f"({years_until_dry:.2f} years), around {dry_date}.")
        else:
            print("\nWarning: Trend suggests lake would already be dry based on current data.")

    print("\nThis forecast is based on historical data and trends.")
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

    for variable in variables:
        generate_plots.plot_trend(data, variable, trend_folder_path)

        if variable != 'lakelevel':
            generate_plots.plot_correlation(data, variable, correlation_folder_path)
    
    generate_plots.plot_seasonal_correlation(data, correlation_folder_path)

    print(f"\nGraphs saved to {trend_folder_path} and {correlation_folder_path}")

if __name__ == '__main__':
    main()
