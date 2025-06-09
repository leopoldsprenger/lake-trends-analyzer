import pandas as pd
import sys

def reformat_csv(file_path):
    # Read CSV
    df = pd.read_csv(file_path)
    
    # Keep only 'param', 'wert', 'datum'
    df = df[['PARAM', 'WERT', 'DATUM']]
    
    # Pivot so each unique 'param' becomes a column
    df_pivot = df.pivot_table(index='DATUM', columns='PARAM', values='WERT', aggfunc='first').reset_index()
    
    # Reformat 'datum' from Day/Month/Year to YYYY-MM-dd
    df_pivot['DATUM'] = pd.to_datetime(df_pivot['DATUM'], dayfirst=True).dt.strftime('%Y-%m-%d')
    
    # Move 'datum' to the front and set as index
    cols = df_pivot.columns.tolist()
    cols.insert(0, cols.pop(cols.index('DATUM')))
    df_pivot = df_pivot[cols]
    df_pivot.set_index('DATUM', inplace=True)
    
    # Save to new CSV
    output_path = file_path.replace('.csv', '_formatted.csv')
    df_pivot.to_csv(output_path)
    print(f"Formatted CSV saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python format.py <csv_file_path>")
    else:
        reformat_csv(sys.argv[1])