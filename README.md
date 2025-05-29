<<<<<<< HEAD
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
=======
# Internet Speed Test Utility

Python GUI tool to test, log, and visualize internet speeds with optional background music.

## Features

- Internet speed testing (Download, Upload, Ping, ISP, Country, Location)
- Results logged with timestamp to `internet_data.txt`
- Scatter plot of test results using `matplotlib`
- Automatic testing at custom intervals
- Sound effects with mute toggle
- Custom background music support (`.mp3` playback)

## Custom Music

You can add your own `.mp3` files to play as background music.

### How to Add Music:

1. Navigate to the `sounds/music/` directory.
2. Place your `.mp3` files into this folder (other formats are not supported).
3. Click the **"Music ON"** button to start background playback.
4. The app will randomly loop through all `.mp3` files in that folder.
5. To skip a song, toggle the music OFF and then ON again.

### How to Customize Sound Effects:

1. Navigate to the `sounds` folder.
2. Replace the `.wav` file with your own. Do not change the filename or file format!

## Requirements

Install the required Python libraries:

```bash
pip install speedtest-cli pandas matplotlib pillow pygame
>>>>>>> dd8a8c3 (Changed program to GUI)
