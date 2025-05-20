import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

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

def calculate_trend(data, variable):
    numeric_dates = mdates.date2num(data['date'])
    variable_values = data[variable]

    polynomial_coefficients = np.polyfit(numeric_dates, variable_values, 1)
    trend_line_function = np.poly1d(polynomial_coefficients)

    return trend_line_function

def plot_trend(data, variables, path, marker_threshold=50, max_labels=15):
    for variable in variables:
        plt.figure(figsize=(10, 6))

        label = VARIABLE_LABELS[variable]
        marker_style = 'o' if len(data) <= marker_threshold else None
        color = VARIABLE_GRAPH_COLORS[variable]

        plt.plot(data['date'], data[variable], marker=marker_style, label=label, color=color)

        numeric_dates = mdates.date2num(data['date'])
        trend_line_function = calculate_trend(data, variable)
        plt.plot(data['date'], trend_line_function(numeric_dates), linestyle='--', color='gray', label=f'{label} Trend')

        plt.xlabel('Date')
        plt.ylabel(label)
        plt.title(f"{label} over time")

        step = max(1, len(data) // max_labels)
        xticks = data['date'][::step]
        plt.xticks(xticks, rotation=45)

        plt.grid(True)
        plt.legend()
        plt.tight_layout()

        plt.savefig(path + f'{variable}.png', dpi=300)
        plt.show()
