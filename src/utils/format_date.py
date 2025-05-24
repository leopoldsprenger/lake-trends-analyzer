import csv
import sys
from datetime import datetime

def reformat_dates(input_path, output_path):
    with open(input_path, newline='', encoding='utf-8') as infile, \
         open(output_path, 'w', newline='', encoding='utf-8') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        if fieldnames is None:
            print("Error: Input CSV file is missing a header row.")
            return
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in reader:
            # Only keep keys that are in fieldnames
            row = {k: v for k, v in row.items() if k in fieldnames}
            # Convert date from DD.MM.YYYY to YYYY-MM-DD
            try:
                date_obj = datetime.strptime(row['Date'], '%d.%m.%Y')
                row['Date'] = date_obj.strftime('%Y-%m-%d')
            except Exception as e:
                pass  # Optionally handle or log errors
            writer.writerow(row)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python reformat_csv.py input.csv output.csv")
    else:
        reformat_dates(sys.argv[1], sys.argv[2])