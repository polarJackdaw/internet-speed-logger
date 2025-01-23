# Internet Speed Analyzer

**Internet Speed Analyzer** is a Python script that tests internet speed (download, upload, and ping), logs the results, and generates scatter plots to visualize internet speed trends over time.

## Features

- **Speed Test**: Measure download, upload speeds, and ping using `speedtest`.
- **Data Logging**: Save speed test results to a file (`internet_data.txt`).
- **Scatter Plot**: Generate a scatter plot (`scatter_plot.png`) of download and upload speeds.
- **Error Logging**: Log errors to `error_log.txt` for troubleshooting.

## Requirements

The script requires the following dependencies:
- `speedtest-cli`
- `pandas`
- `matplotlib`
- `numpy`
- `tkinter` (usually included with Python)

Install dependencies using the following command:
```bash
pip install -r requirements.txt
