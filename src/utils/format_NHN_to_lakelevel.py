import csv
import os
import re

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
                with open(file_path, newline='', encoding='utf-8') as csvfile_in:
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
