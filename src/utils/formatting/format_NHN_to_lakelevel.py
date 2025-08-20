import csv
import os
import re
import sys

from detect_csv_encoding import detect_encoding

DEEPEST_POINT = 45.3  # meters
DATA_DIR = 'data'
DECADE_PATTERN = re.compile(r'^\d{4}s$')
YEAR_PATTERN = re.compile(r'^data_from_(\d{4})\.csv$')

def adjust_lakelevel(value):
    try:
        lakelevel_m = float(value)
        new_value = lakelevel_m - DEEPEST_POINT
        return round(new_value, 3)
    except ValueError:
        return value  # Return as is if not a number

def process_directories():
    for root, dirs, files in os.walk(DATA_DIR):
        # Only process directories like 1970s, 1980s, etc.
        if not DECADE_PATTERN.match(os.path.basename(root)):
            continue
        for file in files:
            match = YEAR_PATTERN.match(file)
            if match:
                year = int(match.group(1))
                if 1970 <= year <= 2025:
                    file_path = os.path.join(root, file)
                    # Read and process the CSV
                    with open(file_path, newline='', encoding=detect_encoding(file_path)) as csvfile_in:
                        reader = csv.DictReader(csvfile_in)
                        fieldnames = reader.fieldnames
                        if fieldnames is None:
                            print(f"Error: Input file '{file_path}' is empty or missing a header row.")
                            continue
                        rows = []
                        for row in reader:
                            if 'LakeLevel' in row:
                                row['LakeLevel'] = adjust_lakelevel(row['LakeLevel'])
                            rows.append(row)
                    # Overwrite the file with the formatted data
                    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile_out:
                        writer = csv.DictWriter(csvfile_out, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(rows)

def process_single_file(input_file, output_file):
    with open(input_file, newline='', encoding=detect_encoding(input_file)) as csvfile_in, \
         open(output_file, 'w', newline='', encoding='utf-8') as csvfile_out:
        reader = csv.DictReader(csvfile_in)
        fieldnames = reader.fieldnames
        if fieldnames is None:
            print(f"Error: Input file '{input_file}' is empty or missing a header row.")
            return
        writer = csv.DictWriter(csvfile_out, fieldnames=fieldnames)
        writer.writeheader()
        for row in reader:
            if 'LakeLevel' in row:
                row['LakeLevel'] = adjust_lakelevel(row['LakeLevel'])
            writer.writerow(row)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        process_directories()
    elif len(sys.argv) == 3:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        process_single_file(input_file, output_file)
    else:
        print("Usage: python format_NHN_to_lakelevel.py [input_file output_file]")
        print("Or run without arguments to process all directories in 'data'.")