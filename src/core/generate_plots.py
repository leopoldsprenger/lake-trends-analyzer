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
    max_labels: int = 15
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

    label = VARIABLE_LABELS[variable]
    marker_style = '.' if len(data) <= marker_threshold else None  # Use markers for small datasets
    color = VARIABLE_GRAPH_COLORS[variable]

    plt.plot(data['date'], data[variable], marker=marker_style, label=label, color=color)

    numeric_dates = mdates.date2num(data['date'])
    trend_line_function = calculate_trend(data, 'date', variable)
    plt.plot(data['date'], trend_line_function(numeric_dates), linestyle='--', color='gray', label=f'{label} Trend')

    plt.xlabel('Date')
    plt.ylabel(label)
    plt.title(f"{label} over time")

    step = max(1, len(data) // max_labels)
    xticks = data['date'][::step]  # Reduce number of x-ticks for readability
    plt.xticks(xticks, rotation=45)

    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    plt.savefig(path + f'{variable}.png', dpi=300)

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

    label = VARIABLE_LABELS[variable]
    color = VARIABLE_GRAPH_COLORS[variable]
    data = data[data[variable] != 0]  # Remove zero values for better correlation
    variable_values = data[variable]

    plt.scatter(variable_values, data['lakelevel'], marker='.', color=color, label=label)

    min_value = data[variable].min()
    max_value = data[variable].max()
    xticks = np.linspace(min_value, max_value, num=max_labels)
    plt.xticks(xticks, [f"{x:.2f}" for x in xticks])

    trend_line_function = calculate_trend(data, variable, 'lakelevel')
    plt.plot(xticks, trend_line_function(xticks), linestyle='--', color='gray', label=f'{label} Trend')

    plt.xlabel(label)
    plt.ylabel(VARIABLE_LABELS['lakelevel'])
    plt.title(f"{VARIABLE_LABELS['lakelevel']} vs {label}")

    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    plt.savefig(path + f'{variable}.png', dpi=300)

def plot_seasonal_correlation(
    data: pd.DataFrame,
    path: str,
    max_labels: int = 12
) -> None:
    """
    Plot the seasonal (monthly) average of lake level.

    Args:
        data (pd.DataFrame): DataFrame containing the data.
        path (str): Output directory for the plot.
        max_labels (int): Max number of x-axis labels.

    Returns:
        None
    """
    plt.figure(figsize=(10, 6))

    # Ensure 'date' column is datetime
    if not np.issubdtype(data['date'].dtype, np.datetime64):
        data['date'] = pd.to_datetime(data['date'], errors='coerce')

    data['month'] = data['date'].dt.month  # Extract month from date
    monthly_means = data.groupby('month')['lakelevel'].mean().reset_index()  # Mean lake level per month

    plt.plot(monthly_means['month'], monthly_means['lakelevel'], marker='o', color='gold', label=VARIABLE_LABELS['lakelevel'])

    # Use month names for x-tick labels
    plt.xticks(monthly_means['month'], monthly_means['month'].apply(lambda x: calendar.month_name[x]), rotation=45)

    plt.xlabel('Month')
    plt.ylabel(VARIABLE_LABELS['lakelevel'])
    plt.title(f"Seasonal Correlation of {VARIABLE_LABELS['lakelevel']}")

    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    plt.savefig(path + 'seasonal.png', dpi=300)