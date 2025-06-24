import os
import sys
import time
import json
import requests
import threading
import queue
from PIL import Image, ImageGrab
import configparser
import pyautogui
import win32gui
import win32con
from datetime import datetime, timezone
import base64
import re

# Directory setup
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir + "/..")

# Configuration
config = configparser.ConfigParser()
config.read("settings/nm_config.ini")

# Global variables
MacroState = 0
PublicJoined = 0
logsize = 0
HoneyUpdate = 0
status_buffer = queue.Queue()
command_buffer = queue.Queue()

# Command-line arguments
if len(sys.argv) < 2:
    print("This script needs to be run by Natro Macro! You are not supposed to run it manually.")
    sys.exit(1)

discordMode = int(sys.argv[1])
discordCheck = int(sys.argv[2])
webhook = sys.argv[3]
bottoken = sys.argv[4]
MainChannelCheck = int(sys.argv[5])
MainChannelID = sys.argv[6]
ReportChannelCheck = int(sys.argv[7])
ReportChannelID = sys.argv[8]
WebhookEasterEgg = int(sys.argv[9])
ssCheck = int(sys.argv[10])
ssDebugging = int(sys.argv[11])
CriticalSSCheck = int(sys.argv[12])
AmuletSSCheck = int(sys.argv[13])
MachineSSCheck = int(sys.argv[14])
BalloonSSCheck = int(sys.argv[15])
ViciousSSCheck = int(sys.argv[16])
DeathSSCheck = int(sys.argv[17])
PlanterSSCheck = int(sys.argv[18])
HoneySSCheck = int(sys.argv[19])
criticalCheck = int(sys.argv[20])
discordUID = sys.argv[21]
CriticalErrorPingCheck = int(sys.argv[22])
DisconnectPingCheck = int(sys.argv[23])
GameFrozenPingCheck = int(sys.argv[24])
PhantomPingCheck = int(sys.argv[25])
UnexpectedDeathPingCheck = int(sys.argv[26])
EmergencyBalloonPingCheck = int(sys.argv[27])
commandPrefix = sys.argv[28]
NightAnnouncementCheck = int(sys.argv[29])
NightAnnouncementName = sys.argv[30]
NightAnnouncementPingID = sys.argv[31]
NightAnnouncementWebhook = sys.argv[32]
PrivServer = sys.argv[33]
DebugLogEnabled = int(sys.argv[34])
MonsterRespawnTime = int(sys.argv[35])
HoneyUpdateSSCheck = int(sys.argv[36])

# Planters dictionary with base64 images
planters = {
    "blueclayplanter": {
        "bitmap": "iVBORw0KGgoAAAANSUhEUgAAACgAAAAoCAMAAAC7IEhfAAAB2lBMVEUAAAAeHh42NjY1NTUyMjIoKCgkJCQaGho1NTU2NjYzMzM0NDQzMzMvLy8tLS0qKio2NjY2NjYzMzM0NDQxMTEuLi4uLi4qKio2NjY1NTU0NDQsLCwvLy8kJCQyMjIzMzMzMzMzMzMyMjI0NDQ1NTUyMjIyMjIxMTEvLy8wMDEtLS0tLS05WbpAZs8/UH82NjY2NjdAZs5NcddAZcw4WLZOctg2N0I1NjY5WrsyTqE4WLg3V7QyT6Q5Wrg1VLE/UIJMb9Y9Ycc6W70tSJU+UYRMb9NFadFCZ9BBZ85Mbco4VbEzUKc3UKYxTZ4sRpM3O0w1Nz01NztJbdVFaM1KacJBYLo2VrMwTKAuSpo/VJE3TJFAU403SYo/Uoc4R3s3RHA6QmQ3P2A2PVc2O1E2NjlNb9BHactBZMlGZ8ZFZL40VK40U6w3U6szUqpAWaQ2Tp88U5wwTJw1SY03Qmw2QGk2OkdGa9NHa9JJa88+ZMpKasg6XcBEYbU8W643VK1EXqo4U6Y3UaItSJc6To41RYs/Uok3RXg3PVtEZsJAYcI/YL4+XbdBXbFGYK9EXKM2TZo/VplBVpY3TJU7TIo7S4c4SIIyO1xKbM9CZMY8X8I4Va49UJIuQ4U1QYKebRTcAAAALHRSTlMABP33xTITCfH73sqGY0Ia6uK7tXtMLB3awKxGOyWwpZmTb9fQzoBsW1lZI7SYQXAAAANuSURBVDjLfdVnV9pQGMDxECxiAdFau/ceofdmEPaSpSAbyl6Ce++9q3bvPb5rb5KCKNj/i5wc7i95yD05J1i1ZuUjheJGE5dMDABoa2q6pLjcjB3rqvyOVAMAhGwgECj1FQulAAsBaGm/eUVUwx7fbAOh+YLjw9s30R5Uf79z6MWrqc/5+TIUXzpfdecuQPbJmxUnRanVFGV19vesDD1/8Z2m6ZdTsyHQpBSY6NQFWFhDxvptYGj49cT79J7DYbE4ssmJWPfC4BQLLgr/9JYUFqKUMxKbSO45LE9qs2xSVOQTFPPDr0qDuRVrZDOJTF3ZAbUzNo8rOHgK7EeskYknDUsuqRcHD8BZHmo+dbvpZEOXfq6m3HShAr/QKvK1o05Z9t5GKcqlomfBPQHmaZWKjL1PZy0CcGSz6fSHzWg/2ioXqSJzQCbiYXFQhepe6okOD6+txYaHBgaWnJSasi64uAXyMzzNwXMtgZc8DFspCi2r+ajwoptEd+PgrgCbb7OvOIio2+1aCIfDiy6Xu1t12C8BYnfL66qGkSqhXY0AZXCXbKyE6DwQ4Fm8OPgfSK6zsAPjOi8OTdHkSdOXuw6guJWHzTLIrp8EbV0eFl5vrr6O+zYVeYygaNuqltgKwU7sX514ybBqs9F8JIkOy8s2249VrZYgiMlyS2sFSqTBbcJEaLXaLi5unSNCKdimrEBRB8gQJ/R0JoTfxyopYF5fb7ifGKP9K7hWha0tfRtmhl98ahZOmFGj0WvWj0/7v4KOKryM9037vHo0yDid8BnN6ILxhN/u03l99t8suH54Rzw4s7MzQph1dr8/odONGrwJf3x0XKfz2UsacWcVSmQgN2JPGOM7du+IwaxDwB9n0IDRke2gRi7Camcbxqd18biZf1Kv0WhEjusdxK9ihymlwS1Cb2CIujKgXVIDRWfgDNGwHDiD1SYHc3pTA8fMHYOdOLtNHMZfM+Yhenv7wI0jUHIRzDFEr8FEML0MQuhgmpkkNj4GwQPsSK3i0EfTs0kt4fnjQROf/UR4TD9W1IivHIWia+DAMDbJGY8J7YoBnW1kShrNJRF2tHNt5RSDCMFvEuPZSs3OQ4CfkWDHkwN2bnb/SyaVyuTyxQBb1kC8/Wy9w863AwAgH+BqEV98qMQadaoDB5Wk8ltXJLXfjr8sUSDBBtdhwQAAAABJRU5ErkJggg==",
        "name": "Blue Clay Planter",
        "color": 5403341
    },
    "candyplanter": {
        "bitmap": "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",
        "name": "Candy Planter",
        "color": 12822478
    },
    # Additional planters omitted for brevity, follow the same structure
}

# Timers dictionary
timers = {
    "mobs": {
        "bitmap": "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",
        "color": 9109504,
        "values": {
            1: {"varname": "BugrunLadybugs", "name": "Ladybugs", "cooldown": 330, "regex": r"i)^ladybug(s)?"},
            2: {"varname": "BugrunRhinoBeetles", "name": "Rhino Beetles", "cooldown": 330, "regex": r"i)^(rhino|beetle|rhinobeetle)(s)?"},
            # Additional mob timers omitted for brevity
        }
    },
    "machines": {
        "bitmap": "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",
        "color": 16766720,
        "values": {
            1: {"varname": "Clock", "name": "Wealth Clock", "cooldown": 3600, "regex": r"i)^(wealth|clock|wealthclock)"},
            # Additional machine timers omitted for brevity
        }
    },
    # Beesmas timers omitted for brevity
}

# Blender items (placeholders, actual bitmaps need to be sourced)
blender = {
    "BlueExtract": {"name": "Blue Extract", "color": 2703225},
    "RedExtract": {"name": "Red Extract", "color": 12660528},
    # Additional blender items omitted for brevity
}

# Settings dictionary
settings = {
    "webhook": {"enum": 1, "type": "str", "section": "Status", "regex": r"i)^(https:\/\/(canary\.|ptb\.)?(discord|discordapp)\.com\/api\/webhooks\/([\d]+)\/([a-z0-9_-]+)|<blank>)$"},
    "ReportChannelID": {"enum": 4, "type": "str", "section": "Status", "regex": r"i)^\d{17,20}$"},
    # Additional settings omitted for brevity
}

# Utility functions
def now_unix():
    return int(time.time())

def update_config(section, key, value):
    if not config.has_section(section):
        config.add_section(section)
    config.set(section, key, str(value))
    with open("settings/nm_config.ini", "w") as f:
        config.write(f)

def nm_status(status):
    state_string = status.split("] ")[1]
    state = state_string.split(": ")[0]
    objective = state_string.split(": ")[1]

    if DebugLogEnabled:
        with open("settings/debug_log.txt", "a") as log:
            log.write(status.replace("\n", " - ") + "\n")
        global logsize
        logsize = os.path.getsize("settings/debug_log.txt")

    if discordCheck:
        color = determine_color(state, objective)
        content = determine_content(state, objective)
        message = status.split("]")[1].strip()
        pBM = None
        if ssCheck and should_take_screenshot(state, objective):
            pBM = take_screenshot()
        Discord.send_embed(message, color, content, pBM)
        if NightAnnouncementCheck and not PublicJoined and state_string == "Detected: Night" and NightAnnouncementWebhook:
            send_night_announcement()

def determine_color(state, objective):
    colors = [16711680, 16744192, 16776960, 65280, 255, 4915330, 9699539]
    if WebhookEasterEgg:
        global color_index
        color_index = (color_index % 7) + 1 if 'color_index' in globals() else 0
        return colors[color_index]
    if state in ["Disconnected", "You Died", "Failed", "Error", "Aborting", "Missing", "Canceling"] or "Phantom" in objective or "No Balloon Convert" in objective:
        return 15085139
    # Additional color logic omitted for brevity
    return 5066239

def determine_content(state, objective):
    if criticalCheck and discordUID:
        if (CriticalErrorPingCheck and state == "Error") or (DisconnectPingCheck and "Disconnected" in state):
            return f"<@{discordUID}>"
    return ""

def should_take_screenshot(state, objective):
    if CriticalSSCheck and determine_content(state, objective):
        return True
    # Additional screenshot conditions omitted for brevity
    return False

def take_screenshot():
    hwnd = get_roblox_hwnd()
    if hwnd:
        x, y, w, h = get_roblox_client_pos(hwnd)
        return ImageGrab.grab(bbox=(x, y, x + w, y + h))
    return None

def send_night_announcement():
    payload = {
        "content": f"<@{NightAnnouncementPingID}>" if NightAnnouncementPingID else "",
        "embeds": [{
            "author": {
                "name": f"Night Detected in {NightAnnouncementName}'s Server" if NightAnnouncementName else "Night Detected",
                "url": PrivServer,
                "icon_url": "attachment://moon.png"
            },
            "description": f"A Vicious Bee **may** be found in [this server]({PrivServer})!",
            "color": 0,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }]
    }
    # Implementation for sending with moon bitmap omitted for brevity

def nm_honey():
    # Placeholder for honey update logic
    pass

def nm_command(command):
    # Placeholder for command handling logic
    pass

# Discord class
class Discord:
    base_url = "https://discord.com/api/v10/"

    @staticmethod
    def send_embed(message, color=5066239, content="", pBitmap=None, channel="", replyID=0):
        payload = {
            "content": content,
            "embeds": [{"description": message, "color": color}]
        }
        if pBitmap:
            payload["embeds"][0]["image"] = {"url": "attachment://ss.png"}
        headers = {"Content-Type": "application/json"}
        if discordMode == 0:
            url = f"{webhook}?wait=true"
        else:
            url = f"{Discord.base_url}/channels/{channel or MainChannelID}/messages"
            headers["Authorization"] = f"Bot {bottoken}"
        response = requests.post(url, json=payload, headers=headers)
        return response.text

    # Additional Discord methods omitted for brevity

# Main loop
def main_loop():
    iteration = 0
    while True:
        if not status_buffer.empty():
            nm_status(status_buffer.get())
        if iteration % 5 == 0:
            Discord.get_commands(MainChannelID)
        if not command_buffer.empty():
            nm_command(command_buffer.get())
        if iteration % 10 == 0:
            nm_honey()
        if DebugLogEnabled and logsize > 8000000:
            nm_trim_log(4194304)
        time.sleep(0.1)
        iteration += 1

def nm_trim_log(size):
    with open("settings/debug_log.txt", "r") as f:
        content = f.read()
    if len(content) > size:
        content = content[-size:]
        with open("settings/debug_log.txt", "w") as f:
            f.write(content.split("\n", 1)[1] if "\n" in content else content)
    global logsize
    logsize = os.path.getsize("settings/debug_log.txt")

def get_roblox_hwnd():
    return win32gui.FindWindow(None, "Roblox")

def get_roblox_client_pos(hwnd):
    rect = win32gui.GetClientRect(hwnd)
    point = win32gui.ClientToScreen(hwnd, (rect[0], rect[1]))
    return (point[0], point[1], rect[2] - rect[0], rect[3] - rect[1])

# Start the main loop
threading.Thread(target=main_loop, daemon=True).start()

# Initial Discord connection message
Discord.send_embed("Connected to Discord!", 5066239)
