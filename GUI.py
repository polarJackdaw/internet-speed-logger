import datetime
import speedtest
import tkinter as tk
from tkinter import messagebox
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import threading
from PIL import Image, ImageTk, ImageSequence
import pygame
import os
import subprocess
import sys
import matplotlib.colors as mcolors
import random
import json

# ==== Load settings from JSON ====
SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "settings.json")

def load_settings():
    try:
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        log_error(f"Failed to load settings: {e}")
        return {}

settings = load_settings()

# ==== Initialize Pygame Mixer ====
pygame.mixer.init()
loaded_sounds = {}

# ==== Path to sound folder ====
SOUND_FOLDER = os.path.join(os.path.dirname(__file__), "sounds")
MUSIC_FOLDER = os.path.join(os.path.dirname(__file__), settings.get("music_folder", "sounds/music"))


def load_sound(filename):
    full_path = os.path.join(SOUND_FOLDER, filename)
    if os.path.exists(full_path):
        loaded_sounds[filename] = pygame.mixer.Sound(full_path)
    else:
        loaded_sounds[filename] = None

for sound_file in ["click.wav", "plot.wav", "auto_on.wav", "auto_off.wav", "interval.wav"]:
    load_sound(sound_file)


# Load click sound once globally
click_sound_path = os.path.join(SOUND_FOLDER, "click.wav")
click_sound = None
if os.path.exists(click_sound_path):
    click_sound = pygame.mixer.Sound(click_sound_path)

# Sound enabled flag
sound_enabled = True


def play_sound(filename):
    if not sound_enabled:
        return
    sound = loaded_sounds.get(filename)
    if sound:
        sound.play()

def log_error(error="Error"):
    with open("error_log.txt", "a") as error_file:
        error_file.write(f"{datetime.datetime.now()} - Error: {str(error)}\n")

def collect_data():
    try:
        now = datetime.datetime.now()
        user_date = now.strftime("%Y-%m-%d")
        user_time = now.strftime("%H:%M:%S")

        st = speedtest.Speedtest(secure=True)
        speed_download = st.download() / 1_000_000
        speed_upload = st.upload() / 1_000_000
        ping = int(st.results.ping)

        client = st.results.client
        isp = client.get("isp", "Unknown")
        country = client.get("country", "Unknown")
        lat = client.get("lat", 0.0)
        lon = client.get("lon", 0.0)

        speed_download = round(speed_download, 3)
        speed_upload = round(speed_upload, 3)

        data = [user_date, user_time, speed_download, speed_upload, ping, isp, country, lat, lon]
        with open("internet_data.txt", "a") as file:
            file.write(",".join(map(str, data)) + "\n")
        return data
    except Exception as e:
        log_error(e)
        return None

def open_image(path):
    try:
        top = tk.Toplevel(root)
        top.title("Scatter Plot")
        img = Image.open(path)
        photo = ImageTk.PhotoImage(img)
        label = tk.Label(top, image=photo)
        label.image = photo  # Keep reference
        label.pack()
    except Exception as e:
        log_error(f"Failed to open image: {e}")


def save_scatter_plot():
    try:
        play_sound("plot.wav")
        data = pd.read_csv('internet_data.txt', header=None)
        if data.shape[1] < 4:
            raise ValueError("Data file does not have the required columns.")
        times = data[1]
        download_speeds = data[2]
        upload_speeds = data[3]
        times_in_hours = [int(h) + int(m) / 60 + int(s) / 3600 for h, m, s in (t.split(':') for t in times)]

        all_speeds = pd.concat([download_speeds, upload_speeds])
        min_speed = all_speeds.min()
        max_speed = all_speeds.max()

        colors_list = ['red', 'orange', 'yellow', 'green', 'blue', 'violet']
        cmap = mcolors.LinearSegmentedColormap.from_list("speed_cmap", colors_list)
        norm = mcolors.Normalize(vmin=min_speed, vmax=max_speed)

        fig, ax = plt.subplots(figsize=(10, 6))

        dl_colors = cmap(norm(download_speeds))
        ul_colors = cmap(norm(upload_speeds))

        ax.scatter(times_in_hours[:-1], download_speeds[:-1], color=dl_colors[:-1], label='Download', s=30, edgecolor='k', linewidth=0.3)
        ax.scatter(times_in_hours[:-1], upload_speeds[:-1], color=ul_colors[:-1], label='Upload', s=30, edgecolor='k', linewidth=0.3)

        ax.scatter(times_in_hours[-1], download_speeds.iloc[-1], color=dl_colors[-1], label='Latest Download', s=40, edgecolor='black', linewidth=1.5, marker='o')
        ax.scatter(times_in_hours[-1], upload_speeds.iloc[-1], color=ul_colors[-1], label='Latest Upload', s=40, edgecolor='black', linewidth=1.5, marker='o')

        avg_dl = download_speeds.mean()
        avg_ul = upload_speeds.mean()
        ax.axhline(avg_dl, color='blue', linestyle='--', linewidth=1.2, label=f'Avg Download ({avg_dl:.2f} Mbps)')
        ax.axhline(avg_ul, color='red', linestyle='--', linewidth=1.2, label=f'Avg Upload ({avg_ul:.2f} Mbps)')

        ax.set_xlabel('Hour')
        ax.set_ylabel('Speed (Mbps)')
        ax.set_title('Download and Upload Speeds')
        ax.set_xticks(np.arange(0, 25, 1))
        ax.set_xlim([0, 24])

        # Colorbar on right
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax)
        cbar.set_label('Speed (Mbps)')

        # Legend below plot, centered
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=False)

        plt.tight_layout(rect=[0, 0.05, 1, 1])  # leave space below for legend

        plt.savefig("scatter_plot.png", bbox_inches='tight')
        plt.close()

        open_image("scatter_plot.png")

    except Exception as e:
        log_error(e)


# ==== GUI ====
root = tk.Tk()
root.title("🌐 Internet Speed Tester")
root.configure(bg="#1e1e2e")

frame = tk.Frame(root, bg="#1e1e2e", padx=20, pady=20)
frame.pack()

title_label = tk.Label(frame, text="Internet Speed Test Utility", font=("Segoe UI", 18, "bold"),
                       fg="#ffffff", bg="#1e1e2e")
title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

output_text = tk.StringVar()
output_label = tk.Label(frame, textvariable=output_text, justify=tk.LEFT, anchor="w",
                        wraplength=480, font=("Consolas", 11), fg="#e0e0e0", bg="#1e1e2e")
output_label.grid(row=4, column=0, columnspan=3, pady=20)

# Load GIF & PNG
idle_img = ImageTk.PhotoImage(Image.open("idle.png"))
gif = Image.open("loading.gif")
gif_frames = [ImageTk.PhotoImage(frame.copy().convert("RGBA")) for frame in ImageSequence.Iterator(gif)]
gif_label = tk.Label(frame, image=idle_img, bg="#1e1e2e")
gif_label.grid(row=5, column=0, columnspan=3)

testing = tk.BooleanVar(value=False)
def animate_gif(frame_index=0):
    if not root.winfo_exists():
        return  # Stop if root window is destroyed
    if testing.get():
        gif_label.configure(image=gif_frames[frame_index])
        root.after(100, animate_gif, (frame_index + 1) % len(gif_frames))
    else:
        gif_label.configure(image=idle_img)

auto_test_enabled = tk.BooleanVar(value=False)
auto_test_interval = tk.IntVar(value=5)  # minutes

def schedule_auto_test():
    if auto_test_enabled.get():
        handle_speed_test()
        root.after(auto_test_interval.get() * 60 * 1000, schedule_auto_test)

def toggle_auto_test():
    auto_test_enabled.set(not auto_test_enabled.get())
    if auto_test_enabled.get():
        if sound_enabled:
            play_sound("auto_on.wav")
        auto_btn.config(text="Auto Test: ON", bg="green")
        schedule_auto_test()
    else:
        if sound_enabled:
            play_sound("auto_off.wav")
        auto_btn.config(text="Auto Test: OFF", bg="red")

def handle_speed_test():
    if sound_enabled and click_sound:
        click_sound.play(loops=-1)
    output_text.set("Testing internet speed...\nPlease wait...")
    testing.set(True)
    animate_gif()
    threading.Thread(target=run_speed_test, daemon=True).start()

def run_speed_test():
    result = collect_data()
    testing.set(False)
    if click_sound:
        click_sound.stop()

    if result:
        dl_mbps = result[2]
        ul_mbps = result[3]
        dl_mbs = round(dl_mbps / 8, 3)
        ul_mbs = round(ul_mbps / 8, 3)

        try:
            df = pd.read_csv("internet_data.txt", header=None)

            if not df.empty and df.shape[1] >= 4:
                # === Averages ===
                avg_dl = df[2].mean()
                avg_ul = df[3].mean()
                avg_dl_mbs = round(avg_dl / 8, 3)
                avg_ul_mbs = round(avg_ul / 8, 3)
                tests_run = len(df)

                # === Comparisons ===
                diff_dl_pct = ((dl_mbps - avg_dl) / avg_dl) * 100
                diff_ul_pct = ((ul_mbps - avg_ul) / avg_ul) * 100

                comparison_dl = f"{abs(round(diff_dl_pct, 2))}% {'faster' if diff_dl_pct > 0 else 'slower'} than average download"
                comparison_ul = f"{abs(round(diff_ul_pct, 2))}% {'faster' if diff_ul_pct > 0 else 'slower'} than average upload"

                # === Extremes ===
                max_dl = df[2].max()
                min_dl = df[2].min()
                max_ul = df[3].max()
                min_ul = df[3].min()

                max_dl_mbs = round(max_dl / 8, 3)
                min_dl_mbs = round(min_dl / 8, 3)
                max_ul_mbs = round(max_ul / 8, 3)
                min_ul_mbs = round(min_ul / 8, 3)
            else:
                avg_dl = avg_ul = avg_dl_mbs = avg_ul_mbs = 0
                max_dl = min_dl = dl_mbps
                max_ul = min_ul = ul_mbps
                max_dl_mbs = min_dl_mbs = dl_mbs
                max_ul_mbs = min_ul_mbs = ul_mbs
                tests_run = 1
                comparison_dl = "N/A (first test)"
                comparison_ul = "N/A (first test)"
        except Exception as e:
            log_error(f"Error reading/parsing data: {e}")
            avg_dl = avg_ul = avg_dl_mbs = avg_ul_mbs = 0
            max_dl = min_dl = dl_mbps
            max_ul = min_ul = ul_mbps
            max_dl_mbs = min_dl_mbs = dl_mbs
            max_ul_mbs = min_ul_mbs = ul_mbs
            tests_run = 1
            comparison_dl = "N/A (error)"
            comparison_ul = "N/A (error)"

        output_text.set(
            f"📅 Date: {result[0]}\n"
            f"⏰ Time: {result[1]}\n"
            f"⬇️ Download: {dl_mbps} Mbps ({dl_mbs} MB/s)\n"
            f"⬇️ GB 1/15/30/60 min: {round(dl_mbs * 60 / 1000, 3)}/{round(dl_mbs * 900 / 1000, 3)}/{round(dl_mbs * 1800 / 1000, 3)}/{round(dl_mbs * 3600 / 1000, 3)}\n"
            f"⬆️ Upload: {ul_mbps} Mbps ({ul_mbs} MB/s)\n"
            f"⬇️ GB 1/15/30/60 min: {round(ul_mbs * 60 / 1000, 3)}/{round(ul_mbs * 900 / 1000, 3)}/{round(ul_mbs * 1800 / 1000, 3)}/{round(ul_mbs * 3600 / 1000, 3)}\n"
            f"🏓 Ping: {result[4]} ms\n"
            f"🌐 ISP: {result[5]}\n"
            f"🏳️ Country: {result[6]}\n"
            f"📍 Latitude: {result[7]}\n"
            f"📍 Longitude: {result[8]}\n\n"

            f"📊 Average Download: {round(avg_dl, 2)} Mbps ({avg_dl_mbs} MB/s)\n"
            f"📊 Average Upload: {round(avg_ul, 2)} Mbps ({avg_ul_mbs} MB/s)\n"
            f"🔁 Total Tests Run: {tests_run}\n"
            f"📉 Download Comparison: {comparison_dl}\n"
            f"📈 Upload Comparison: {comparison_ul}\n\n"

            f"🚀 Fastest Download: {round(max_dl, 2)} Mbps ({max_dl_mbs} MB/s)\n"
            f"🐢 Slowest Download: {round(min_dl, 2)} Mbps ({min_dl_mbs} MB/s)\n"
            f"🚀 Fastest Upload: {round(max_ul, 2)} Mbps ({max_ul_mbs} MB/s)\n"
            f"🐢 Slowest Upload: {round(min_ul, 2)} Mbps ({min_ul_mbs} MB/s)"
        )

    else:
        output_text.set("❌ An error occurred during the speed test.\nCheck error_log.txt.")


btn_style = {"font": ("Segoe UI", 12), "bg": "#3b82f6", "fg": "white", "activebackground": "#2563eb", "width": 25, "bd": 0, "relief": tk.FLAT}

test_button = tk.Button(frame, text="🚀 Test Internet Speed", command=handle_speed_test, **btn_style)
test_button.grid(row=1, column=0, columnspan=3, pady=10)

plot_button = tk.Button(frame, text="📈 Generate Scatter Plot", command=save_scatter_plot, **btn_style)
plot_button.grid(row=2, column=0, columnspan=3, pady=10)

auto_btn = tk.Button(frame, text="Auto Test: OFF", command=toggle_auto_test,
                     font=("Segoe UI", 12), fg="white", width=25, bg="red", bd=0, relief=tk.FLAT)
auto_btn.grid(row=6, column=0, columnspan=3, pady=(20, 5))

interval_label = tk.Label(frame, text="Interval (min):", font=("Segoe UI", 11),
                          fg="#ffffff", bg="#1e1e2e")
interval_label.grid(row=7, column=0, sticky="e", padx=(0, 10))

interval_spinbox = tk.Spinbox(frame, from_=1, to=120, width=5, textvariable=auto_test_interval, font=("Segoe UI", 11))
interval_spinbox.grid(row=7, column=1, sticky="w")

def on_interval_change(event):
    if sound_enabled:
        play_sound("interval.wav")

interval_spinbox.bind("<ButtonRelease-1>", on_interval_change)
interval_spinbox.bind("<KeyRelease>", on_interval_change)

# === Mute Button ===
def toggle_mute():
    global sound_enabled
    sound_enabled = not sound_enabled

    if not sound_enabled and click_sound:
        click_sound.stop()  # Stop sound immediately when muting

    elif sound_enabled and click_sound and testing.get():
        # If unmuting AND test is running, restart the looping sound
        click_sound.play(loops=-1)

    if sound_enabled:
        mute_button.config(text="🔈 Sound ON", bg="green")
    else:
        mute_button.config(text="🔇 Muted", bg="red")


mute_button = tk.Button(frame, text="🔈 Sound ON", command=toggle_mute,
                        font=("Segoe UI", 12), fg="white", width=15, bg="green", bd=0, relief=tk.FLAT)
mute_button.grid(row=8, column=0, pady=(10, 20))

# === Music Button and Logic ===

# List all mp3 files in the MUSIC_FOLDER
music_files = [f for f in os.listdir(MUSIC_FOLDER) if f.lower().endswith(".mp3")]

music_playing = False

def play_random_song():
    if not music_files:
        return
    song = random.choice(music_files)
    song_path = os.path.join(MUSIC_FOLDER, song)
    try:
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.play()
    except Exception as e:
        log_error(f"Music playback error: {e}")

def check_music():
    # Called periodically to check if music ended
    if not pygame.mixer.music.get_busy() and music_playing:
        play_random_song()
    root.after(1000, check_music)

def toggle_music():
    global music_playing
    if music_playing:
        pygame.mixer.music.stop()
        music_playing = False
        music_button.config(text="🎵 Music OFF", bg="red")
    else:
        if not music_files:
            messagebox.showwarning("No Music", "No mp3 files found in the 'sounds/music' folder.")
            return
        music_playing = True
        music_button.config(text="🎵 Music ON", bg="green")
        play_random_song()
        check_music()

music_button = tk.Button(frame, text="🎵 Music OFF", command=toggle_music,
                         font=("Segoe UI", 12), fg="white", width=15, bg="red", bd=0, relief=tk.FLAT)
music_button.grid(row=8, column=1, pady=(10, 20), padx=(10,0))

root.mainloop()
