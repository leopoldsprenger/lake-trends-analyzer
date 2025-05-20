import argparse
import numpy as np
import pandas as pd
import matplotlib.dates as mdates
import generate_plots

def parse_arguments():
    parser = argparse.ArgumentParser(description='Lake Trend Analyzer')

    parser.add_argument('input', type=str, help='Input CSV file')
    parser.add_argument('--variables', type=str, nargs='+', help='Variables to analyze')

    return parser.parse_args()

def load_data(filepath):
    return pd.read_csv(filepath)

def forecast_future_lake_level(data):
    data['date'] = pd.to_datetime(data['date'])

    trend_line_function = generate_plots.calculate_trend(data, 'lakelevel')
    last_date = data['date'].max()

    years = [1, 10, 50, 100]
    days_in_year = 365.25

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
            print(f"Warning: Lake is projected to dry out in {int(days_until_dry)} days "
                    f"({years_until_dry:.2f} years), around {dry_date}.")
        else:
            print("\nWarning: Trend suggests lake would already be dry based on current data.")

    print("\nThis forecast is based on historical data and trends.")
    print("The forecast is subject to uncertainty and may not reflect actual future conditions.")

def main():
    trend_folder_path = 'graphs/trends/'

    arguments = parse_arguments()
    filepath = arguments.input

    data = load_data(filepath)
    data.columns = [col.lower() for col in data.columns]
    print(data.head())

    if arguments.variables is not None:
        variables = arguments.variables
    else:
        variables = [col for col in data.columns if col != 'date']

    print(f"\nInput file: {filepath}")
    print(f"Output variables: {variables}\n")

    forecast_future_lake_level(data)
    generate_plots.plot_trend(data, variables, trend_folder_path)

if __name__ == '__main__':
    main()
