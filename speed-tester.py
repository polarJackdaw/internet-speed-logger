import datetime
import speedtest
import tkinter as tk
from tkinter import messagebox
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def print_commands():
    print("Commands: ")
    print("1. Test and display internet speed")
    print("2. Make a scatter plot 'scatter_plot.png'")
    print("3. Show commands")

# Write error to error_log.txt
def log_error(error="Error"):
    with open("error_log.txt", "a") as error_file:
        error_file.write(f"{datetime.datetime.now()} - Error: {str(error)}\n")

# Function to log internet speed test results to internet_data.txt
def collect_data():
    try:
        # Get date and time
        user_now = datetime.datetime.now()
        user_date = user_now.strftime("%Y-%m-%d")
        user_time = user_now.strftime("%H:%M:%S")
        
        # Get results
        st = speedtest.Speedtest(secure=True)
        speed_download = st.download() / 1_000_000
        speed_upload = st.upload() / 1_000_000
        ping = int(st.results.ping)
        
        # Safely fetch client details
        client = st.results.client
        isp = client.get("isp", "Unknown")
        country = client.get("country", "Unknown")
        lat = client.get("lat", 0.0)
        lon = client.get("lon", 0.0)

        # Round speeds to 3 decimal places
        speed_download = round(speed_download, 3)
        speed_upload = round(speed_upload, 3)

        # List all data
        data = [
            user_date,
            user_time,
            speed_download,
            speed_upload,
            ping,
            isp,
            country,
            lat,
            lon
        ]
        
        # Write data to file
        with open("internet_data.txt", "a") as file:
            file.write(",".join(map(str, data)) + "\n")

        return data
    except Exception as e:
        log_error(e)
        return e

# Function to save the scatter plot for download and upload speeds
def save_scatter_plot():
    try:
        # Read data from the file
        try:
            data = pd.read_csv('internet_data.txt', header=None)
        except FileNotFoundError:
            print("Error: Data file 'internet_data.txt' not found.")
            return
        except Exception as e:
            print(f"Error: Could not read data file: {e}")
            return

        # Ensure the data has the necessary columns
        if data.shape[1] < 4:
            print("Error: Data file does not have the required columns.")
            return

        # Extract Time, Download, and Upload columns
        times = data[1]  # Time is in the second column (format: HH:MM:SS)
        download_speeds = data[2]
        upload_speeds = data[3]

        # Convert Time (HH:MM:SS) to hours (0 to 24)
        times_in_hours = []
        for t in times:
            hours, minutes, seconds = map(int, t.split(':'))
            total_hours = hours + minutes / 60 + seconds / 3600
            times_in_hours.append(total_hours)

        # Convert to numpy arrays for scatter plotting
        times_in_hours = np.array(times_in_hours)
        download_speeds = np.array(download_speeds)
        upload_speeds = np.array(upload_speeds)

        # Create the scatter plot
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.scatter(times_in_hours, download_speeds, color='b', marker='o', label='Download Speeds', s=20)
        ax.scatter(times_in_hours, upload_speeds, color='g', marker='o', label='Upload Speeds', s=20)

        # Labels and title
        ax.set_xlabel('Hour of the Day')
        ax.set_ylabel('Speed (Mbps)')
        ax.set_title('Download and Upload Speeds (Scatter Plot)')
        ax.set_xticks(np.arange(0, 25, 1))
        ax.set_xlim([0, 24])
        ax.legend()

        # Save the plot as an image file
        image_path = "scatter_plot.png"
        plt.savefig(image_path)
        plt.close(fig)  # Close the figure to free up memory
        print(f"Scatter plot saved as {image_path}")
    except Exception as e:
        log_error(e)

# Main function
if __name__ == "__main__":
    print_commands()
    while True:
        print("")
        user_i = input("@: ")

        if user_i == "1":
            try:
                print("Testing internet speed...")
                data = collect_data()
                print("Date: ", data[0])
                print("Time: ", data[1])
                print("Download: ", data[2])
                print("Upload: ", data[3])
                print("Ping: ", data[4])
                print("ISP: ", data[5])
                print("Country: ", data[6])
                print("Latitude: ", data[7])
                print("Longitude: ", data[8])
            except Exception as e:
                print("An error occurred, check error_log.txt for more details.")
                log_error(e)
        elif user_i == "2":
            save_scatter_plot()
        elif user_i == "3":
            print_commands()
        else:
            print(f"Invalid command: {user_i}")
