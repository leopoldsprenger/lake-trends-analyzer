import requests
from datetime import datetime, timedelta
import sys
import csv
import os

def get_weather_data_year(lat, lon, year):
    url = "https://archive-api.open-meteo.com/v1/archive"
    start_date = f"{year}-01-01"
    end_date = f"{year}-12-31"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": "temperature_2m,relative_humidity_2m,precipitation,windspeed_10m",
        "timezone": "Europe/Berlin"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    hourly = data.get("hourly", {})
    times = hourly.get("time", [])
    weather_by_date = {}
    for i, t in enumerate(times):
        date = t[:10]
        if date not in weather_by_date:
            weather_by_date[date] = {"temperature_2m": [], "relative_humidity_2m": [], "precipitation": [], "windspeed_10m": []}
        for key in ["temperature_2m", "relative_humidity_2m", "precipitation", "windspeed_10m"]:
            value = hourly.get(key, [None]*len(times))[i]
            if value is not None:
                weather_by_date[date][key].append(value)
    # Calculate daily averages
    daily_averages = {}
    for date, vals in weather_by_date.items():
        daily_averages[date] = {}
        for key in ["temperature_2m", "relative_humidity_2m", "precipitation", "windspeed_10m"]:
            filtered = [v for v in vals[key] if v is not None]
            daily_averages[date][key] = sum(filtered)/len(filtered) if filtered else None
    return daily_averages

def get_decade(year):
    decade_start = (year // 10) * 10
    return f"{decade_start}s"

if __name__ == "__main__":
    lat, lon = 52.5786, 13.8872

    if len(sys.argv) == 3 and sys.argv[1].endswith('.csv'):
        input_csv = sys.argv[1]
        try:
            year_to_process = int(sys.argv[2])
        except ValueError:
            print("Year must be an integer, e.g., 2017")
            sys.exit(1)
        decade = get_decade(year_to_process)
        output_dir = f"data/{decade}"
        os.makedirs(output_dir, exist_ok=True)
        output_csv = os.path.join(output_dir, f"data_from_{year_to_process}.csv")

        print("Fetching weather data for the whole year...")
        weather_data = get_weather_data_year(lat, lon, year_to_process)

        with open(input_csv, newline='', encoding='utf-8') as infile, \
             open(output_csv, 'w', newline='', encoding='utf-8') as outfile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames.copy()
            insert_idx = fieldnames.index('LakeLevel') + 1
            new_headers = ['Temperature', 'Windspeed', 'Humidity', 'Precipitation']
            for h in reversed(new_headers):
                fieldnames.insert(insert_idx, h)
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in reader:
                date_str = row['Date']
                try:
                    row_year = datetime.strptime(date_str, "%Y-%m-%d").year
                except ValueError:
                    row_year = None
                if row_year != year_to_process:
                    continue
                try:
                    datetime.strptime(date_str, "%Y-%m-%d")
                except ValueError:
                    for h in new_headers:
                        row[h] = ''
                    writer.writerow(row)
                    continue
                weather = weather_data.get(date_str, None)
                mapping = {
                    'Temperature': weather['temperature_2m'] if weather else None,
                    'Windspeed': weather['windspeed_10m'] if weather else None,
                    'Humidity': weather['relative_humidity_2m'] if weather else None,
                    'Precipitation': weather['precipitation'] if weather else None
                }
                for h in new_headers:
                    val = mapping[h]
                    if val is None:
                        row[h] = ''
                    elif val == 0.0:
                        row[h] = 0
                    else:
                        row[h] = round(val, 2)
                writer.writerow(row)
        print(f"Done. Output written to {output_csv}")
    else:
        print("Usage:")
        print("  python get_weather_data.py input.csv YEAR")
        sys.exit(1)
