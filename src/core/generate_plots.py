import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import calendar
import pandas as pd

VARIABLE_LABELS = {
    'temperature': 'Temperature (°C)',
    'humidity': 'Humidity (%)',
    'precipitation': 'Precipitation (mm)',
    'windspeed': 'Wind Speed (km/h)',
    'lakelevel': 'Lake Level (m)',
}

VARIABLE_GRAPH_COLORS = {
    'temperature': 'red',
    'humidity': 'purple',
    'precipitation': 'green',
    'windspeed': 'orange',
    'lakelevel': 'blue',
}

def get_variable_label(variable: str) -> str:
    return VARIABLE_LABELS.get(variable, variable.capitalize())

def get_variable_color(variable: str) -> str:
    return VARIABLE_GRAPH_COLORS.get(variable, 'black')  # Default to black if not found

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

    polynomial_coefficients = np.polyfit(x_variable_values, y_variable_values, 1)
    trend_line_function = np.poly1d(polynomial_coefficients)

    return trend_line_function

def plot_trend(
    data: pd.DataFrame,
    variable: str,
    path: str,
    marker_threshold: int = 50,
    max_labels: int = 15,
    use_years: bool = False
) -> None:
    """
    Plot the time series and trend line for a given variable.

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

def plot_correlation(
    data: pd.DataFrame,
    variable: str,
    path: str,
    max_labels: int = 15
) -> None:
    """
    Plot the correlation between a variable and lake level.

    Args:
        data (pd.DataFrame): DataFrame containing the data.
        variable (str): Variable to correlate with lake level.
        path (str): Output directory for the plot.
        max_labels (int): Max number of x-axis labels.

    Returns:
        None
    """
    plt.figure(figsize=(10, 6))

    variable_label = get_variable_label(variable)
    lake_level_label = get_variable_label('lakelevel')
    color = get_variable_color(variable)
    if variable not in data.columns:
        raise ValueError(f"Variable '{variable}' not found in the data.")
    alpha = 0.25 if len(data) > 1000 else 1.0  # Adjust alpha for large datasets
    data = data[data[variable] != 0]  # Remove zero values for better correlation
    variable_values = data[variable]

    plt.scatter(variable_values, data['lakelevel'], marker='.', color=color, label=lake_level_label, alpha=alpha)

    min_value = data[variable].min()
    max_value = data[variable].max()
    xticks = np.linspace(min_value, max_value, num=max_labels)
    plt.xticks(xticks, [f"{x:.2f}" for x in xticks])

    trend_line_function = calculate_trend(data, variable, 'lakelevel')
    plt.plot(xticks, trend_line_function(xticks), linestyle='--', color='gray', label=f'{lake_level_label} Trend')

    plt.xlabel(variable_label)
    plt.ylabel(lake_level_label)
    plt.title(f"{lake_level_label} vs {variable_label}")

    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    plt.savefig(path + f'{variable}_correlation.png', dpi=300)

def plot_seasonal_correlation(
    data: pd.DataFrame,
    path: str
) -> None:
    """
    Plot the seasonal (monthly) average of lake level.

    Args:
        data (pd.DataFrame): DataFrame containing the data.
        path (str): Output directory for the plot.

    Returns:
        None
    """
    lake_level_label = get_variable_label('lakelevel')

    plt.figure(figsize=(10, 6))

    # Ensure 'date' column is datetime
    if not np.issubdtype(data['date'].dtype, np.datetime64):
        data['date'] = pd.to_datetime(data['date'], errors='coerce')

    data['month'] = data['date'].dt.month  # Extract month from date
    monthly_means = data.groupby('month')['lakelevel'].mean().reset_index()  # Mean lake level per month

    plt.plot(monthly_means['month'], monthly_means['lakelevel'], marker='o', color='gold', label=lake_level_label)

    # Use month names for x-tick labels
    plt.xticks(monthly_means['month'], monthly_means['month'].apply(lambda x: calendar.month_name[x]), rotation=45)

    plt.xlabel('Month')
    plt.ylabel(lake_level_label)
    plt.title(f"Seasonal Correlation of {lake_level_label}")

    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    plt.savefig(path + 'seasonal_correlation.png', dpi=300)