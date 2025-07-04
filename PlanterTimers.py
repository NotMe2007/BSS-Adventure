# Natro Macro (https://github.com/NatroTeam/NatroMacro)
# Copyright © Natro Team (https://github.com/NatroTeam)
#
# This file is part of Natro Macro. Our source code will always be open and available.
#
# Natro Macro is free software: you can redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Natro Macro is distributed in the hope that it will be useful. This does not give you the right
# to steal sections from our code, distribute it under your own name, then slander the macro.
#
# You should have received a copy of the license along with Natro Macro. If not, please redownload
# from an official source.

import os
import sys
import time
import configparser
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import win32gui
import win32con

# Directory setup
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir + "/..")

# Configuration
config = configparser.ConfigParser()
config.read("settings/nm_config.ini")

# Global variables for GUI positioning and transparency
timer_x = int(config.get("Planters", "TimerX", fallback=0))
timer_y = int(config.get("Planters", "TimerY", fallback=0))
timer_gui_transparency = int(config.get("Planters", "TimerGuiTransparency", fallback=0))

# Image handling
image_cache = {}

def load_image(path):
    if path not in image_cache:
        if os.path.exists(path):
            image = Image.open(path)
            image_cache[path] = ImageTk.PhotoImage(image)
        else:
            image_cache[path] = None
    return image_cache[path]

# Utility functions
def duration_from_seconds(seconds, format_str):
    if seconds > 360000:
        return format_str.replace("'", "")
    if seconds <= 0:
        return "Ready"
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    result = ""
    if hours > 0 and "h" in format_str:
        result += f"{hours}h "
    if minutes > 0 and "m" in format_str:
        result += f"{minutes}m "
    if secs > 0 and "s" in format_str:
        result += f"{secs}s"
    return result.strip()

# Get current Unix timestamp
def now_unix():
    return int(time.time())

def update_config(section, key, value):
    if not config.has_section(section):
        config.add_section(section)
    config.set(section, key, str(value))
    with open("settings/nm_config.ini", "w") as f:
        config.write(f)

# GUI setup
root = tk.Tk()
root.title("Timers Revision 4.0")
root.attributes("-topmost", True)
root.geometry(f"490x208+{timer_x}+{timer_y}")
root.resizable(False, False)
root.overrideredirect(True)  # Remove window border for custom look

# Transparency
def set_timer_gui_transparency(*args):
    global timer_gui_transparency
    if isinstance(args[0], tk.Event) or len(args) == 0:
        transparency = transparency_scale.get()
        update_config("Planters", "TimerGuiTransparency", transparency)
    else:
        transparency = timer_gui_transparency
    alpha = 1.0 - (transparency / 100.0)
    root.attributes("-alpha", alpha)

# Planter GUI elements
planter_fields = [tk.Label(root) for _ in range(3)]
planter_names = [tk.Label(root) for _ in range(3)]
planter_nectars = [tk.Label(root) for _ in range(3)]
planter_timers = [tk.Label(root, text="h m s", justify="center") for _ in range(3)]

for i in range(3):
    planter_fields[i].place(x=2 + i * 86, y=35, width=40, height=40)
    planter_names[i].place(x=44 + i * 86, y=35, width=40, height=40)
    planter_nectars[i].place(x=34 + i * 86, y=16, width=18, height=18)
    planter_timers[i].place(x=2 + i * 86, y=2, width=82, height=20)

# Timer labels and buttons
monster_labels = ["Next King", "Next Bear", "Next Wolf"]
monster_timers = [tk.Label(root, text="h m s", justify="center") for _ in range(3)]
for i, label in enumerate(monster_labels):
    tk.Label(root, text=label, justify="center").place(x=258, y=4 + i * 36, width=66, height=20)
    monster_timers[i].place(x=262, y=20 + i * 36, width=58, height=20)

# Stats
stats_labels = ["Per Hour", "Session", "Reset"]
stats_values = [tk.Label(root, text="0", justify="center") for _ in range(3)]
for i, label in enumerate(stats_labels):
    tk.Label(root, text=label, justify="center").place(x=322, y=4 + i * 36, width=66, height=20)
    stats_values[i].place(x=326, y=20 + i * 36, width=58, height=20)
stats_values[2].config(text="N/A")  # Reset timer

# Transparency control
tk.Label(root, text="Transparency").place(x=390, y=90)
transparency_scale = tk.Scale(root, from_=0, to=70, orient="horizontal", command=set_timer_gui_transparency)
transparency_scale.set(timer_gui_transparency)
transparency_scale.place(x=390, y=105, width=100)

# Planter buttons
def reset_planter_timer(i):
    planter_name = config.get("Planters", f"PlanterName{i+1}", fallback="None")
    if planter_name != "None":
        update_config("Planters", f"PlanterHarvestTime{i+1}", now_unix() - 1)

# Function to set planter timer with delta
def set_planter_timer(i, delta):
    planter_name = config.get("Planters", f"PlanterName{i+1}", fallback="None")
    if planter_name != "None":
        harvest_time = int(config.get("Planters", f"PlanterHarvestTime{i+1}", fallback=now_unix()))
        new_time = max(now_unix(), harvest_time + delta)
        update_config("Planters", f"PlanterHarvestTime{i+1}", new_time)
        est_percent = min(max((new_time - now_unix()) // 864, 0), 100)
        update_config("Planters", f"PlanterEstPercent{i+1}", est_percent)

# Function to set planter data
def set_planter_data(i):
    planter_name = config.get("Planters", f"PlanterName{i+1}", fallback="None")
    if planter_name == "None":
        add_planter_data(i)
    else:
        for key in ["Name", "Field", "Nectar", "HarvestFull"]:
            update_config("Planters", f"Planter{key}{i+1}", "None" if key != "HarvestFull" else "")
        update_config("Planters", f"PlanterHarvestTime{i+1}", 2147483647)
        update_config("Planters", f"PlanterEstPercent{i+1}", 0)
        update_config("Planters", f"PlanterGlitter{i+1}", 0)
        update_config("Planters", f"PlanterGlitterC{i+1}", 0)
        update_config("Planters", f"MPlanterHold{i+1}", 0)
        update_config("Planters", f"PlanterHarvestNow{i+1}", 0)
        update_config("Planters", f"MPlanterSmoking{i+1}", 0)

# Create buttons for each planter
for i in range(3):
    tk.Button(root, text="Ready", command=lambda i=i: reset_planter_timer(i)).place(x=1 + i * 86, y=76, width=42, height=15)
    tk.Button(root, text="Add", command=lambda i=i: set_planter_data(i)).place(x=43 + i * 86, y=76, width=42, height=15)
    tk.Button(root, text="-1HR", command=lambda i=i: set_planter_timer(i, -3600)).place(x=1 + i * 86, y=92, width=42, height=15)
    tk.Button(root, text="+1HR", command=lambda i=i: set_planter_timer(i, 3600)).place(x=43 + i * 86, y=92, width=42, height=15)

# Blender GUI elements
blender_items = [tk.Label(root) for _ in range(3)]
blender_timers = [tk.Label(root, text="h m s", justify="center") for _ in range(3)]
blender_amounts = [tk.Label(root, font=("Tahoma", 7)) for _ in range(3)]
for i in range(3):
    blender_items[i].place(x=24 + i * 86, y=140, width=40, height=40)
    blender_timers[i].place(x=2 + i * 86, y=110, width=82, height=20)
    blender_amounts[i].place(x=4 + i * 85, y=123, width=80, height=20)

# Function to reset blender timer
def reset_blender_timer(i):
    blender_item = config.get("Blender", f"BlenderItem{i+1}", fallback="None")
    if blender_item != "None":
        update_config("Blender", f"BlenderCount{i+1}", 0)
        update_config("Blender", f"BlenderTime{i+1}", 0)
        update_config("Blender", f"BlenderRot", i + 1)
        update_config("Blender", f"BlenderEnd", 1)

# Function to set blender data
def set_blender_amount(i, delta):
    blender_item = config.get("Blender", f"BlenderItem{i+1}", fallback="None")
    if blender_item != "None":
        amount = int(config.get("Blender", f"BlenderAmount{i+1}", fallback=1))
        if delta < 0 and amount > 1:
            amount += delta
        elif delta > 0:
            amount += delta
        update_config("Blender", f"BlenderAmount{i+1}", amount)
        blender_amounts[i].config(text=f"({config.get('Blender', f'BlenderCount{i+1}', fallback=0)}/{amount}) [{'∞' if config.get('Blender', f'BlenderIndex{i+1}', fallback='1') == 'Infinite' else config.get('Blender', f'BlenderIndex{i+1}', fallback='1')}]")

# Function to set blender data
for i in range(3):
    tk.Button(root, text="Ready", command=lambda i=i: reset_blender_timer(i)).place(x=1 + i * 86, y=184, width=42, height=15)
    tk.Button(root, text="Add", command=lambda i=i: set_blender_data(i)).place(x=43 + i * 86, y=184, width=42, height=15)
    tk.Button(root, text="-1", command=lambda i=i: set_blender_amount(i, -1)).place(x=17 + i * 86, y=200, width=25, height=15)
    tk.Button(root, text="+1", command=lambda i=i: set_blender_amount(i, 1)).place(x=44 + i * 86, y=200, width=25, height=15)

# Shrine GUI elements
shrine_items = [tk.Label(root) for _ in range(2)]
shrine_timers = [tk.Label(root, text="h m s", justify="center") for _ in range(2)]
shrine_amounts = [tk.Label(root, font=("Tahoma", 7)) for _ in range(2)]
for i in range(2):
    shrine_items[i].place(x=302 + i * 114, y=140, width=40, height=40)
    shrine_timers[i].place(x=280 + i * 115, y=110, width=82, height=20)
    shrine_amounts[i].place(x=282 + i * 114, y=123, width=80, height=20)

# Function to reset shrine timer
def reset_shrine_timer(i):
    shrine_item = config.get("Shrine", f"ShrineItem{i+1}", fallback="None")
    if shrine_item != "None":
        update_config("Shrine", "LastShrine", 0)
        update_config("Shrine", f"ShrineRot", i + 1)

# Function to set shrine data
def set_shrine_amount(i, delta):
    shrine_item = config.get("Shrine", f"ShrineItem{i+1}", fallback="None")
    if shrine_item != "None":
        amount = int(config.get("Shrine", f"ShrineAmount{i+1}", fallback=1))
        if delta < 0 and amount > 1:
            amount += delta
        elif delta > 0:
            amount += delta
        update_config("Shrine", f"ShrineAmount{i+1}", amount)
        shrine_amounts[i].config(text=f"({amount}) [{'∞' if config.get('Shrine', f'ShrineIndex{i+1}', fallback='1') == 'Infinite' else config.get('Shrine', f'ShrineIndex{i+1}', fallback='1')}]")

# Function to set shrine data
for i in range(2):
    tk.Button(root, text="Ready", command=lambda i=i: reset_shrine_timer(i)).place(x=279 + i * 115, y=184, width=42, height=15)
    tk.Button(root, text="Add", command=lambda i=i: set_shrine_data(i)).place(x=321 + i * 114, y=184, width=42, height=15)
    tk.Button(root, text="-1", command=lambda i=i: set_shrine_amount(i, -1)).place(x=295 + i * 114, y=200, width=25, height=15)
    tk.Button(root, text="+1", command=lambda i=i: set_shrine_amount(i, 1)).place(x=322 + i * 114, y=200, width=25, height=15)

# Additional GUI elements
day_or_night = tk.Label(root, text="Day Detected", justify="center")
day_or_night.place(x=388, y=73, width=112, height=20)
status_label = tk.Label(root, text="Status:", justify="center")
status_label.place(x=391, y=2, width=110, height=60)
status_value = tk.Label(root, text="unknown", justify="left")
status_value.place(x=392, y=13, width=104, height=56)

# Main loop
def update_gui():
    # Planters
    for i in range(3):
        planter_data = {
            "field": config.get("Planters", f"PlanterField{i+1}", fallback="None"),
            "name": config.get("Planters", f"PlanterName{i+1}", fallback="None"),
            "nectar": config.get("Planters", f"PlanterNectar{i+1}", fallback="None"),
            "harvest_time": int(config.get("Planters", f"PlanterHarvestTime{i+1}", fallback=2147483647)),
            "est_percent": config.get("Planters", f"PlanterEstPercent{i+1}", fallback="0"),
            "hold": int(config.get("Planters", f"MPlanterHold{i+1}", fallback=0)),
            "smoking": int(config.get("Planters", f"MPlanterSmoking{i+1}", fallback=0))
        }
        planter_mode = int(config.get("Planters", "PlanterMode", fallback=0))

        for key, widget in [("field", planter_fields[i]), ("name", planter_names[i]), ("nectar", planter_nectars[i])]:
            path = f"nm_image_assets/ptimers/{key}s/{planter_data[key]}.png" if planter_data[key] != "None" else ""
            widget.config(image=load_image(path))

        timer = planter_data["harvest_time"] - now_unix()
        format_str = "'No Planter'" if timer > 360000 else "h'h' m'm' s's'" if timer > 0 else "'Ready'"
        if timer <= 0 and planter_mode == 1:
            format_str = "'Smoking'" if planter_data["smoking"] else "'Holding'" if planter_data["hold"] else "'Ready'"
        planter_timers[i].config(text=duration_from_seconds(timer, format_str))

    # Blenders
    for i in range(3):
        blender_data = {
            "item": config.get("Blender", f"BlenderItem{i+1}", fallback="None"),
            "time": int(config.get("Blender", f"BlenderTime{i+1}", fallback=0)),
            "count": int(config.get("Blender", f"BlenderCount{i+1}", fallback=0)),
            "amount": int(config.get("Blender", f"BlenderAmount{i+1}", fallback=1)),
            "index": config.get("Blender", f"BlenderIndex{i+1}", fallback="1")
        }
        blender_items[i].config(image=load_image(f"nm_image_assets/gui/blendershrine/{blender_data['item']}.png" if blender_data["item"] != "None" else ""))
        timer = blender_data["time"] - now_unix()
        format_str = "'No Item'" if blender_data["item"] == "None" else "h'h' m'm' s's'" if timer > 0 else "'Ready'"
        blender_timers[i].config(text=duration_from_seconds(timer, format_str))
        blender_amounts[i].config(text=f"({blender_data['count']}/{blender_data['amount']}) [{'∞' if blender_data['index'] == 'Infinite' else blender_data['index']}]")

    # Shrines
    for i in range(2):
        shrine_data = {
            "item": config.get("Shrine", f"ShrineItem{i+1}", fallback="None"),
            "amount": int(config.get("Shrine", f"ShrineAmount{i+1}", fallback=1)),
            "index": config.get("Shrine", f"ShrineIndex{i+1}", fallback="1")
        }
        last_shrine = int(config.get("Shrine", "LastShrine", fallback=0))
        shrine_items[i].config(image=load_image(f"nm_image_assets/gui/blendershrine/{shrine_data['item']}.png" if shrine_data["item"] != "None" else ""))
        timer = last_shrine + 3600 * (i + 1) - now_unix()
        format_str = "'No Item'" if shrine_data["item"] == "None" else "h'h' m'm' s's'" if timer > 0 else "'Ready'"
        shrine_timers[i].config(text=duration_from_seconds(timer, format_str))
        shrine_amounts[i].config(text=f"({shrine_data['amount']}) [{'∞' if shrine_data['index'] == 'Infinite' else shrine_data['index']}]")

    # Monster timers
    monster_times = {
        "king": int(config.get("Collect", "LastKingBeetle", fallback=0)),
        "tunnel": int(config.get("Collect", "LastTunnelBear", fallback=0)),
        "wolf": int(config.get("Collect", "LastBugrunWerewolf", fallback=0))
    }
    intervals = {"king": 86400, "tunnel": 172800, "wolf": 3600}
    for i, key in enumerate(["king", "tunnel", "wolf"]):
        timer = monster_times[key] - (now_unix() - intervals[key])
        format_str = "'N/A'" if timer > 360000 else "h'h' m'm' s's'" if timer > 0 else "'Now'"
        monster_timers[i].config(text=duration_from_seconds(timer, format_str))

    # Stats and status
    stats_values[0].config(text=config.get("Status", "HoneyAverage", fallback="0"))
    stats_values[1].config(text=config.get("Status", "SessionTotalHoney", fallback="0"))
    day_or_night.config(text=f"{config.get('Planters', 'dayOrNight', fallback='Day')} Detected")
    # Status from another window (simplified)
    status_value.config(text="unknown")

    root.after(1000, update_gui)

# Placeholder functions for adding data (to be implemented with sub-GUIs)
def add_planter_data(i):
    pass  # Implement sub-GUI for adding planter data

def set_blender_data(i):
    pass  # Implement sub-GUI for adding blender data

def set_shrine_data(i):
    pass  # Implement sub-GUI for adding shrine data

# Start GUI
set_timer_gui_transparency()
update_gui()
root.mainloop()

# Save position on exit
def save_timer_gui():
    x, y = root.winfo_x(), root.winfo_y()
    if x > 0:
        update_config("Planters", "TimerX", x)
    if y > 0:
        update_config("Planters", "TimerY", y)

root.protocol("WM_DELETE_WINDOW", lambda: [save_timer_gui(), root.destroy()])
