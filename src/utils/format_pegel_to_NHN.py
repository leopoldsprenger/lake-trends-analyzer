import csv
import sys

DEEPEST_POINT = 45.3  # meters

input_file = sys.argv[1] if len(sys.argv) > 1 else 'waterlevel.csv'
output_file = sys.argv[2] if len(sys.argv) > 2 else 'formatted_waterlevel.csv'

def adjust_lakelevel(value):
    try:
        lakelevel_m = float(value)
        new_value = lakelevel_m - DEEPEST_POINT
        return round(new_value, 3)
    except ValueError:
        return value  # Return as is if not a number

with open(input_file, newline='', encoding='utf-8') as csvfile_in, \
     open(output_file, 'w', newline='', encoding='utf-8') as csvfile_out:
    reader = csv.DictReader(csvfile_in)
    fieldnames = reader.fieldnames
    if fieldnames is None:
        print(f"Error: Input file '{input_file}' is empty or missing a header row.")
        sys.exit(1)
    writer = csv.DictWriter(csvfile_out, fieldnames=fieldnames)
    writer.writeheader()
    for row in reader:
        if 'LakeLevel' in row:
            row['LakeLevel'] = adjust_lakelevel(row['LakeLevel'])
        writer.writerow(row)
