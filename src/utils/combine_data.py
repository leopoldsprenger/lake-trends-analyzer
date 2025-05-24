import os
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
OUTPUT_FILE = os.path.join(DATA_DIR, 'data_since_1970.csv')

def find_csv_files(data_dir):
    csv_files = []
    for decade_folder in sorted(os.listdir(data_dir)):
        decade_path = os.path.join(data_dir, decade_folder)
        if os.path.isdir(decade_path) and decade_folder.endswith('s'):
            for file in sorted(os.listdir(decade_path)):
                if file.endswith('.csv'):
                    csv_files.append(os.path.join(decade_path, file))
    return csv_files

def combine_csvs(csv_files, output_file):
    combined_df = pd.concat([pd.read_csv(f) for f in csv_files], ignore_index=True)
    combined_df.to_csv(output_file, index=False)
    print(f"Combined {len(csv_files)} files into {output_file}")

if __name__ == "__main__":
    csv_files = find_csv_files(DATA_DIR)
    if not csv_files:
        print("No CSV files found.")
    else:
        combine_csvs(csv_files, OUTPUT_FILE)