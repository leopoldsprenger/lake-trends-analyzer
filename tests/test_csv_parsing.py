import io
import unittest
import pandas as pd

def get_sample_csv():
    return """date,lakelevel,temperature
2024-01-01,50.2,15.1
2024-01-02,50.4,15.3
2024-01-03,50.1,14.9
"""

class TestCSVParsing(unittest.TestCase):
    def setUp(self):
        self.sample_csv = get_sample_csv()

    def test_csv_parsing(self):
        df = pd.read_csv(io.StringIO(self.sample_csv))
        self.assertEqual(list(df.columns), ['date', 'lakelevel', 'temperature'])
        self.assertEqual(len(df), 3)
        self.assertEqual(df['lakelevel'].iloc[0], 50.2)
        self.assertEqual(df['temperature'].iloc[2], 14.9)

    def test_data_entry(self):
        df = pd.read_csv(io.StringIO(self.sample_csv))
        new_row = {'date': '2024-01-04', 'lakelevel': 50.0, 'temperature': 14.8}
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        self.assertEqual(len(df), 4)
        self.assertEqual(df.iloc[3]['date'], '2024-01-04')
        self.assertEqual(df.iloc[3]['lakelevel'], 50.0)
        self.assertEqual(df.iloc[3]['temperature'], 14.8)

if __name__ == '__main__':
    unittest.main()
