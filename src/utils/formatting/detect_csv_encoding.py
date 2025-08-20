import chardet

def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        raw = f.read(4096)
    return chardet.detect(raw)['encoding']

if __name__ == "__main__":
    import csv
    import sys

    input_file = sys.argv[1] if len(sys.argv) > 1 else 'waterlevel.csv'
    print(f"Input file: {input_file}")
    print("Detected encoding:", detect_encoding(input_file))