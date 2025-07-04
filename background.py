# Natro Macro Background Script (Python Conversion)
# Copyright © Natro Team (https://github.com/NatroTeam)
# Licensed under GNU General Public License v3.0 or later

import pyautogui
import win32gui
import win32con
import time
import sys
import ctypes
from PIL import ImageGrab
import configparser
from ctypes.wintypes import HWND, UINT, LPARAM  
if len(sys.argv) == 1:
    print("This script needs to be run by Natro Macro! You are not supposed to run it manually.")
    sys.exit()

# Global variables
resetTime = time.time()
LastState = 0
LastConvertBalloon = time.time()
VBState = 0
state = 0
MacroState = 2
NightLastDetected = float(sys.argv[1]) if len(sys.argv) > 1 else time.time()
VBLastKilled = float(sys.argv[2]) if len(sys.argv) > 2 else time.time()
StingerCheck = int(sys.argv[3]) if len(sys.argv) > 3 else 0
StingerDailyBonusCheck = int(sys.argv[4]) if len(sys.argv) > 4 else 0
AnnounceGuidingStar = int(sys.argv[5]) if len(sys.argv) > 5 else 0
ReconnectInterval = int(sys.argv[6]) if len(sys.argv) > 6 else 0
ReconnectHour = int(sys.argv[7]) if len(sys.argv) > 7 else 0
ReconnectMin = int(sys.argv[8]) if len(sys.argv) > 8 else 0
EmergencyBalloonPingCheck = int(sys.argv[9]) if len(sys.argv) > 9 else 0
ConvertBalloon = sys.argv[10] if len(sys.argv) > 10 else "Never"
NightMemoryMatchCheck = int(sys.argv[11]) if len(sys.argv) > 11 else 0
LastNightMemoryMatch = float(sys.argv[12]) if len(sys.argv) > 12 else time.time()

# Configuration
config = configparser.ConfigParser()
config.read("settings/nm_config.ini")

# Image paths
IMAGE_PATH = "nm_image_assets/"

# Window handling
def get_roblox_window():
    hwnd = win32gui.FindWindow(None, "Roblox")
    if hwnd:
        rect = win32gui.GetWindowRect(hwnd)
        return hwnd, rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1]
    return None, 0, 0, 0, 0

import threading

config_lock = threading.Lock()

def update_config(section, key, value):
    with config_lock:
        config.read("settings/nm_config.ini")
        if not config.has_section(section):
            config.add_section(section)
        config.set(section, key, str(value))
        with open("settings/nm_config.ini", "w") as f:
            config.write(f)

# Message passing
class COPYDATASTRUCT(ctypes.Structure):
    """
    Structure used for sending data between Windows applications using WM_COPYDATA.
    dwData: user-defined data to be passed to the receiving application.
    cbData: size of the data in bytes.
    lpData: pointer to data to be passed.
    """
    _fields_ = [("dwData", ctypes.c_ulong),
                ("cbData", ctypes.c_ulong),
                ("lpData", ctypes.c_void_p)]

def send_wm_copydata(string, target_title, wparam=0):
    target_hwnd = win32gui.FindWindow(None, target_title)
    if not target_hwnd:
        return -1
    buf = ctypes.create_unicode_buffer(string)
    cds = COPYDATASTRUCT()
    cds.dwData = wparam
    cds.cbData = (len(string) + 1) * 2
    cds.lpData = ctypes.cast(buf, ctypes.c_void_p)
    return win32gui.SendMessage(target_hwnd, win32con.WM_COPYDATA, wparam, ctypes.addressof(cds))

# Helper functions
def nm_deathCheck():
    global LastDeathDetected
    LastDeathDetected = globals().get('LastDeathDetected', 0)
    if time.time() - resetTime > 20 and time.time() - LastDeathDetected > 10:
        try:
            if pyautogui.locateOnScreen(IMAGE_PATH + "died.png", region=(windowX + windowWidth//2, windowY + windowHeight//2, windowWidth//2, windowHeight//2), confidence=0.5):
                if win32gui.FindWindow(None, "natro_macro"):
                    win32gui.PostMessage(win32gui.FindWindow(None, "natro_macro"), 0x5555, 1, 1)
                    send_wm_copydata("You Died", "natro_macro")
                LastDeathDetected = time.time()
        except:
            pass

def nm_guidCheck():
    global windowX, windowY, windowWidth, windowHeight, offsetY, state
    LastFieldGuidDetected = globals().get('LastFieldGuidDetected', 1)
    FieldGuidDetected = globals().get('FieldGuidDetected', 0)
    confirm = globals().get('confirm_guid', 0)
    try:
        if pyautogui.locateOnScreen(IMAGE_PATH + "boostguidingstar.png", region=(windowX, windowY + offsetY + 30, windowWidth, 60), confidence=0.5):
            confirm = 0
            if FieldGuidDetected == 0 and state == 1:
                FieldGuidDetected = 1
                if win32gui.FindWindow(None, "natro_macro"):
                    win32gui.PostMessage(win32gui.FindWindow(None, "natro_macro"), 0x5555, 6, 1)
                    send_wm_copydata("Detected: Guiding Star Active", "natro_macro")
                LastFieldGuidDetected = time.time()
        elif time.time() - LastFieldGuidDetected > 5 and FieldGuidDetected:
            confirm += 1
            if confirm >= 5:
                confirm = 0
                FieldGuidDetected = 0
                if win32gui.FindWindow(None, "natro_macro"):
                    win32gui.PostMessage(win32gui.FindWindow(None, "natro_macro"), 0x5555, 6, 0)
    except:
        pass
    globals()['LastFieldGuidDetected'] = LastFieldGuidDetected
    globals()['FieldGuidDetected'] = FieldGuidDetected
    globals()['confirm_guid'] = confirm

def nm_popStarCheck():
    global state
    HasPopStar = globals().get('HasPopStar', 0)
    PopStarActive = globals().get('PopStarActive', 0)
    try:
        if pyautogui.locateOnScreen(IMAGE_PATH + "popstar_counter.png", region=(windowX + windowWidth//2 - 275, windowY + 3*windowHeight//4, 550, windowHeight//4), confidence=0.7):
            if HasPopStar == 0:
                HasPopStar = 1
                if win32gui.FindWindow(None, "natro_macro"):
                    win32gui.PostMessage(win32gui.FindWindow(None, "natro_macro"), 0x5555, 7, 1)
            if HasPopStar and PopStarActive == 1:
                PopStarActive = 0
                if win32gui.FindWindow(None, "natro_macro"):
                    win32gui.PostMessage(win32gui.FindWindow(None, "natro_macro"), 0x5555, 8, 0)
                if win32gui.FindWindow(None, "StatMonitor.ahk"):
                    win32gui.PostMessage(win32gui.FindWindow(None, "StatMonitor.ahk"), 0x5556, 1, 0)
        else:
            if HasPopStar and PopStarActive == 0 and state == 1:
                PopStarActive = 1
                if win32gui.FindWindow(None, "natro_macro"):
                    win32gui.PostMessage(win32gui.FindWindow(None, "natro_macro"), 0x5555, 8, 1)
                if win32gui.FindWindow(None, "StatMonitor.ahk"):
                    win32gui.PostMessage(win32gui.FindWindow(None, "StatMonitor.ahk"), 0x5556, 1, 1)
    except:
        pass
    globals()['HasPopStar'] = HasPopStar
    globals()['PopStarActive'] = PopStarActive

def nm_dayOrNight():
    global NightLastDetected, StingerCheck, StingerDailyBonusCheck, VBLastKilled, VBState, NightMemoryMatchCheck, LastNightMemoryMatch
    confirm = globals().get('confirm_daynight', 0)
    if StingerCheck == 0 and NightMemoryMatchCheck == 0:
        return
    if (VBState == 1 and (time.time() - NightLastDetected > 400 or time.time() - NightLastDetected < 0)) or \
       (VBState == 2 and (time.time() - VBLastKilled > 600 or time.time() - VBLastKilled < 0)):
        VBState = 0
        if win32gui.FindWindow(None, "natro_macro"):
            win32gui.PostMessage(win32gui.FindWindow(None, "natro_macro"), 0x5555, 3, 0)
    
    pBMScreen = ImageGrab.grab(bbox=(windowX + windowWidth//2, windowY, 60, 100))
    if not pyautogui.locate(IMAGE_PATH + "toppollen.png", pBMScreen, confidence=0.8):
        return
    
    pBMScreen = ImageGrab.grab(bbox=(windowX, windowY + 2*windowHeight//5, windowWidth, 3*windowHeight//5))
    day_bitmaps = [IMAGE_PATH + "day1.png", IMAGE_PATH + "day2.png"]  # Adjust paths as needed
    for bitmap in day_bitmaps:
        if pyautogui.locate(bitmap, pBMScreen, confidence=0.6):
            dayOrNight = "Day"
            break
    else:
        pBMScreen = ImageGrab.grab(bbox=(windowX, windowY + windowHeight//2, windowWidth, windowHeight//2))
        night_bitmaps = [IMAGE_PATH + "night1.png", IMAGE_PATH + "night2.png"]  # Adjust paths as needed
        for bitmap in night_bitmaps:
            if pyautogui.locate(bitmap, pBMScreen, confidence=0.4):
                dayOrNight = "Dusk"
                break
        else:
            dayOrNight = "Day"
    
    if dayOrNight in ["Dusk", "Night"]:
        confirm += 1
    else:
        confirm = 0
    
    if confirm >= 5:
        dayOrNight = "Night"
        if time.time() - NightLastDetected > 300 or time.time() - NightLastDetected < 0:
            NightLastDetected = time.time()
            update_config("Collect", "NightLastDetected", NightLastDetected)
            if win32gui.FindWindow(None, "natro_macro"):
                win32gui.PostMessage(win32gui.FindWindow(None, "natro_macro"), 0x5555, 2, int(NightLastDetected))
                send_wm_copydata("Detected: Night", "natro_macro")
            if (StingerCheck == 1 and (StingerDailyBonusCheck == 0 or time.time() - VBLastKilled > 79200) and VBState == 0) or \
               (NightMemoryMatchCheck == 1 and time.time() - LastNightMemoryMatch > 28800):
                VBState = 1
                if win32gui.FindWindow(None, "natro_macro"):
                    win32gui.PostMessage(win32gui.FindWindow(None, "natro_macro"), 0x5555, 3, 1)
    
    if win32gui.FindWindow(None, "PlanterTimers.ahk"):
        update_config("Planters", "DayOrNight", dayOrNight)
    globals()['confirm_daynight'] = confirm

def nm_backpackPercent():
    global windowX, windowY, windowWidth, windowHeight, offsetY
    try:
        backpackColor = pyautogui.pixel(windowX + windowWidth//2 + 59 + 3, windowY + offsetY + 6)
    except:
        return 0
    r, g, b = backpackColor[0], backpackColor[1], backpackColor[2]
    if r <= 0x69:
        if r <= 0x4B:
            if r <= 0x42:
                if r <= 0x41 and g <= 0xFF and b <= 0x80 and b > 0x86:
                    return 0
                elif r > 0x41 and g <= 0xFF and b <= 0x80 and b > 0x85:
                    return 5
                else:
                    return 0
            else:
                if r <= 0x47:
                    if r <= 0x44 and g <= 0xFE and b <= 0x85 and b > 0x84:
                        return 10
                    elif r > 0x44 and g <= 0xFB and b <= 0x84 and b > 0x82:
                        return 15
                    else:
                        return 0
                elif r > 0x47 and g <= 0xF7 and b <= 0x82 and b > 0x80:
                    return 20
                else:
                    return 0
        else:
            if r <= 0x5B:
                if r <= 0x4F and g <= 0xF2 and b <= 0x80 and b > 0x7D:
                    return 25
                else:
                    if r <= 0x55 and g <= 0xEC and b <= 0x7D and b > 0x7A:
                        return 30
                    elif r > 0x55 and g <= 0xE5 and b <= 0x7A and b > 0x76:
                        return 35
                    else:
                        return 0
            else:
                if r <= 0x62 and g <= 0xDC and b <= 0x76 and b > 0x72:
                    return 40
                elif r > 0x62 and g <= 0xD2 and b <= 0x72 and b > 0x6D:
                    return 45
                else:
                    return 0
    else:
        if r <= 0x9C:
            if r <= 0x85:
                if r <= 0x7B:
                    if r <= 0x72 and g <= 0xC8 and b <= 0x6D and b > 0x68:
                        return 50
                    elif r > 0x72 and g <= 0xBC and b <= 0x68 and b > 0x62:
                        return 55
                    else:
                        return 0
                elif r > 0x7B and g <= 0xAF and b <= 0x62 and b > 0x5C:
                    return 60
                else:
                    return 0
            else:
                if r <= 0x90 and g <= 0xA0 and b <= 0x5C and b > 0x55:
                    return 65
                elif r > 0x90 and g <= 0x91 and b <= 0x55 and b > 0x4E:
                    return 70
                else:
                    return 0
        else:
            if r <= 0xC4:
                if r <= 0xA9 and g <= 0x80 and b <= 0x4E and b > 0x46:
                    return 75
                else:
                    if r <= 0xB6 and g <= 0x6E and b <= 0x46 and b > 0x3F:
                        return 80
                    elif r > 0xB6 and g <= 0x5D and b <= 0x3F and b > 0x37:
                        return 85
                    else:
                        return 0
            else:
                if r <= 0xD3 and g <= 0x4A and b <= 0x37 and b > 0x2E:
                    return 90
                else:
                    if (r == 0xF7 and g == 0x00 and b == 0x17) or (r >= 0xE0 and g <= 0x24 and b <= 0x27 and b > 0x10):
                        return 100
                    elif g <= 0x34 and b <= 0x2E:
                        return 95
                    else:
                        return 0
    return 0

PackFilterArray = []
LastBackpackPercentFiltered = 0
i = 0
samplesize = 6

def nm_backpackPercentFilter():
    global PackFilterArray, LastBackpackPercentFiltered, i
    if len(PackFilterArray) == samplesize:
        PackFilterArray.pop(0)
    PackFilterArray.append(nm_backpackPercent())
    BackpackPercentFiltered = round(sum(PackFilterArray) / len(PackFilterArray))
    if i == 0 and win32gui.FindWindow(None, "StatMonitor.ahk"):
        win32gui.PostMessage(win32gui.FindWindow(None, "StatMonitor.ahk"), 0x5557, BackpackPercentFiltered, 60 * int(time.strftime("%M")) + int(time.strftime("%S")))
    i = (i + 1) % 6
    if BackpackPercentFiltered != LastBackpackPercentFiltered:
        if win32gui.FindWindow(None, "natro_macro"):
            win32gui.PostMessage(win32gui.FindWindow(None, "natro_macro"), 0x5555, 5, BackpackPercentFiltered)
        LastBackpackPercentFiltered = BackpackPercentFiltered

fieldnames = ["PineTree", "Stump", "Bamboo", "BlueFlower", "MountainTop", "Cactus", "Coconut", "Pineapple", "Spider", "Pumpkin", "Dandelion", "Sunflower", "Clover", "Pepper", "Rose", "Strawberry", "Mushroom"]

def nm_guidingStarDetect():
    global LastGuidDetected
    LastGuidDetected = globals().get('LastGuidDetected', 0)
    if AnnounceGuidingStar == 0 or time.time() - LastGuidDetected < 10:
        return
    xi = windowX + windowWidth // 2
    yi = windowY + windowHeight // 2
    ww = windowWidth // 2
    wh = windowHeight // 2
    for i in range(1, 3):
        try:
            if pyautogui.locateOnScreen(IMAGE_PATH + f"guiding_star_icon{i}.png", region=(xi, yi, ww, wh), confidence=0.5):
                for field in fieldnames:
                    if pyautogui.locateOnScreen(IMAGE_PATH + f"guiding_star_{field}.png", region=(xi, yi, ww, wh), confidence=0.5):
                        if win32gui.FindWindow(None, "natro_macro"):
                            send_wm_copydata(field, "natro_macro", 1)
                            LastGuidDetected = time.time()
                        break
                break
        except:
            pass
    globals()['LastGuidDetected'] = LastGuidDetected

LastDailyReconnect = 0

def nm_dailyReconnect():
    global LastDailyReconnect
    if not ReconnectHour or not ReconnectMin or not ReconnectInterval or time.time() - LastDailyReconnect < 60:
        return
    RChourUTC = int(time.strftime("%H", time.gmtime()))
    RCminUTC = int(time.strftime("%M", time.gmtime()))
    HourReady = any((ReconnectHour + ReconnectInterval * i) % 24 == RChourUTC for i in range(24 // ReconnectInterval))
    if ReconnectMin == RCminUTC and HourReady and MacroState == 2:
        LastDailyReconnect = time.time()
        if win32gui.FindWindow(None, "natro_macro"):
            send_wm_copydata("Closing: Roblox, Daily Reconnect", "natro_macro")
            win32gui.PostMessage(win32gui.FindWindow(None, "natro_macro"), 0x5557, 60)

LastEmergency = 0

def nm_EmergencyBalloon():
    global LastEmergency, LastConvertBalloon
    if EmergencyBalloonPingCheck == 1 and ConvertBalloon != "Never" and time.time() - LastEmergency > 60:
        time_since_convert = time.time() - LastConvertBalloon
        if time_since_convert > 2700 and time_since_convert < 3600:
            if win32gui.FindWindow(None, "natro_macro"):
                duration = f"{int(time_since_convert // 60)}m {int(time_since_convert % 60)}s"
                send_wm_copydata(f"Detected: No Balloon Convert in {duration}", "natro_macro")
                LastEmergency = time.time()

def nm_sendHeartbeat():
    if win32gui.FindWindow(None, "Heartbeat.ahk"):
        win32gui.PostMessage(win32gui.FindWindow(None, "Heartbeat.ahk"), 0x5556, 2, 0)

# Window procedure
def wndProc(hwnd, msg, wParam, lParam):
    global state, LastState
    if msg == 0x5552:  # nm_setGlobalInt
        pass  # Placeholder: requires EnumInt mapping
    elif msg == 0x5553:  # nm_setGlobalStr
        pass  # Placeholder: requires EnumStr mapping
    elif msg == 0x5554:  # nm_setGlobalNum
        global resetTime, NightLastDetected, VBState, StingerCheck, VBLastKilled, LastConvertBalloon, NightMemoryMatchCheck, LastNightMemoryMatch
        arr = ["resetTime", "NightLastDetected", "VBState", "StingerCheck", "VBLastKilled", "LastConvertBalloon", "NightMemoryMatchCheck", "LastNightMemoryMatch"]
        if wParam < len(arr):
            globals()[arr[wParam]] = lParam
    elif msg == 0x5555:  # nm_setState
        state = wParam
        LastState = lParam
    elif msg == 0x5556:  # nm_sendHeartbeat
        nm_sendHeartbeat()
    return win32gui.DefWindowProc(hwnd, msg, wParam, lParam)

# Main loop
while True:
    roblox_hwnd, windowX, windowY, windowWidth, windowHeight = get_roblox_window()
    if roblox_hwnd:
        # offsetY is used to adjust for any vertical offset in the Roblox window UI; set this based on your Roblox.ahk logic if needed.
        offsetY = 0
        nm_deathCheck()
        nm_guidCheck()
        nm_popStarCheck()
        nm_dayOrNight()
        nm_backpackPercentFilter()
        nm_guidingStarDetect()
        nm_dailyReconnect()
        nm_EmergencyBalloon()
    win32gui.PumpWaitingMessages()
    win32gui.PumpWaitingMessages()
    time.sleep(0.1)
