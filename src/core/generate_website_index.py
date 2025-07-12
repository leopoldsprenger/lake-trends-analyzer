import os
import json
import csv

BASE_DIR = 'output'
TIMESERIES_DIR = os.path.join(BASE_DIR, 'timeseries_graphs')
SEASONAL_DIR = os.path.join(BASE_DIR, 'seasonal_graphs')
CORRELATION_DIR = os.path.join(BASE_DIR, 'correlation_graphs')

# Map CSV file path to its data type
CSV_PATH_TYPE_MAP = {
    'data/biological_data.csv': 'biological',
    'data/chemical_data.csv': 'chemical',
    'data/physical_data.csv': 'physical',
}

def build_csv_source_map():
    source_map = {}
    for csv_path, dtype in CSV_PATH_TYPE_MAP.items():
        if not os.path.exists(csv_path):
            continue
        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            try:
                headers = next(reader)
            except StopIteration:
                continue
            for h in headers:
                h_clean = h.strip().lower()
                if h_clean and h_clean != 'lakelevel':  # skip lakelevel, handled separately
                    source_map[h_clean] = dtype
    return source_map

def get_csv_source(filename):
    # Remove extension and directory, get variable name
    var = os.path.basename(filename)
    if var.endswith('_timeseries.png'):
        var = var.replace('_timeseries.png', '')
    elif var.endswith('_seasonal_correlation.png'):
        var = var.replace('_seasonal_correlation.png', '')
    elif var.endswith('_correlation.png'):
        var = var.replace('_correlation.png', '')
    # Always include lakelevel as physical
    if 'lakelevel' in filename:
        return 'physical'
    # Lookup in mapping, default to 'unknown'
    return CSV_SOURCE_MAP.get(var.lower(), 'unknown')

def list_pngs_with_source(directory):
    return [
        {
            'path': os.path.join(directory, f).replace('\\', '/'),
            'csv_source': get_csv_source(f)
        }
        for f in os.listdir(directory)
        if f.lower().endswith('.png')
    ]

def generate_json_index():
    global CSV_SOURCE_MAP
    CSV_SOURCE_MAP = build_csv_source_map()
    index = {
        'timeseries_graphs': list_pngs_with_source(TIMESERIES_DIR),
        'seasonal_correlations': list_pngs_with_source(SEASONAL_DIR),
        'correlation_graphs': {}
    }

    for y_var in os.listdir(CORRELATION_DIR):
        y_path = os.path.join(CORRELATION_DIR, y_var)
        if os.path.isdir(y_path):
            index['correlation_graphs'][y_var] = list_pngs_with_source(y_path)

    with open('index.json', 'w') as f:
        json.dump(index, f, indent=2)

    print("JSON Index generated successfully.")

if __name__ == '__main__':
    generate_json_index()