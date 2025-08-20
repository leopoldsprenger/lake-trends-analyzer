import csv
import sys

from detect_csv_encoding import detect_encoding

# Constants for calculation
NORMALSTAU = 65.49  # meters
DHHN92_OFFSET = 1.35  # meters (135 cm)

input_file = sys.argv[1] if len(sys.argv) > 1 else 'waterlevel.csv'
output_file = sys.argv[2] if len(sys.argv) > 2 else 'formatted_waterlevel.csv'

def format_waterlevel(value):
    try:
        # Convert to float and from cm to meters
        original_m = float(value) / 100.0
        # Adjust waterlevel: reference to DHHN92
        new_value = NORMALSTAU + (original_m - DHHN92_OFFSET)
        return round(new_value, 3)
    except ValueError:
        return value  # Return as is if not a number

with open(input_file, newline='', encoding=detect_encoding(input_file)) as csvfile_in, \
     open(output_file, 'w', newline='', encoding='utf-8') as csvfile_out:
    reader = csv.DictReader(csvfile_in)
    fieldnames = reader.fieldnames
    writer = csv.DictWriter(csvfile_out, fieldnames=fieldnames)
    writer.writeheader()
    for row in reader:
        if 'LakeLevel' in row:
            row['LakeLevel'] = format_waterlevel(row['LakeLevel'])
        writer.writerow(row)
