# Lake Trends Analyzer

**Lake Trends Analyzer** is a modular Python scaffold being developed to support early-stage analysis of lake-related environmental data as part of the **TOTCUS** global water and climate research initiative.

This project is currently in the **design and prototyping phase**, focusing on defining structure, expected input formats, and planned capabilities. While implementation is in progress, the repository contains code stubs, placeholder scripts, and dataset samples for testing purposes.

---

## 🌍 Project Context

This tool is part of our school’s involvement in **TOTCUS**, an international program studying the impact of environmental change on aquatic ecosystems. Our local contributions involve collecting weather and lake condition data from a nearby lake.

The Python version aims to explore concepts like trend detection, data visualization, and long-term lake level forecasting using common data science libraries.

---

## 🧰 Planned Features

> ✨ *Note: Features below are design targets. Implementation is ongoing.*

- 📊 **Graphing Capabilities**
  - Time series plots for each environmental variable
  - Correlation scatterplots between lake level and other variables
  - Trendlines for both time and correlation plots

- 🔮 **Forecasting Support**
  - Simple lake level projection using linear regression or exponential smoothing
  - Warning system if levels show signs of drying out

- 🧱 **Flexible CSV Input Handling**
  - Auto-detect known columns like `temperature`, `lakelevel`, etc.
  - Skip unknown or malformed data gracefully

- 🧪 **Mock Data for Testing**
  - Sample CSVs in `data/` folder for testing graph generation and preprocessing logic


---

## ⚙️ Setup Instructions

Install dependencies (planned or in use):

```bash
pip install requirements.txt
```

Run the script:

```bash
python src/main.py --file data/mock_dataset_10.csv --var temperature
```

---

## 📉 Example Outputs (Concept)

> **Note:** These are goals for future output. Sample graphs may be generated manually during testing.

- `graphs/timeseries/temperature.png` — Temperature trends over time
- `graphs/correlations/lakelevel_vs_temperature.png` — Correlation graph

---

## 🧭 Roadmap (Python Phase)

- [x] Set up basic project structure
- [x] Implement CSV parsing
- [x] Develop basic time series plotting
- [x] Add a trend line to the graphs
- [x] Export static images of graphs
- [x] Add linear forecasting prototype
- [ ] Implement correlation graphing for multiple variables

---

## 🤝 Contributions

This Project is part of our school's exploratory phase with the **TOTCUS** initiative. All feedback is welcome as we move toward a more robust, high-performance version of this tool.
