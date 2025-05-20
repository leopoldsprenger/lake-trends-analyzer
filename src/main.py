import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description='Lake Trend Analyzer')

    parser.add_argument('input', type=str, help='Input CSV file')
    parser.add_argument('--variables', type=str, nargs='+', help='Variables to analyze')

    return parser.parse_args()

def main():
    arguments = parse_arguments()
    filepath = arguments.input
    variables = arguments.variables

    print(f"Input file: {filepath}")
    print(f"Output variables: {variables}")

if __name__ == '__main__':
    main()
