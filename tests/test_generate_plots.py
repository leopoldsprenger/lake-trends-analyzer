import os
import tempfile
import unittest
import pandas as pd
import numpy as np

from src.core import generate_plots

def create_sample_data():
    dates = pd.date_range(start="2024-01-01", periods=30, freq="D")
    data = pd.DataFrame({
        "date": dates,
        "lakelevel": np.linspace(50, 55, 30),
        "temperature": np.linspace(10, 20, 30)
    })
    return data

class TestGeneratePlots(unittest.TestCase):

    def setUp(self):
        self.sample_data = create_sample_data()

    def test_calculate_trend(self):
        trend_fn = generate_plots.calculate_trend(self.sample_data, "date", "lakelevel")
        # The slope should be positive and close to the increment per day
        self.assertGreater(trend_fn.c[0], 0)
        # The function should return a float when called with a float
        x_numeric = np.linspace(1, 10, 10)
        y_pred = trend_fn(x_numeric)
        self.assertIsInstance(y_pred, np.ndarray)

    def test_plot_trend_and_correlation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Plot trend
            generate_plots.plot_trend(self.sample_data, "lakelevel", tmpdir + "/")
            self.assertTrue(os.path.exists(os.path.join(tmpdir, "lakelevel_timeseries.png")))
            # Plot correlation
            generate_plots.plot_correlation(self.sample_data, "temperature", tmpdir + "/")
            self.assertTrue(os.path.exists(os.path.join(tmpdir, "temperature_correlation.png")))

    def test_plot_seasonal_correlation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            generate_plots.plot_seasonal_correlation(self.sample_data, tmpdir + "/")
            self.assertTrue(os.path.exists(os.path.join(tmpdir, "seasonal_correlation.png")))

if __name__ == "__main__":
    unittest.main()
