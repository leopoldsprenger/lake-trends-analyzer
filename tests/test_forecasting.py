import unittest
import pandas as pd
import numpy as np
import io
import sys
import re

from src.cli import main as cli_main

class TestForecastFutureLakeLevelOutput(unittest.TestCase):
    def setUp(self):
        # Prepare sample data
        dates = pd.date_range(start="2020-01-01", periods=100, freq="D")
        lakelevel = np.linspace(50, 45, 100)  # Decreasing trend
        self.df = pd.DataFrame({"date": dates, "lakelevel": lakelevel})

    def test_forecast_future_lake_level_output(self):
        captured = io.StringIO()
        original_stdout = sys.stdout
        sys.stdout = captured
        try:
            cli_main.forecast_future_lake_level(self.df)
        finally:
            sys.stdout = original_stdout

        output = captured.getvalue()
        self.assertIn("Forecast based on recent trend", output)
        self.assertRegex(output, r"Forecast for 1 years.*:")
        self.assertRegex(output, r"Forecast for 10 years.*:")
        self.assertTrue(
            "Warning: Lake is projected to dry out" in output or
            "Trend suggests lake would already be dry" in output
        )

if __name__ == "__main__":
    unittest.main()
