import argparse
import numpy as np
import pandas as pd
import matplotlib.dates as mdates
import difflib
import sys
from pathlib import Path
import os

core_path = Path(__file__).resolve().parent.parent / "core"
sys.path.append(str(core_path))

import generate_plots
import analysis
import generate_website_index

def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments for the Lake Trend Analyzer.

    Returns:
        argparse.Namespace: Parsed arguments with input file and variables.
    """

    parser = argparse.ArgumentParser(description='Lake Trend Analyzer')

    parser.add_argument('parameter_source', type=str, help='Source CSV file for parameters')
    parser.add_argument('--variables', type=str, nargs='+', help='Variables to analyze')
    parser.add_argument('--y_variable_source', type=str, help='Source CSV file for the y variable on correlation graphs.')
    parser.add_argument('--y_variable', type=str, help='Variable on correlation graphs.')

    return parser.parse_args()

def load_x_variable_data(filepath: str) -> pd.DataFrame:
    """
    Load CSV data from the given file path, cleaning stray commas and empty values.
    Interpolates missing values for numeric columns.

    Args:
        filepath (str): Path to the CSV file.

    Returns:
        pd.DataFrame: Loaded data as a pandas DataFrame.
    """

    dataframe = pd.read_csv(filepath, dtype=str)

    dataframe = dataframe.map(lambda x: x.strip().replace(',', '') if isinstance(x, str) else x)
    dataframe = dataframe.replace('', np.nan)
    dataframe.columns = [col.lower() for col in dataframe.columns]  # Standardize column names to lowercase

    # Try to convert columns to numeric where possible (except 'date')
    for col in dataframe.columns:
        if col.lower() != 'date':
            dataframe[col] = pd.to_numeric(dataframe[col], errors='coerce')

    # Convert 'date' to datetime and set as index for interpolation
    dataframe['date'] = pd.to_datetime(dataframe['date'], errors='coerce')
    dataframe = dataframe.set_index('date')

    # Interpolate numeric columns
    dataframe = dataframe.interpolate(method='time')
    dataframe = dataframe.reset_index()

    # Filter out years 1970 and 2025
    dataframe = dataframe[~dataframe['date'].dt.year.isin([1970, 2025])]

    return dataframe

def load_y_variable_data(filepath: str, y_variable: str) -> pd.DataFrame:
    """
    Load y variable data from the dedicated CSV.

    Args:
        filepath (str): Path to the CSV file.
        y_variable (str): y variable decided by the user.

    Returns:
        pd.DataFrame: Loaded data as a pandas DataFrame.
    """

    dataframe = pd.read_csv(filepath, dtype=str)

    dataframe = dataframe.map(lambda x: x.strip().replace(',', '') if isinstance(x, str) else x)
    dataframe = dataframe.replace('', np.nan)
    dataframe.columns = [col.lower() for col in dataframe.columns]
    dataframe = dataframe.dropna(subset=['date', y_variable])

    if not np.issubdtype(dataframe['date'].dtype, np.datetime64):
        dataframe['date'] = pd.to_datetime(dataframe['date'], errors='coerce')

    dataframe[y_variable] = pd.to_numeric(dataframe[y_variable], errors='coerce')
    dataframe = dataframe.dropna(subset=['date', y_variable])

    return dataframe[['date', y_variable]]

def load_and_process_x_data(filepath: str) -> pd.DataFrame:
    """
    Load and preprocess x variable data from the dedicated CSV before graphing.

    Args:
        filepath (str): Path to the CSV file.

    Returns:
        pd.DataFrame: Loaded and preprocessed x_data as a pandas DataFrame.
    """

    x_data = load_x_variable_data(filepath)
    x_data.columns = [col.lower() for col in x_data.columns]  # Standardize column names to lowercase

    # Remove rows with NaN in 'date'
    x_data = x_data.dropna(subset=['date'])

    # Convert 'date' to datetime if not already
    if not np.issubdtype(x_data['date'].dtype, np.datetime64):
        x_data['date'] = pd.to_datetime(x_data['date'], errors='coerce')
    
    x_data = x_data.dropna(subset=['date'])

    return x_data

def get_variables_from_data(arguments: argparse.Namespace, data: pd.DataFrame) -> list:
    """
    Get all variables from the dataset which have been specified through arguments.

    Args:
        arguments (argparse.Namespace): Command line arguments where the input variables are stored.
        data (pd.DataFrame): Data from which to grab the variables from if none where specified.

    Returns:
        list: List of variable names in lower case.
    """
    if arguments.variables is None:
        variables = [col for col in data.columns if col != 'date']
        return variables

    variables = arguments.variables
    
    for variable in variables:
        if variable not in data.columns:
            close_matches = difflib.get_close_matches(variable, data.columns, n=1)
            suggestion = f" Did you mean '{close_matches[0]}'?" if close_matches else ""
            raise ValueError(f"No variable '{variable}' found in data.{suggestion}")
    
    return variables

def generate_timeseries_graph(data: pd.DataFrame, 
                              variable: str, 
                              folderpath: str, 
                              use_months: bool = False, 
                              use_years: bool = False) -> None:
    """
    Generate timeseries graph for given variable.

    Args:
        data (pd.DataFrame): Dataframe for the variable.
        variable (str): Name of the variable header in lower case.
        folderpath (str): Path to the folder where the correlation graphs will be saved to.
        use_months (bool): Flag if the graph should use monthly averages.
        use_years (bool): Flag if the graph should use yearly averages.
    """

    if variable == 'lakelevel':
        plot_data = data.copy()
        plot_data = plot_data.dropna(subset=['date', 'lakelevel'])
    elif use_years:
        plot_data = data.set_index('date').resample('YE')[variable].mean().reset_index()    
    elif use_months:
        plot_data = data.set_index('date').resample('ME')[variable].mean().reset_index()
    else:  # use_days
        plot_data = data[['date', variable]].copy()
    
    # Interpolate after resampling
    plot_data[variable] = plot_data[variable].interpolate(method='linear')
    plot_data = plot_data.dropna(subset=[variable])
    
    # Always drop rows with missing date (shouldn't happen, but for safety)
    plot_data = plot_data.dropna(subset=['date'])

    if plot_data.empty:
        print(f"Skipping timeseries plot for '{variable}' due to insufficient data.")
        return

    generate_plots.plot_timeseries(plot_data, variable, folderpath, use_years=use_years)

def generate_correlation_graph(x_data: pd.DataFrame, 
                               y_data: pd.DataFrame, 
                               x_variable: str, 
                               y_variable: str, 
                               folderpath: str, 
                               use_monthly_averages: bool = False) -> None:
    """
    Generate correlation graph for an x variable and a y variable.

    Args:
        x_data (pd.DataFrame): Dataframe for the x variable.
        y_data (pd.DataFrame): Dataframe for the y variable.
        x_variable (str): Name of the x variable header in lower case.
        y_variable (str): Name of the y variable header in lower case.
        folderpath (str): Path to the folder where the correlation graphs will be saved to.
        use_monthly_averages (bool): Flag if the graph should use monthly averages.
    """

    correlation_data = None

    if use_monthly_averages:
        x_monthly_data = x_data.set_index('date').resample('ME')[x_variable].mean().reset_index()
        y_monthly_data = y_data.set_index('date').resample('ME')[y_variable].mean().reset_index()
        
        correlation_data = pd.merge(x_monthly_data, y_monthly_data, on='date', how='left')
        correlation_data = correlation_data.dropna(subset=[x_variable, y_variable])
    else:
        correlation_data = pd.merge(x_data[['date', x_variable]], y_data, on='date', how='left')
        correlation_data = correlation_data.dropna(subset=[x_variable, y_data])

    if correlation_data.empty:
        print(f"Skipping correlation plot for '{x_variable}' due to insufficient data.")
        return

    generate_plots.plot_correlation(correlation_data, x_variable, y_variable, folderpath)

def generate_seasonal_graph(data: pd.DataFrame, variable: str, folderpath: str) -> None:
    """
    Generate seasonal graphs for a variable.

    Args:
        data: Dataframe to the CSV from which the variable is from.
        variable: Name of the variable header in lower case.
        folderpath: Path to the folder where the graph will be saved to.
    """

    if data.empty:
        print(f"Skipping seasonal correlation plot for {variable} due to insufficient data.")
        return

    if variable == 'lakelevel':
        seasonal_data = load_y_variable_data('data/lakelevel_data.csv', 'lakelevel')
    else:
        seasonal_data = data

    generate_plots.plot_seasonal_correlation(seasonal_data, variable, folderpath)

def generate_graphs(x_data: pd.DataFrame, 
                    y_data: pd.DataFrame, 
                    variables: list, 
                    y_variable: str, 
                    timeseries_folder_path: str, 
                    correlation_folder_path: str, 
                    seasonal_folder_path: str) -> None:
    """
    Generate all graphs for every independent x variable and an affected y variable.

    Args:
        x_data (pd.DataFrame): Dataframe for the x variable.
        y_data (pd.DataFrame): Dataframe for the y variable.
        variables (list): List of x variable header names in lower case.
        y_variable (str): Name of the y variable header in lower case.
        timeseries_folder_path (str): Path to the timeseries graphs output folder
        correlation_folder_path (str): Path to the correlation graphs output folder
        seasonal_folder_path (str): Path to the seasonal graphs output folder
    """

    # Determine time scale based on date range
    date_min = x_data['date'].min()
    date_max = x_data['date'].max()
    date_range_years = (date_max - date_min).days / 365.25

    use_years = date_range_years > 10
    use_months = 2 < date_range_years <= 10

    for variable in variables:
        if variable == 'lakelevel':
            plot_data = y_data.copy()
        else:
            plot_data = x_data

        generate_timeseries_graph(plot_data, variable, timeseries_folder_path, use_months=use_months, use_years=use_years)

        use_monthly_averages = (use_years or use_months) == True
        if variable != y_variable:
            generate_correlation_graph(x_data, y_data, variable, y_variable, correlation_folder_path, use_monthly_averages=use_monthly_averages)

        generate_seasonal_graph(x_data, variable, seasonal_folder_path)

def main() -> None:
    """
    Main function to execute the Lake Trend Analyzer workflow:
    1. Parse command-line arguments.
    2. Load and preprocess data.
    3. Perform analysis and generate plots.
    """

    arguments = parse_arguments()
    x_data_filepath = arguments.parameter_source

    y_variable = arguments.y_variable if not None else 'lakelevel'
    y_data_filepath = arguments.y_variable_source if not None else 'data/lakelevel_data.csv'

    timeseries_folder_path = f'output/timeseries_graphs/'
    correlation_folder_path = f'output/correlation_graphs/{y_variable}/'
    seasonal_folder_path = 'output/seasonal_graphs/'

    # Ensure the output directories for every variable exist
    os.makedirs(timeseries_folder_path, exist_ok=True)
    os.makedirs(correlation_folder_path, exist_ok=True)
    os.makedirs(seasonal_folder_path, exist_ok=True)

    x_data = load_and_process_x_data(x_data_filepath)

    # Always use lakelevel from data/lakelevel_data.csv
    if y_variable == 'lakelevel':
        y_data = load_y_variable_data('data/lakelevel_data.csv', 'lakelevel')
    else:
        y_data = load_y_variable_data(y_data_filepath, y_variable)
    
    x_data = pd.merge(x_data, y_data, on='date', how='left')

    variables = get_variables_from_data(arguments, x_data)
    
    # avoid double graphing when the y variable has the same dataset as the x variables
    if f"{y_variable}_y" in variables:
        x_data.drop(f'{y_variable}_y', axis=1, inplace=True)
        x_data.rename(columns={f"{y_variable}_x": y_variable}, inplace=True)

        variables.remove(f"{y_variable}_y")
        duplicate_y_variable_index = variables.index(f"{y_variable}_x")
        variables[duplicate_y_variable_index] = y_variable

    # Only forecast if lakelevel data is present
    if y_variable == 'lakelevel':
        analysis.forecast_future_lake_level(y_data, file_path='output/lake_level_forecast.txt')

    generate_graphs(x_data, y_data, variables, y_variable, timeseries_folder_path, correlation_folder_path, seasonal_folder_path)

    print("All graphs generated successfully.")

    generate_website_index.generate_json_index()

if __name__ == '__main__':
    main()
