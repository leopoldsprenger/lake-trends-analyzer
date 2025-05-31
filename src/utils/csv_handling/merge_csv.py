import csv
import sys

def merge_csv(file1_path, file2_path, output_path):
    # Read both files
    with open(file1_path, newline='') as f1, open(file2_path, newline='') as f2:
        reader1 = csv.DictReader(f1)
        reader2 = csv.DictReader(f2)

        data1 = list(reader1)
        data2 = {row['Date']: row for row in reader2}

        # Determine new fields from file2 (excluding 'Date')
        extra_fields = [key for key in reader2.fieldnames if key != 'Date']
        fieldnames = reader1.fieldnames + extra_fields

        # Prepare merged data
        merged_rows = []
        for row in data1:
            date = row['Date']
            extras = data2.get(date, {})
            for field in extra_fields:
                row[field] = extras.get(field, '')
            merged_rows.append(row)

    # Write to output file
    with open(output_path, 'w', newline='') as fout:
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(merged_rows)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python merge_csv.py file1.csv file2.csv output.csv")
    else:
        merge_csv(sys.argv[1], sys.argv[2], sys.argv[3])