import pandas as pd
import numpy as np
import matplotlib.dates as mdates

def forecast_future_lake_level(data: pd.DataFrame, file_path: str) -> None:
    """
    Forecast future lake levels based on recent trend after detecting major trajectory changes.

    Args:
        data (pd.DataFrame): DataFrame containing at least 'date' and 'lakelevel' columns.

    Returns:
        None
    """
    file = open(file_path, 'w')

    data = data.copy()
    data['date'] = pd.to_datetime(data['date'])
    data = data.sort_values('date')

    # Convert dates to matplotlib float format for regression
    x = mdates.date2num(data['date'])
    y = data['lakelevel'].values

    # Calculate rolling slope to detect change points
    window = max(10, len(data) // 10)  # Use a window of at least 10 or 10% of data
    slopes = pd.Series(np.polyfit(x[i:i+window], y[i:i+window], 1)[0]
                       for i in range(len(x) - window + 1))
    # Find where the slope changes significantly (e.g., by more than 2x std deviation)
    slope_diff = slopes.diff().abs()
    threshold = 2 * slope_diff.std()
    change_points = slope_diff[slope_diff > threshold].index.tolist()

    # Use the most recent segment after the last major change point
    if change_points:
        last_change_idx = change_points[-1]
        start_idx = last_change_idx
        x_recent = x[start_idx:]
        y_recent = y[start_idx:]
        data_recent = data.iloc[start_idx:]
    else:
        x_recent = x
        y_recent = y
        data_recent = data

    # Fit trend line to recent segment
    trend_line_function = np.poly1d(np.polyfit(x_recent, y_recent, 1))
    last_date = data_recent['date'].max()

    years = [1, 10, 50, 100]
    days_in_year = 365.25

    file.write("Forecast based on recent trend after major trajectory change detection:\n\n")
    for year in years:
        future_date = last_date + pd.Timedelta(days=year * days_in_year)
        future_numeric = mdates.date2num(future_date)
        forecast = trend_line_function(future_numeric)
        file.write(f"Forecast for {year} years ({future_date.date()}): {forecast:.2f} m\n")

    slope = trend_line_function.c[0]
    if slope < 0:
        last_numeric = mdates.date2num(last_date)
        intercept = trend_line_function.c[1]
        zero_day = -intercept / slope
        days_until_dry = zero_day - last_numeric

        if days_until_dry > 0:
            years_until_dry = days_until_dry / days_in_year
            dry_date = mdates.num2date(zero_day).date()
            file.write(f"\nWarning: Lake is projected to dry out in {int(days_until_dry)} days "
                        f"({years_until_dry:.2f} years), around {dry_date}.\n")
        else:
            file.write("\nWarning: Trend suggests lake would already be dry based on current data.\n")

    file.write("\nThis forecast is based on the most recent trend segment after detecting major changes.\nThe forecast is subject to uncertainty and may not reflect actual future conditions.")

    file.close()
    print(f"Forecast saved to {file_path}")