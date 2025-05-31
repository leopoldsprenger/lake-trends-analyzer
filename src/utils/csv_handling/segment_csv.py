import argparse
import os
import pandas as pd

def segment_data_by_year(input_file, output_dir):
    # Read the CSV file
    df = pd.read_csv(input_file, parse_dates=['Date'])

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Group by year
    df['Year'] = df['Date'].dt.year
    for year, group in df.groupby('Year'):
        decade_dir = os.path.join(output_dir, f"{(year // 10) * 10}s")
        os.makedirs(decade_dir, exist_ok=True)
        output_path = os.path.join(decade_dir, f"data_from_{year}.csv")
        group.drop(columns=['Year']).to_csv(output_path, index=False)
        print(f"Saved {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Segment CSV data into annual files by year.")
    parser.add_argument("input_file", help="Path to input CSV file (must have 'Date' column)")
    parser.add_argument("--output_dir", default="data", help="Directory to save annual files (default: data)")
    args = parser.parse_args()

    segment_data_by_year(args.input_file, args.output_dir)

if __name__ == "__main__":
    main()