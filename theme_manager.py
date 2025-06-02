import os
import shutil
import tkinter as tk
from tkinter import simpledialog, ttk
import pygame
import json

THEMES_FOLDER = "themes"
SETTINGS_FILE = "settings.json"
SOUNDS_FOLDER = "sounds"

# Initialize pygame mixer
pygame.mixer.init()

def play_sound(filename):
    path = os.path.join(SOUNDS_FOLDER, filename)
    if os.path.exists(path):
        try:
            sound = pygame.mixer.Sound(path)
            sound.play()
        except pygame.error:
            pass  # silently ignore if sound can't be played

def apply_theme(theme_filename):
    theme_path = os.path.join(THEMES_FOLDER, theme_filename)
    if not os.path.exists(theme_path):
        play_sound("error.wav")
        return

    # Preserve current music_folder
    current_music_folder = None
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                current_settings = json.load(f)
                current_music_folder = current_settings.get("music_folder")
        except Exception:
            play_sound("error.wav")
            return

    # Load the new theme
    try:
        with open(theme_path, "r") as f:
            new_settings = json.load(f)
    except Exception:
        play_sound("error.wav")
        return

    # Override music_folder with the preserved value
    if current_music_folder is not None:
        new_settings["music_folder"] = current_music_folder

    # Save merged settings to the main settings file
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(new_settings, f, indent=2)
        play_sound("apply.wav")
    except Exception:
        play_sound("error.wav")

def save_current_theme():
    if not os.path.exists(SETTINGS_FILE):
        play_sound("error.wav")
        return

    name = simpledialog.askstring("Save Theme", "Enter a name for the new theme:")
    if not name:
        return

    filename = f"{name.strip().lower().replace(' ', '_')}_settings.json"
    dest_path = os.path.join(THEMES_FOLDER, filename)

    try:
        shutil.copy(SETTINGS_FILE, dest_path)
        play_sound("save.wav")
        refresh_theme_list()
    except Exception:
        play_sound("error.wav")

def delete_selected_theme():
    selected = listbox.curselection()
    if not selected:
        play_sound("error.wav")
        return

    theme_file = listbox.get(selected[0])

    try:
        os.remove(os.path.join(THEMES_FOLDER, theme_file))
        play_sound("delete.wav")
        refresh_theme_list()
    except Exception:
        play_sound("error.wav")

def refresh_theme_list():
    listbox.delete(0, tk.END)
    themes = [f for f in os.listdir(THEMES_FOLDER) if f.endswith(".json")]
    for theme in themes:
        listbox.insert(tk.END, theme)

def apply_custom_style(root):
    style = ttk.Style()
    style.theme_use("clam")

    root.configure(bg="#1e1e2e")
    style.configure("TFrame", background="#1e1e2e")
    style.configure("TLabel", background="#1e1e2e", foreground="#f0f0f0", font=("Segoe UI", 12))
    style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6)
    style.map("TButton",
              background=[("active", "#444"), ("!disabled", "#444")],
              foreground=[("active", "#fff")])

def create_theme_manager_gui():
    global listbox

    root = tk.Tk()
    root.title("🎨 Theme Manager")
    root.geometry("430x500")
    apply_custom_style(root)

    main_frame = ttk.Frame(root, padding=20)
    main_frame.pack(fill=tk.BOTH, expand=True)

    title = ttk.Label(main_frame, text="🎨 Available Themes:")
    title.pack(pady=(0, 10))

    listbox_frame = ttk.Frame(main_frame)
    listbox_frame.pack(fill=tk.BOTH, expand=True)

    listbox = tk.Listbox(listbox_frame, bg="#2a2a40", fg="#ffffff", font=("Segoe UI", 10),
                         selectbackground="#7e57c2", selectforeground="#ffffff",
                         relief="flat", height=10, activestyle="none")
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    listbox.config(yscrollcommand=scrollbar.set)

    refresh_theme_list()

    button_frame = ttk.Frame(main_frame)
    button_frame.pack(pady=20, fill=tk.X)

    apply_btn = tk.Button(button_frame, text="Apply Theme", bg="#307233", fg="white",
                          font=("Segoe UI", 15), command=lambda: apply_theme(listbox.get(listbox.curselection()[0])) if listbox.curselection() else play_sound("error.wav"))
    apply_btn.pack(fill=tk.X, pady=5)

    save_btn = tk.Button(button_frame, text="Save Current As New", bg="#1b6bac", fg="white",
                         font=("Segoe UI", 15), command=save_current_theme)
    save_btn.pack(fill=tk.X, pady=5)

    delete_btn = tk.Button(button_frame, text="Delete Selected Theme", bg="#9e2d25", fg="white",
                           font=("Segoe UI", 15), command=delete_selected_theme)
    delete_btn.pack(fill=tk.X, pady=5)

    root.mainloop()

if __name__ == "__main__":
    if not os.path.exists(THEMES_FOLDER):
        os.makedirs(THEMES_FOLDER)
    if not os.path.exists(SOUNDS_FOLDER):
        os.makedirs(SOUNDS_FOLDER)
    create_theme_manager_gui()
