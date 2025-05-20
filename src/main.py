import argparse
import pandas as pd
import generate_plots

def parse_arguments():
    parser = argparse.ArgumentParser(description='Lake Trend Analyzer')

    parser.add_argument('input', type=str, help='Input CSV file')
    parser.add_argument('--variables', type=str, nargs='+', help='Variables to analyze')

    return parser.parse_args()

def load_data(filepath):
    return pd.read_csv(filepath)

def main():
    arguments = parse_arguments()
    filepath = arguments.input
    variables = arguments.variables

    print(f"Input file: {filepath}")
    print(f"Output variables: {variables}")

    data = load_data(filepath)
    data.columns = [col.lower() for col in data.columns]
    print(data.head())

    generate_plots.plot_trend(data, variables)

if __name__ == '__main__':
    main()
