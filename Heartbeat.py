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

import sys
import os
import time
import subprocess
import psutil
import win32gui
import win32con
import win32process
import ctypes
from ctypes.wintypes import HWND, UINT, LPARAM

# Define Windows message constants
WM_HEARTBEAT = 0x5556
WM_SET_GLOBAL_INT = 0x5552
WM_COPYDATA = 0x004A

# Global variables
last_roblox_window = last_status_heartbeat = last_main_heartbeat = last_background_heartbeat = time.time()
macro_state = 0
prev_macro_state = 0

# Path to the main macro script (assumed to be in the same directory)
script_dir = os.path.dirname(os.path.abspath(__file__))
macro_path = [sys.executable, os.path.join(script_dir, "natro_macro.py")]

# COPYDATASTRUCT for WM_COPYDATA
class COPYDATASTRUCT(ctypes.Structure):
    _fields_ = [
        ("dwData", ctypes.c_ulong),
        ("cbData", ctypes.c_ulong),
        ("lpData", ctypes.c_void_p)
    ]

def send_wm_copydata(hwnd, string, wparam=0):
    """Send a WM_COPYDATA message with a string to another window."""
    buf = ctypes.create_unicode_buffer(string)
    cds = COPYDATASTRUCT()
    cds.dwData = wparam
    cds.cbData = (len(string) + 1) * 2  # Size in bytes (Unicode)
    cds.lpData = ctypes.cast(buf, ctypes.c_void_p)
    return win32gui.SendMessage(hwnd, WM_COPYDATA, 0, ctypes.addressof(cds))

def is_roblox_running():
    """Check if Roblox processes are running."""
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] in ['RobloxPlayerBeta.exe', 'ApplicationFrameHost.exe', 'RobloxPlayer.exe']:
            return True
    return False

def wndProc(hwnd, msg, wParam, lParam):
    """Window procedure to handle messages."""
    global last_roblox_window, last_status_heartbeat, last_main_heartbeat, last_background_heartbeat
    global macro_state, prev_macro_state

    if msg == win32con.WM_TIMER and wParam == 1:
        current_time = time.time()

        # Update the last Roblox window time if Roblox is running
        if is_roblox_running():
            last_roblox_window = current_time

        # Request heartbeats
        for title in ["natro_macro", "Status", "background"]:
            script_hwnd = win32gui.FindWindow(None, title)
            if script_hwnd:
                win32gui.PostMessage(script_hwnd, WM_HEARTBEAT, 0, 0)

        # Check for timeouts
        reason = None
        if ((macro_state == 2 and (
            (current_time - last_main_heartbeat > 120 and (reason := "Macro Unresponsive Timeout!")) or
            (current_time - last_background_heartbeat > 120 and (reason := "Background Script Timeout!")) or
            (current_time - last_status_heartbeat > 120 and (reason := "Status Script Timeout!")) or
            (current_time - last_roblox_window > 600 and (reason := "No Roblox Window Timeout!"))
        )) or
        (macro_state == 1 and (
            (current_time - last_main_heartbeat > 120 and (reason := "Macro Unresponsive Timeout!")) or
            (current_time - last_background_heartbeat > 120 and (reason := "Background Script Timeout!")) or
            (current_time - last_status_heartbeat > 120 and (reason := "Status Script Timeout!"))
        ))):
            # Restart logic
            prev_macro_state = macro_state
            macro_state = 0

            # Close existing Natro Macro and Roblox processes
            pids_to_close = set()
            def enum_windows_callback(hwnd, lparam):
                title = win32gui.GetWindowText(hwnd)
                if any(t in title for t in ["natro_macro", "Status", "background"]):
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    lparam.add(pid)
                return True
            win32gui.EnumWindows(enum_windows_callback, pids_to_close)
            for pid in pids_to_close:
                try:
                    psutil.Process(pid).terminate()
                except psutil.NoSuchProcess:
                    pass
            for proc in psutil.process_iter(['name', 'cmdline']):
                cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                if 'Roblox' in proc.info['name'] or 'ROBLOXCORPORATION' in cmdline:
                    try:
                        proc.terminate()
                    except psutil.NoSuchProcess:
                        pass

            # Start new instance
            force_start = (prev_macro_state == 2)
            subprocess.Popen(macro_path + [str(force_start), str(hwnd)])

            # Wait for the new macro window (assuming title "Natro")
            start_time = time.time()
            main_hwnd = 0
            while time.time() - start_time < 300:  # 5-minute timeout
                main_hwnd = win32gui.FindWindow(None, "Natro")
                if main_hwnd:
                    break
                time.sleep(1)
            if main_hwnd:
                send_wm_copydata(main_hwnd, f"Error: {reason}\nSuccessfully restarted macro!")
                time.sleep(1)
                last_roblox_window = last_status_heartbeat = last_main_heartbeat = last_background_heartbeat = current_time

        # Adjust heartbeat times based on macro_state
        elif macro_state == 1:
            last_roblox_window += 5
        elif macro_state == 0:
            last_background_heartbeat += 5
            last_roblox_window += 5

    elif msg == WM_HEARTBEAT:
        # Update heartbeat times based on wParam
        script = wParam
        if script == 1:
            last_main_heartbeat = time.time()
        elif script == 2:
            last_background_heartbeat = time.time()
        elif script == 3:
            last_status_heartbeat = time.time()

    elif msg == WM_SET_GLOBAL_INT:
        # Set global variables (e.g., MacroState where wParam == 23)
        var = wParam
        value = lParam
        if var == 23:
            macro_state = value

    return win32gui.DefWindowProc(hwnd, msg, wParam, lParam)

# Main message loop
while True:
    if wndProc == 0:  # WM_QUIT
        break
