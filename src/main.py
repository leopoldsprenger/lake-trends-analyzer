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

    data = load_data(filepath)
    data.columns = [col.lower() for col in data.columns]
    print(data.head())

    if arguments.variables is not None:
        variables = arguments.variables
    else:
        variables = [col for col in data.columns if col != 'date']

    trend_folder_path = 'graphs/trends/'

    print(f"Input file: {filepath}")
    print(f"Output variables: {variables}")

    generate_plots.plot_trend(data, variables, trend_folder_path)

if __name__ == '__main__':
    main()
