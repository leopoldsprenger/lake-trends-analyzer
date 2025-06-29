import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import calendar
import pandas as pd

def load_variable_dict_from_file(file_path: str) -> dict:
    """
    Load a variable dictionary from a txt file.
    Each line should be in the format: key: value
    """
    variable_dict = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or ':' not in line:
                    continue
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                if not key or not value:
                    raise ValueError(f"Invalid line in {file_path}: '{line}'")
                variable_dict[key] = value
    except Exception as e:
        raise RuntimeError(f"Error loading variable dictionary from {file_path}: {e}")
    return variable_dict

def load_variable_labels(file_path: str) -> dict:
    """
    Load variable labels from a txt file.
    """
    return load_variable_dict_from_file(file_path)

def load_variable_graph_colors(file_path: str) -> dict:
    """
    Load variable graph colors from a txt file.
    """
    return load_variable_dict_from_file(file_path)

def get_variable_label(variable: str) -> str:
    return load_variable_labels('assets/variable_labels.txt').get(variable, variable.capitalize())

def get_variable_color(variable: str) -> str:
    return load_variable_graph_colors('assets/variable_graph_colors.txt').get(variable, 'black')  # Default to black if not found

def calculate_trend(
    data: pd.DataFrame,
    x_variable: str,
    y_variable: str
) -> np.poly1d:
    """
    Calculate a linear trend line (1st degree polynomial) for the given variables.

    Args:
        data (pd.DataFrame): DataFrame containing the data.
        x_variable (str): Name of the x-axis variable (can be 'date').
        y_variable (str): Name of the y-axis variable.

    Returns:
        np.poly1d: A polynomial function representing the trend line.
    """
    if x_variable == 'date':
        x_variable_values = mdates.date2num(data['date'])  # Convert dates to matplotlib float format
    else:
        x_variable_values = data[x_variable]
    y_variable_values = data[y_variable]

    # Add check for empty arrays
    if len(x_variable_values) == 0 or len(y_variable_values) == 0:
        raise ValueError(f"Cannot calculate trend: no data for {x_variable} vs {y_variable}")

    polynomial_coefficients = np.polyfit(x_variable_values, y_variable_values, 1)
    trend_line_function = np.poly1d(polynomial_coefficients)

    return trend_line_function

def plot_timeseries(
    data: pd.DataFrame,
    variable: str,
    path: str,
    marker_threshold: int = 50,
    max_labels: int = 15,
    use_years: bool = False
) -> None:
    """
    Plot the time series and trend line for a given variable.
    Note: The 'lakelevel' column is always sourced from data/lakelevel_data.csv.

    Args:
        data (pd.DataFrame): DataFrame containing the data.
        variable (str): Variable to plot.
        path (str): Output directory for the plot.
        marker_threshold (int): Max number of points to use markers for.
        max_labels (int): Max number of x-axis labels.

    Returns:
        None
    """
    plt.figure(figsize=(10, 6))

    label = get_variable_label(variable)
    marker_style = '.' if len(data) <= marker_threshold else None  # Use markers for small datasets
    color = get_variable_color(variable)

    plt.plot(data['date'], data[variable], marker=marker_style, label=label, color=color)

    numeric_dates = mdates.date2num(data['date'])
    trend_line_function = calculate_trend(data, 'date', variable)
    plt.plot(data['date'], trend_line_function(numeric_dates), linestyle='--', color='gray', label=f'{label} Trend')

    plt.xlabel('Date')
    plt.ylabel(label)
    plt.title(f"{label} over time")

    if use_years:
        # Use years only for x labels, but limit to max_labels
        years = pd.to_datetime(data['date']).dt.year
        unique_years = np.sort(years.unique())
        step = max(1, len(unique_years) // max_labels)
        selected_years = unique_years[::step]
        xticks = [data['date'][years[years == y].index[0]] for y in selected_years]
        plt.xticks(
            xticks,
            [str(y) for y in selected_years],
            rotation=45
        )
    else:
        # Use normal dates with max label rule
        step = max(1, len(data) // max_labels)
        xticks = data['date'][::step]
        plt.xticks(xticks, rotation=45)

    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    plt.savefig(path + f'{variable}_timeseries.png', dpi=300)
    plt.close()

def plot_correlation(
    data: pd.DataFrame,
    x_variable: str,
    y_variable: str,
    path: str,
    max_labels: int = 15
) -> None:
    """
    Plot the correlation between a variable and lake level.
    Note: The 'lakelevel' column is always sourced from data/lakelevel_data.csv.

    Args:
        data (pd.DataFrame): DataFrame containing the data.
        variable (str): Variable to correlate with lake level.
        path (str): Output directory for the plot.
        max_labels (int): Max number of x-axis labels.

    Returns:
        None
    """
    plt.figure(figsize=(10, 6))

    x_variable_label = get_variable_label(x_variable)
    y_variable_label = get_variable_label(y_variable)
    color = get_variable_color(x_variable)
    if x_variable not in data.columns:
        raise ValueError(f"Variable '{x_variable}' not found in the data.")
    alpha = 0.25 if len(data) > 1000 else 1.0  # Adjust alpha for large datasets
    data = data[data[x_variable] != 0]  # Remove zero values for better correlation
    variable_values = data[x_variable]

    # Add check for empty data after filtering
    if data.empty or data[y_variable].dropna().empty or variable_values.dropna().empty:
        print(f"Skipping correlation plot for '{x_variable}' due to insufficient data after filtering.")
        return

    plt.scatter(variable_values, data[y_variable], marker='.', color=color, label=y_variable_label, alpha=alpha)

    min_value = data[x_variable].min()
    max_value = data[x_variable].max()
    xticks = np.linspace(min_value, max_value, num=max_labels)
    plt.xticks(xticks, [f"{x:.2f}" for x in xticks])

    trend_line_function = calculate_trend(data, x_variable, y_variable)
    plt.plot(xticks, trend_line_function(xticks), linestyle='--', color='gray', label=f'{y_variable_label} Trend')

    plt.xlabel(x_variable_label)
    plt.ylabel(y_variable_label)
    plt.title(f"{y_variable_label} vs {x_variable_label}")

    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    plt.savefig(path + f'{x_variable}_correlation.png', dpi=300)
    plt.close()

def plot_seasonal_correlation(
    data: pd.DataFrame,
    variable: str,
    path: str
) -> None:
    """
    Plot the seasonal (monthly) average of lake level.
    Note: The 'lakelevel' column is always sourced from data/lakelevel_data.csv.

    Args:
        data (pd.DataFrame): DataFrame containing the data.
        path (str): Output directory for the plot.

    Returns:
        None
    """
    label = get_variable_label(variable)

    plt.figure(figsize=(10, 6))

    # Ensure 'date' column is datetime
    if not np.issubdtype(data['date'].dtype, np.datetime64):
        data['date'] = pd.to_datetime(data['date'], errors='coerce')

    data['month'] = data['date'].dt.month  # Extract month from date
    monthly_means = data.groupby('month')[variable].mean().reset_index()  # Mean lake level per month

    plt.plot(monthly_means['month'], monthly_means[variable], marker='o', color=get_variable_color(variable), label=label)

    # Use month names for x-tick labels
    plt.xticks(monthly_means['month'], monthly_means['month'].apply(lambda x: calendar.month_name[x]), rotation=45)

    plt.xlabel('Month')
    plt.ylabel(label)
    plt.title(f"Seasonal Correlation of {label}")

    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    plt.savefig(path + f'{variable}_seasonal_correlation.png', dpi=300)
    plt.close()