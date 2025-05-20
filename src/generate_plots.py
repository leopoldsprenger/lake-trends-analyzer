import matplotlib.pyplot as plt

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

def plot_trend(data, variables, marker_threshold=50, max_labels=15):
    for variable in variables:
        plt.figure(figsize=(10, 6))

        label = VARIABLE_LABELS[variable]
        marker_style = 'o' if len(data) <= marker_threshold else None
        color = VARIABLE_GRAPH_COLORS[variable]

        plt.plot(data['date'], data[variable], marker=marker_style, label=label, color=color)

        plt.xlabel('Date')
        plt.ylabel(label)
        plt.title(f"{label} over time")

        step = max(1, len(data) // max_labels)
        xticks = data['date'][::step]
        plt.xticks(xticks, rotation=45)

        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()
