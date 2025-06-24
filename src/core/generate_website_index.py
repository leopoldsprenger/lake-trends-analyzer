import os
import json

BASE_DIR = 'output'
TIMESERIES_DIR = os.path.join(BASE_DIR, 'timeseries_graphs')
SEASONAL_DIR = os.path.join(BASE_DIR, 'seasonal_graphs')
CORRELATION_DIR = os.path.join(BASE_DIR, 'correlation_graphs')

def list_pngs(directory):
    return [
        os.path.join(directory, f).replace('\\', '/')
        for f in os.listdir(directory)
        if f.lower().endswith('.png')
    ]

def generate_json_index():
    index = {
        'timeseries_graphs': list_pngs(TIMESERIES_DIR),
        'seasonal_correlations': list_pngs(SEASONAL_DIR),
        'correlation_graphs': {}
    }

    for y_var in os.listdir(CORRELATION_DIR):
        y_path = os.path.join(CORRELATION_DIR, y_var)
        if os.path.isdir(y_path):
            index['correlation_graphs'][y_var] = list_pngs(y_path)

    with open('website/index.json', 'w') as f:
        json.dump(index, f, indent=2)

    print("JSON Index generated successfully.")
