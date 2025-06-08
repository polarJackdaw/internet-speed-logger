import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title("Styled Progressbar")
root.geometry("400x150")

style = ttk.Style(root)

# Create a new custom style
style.theme_use('default')  # Make sure you're not using a native style
style.configure("custom.Horizontal.TProgressbar",
                troughcolor='#eeeeee',
                background='#4CAF50',
                thickness=20)

# Use the custom style
progress = ttk.Progressbar(root, style="custom.Horizontal.TProgressbar",
                           orient="horizontal", length=300, mode="determinate")
progress.pack(pady=40)
progress["value"] = 60  # Set progress

root.mainloop()
