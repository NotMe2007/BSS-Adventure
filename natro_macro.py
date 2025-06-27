##################################################################################################################################################################################################################
# Natro Macro (https://github.com/NatroTeam/NatroMacro)
# Copyright © Natro Team (https://github.com/NatroTeam)
#
# This file is part of Natro Macro. Our source code will always be open and available.
#
# Natro Macro is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# Natro Macro is distributed in the hope that it will be useful. This does not give you the right to steal sections from our code, distribute it under your own name, then slander the macro.
#
# You should have received a copy of the license along with Natro Macro. If not, please redownload from an official source.
##################################################################################################################################################################################################################

##################################
# Imports
##################################

import os
import sys
import time
import subprocess
import psutil
import ctypes
import configparser
import pyautogui
import win32gui
import win32con
import threading
import queue
from pathlib import Path

###########################################################
# Directory setup
###########################################################

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir + "/..")

###########################################################
# Configuration
###########################################################
config = configparser.ConfigParser()
config.read("settings/nm_config.ini")

# Global variables
MacroState = 0
VersionID = "1.0.1"
status_buffer = queue.Queue()
command_buffer = queue.Queue()
################################################
# Key mappings (note: thise are note 100% accurate, they are based on the AHK scancodes) 
# please check if we can get the actual scancodes from Roblox or AHK and inprove this
################################################
FwdKey = "w"        # sc011
LeftKey = "a"       # sc01e
BackKey = "s"       # sc01f
RightKey = "d"      # sc020
RotLeft = ","       # sc033
RotRight = "."      # sc034
RotUp = "pageup"    # sc149
RotDown = "pagedown"# sc151
ZoomIn = "i"        # sc017
ZoomOut = "o"       # sc018
SC_E = "e"          # sc012
SC_R = "r"          # sc013
SC_L = "l"          # sc026
SC_Esc = "esc"      # sc001
SC_Enter = "enter"  # sc01c
SC_LShift = "shift" # sc02a
SC_Space = "space"  # sc039
SC_1 = "1"          # sc002

################################
# Functions
################################

# Check for admin privileges
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False
# Elevate script to run as admin if not already
def elevate_script():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit(0)

# Close remnant Natro scripts and start heartbeat
def close_scripts():
    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        if 'python' in proc.info['name'].lower() and proc.info['exe'] != sys.executable:
            try:
                proc.terminate()
            except psutil.NoSuchProcess:
                pass
# Start a heartbeat script to keep the macro alive
def start_heartbeat():
    heartbeat_path = os.path.join(os.getcwd(), "submacros", "heartbeat.py")
    if not os.path.exists(heartbeat_path):
        with open(heartbeat_path, "w") as f:
            f.write("# Placeholder heartbeat script\nwhile True:\n    time.sleep(1)")
    subprocess.Popen([sys.executable, heartbeat_path], creationflags=subprocess.CREATE_NO_WINDOW)

# Initialization
def initialize():
    elevate_script()
    close_scripts()
    start_heartbeat()
    
    # Check screen DPI (approximation for Python)
    if pyautogui.size()[0] / 96 != 1:  # Assuming 96 DPI as default (mine is 3200 dpi)
        print("WARNING: Display scale is not 100%. The macro may not work correctly.")
        print("Set scale to 100% in Display Settings and restart Roblox.")

    create_folders()

# Create settings folders
def create_folders():
    for folder in ["settings", "settings/imported"]:
        if not os.path.exists(folder):
            try:
                os.makedirs(folder)
            except OSError:
                print(f"Error: Could not create '{folder}' directory. Move the macro to a writable folder.")

# Import patterns
patterns = {}
patternlist = []

# Function to import patterns from the 'patterns' directory
def import_patterns():
    global patterns, patternlist
    patterns = {}
    patternlist = []

    # Check if the imported patterns file exists
    imported_file = Path("settings/imported/patterns.py") 
    imported_content = imported_file.read_text() if imported_file.exists() else ""

    # Read all pattern files from the 'patterns' directory
    import_content = ""
    for file_path in Path("patterns").glob("*.py"):
        pattern_name = file_path.stem
        pattern_content = file_path.read_text()
        
        # Basic syntax check placeholder (expand as needed)
        if "patterns[" in pattern_content.lower():
            print(f"Error: Pattern '{pattern_name}' seems deprecated. Check for updates.")
            continue

        # Check if the pattern is already imported
        if f'("{pattern_name}")\n{pattern_content}\n\n' not in imported_content:
            # Placeholder for syntax validation (e.g., run in a sandbox)
            try:
                patterns[pattern_name] = pattern_content
                patternlist.append(pattern_name)
                import_content += f'("{pattern_name}")\n{pattern_content}\n\n'
            except Exception as e:
                print(f"Unable to import '{pattern_name}': {e}")
                continue

    # Write the imported patterns to the file if they differ
    if import_content != imported_content:
        imported_file.write_text(import_content)

# Import paths
paths = {
    "gtb": {}, "gtc": {}, "gtf": {}, "gtp": {}, "gtq": {}, "wf": {}
}

# Define path names for each category
path_names = {
    "gtb": ["blue", "mountain", "red"],
    "gtc": ["clock", "antpass", "robopass", "honeydis", "treatdis", "blueberrydis", "strawberrydis", "coconutdis", "gluedis", "royaljellydis", "blender", "windshrine",
            "stockings", "wreath", "feast", "gingerbread", "snowmachine", "candles", "samovar", "lidart", "gummybeacon", "rbpdelevel",
            "honeylb", "honeystorm", "stickerstack", "stickerprinter", "normalmm", "megamm", "nightmm", "extrememm", "wintermm"],
    "gtf": ["bamboo", "blueflower", "cactus", "clover", "coconut", "dandelion", "mountaintop", "mushroom", "pepper", "pinetree", "pineapple", "pumpkin",
            "rose", "spider", "strawberry", "stump", "sunflower"],
    "gtp": ["bamboo", "blueflower", "cactus", "clover", "coconut", "dandelion", "mountaintop", "mushroom", "pepper", "pinetree", "pineapple", "pumpkin",
            "rose", "spider", "strawberry", "stump", "sunflower"],
    "gtq": ["black", "brown", "bucko", "honey", "polar", "riley"],
    "wf": ["bamboo", "blueflower", "cactus", "clover", "coconut", "dandelion", "mountaintop", "mushroom", "pepper", "pinetree", "pineapple", "pumpkin",
           "rose", "spider", "strawberry", "stump", "sunflower"]
}

# Function to import paths from the 'paths' directory
def import_paths():
    global paths
    for category, names in path_names.items():
        for name in names:
            file_path = Path(f"paths/{category}-{name}.ahk")
            try:
                content = file_path.read_text()
                if "paths[" in content.lower():
                    print(f"Error: Path '{category}-{name}' seems deprecated. Check for updates.")
                paths[category][name] = content
            except FileNotFoundError:
                print(f"Error: Could not find '{category}-{name}' path. Ensure it exists in 'paths' folder.")
            except Exception as e:
                print(f"Error importing '{category}-{name}': {e}")


# Function to handle status updates
def nm_status(status):
    # Placeholder for status handling
    pass

# Function to handle commands
def nm_command(command):
    # Placeholder for command handling
    pass

# Function to handle walking in the game
def nm_walk(distance, direction):
    # Placeholder for game walking function
    pass

# Function to handle game reset
def nm_reset():
    # Placeholder for game reset function
    pass


# Define the path to the INI file
inipath = os.path.join(os.getcwd(), "settings", "nm_config.ini")
###########################################
# Import configuration settings
###########################################
def nm_import_config():
    global config
    config = {# "Version": VersionID,
        "Settings": {
            "GuiTheme": "MacLion3",
            "AlwaysOnTop": 0,
            "MoveSpeedNum": 28,
            "MoveMethod": "Cannon",
            "SprinklerType": "Supreme",
            "MultiReset": 0,
            "ConvertBalloon": "Gather",
            "ConvertMins": 30,
            "LastConvertBalloon": 1,
            "GatherDoubleReset": 1,
            "DisableToolUse": 0,
            "AnnounceGuidingStar": 0,
            "NewWalk": 1,
            "HiveSlot": 6,
            "HiveBees": 50,
            "ConvertDelay": 5,
            "PrivServer": "",
            "FallbackServer1": "",
            "FallbackServer2": "",
            "FallbackServer3": "",
            "ReconnectMethod": "Deeplink",
            "ReconnectInterval": "",
            "ReconnectHour": "",
            "ReconnectMin": "",
            "ReconnectMessage": 0,
            "PublicFallback": 1,
            "GuiX": "",
            "GuiY": "",
            "GuiTransparency": 0,
            "BuffDetectReset": 0,
            "ClickCount": 1000,
            "ClickDelay": 10,
            "ClickMode": 1,
            "ClickDuration": 50,
            "KeyDelay": 20,
            "StartHotkey": "F1",
            "PauseHotkey": "F2",
            "StopHotkey": "F3",
            "AutoClickerHotkey": "F4",
            "TimersHotkey": "F5",
            "ShowOnPause": 0,
            "IgnoreUpdateVersion": "",
            "FDCWarn": 1,
            "priorityListNumeric": 12345678
        },
        "Status": {# "Version": VersionID,
            "StatusLogReverse": 0,
            "TotalRuntime": 0,
            "SessionRuntime": 0,
            "TotalGatherTime": 0,
            "SessionGatherTime": 0,
            "TotalConvertTime": 0,
            "SessionConvertTime": 0,
            "TotalViciousKills": 0,
            "SessionViciousKills": 0,
            "TotalBossKills": 0,
            "SessionBossKills": 0,
            "TotalBugKills": 0,
            "SessionBugKills": 0,
            "TotalPlantersCollected": 0,
            "SessionPlantersCollected": 0,
            "TotalQuestsComplete": 0,
            "SessionQuestsComplete": 0,
            "TotalDisconnects": 0,
            "SessionDisconnects": 0,
            "DiscordMode": 0,
            "DiscordCheck": 0,
            "Webhook": "",
            "BotToken": "",
            "MainChannelCheck": 1,
            "MainChannelID": "",
            "ReportChannelCheck": 1,
            "ReportChannelID": "",
            "WebhookEasterEgg": 0,
            "ssCheck": 0,
            "ssDebugging": 0,
            "CriticalSSCheck": 1,
            "AmuletSSCheck": 1,
            "MachineSSCheck": 1,
            "BalloonSSCheck": 1,
            "ViciousSSCheck": 1,
            "DeathSSCheck": 1,
            "PlanterSSCheck": 1,
            "HoneySSCheck": 0,
            "criticalCheck": 0,
            "discordUID": "",
            "CriticalErrorPingCheck": 1,
            "DisconnectPingCheck": 1,
            "GameFrozenPingCheck": 1,
            "PhantomPingCheck": 1,
            "UnexpectedDeathPingCheck": 0,
            "EmergencyBalloonPingCheck": 0,
            "commandPrefix": "?",
            "NightAnnouncementCheck": 0,
            "NightAnnouncementName": "",
            "NightAnnouncementPingID": "",
            "NightAnnouncementWebhook": "",
            "DebugLogEnabled": 1,
            "SessionTotalHoney": 0,
            "HoneyAverage": 0,
            "HoneyUpdateSSCheck": 1
        },
        "Gather": {# "Version": VersionID,
            "FieldName1": "Sunflower",
            "FieldName2": "None",
            "FieldName3": "None",
            "FieldPattern1": "Squares",
            "FieldPattern2": "Lines",
            "FieldPattern3": "Lines",
            "FieldPatternSize1": "M",
            "FieldPatternSize2": "M",
            "FieldPatternSize3": "M",
            "FieldPatternReps1": 3,
            "FieldPatternReps2": 3,
            "FieldPatternReps3": 3,
            "FieldPatternShift1": 0,
            "FieldPatternShift2": 0,
            "FieldPatternShift3": 0,
            "FieldPatternInvertFB1": 0,
            "FieldPatternInvertFB2": 0,
            "FieldPatternInvertFB3": 0,
            "FieldPatternInvertLR1": 0,
            "FieldPatternInvertLR2": 0,
            "FieldPatternInvertLR3": 0,
            "FieldUntilMins1": 20,
            "FieldUntilMins2": 15,
            "FieldUntilMins3": 15,
            "FieldUntilPack1": 95,
            "FieldUntilPack2": 95,
            "FieldUntilPack3": 95,
            "FieldReturnType1": "Walk",
            "FieldReturnType2": "Walk",
            "FieldReturnType3": "Walk",
            "FieldSprinklerLoc1": "Center",
            "FieldSprinklerLoc2": "Center",
            "FieldSprinklerLoc3": "Center",
            "FieldSprinklerDist1": 10,
            "FieldSprinklerDist2": 10,
            "FieldSprinklerDist3": 10,
            "FieldRotateDirection1": "None",
            "FieldRotateDirection2": "None",
            "FieldRotateDirection3": "None",
            "FieldRotateTimes1": 1,
            "FieldRotateTimes2": 1,
            "FieldRotateTimes3": 1,
            "FieldDriftCheck1": 1,
            "FieldDriftCheck2": 1,
            "FieldDriftCheck3": 1,
            "CurrentFieldNum": 1
        },
        "Collect": {# "Version": VersionID,
            "ClockCheck": 1,
            "LastClock": 1,
            "MondoBuffCheck": 0,
            "MondoAction": "Buff",
            "MondoLootDirection": "Random",
            "LastMondoBuff": 1,
            "AntPassCheck": 0,
            "AntPassBuyCheck": 0,
            "AntPassAction": "Pass",
            "LastAntPass": 1,
            "RoboPassCheck": 0,
            "LastRoboPass": 1,
            "HoneystormCheck": 0,
            "LastHoneystorm": 1,
            "HoneyDisCheck": 0,
            "LastHoneyDis": 1,
            "TreatDisCheck": 0,
            "LastTreatDis": 1,
            "BlueberryDisCheck": 0,
            "LastBlueberryDis": 1,
            "StrawberryDisCheck": 0,
            "LastStrawberryDis": 1,
            "CoconutDisCheck": 0,
            "LastCoconutDis": 1,
            "RoyalJellyDisCheck": 0,
            "LastRoyalJellyDis": 1,
            "GlueDisCheck": 0,
            "LastGlueDis": 1,
            "LastBlueBoost": 1,
            "LastRedBoost": 1,
            "LastMountainBoost": 1,
            "BeesmasGatherInterruptCheck": 0,
            "StockingsCheck": 0,
            "LastStockings": 1,
            "WreathCheck": 0,
            "LastWreath": 1,
            "FeastCheck": 0,
            "LastFeast": 1,
            "RBPDelevelCheck": 0,
            "LastRBPDelevel": 1,
            "GingerbreadCheck": 0,
            "LastGingerbread": 1,
            "SnowMachineCheck": 0,
            "LastSnowMachine": 1,
            "CandlesCheck": 0,
            "LastCandles": 1,
            "SamovarCheck": 0,
            "LastSamovar": 1,
            "LidArtCheck": 0,
            "LastLidArt": 1,
            "GummyBeaconCheck": 0,
            "LastGummyBeacon": 1,
            "MonsterRespawnTime": 0,
            "BugrunInterruptCheck": 0,
            "BugrunLadybugsCheck": 0,
            "BugrunLadybugsLoot": 0,
            "LastBugrunLadybugs": 1,
            "BugrunRhinoBeetlesCheck": 0,
            "BugrunRhinoBeetlesLoot": 0,
            "LastBugrunRhinoBeetles": 1,
            "BugrunSpiderCheck": 0,
            "BugrunSpiderLoot": 0,
            "LastBugrunSpider": 1,
            "BugrunMantisCheck": 0,
            "BugrunMantisLoot": 0,
            "LastBugrunMantis": 1,
            "BugrunScorpionsCheck": 0,
            "BugrunScorpionsLoot": 0,
            "LastBugrunScorpions": 1,
            "BugrunWerewolfCheck": 0,
            "BugrunWerewolfLoot": 0,
            "LastBugrunWerewolf": 1,
            "TunnelBearCheck": 0,
            "TunnelBearBabyCheck": 0,
            "LastTunnelBear": 1,
            "KingBeetleCheck": 0,
            "KingBeetleBabyCheck": 0,
            "KingBeetleAmuletMode": 1,
            "LastKingBeetle": 1,
            "InputSnailHealth": 100.00,
            "SnailTime": 15,
            "InputChickHealth": 100.00,
            "ChickLevel": 10,
            "ChickTime": 15,
            "StumpSnailCheck": 0,
            "ShellAmuletMode": 1,
            "LastStumpSnail": 1,
            "CommandoCheck": 0,
            "LastCommando": 1,
            "CocoCrabCheck": 0,
            "LastCocoCrab": 1,
            "StingerCheck": 0,
            "StingerPepperCheck": 1,
            "StingerMountainTopCheck": 1,
            "StingerRoseCheck": 1,
            "StingerCactusCheck": 1,
            "StingerSpiderCheck": 1,
            "StingerCloverCheck": 1,
            "StingerDailyBonusCheck": 0,
            "NightLastDetected": 1,
            "VBLastKilled": 1,
            "MondoSecs": 120,
            "NormalMemoryMatchCheck": 0,
            "LastNormalMemoryMatch": 1,
            "MegaMemoryMatchCheck": 0,
            "LastMegaMemoryMatch": 1,
            "ExtremeMemoryMatchCheck": 0,
            "LastExtremeMemoryMatch": 1,
            "NightMemoryMatchCheck": 0,
            "LastNightMemoryMatch": 1,
            "WinterMemoryMatchCheck": 0,
            "LastWinterMemoryMatch": 1,
            "MicroConverterMatchIgnore": 0,
            "SunflowerSeedMatchIgnore": 0,
            "JellyBeanMatchIgnore": 0,
            "RoyalJellyMatchIgnore": 0,
            "TicketMatchIgnore": 0,
            "CyanTrimMatchIgnore": 0,
            "OilMatchIgnore": 0,
            "StrawberryMatchIgnore": 0,
            "CoconutMatchIgnore": 0,
            "TropicalDrinkMatchIgnore": 0,
            "RedExtractMatchIgnore": 0,
            "MagicBeanMatchIgnore": 0,
            "PineappleMatchIgnore": 0,
            "StarJellyMatchIgnore": 0,
            "EnzymeMatchIgnore": 0,
            "BlueExtractMatchIgnore": 0,
            "GumdropMatchIgnore": 0,
            "FieldDiceMatchIgnore": 0,
            "MoonCharmMatchIgnore": 0,
            "BlueberryMatchIgnore": 0,
            "GlitterMatchIgnore": 0,
            "StingerMatchIgnore": 0,
            "TreatMatchIgnore": 0,
            "GlueMatchIgnore": 0,
            "CloudVialMatchIgnore": 0,
            "SoftWaxMatchIgnore": 0,
            "HardWaxMatchIgnore": 0,
            "SwirledWaxMatchIgnore": 0,
            "NightBellMatchIgnore": 0,
            "HoneysuckleMatchIgnore": 0,
            "SuperSmoothieMatchIgnore": 0,
            "SmoothDiceMatchIgnore": 0,
            "NeonberryMatchIgnore": 0,
            "GingerbreadMatchIgnore": 0,
            "SilverEggMatchIgnore": 0,
            "GoldEggMatchIgnore": 0,
            "DiamondEggMatchIgnore": 0,
            "MemoryMatchInterruptCheck": 0,
            "StickerPrinterCheck": 0,
            "LastStickerPrinter": 1,
            "StickerPrinterEgg": "Basic"
        },# "Version": VersionID,
        "Shrine": {
            "ShrineCheck": 0,
            "LastShrine": 1,
            "ShrineAmount1": 0,
            "ShrineAmount2": 0,
            "ShrineItem1": "None",
            "ShrineItem2": "None",
            "ShrineIndex1": 1,
            "ShrineIndex2": 1,
            "ShrineRot": 1
        },
        "Blender": {# "Version": VersionID,
            "BlenderRot": 1,
            "BlenderCheck": 1,
            "TimerInterval": 0,
            "BlenderItem1": "None",
            "BlenderItem2": "None",
            "BlenderItem3": "None",
            "BlenderAmount1": 0,
            "BlenderAmount2": 0,
            "BlenderAmount3": 0,
            "BlenderIndex1": 1,
            "BlenderIndex2": 1,
            "BlenderIndex3": 1,
            "BlenderTime1": 0,
            "BlenderTime2": 0,
            "BlenderTime3": 0,
            "BlenderEnd": 0,
            "LastBlenderRot": 1,
            "BlenderCount1": 0,
            "BlenderCount2": 0,
            "BlenderCount3": 0
        },
        "Boost": {# "Version": VersionID,
            "FieldBoostStacks": 0,
            "FieldBooster1": "None",
            "FieldBooster2": "None",
            "FieldBooster3": "None",
            "BoostChaserCheck": 0,
            "HotbarWhile2": "Never",
            "HotbarWhile3": "Never",
            "HotbarWhile4": "Never",
            "HotbarWhile5": "Never",
            "HotbarWhile6": "Never",
            "HotbarWhile7": "Never",
            "FieldBoosterMins": 15,
            "HotbarTime2": 900,
            "HotbarTime3": 900,
            "HotbarTime4": 900,
            "HotbarTime5": 900,
            "HotbarTime6": 900,
            "HotbarTime7": 900,
            "HotbarMax2": 0,
            "HotbarMax3": 0,
            "HotbarMax4": 0,
            "HotbarMax5": 0,
            "HotbarMax6": 0,
            "HotbarMax7": 0,
            "LastHotkey2": 1,
            "LastHotkey3": 1,
            "LastHotkey4": 1,
            "LastHotkey5": 1,
            "LastHotkey6": 1,
            "LastHotkey7": 1,
            "LastWhirligig": 1,
            "LastEnzymes": 1,
            "LastGlitter": 1,
            "LastMicroConverter": 1,
            "LastGuid": 1,
            "AutoFieldBoostActive": 0,
            "AutoFieldBoostRefresh": 12.5,
            "AFBDiceEnable": 0,
            "AFBGlitterEnable": 0,
            "AFBFieldEnable": 0,
            "AFBDiceHotbar": "None",
            "AFBGlitterHotbar": "None",
            "AFBDiceLimitEnable": 1,
            "AFBGlitterLimitEnable": 1,
            "AFBHoursLimitEnable": 0,
            "AFBDiceLimit": 1,
            "AFBGlitterLimit": 1,
            "AFBHoursLimit": 0.01,
            "FieldLastBoosted": 1,
            "FieldLastBoostedBy": "None",
            "FieldNextBoostedBy": "None",
            "AFBdiceUsed": 0,
            "AFBglitterUsed": 0,
            "BlueFlowerBoosterCheck": 1,
            "BambooBoosterCheck": 1,
            "PineTreeBoosterCheck": 1,
            "DandelionBoosterCheck": 1,
            "SunflowerBoosterCheck": 1,
            "CloverBoosterCheck": 1,
            "SpiderBoosterCheck": 1,
            "PineappleBoosterCheck": 1,
            "CactusBoosterCheck": 1,
            "PumpkinBoosterCheck": 1,
            "MushroomBoosterCheck": 1,
            "StrawberryBoosterCheck": 1,
            "RoseBoosterCheck": 1,
            "PepperBoosterCheck": 1,
            "StumpBoosterCheck": 1,
            "CoconutBoosterCheck": 0,
            "StickerStackCheck": 0,
            "LastStickerStack": 1,
            "StickerStackItem": "Tickets",
            "StickerStackMode": 0,
            "StickerStackTimer": 900,
            "StickerStackHive": 0,
            "StickerStackCub": 0,
            "StickerStackVoucher": 0
        },
        "Quests": {# "Version": VersionID,
            "QuestGatherMins": 5,
            "QuestGatherReturnBy": "Walk",
            "QuestBoostCheck": 0,
            "PolarQuestCheck": 0,
            "PolarQuestGatherInterruptCheck": 1,
            "PolarQuestProgress": "Unknown",
            "HoneyQuestCheck": 0,
            "HoneyQuestProgress": "Unknown",
            "BlackQuestCheck": 0,
            "BlackQuestProgress": "Unknown",
            "LastBlackQuest": 1,
            "BrownQuestCheck": 0,
            "BrownQuestProgress": "Unknown",
            "LastBrownQuest": 1,
            "BuckoQuestCheck": 0,
            "BuckoQuestGatherInterruptCheck": 1,
            "BuckoQuestProgress": "Unknown",
            "RileyQuestCheck": 0,
            "RileyQuestGatherInterruptCheck": 1,
            "RileyQuestProgress": "Unknown"
        },
        "Planters": {# "Version": VersionID,
            "LastComfortingField": "None",
            "LastRefreshingField": "None",
            "LastSatisfyingField": "None",
            "LastMotivatingField": "None",
            "LastInvigoratingField": "None",
            "MPlanterGatherA": 0,
            "MPlanterGather1": 0,
            "MPlanterGather2": 0,
            "MPlanterGather3": 0,
            "MPlanterHold1": 0,
            "MPlanterHold2": 0,
            "MPlanterHold3": 0,
            "MPlanterSmoking1": 0,
            "MPlanterSmoking2": 0,
            "MPlanterSmoking3": 0,
            "MPuffModeA": 0,
            "MPuffMode1": 0,
            "MPuffMode2": 0,
            "MPuffMode3": 0,
            "MConvertFullBagHarvest": 0,
            "MGatherPlanterLoot": 1,
            "PlanterHarvestNow1": 0,
            "PlanterHarvestNow2": 0,
            "PlanterHarvestNow3": 0,
            "PlanterSS1": 0,
            "PlanterSS2": 0,
            "PlanterSS3": 0,
            "LastPlanterGatherSlot": 3,
            "PlanterName1": "None",
            "PlanterName2": "None",
            "PlanterName3": "None",
            "PlanterField1": "None",
            "PlanterField2": "None",
            "PlanterField3": "None",
            "PlanterHarvestTime1": 2147483647,
            "PlanterHarvestTime2": 2147483647,
            "PlanterHarvestTime3": 2147483647,
            "PlanterNectar1": "None",
            "PlanterNectar2": "None",
            "PlanterNectar3": "None",
            "PlanterEstPercent1": 0,
            "PlanterEstPercent2": 0,
            "PlanterEstPercent3": 0,
            "PlanterGlitter1": 0,
            "PlanterGlitter2": 0,
            "PlanterGlitter3": 0,
            "PlanterGlitterC1": 0,
            "PlanterGlitterC2": 0,
            "PlanterGlitterC3": 0,
            "PlanterHarvestFull1": "",
            "PlanterHarvestFull2": "",
            "PlanterHarvestFull3": "",
            "PlanterManualCycle1": 1,
            "PlanterManualCycle2": 1,
            "PlanterManualCycle3": 1,
            "dayOrNight": "Day",
            "PlanterMode": 0,
            "nPreset": "Blue",
            "MaxAllowedPlanters": 3,
            "n1priority": "Comforting",
            "n2priority": "Motivating",
            "n3priority": "Satisfying",
            "n4priority": "Refreshing",
            "n5priority": "Invigorating",
            "n1minPercent": 70,
            "n2minPercent": 80,
            "n3minPercent": 80,
            "n4minPercent": 80,
            "n5minPercent": 40,
            "HarvestInterval": 2,
            "AutomaticHarvestInterval": 0,
            "HarvestFullGrown": 0,
            "GotoPlanterField": 0,
            "GatherFieldSipping": 0,
            "ConvertFullBagHarvest": 0,
            "GatherPlanterLoot": 1,
            "PlasticPlanterCheck": 1,
            "CandyPlanterCheck": 1,
            "BlueClayPlanterCheck": 1,
            "RedClayPlanterCheck": 1,
            "TackyPlanterCheck": 1,
            "PesticidePlanterCheck": 1,
            "HeatTreatedPlanterCheck": 0,
            "HydroponicPlanterCheck": 0,
            "PetalPlanterCheck": 0,
            "PaperPlanterCheck": 0,
            "TicketPlanterCheck": 0,
            "PlanterOfPlentyCheck": 0,
            "BambooFieldCheck": 0,
            "BlueFlowerFieldCheck": 1,
            "CactusFieldCheck": 1,
            "CloverFieldCheck": 1,
            "CoconutFieldCheck": 0,
            "DandelionFieldCheck": 1,
            "MountainTopFieldCheck": 0,
            "MushroomFieldCheck": 0,
            "PepperFieldCheck": 1,
            "PineTreeFieldCheck": 1,
            "PineappleFieldCheck": 1,
            "PumpkinFieldCheck": 0,
            "RoseFieldCheck": 1,
            "SpiderFieldCheck": 1,
            "StrawberryFieldCheck": 1,
            "StumpFieldCheck": 0,
            "SunflowerFieldCheck": 1,
            "TimerGuiTransparency": 0,
            "TimerX": 150,
            "TimerY": 150,
            "TimersOpen": 0
        }
    }
# Import the patterns and paths
    if os.path.exists(inipath):
        ini_config = configparser.ConfigParser()
        ini_config.read(inipath)
        for section, options in config.items():
            if ini_config.has_section(section):
                for key in options:
                    if ini_config.has_option(section, key):
                        value = ini_config.get(section, key)
                        try:
                            options[key] = int(value)
                        except ValueError:
                            try:
                                options[key] = float(value)
                            except ValueError:
                                options[key] = value

    # Write the configuration back to the INI file
    ini_config = configparser.ConfigParser()
    for section, options in config.items():
        ini_config[section] = {k: str(v) for k, v in options.items()}
    with open(inipath, 'w') as configfile:
        ini_config.write(configfile)

# Call the function to import configuration
nm_import_config()

# Define nectar and planter names
nectarnames = ["Comforting", "Refreshing", "Satisfying", "Motivating", "Invigorating"]
planternames = ["PlasticPlanter", "CandyPlanter", "BlueClayPlanter", "RedClayPlanter", "TackyPlanter", "PesticidePlanter", "HeatTreatedPlanter", "HydroponicPlanter", "PetalPlanter", "PlanterOfPlenty", "PaperPlanter", "TicketPlanter"]
fieldnames = ["dandelion", "sunflower", "mushroom", "blueflower", "clover", "strawberry", "spider", "bamboo", "pineapple", "stump", "cactus", "pumpkin", "pinetree", "rose", "mountaintop", "pepper", "coconut"]

# Define nectar fields

ComfortingFields = ["Dandelion", "Bamboo", "Pine Tree"]
RefreshingFields = ["Coconut", "Strawberry", "Blue Flower"]
SatisfyingFields = ["Pineapple", "Sunflower", "Pumpkin"]
MotivatingFields = ["Stump", "Spider", "Mushroom", "Rose"]
InvigoratingFields = ["Pepper", "Mountain Top", "Clover", "Cactus"]

##############################################################################
# Planter Configurations
# Each planter is a dict with keys: name, nectar_bonus, speed_bonus, hours
# Ordered from best to worst based on nectar and speed bonuses
##############################################################################
# Bamboo Planters
BambooPlanters = [
    {"name": "HydroponicPlanter", "nectar_bonus": 1.4, "speed_bonus": 1.375, "hours": 8.73},
    {"name": "PetalPlanter", "nectar_bonus": 1.5, "speed_bonus": 1.125, "hours": 12.45},
    {"name": "PesticidePlanter", "nectar_bonus": 1, "speed_bonus": 1.6, "hours": 6.25},
    {"name": "PlanterOfPlenty", "nectar_bonus": 1.5, "speed_bonus": 1, "hours": 16},
    {"name": "BlueClayPlanter", "nectar_bonus": 1.2, "speed_bonus": 1.1875, "hours": 5.06},
    {"name": "TackyPlanter", "nectar_bonus": 1.25, "speed_bonus": 1, "hours": 8},
    {"name": "PlasticPlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 2},
    {"name": "CandyPlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 4},
    {"name": "RedClayPlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 6},
    {"name": "HeatTreatedPlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 12},
    {"name": "PaperPlanter", "nectar_bonus": 0.75, "speed_bonus": 1, "hours": 1},
    {"name": "TicketPlanter", "nectar_bonus": 2, "speed_bonus": 1, "hours": 2}

]

# Blue Flower Planters

BlueFlowerPlanters = [
    {"name": "HydroponicPlanter", "nectar_bonus": 1.4, "speed_bonus": 1.345, "hours": 8.93},
    {"name": "PlanterOfPlenty", "nectar_bonus": 1.5, "speed_bonus": 1, "hours": 16},
    {"name": "TackyPlanter", "nectar_bonus": 1, "speed_bonus": 1.5, "hours": 5.34},
    {"name": "BlueClayPlanter", "nectar_bonus": 1.2, "speed_bonus": 1.1725, "hours": 5.12},
    {"name": "PetalPlanter", "nectar_bonus": 1, "speed_bonus": 1.155, "hours": 12.13},
    {"name": "PlasticPlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 2},
    {"name": "CandyPlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 4},
    {"name": "RedClayPlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 6},
    {"name": "PesticidePlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 10},
    {"name": "HeatTreatedPlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 12},
    {"name": "PaperPlanter", "nectar_bonus": 0.75, "speed_bonus": 1, "hours": 1},
    {"name": "TicketPlanter", "nectar_bonus": 2, "speed_bonus": 1, "hours": 2}
]

# Cactus Planters

CactusPlanters = [
    {"name": "HeatTreatedPlanter", "nectar_bonus": 1.4, "speed_bonus": 1.215, "hours": 9.88},
    {"name": "PlanterOfPlenty", "nectar_bonus": 1.5, "speed_bonus": 1, "hours": 16},
    {"name": "RedClayPlanter", "nectar_bonus": 1.2, "speed_bonus": 1.1075, "hours": 5.42},
    {"name": "HydroponicPlanter", "nectar_bonus": 1, "speed_bonus": 1.25, "hours": 9.6},
    {"name": "BlueClayPlanter", "nectar_bonus": 1, "speed_bonus": 1.125, "hours": 5.34},
    {"name": "PetalPlanter", "nectar_bonus": 1, "speed_bonus": 1.035, "hours": 13.53},
    {"name": "PlasticPlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 2},
    {"name": "CandyPlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 4},
    {"name": "TackyPlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 8},
    {"name": "PesticidePlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 10},
    {"name": "PaperPlanter", "nectar_bonus": 0.75, "speed_bonus": 1, "hours": 1},
    {"name": "TicketPlanter", "nectar_bonus": 2, "speed_bonus": 1, "hours": 2}
]

# Clover Planters

CloverPlanters = [
    {"name": "HeatTreatedPlanter", "nectar_bonus": 1.4, "speed_bonus": 1.17, "hours": 10.26},
    {"name": "TackyPlanter", "nectar_bonus": 1, "speed_bonus": 1.5, "hours": 5.34},
    {"name": "PlanterOfPlenty", "nectar_bonus": 1.5, "speed_bonus": 1, "hours": 16},
    {"name": "RedClayPlanter", "nectar_bonus": 1.2, "speed_bonus": 1.085, "hours": 5.53},
    {"name": "HydroponicPlanter", "nectar_bonus": 1, "speed_bonus": 1.17, "hours": 10.57},
    {"name": "PetalPlanter", "nectar_bonus": 1, "speed_bonus": 1.16, "hours": 12.07},
    {"name": "BlueClayPlanter", "nectar_bonus": 1, "speed_bonus": 1.085, "hours": 5.53},
    {"name": "PlasticPlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 2},
    {"name": "CandyPlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 4},
    {"name": "PesticidePlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 10},
    {"name": "PaperPlanter", "nectar_bonus": 0.75, "speed_bonus": 1, "hours": 1},
    {"name": "TicketPlanter", "nectar_bonus": 2, "speed_bonus": 1, "hours": 2}
]

# Coconut Planters

CoconutPlanters = [
    {"name": "PlanterOfPlenty", "nectar_bonus": 1.5, "speed_bonus": 1.5, "hours": 10.67},
    {"name": "CandyPlanter", "nectar_bonus": 1, "speed_bonus": 1.5, "hours": 2.67},
    {"name": "PetalPlanter", "nectar_bonus": 1, "speed_bonus": 1.447, "hours": 9.68},
    {"name": "HydroponicPlanter", "nectar_bonus": 1.4, "speed_bonus": 1.023, "hours": 11.74},
    {"name": "BlueClayPlanter", "nectar_bonus": 1.2, "speed_bonus": 1.0115, "hours": 5.94},
    {"name": "HeatTreatedPlanter", "nectar_bonus": 1, "speed_bonus": 1.03, "hours": 11.66},
    {"name": "RedClayPlanter", "nectar_bonus": 1, "speed_bonus": 1.015, "hours": 5.92},
    {"name": "PlasticPlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 2},
    {"name": "TackyPlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 8},
    {"name": "PesticidePlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 10},
    {"name": "PaperPlanter", "nectar_bonus": 0.75, "speed_bonus": 1, "hours": 1},
    {"name": "TicketPlanter", "nectar_bonus": 2, "speed_bonus": 1, "hours": 2}
]

# Dandelion Planters

DandelionPlanters = [
    {"name": "PetalPlanter", "nectar_bonus": 1.5, "speed_bonus": 1.4235, "hours": 9.84},
    {"name": "TackyPlanter", "nectar_bonus": 1.25, "speed_bonus": 1.5, "hours": 5.33},
    {"name": "PlanterOfPlenty", "nectar_bonus": 1.5, "speed_bonus": 1, "hours": 16},
    {"name": "HydroponicPlanter", "nectar_bonus": 1.4, "speed_bonus": 1.0485, "hours": 11.45},
    {"name": "BlueClayPlanter", "nectar_bonus": 1.2, "speed_bonus": 1.02425, "hours": 5.86},
    {"name": "HeatTreatedPlanter", "nectar_bonus": 1, "speed_bonus": 1.028, "hours": 11.68},
    {"name": "RedClayPlanter", "nectar_bonus": 1, "speed_bonus": 1.014, "hours": 5.92},
    {"name": "PlasticPlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 2},
    {"name": "CandyPlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 4},
    {"name": "PesticidePlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 10},
    {"name": "PaperPlanter", "nectar_bonus": 0.75, "speed_bonus": 1, "hours": 1},
    {"name": "TicketPlanter", "nectar_bonus": 2, "speed_bonus": 1, "hours": 2}
]

# Mountain Top Planters

MountainTopPlanters = [
    {"name": "PlanterOfPlenty", "nectar_bonus": 1.5, "speed_bonus": 1.5, "hours": 10.67},
    {"name": "HeatTreatedPlanter", "nectar_bonus": 1.4, "speed_bonus": 1.25, "hours": 9.6},
    {"name": "RedClayPlanter", "nectar_bonus": 1.2, "speed_bonus": 1.125, "hours": 5.34},
    {"name": "HydroponicPlanter", "nectar_bonus": 1, "speed_bonus": 1.25, "hours": 9.6},
    {"name": "BlueClayPlanter", "nectar_bonus": 1, "speed_bonus": 1.125, "hours": 5.34},
    {"name": "PlasticPlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 2},
    {"name": "CandyPlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 4},
    {"name": "TackyPlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 8},
    {"name": "PesticidePlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 10},
    {"name": "PetalPlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 14},
    {"name": "PaperPlanter", "nectar_bonus": 0.75, "speed_bonus": 1, "hours": 1},
    {"name": "TicketPlanter", "nectar_bonus": 2, "speed_bonus": 1, "hours": 2}
]

# Mushroom Planters

MushroomPlanters = [
    {"name": "HeatTreatedPlanter", "nectar_bonus": 1.4, "speed_bonus": 1.3425, "hours": 8.94},
    {"name": "TackyPlanter", "nectar_bonus": 1, "speed_bonus": 1.5, "hours": 5.34},
    {"name": "PlanterOfPlenty", "nectar_bonus": 1.5, "speed_bonus": 1, "hours": 16},
    {"name": "PesticidePlanter", "nectar_bonus": 1.3, "speed_bonus": 1, "hours": 10},
    {"name": "CandyPlanter", "nectar_bonus": 1.2, "speed_bonus": 1, "hours": 4},
    {"name": "RedClayPlanter", "nectar_bonus": 1, "speed_bonus": 1.17125, "hours": 5.12},
    {"name": "PetalPlanter", "nectar_bonus": 1, "speed_bonus": 1.1575, "hours": 12.1},
    {"name": "PlasticPlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 2},
    {"name": "BlueClayPlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 6},
    {"name": "HydroponicPlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 12},
    {"name": "PaperPlanter", "nectar_bonus": 0.75, "speed_bonus": 1, "hours": 1},
    {"name": "TicketPlanter", "nectar_bonus": 2, "speed_bonus": 1, "hours": 2}
]

# Pepper Planters

PepperPlanters = [
    {"name": "PlanterOfPlenty", "nectar_bonus": 1.5, "speed_bonus": 1.5, "hours": 10.67},
    {"name": "HeatTreatedPlanter", "nectar_bonus": 1.4, "speed_bonus": 1.46, "hours": 8.22},
    {"name": "RedClayPlanter", "nectar_bonus": 1.2, "speed_bonus": 1.23, "hours": 4.88},
    {"name": "PetalPlanter", "nectar_bonus": 1, "speed_bonus": 1.04, "hours": 13.47},
    {"name": "PlasticPlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 2},
    {"name": "CandyPlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 4},
    {"name": "BlueClayPlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 6},
    {"name": "TackyPlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 8},
    {"name": "PesticidePlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 10},
    {"name": "HydroponicPlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 12},
    {"name": "PaperPlanter", "nectar_bonus": 0.75, "speed_bonus": 1, "hours": 1},
    {"name": "TicketPlanter", "nectar_bonus": 2, "speed_bonus": 1, "hours": 2}
]

# Pine Tree Planters

PineTreePlanters = [
    {"name": "HydroponicPlanter", "nectar_bonus": 1.4, "speed_bonus": 1.42, "hours": 8.46},
    {"name": "PetalPlanter", "nectar_bonus": 1.5, "speed_bonus": 1.08, "hours": 12.97},
    {"name": "PlanterOfPlenty", "nectar_bonus": 1.5, "speed_bonus": 1, "hours": 16},
    {"name": "BlueClayPlanter", "nectar_bonus": 1.2, "speed_bonus": 1.21, "hours": 4.96},
    {"name": "TackyPlanter", "nectar_bonus": 1.25, "speed_bonus": 1, "hours": 8},
    {"name": "PlasticPlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 2},
    {"name": "CandyPlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 4},
    {"name": "RedClayPlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 6},
    {"name": "PesticidePlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 10},
    {"name": "HeatTreatedPlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 12},
    {"name": "PaperPlanter", "nectar_bonus": 0.75, "speed_bonus": 1, "hours": 1},
    {"name": "TicketPlanter", "nectar_bonus": 2, "speed_bonus": 1, "hours": 2}
]

# Pineapple Planters

PineapplePlanters = [
    {"name": "PetalPlanter", "nectar_bonus": 1.5, "speed_bonus": 1.445, "hours": 9.69},
    {"name": "CandyPlanter", "nectar_bonus": 1, "speed_bonus": 1.5, "hours": 2.67},
    {"name": "PlanterOfPlenty", "nectar_bonus": 1.5, "speed_bonus": 1, "hours": 16},
    {"name": "PesticidePlanter", "nectar_bonus": 1.3, "speed_bonus": 1, "hours": 10},
    {"name": "TackyPlanter", "nectar_bonus": 1.25, "speed_bonus": 1, "hours": 8},
    {"name": "RedClayPlanter", "nectar_bonus": 1.2, "speed_bonus": 1.015, "hours": 5.92},
    {"name": "HeatTreatedPlanter", "nectar_bonus": 1, "speed_bonus": 1.03, "hours": 11.66},
    {"name": "HydroponicPlanter", "nectar_bonus": 1, "speed_bonus": 1.025, "hours": 11.71},
    {"name": "BlueClayPlanter", "nectar_bonus": 1, "speed_bonus": 1.0125, "hours": 5.93},
    {"name": "PlasticPlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 2},
    {"name": "PaperPlanter", "nectar_bonus": 0.75, "speed_bonus": 1, "hours": 1},
    {"name": "TicketPlanter", "nectar_bonus": 2, "speed_bonus": 1, "hours": 2}
]

# Pumpkin Planters

PumpkinPlanters = [
    {"name": "PetalPlanter", "nectar_bonus": 1.5, "speed_bonus": 1.285, "hours": 10.9},
    {"name": "PlanterOfPlenty", "nectar_bonus": 1.5, "speed_bonus": 1, "hours": 16},
    {"name": "PesticidePlanter", "nectar_bonus": 1.3, "speed_bonus": 1, "hours": 10},
    {"name": "RedClayPlanter", "nectar_bonus": 1.2, "speed_bonus": 1.055, "hours": 5.69},
    {"name": "TackyPlanter", "nectar_bonus": 1.25, "speed_bonus": 1, "hours": 8},
    {"name": "HeatTreatedPlanter", "nectar_bonus": 1, "speed_bonus": 1.11, "hours": 10.82},
    {"name": "HydroponicPlanter", "nectar_bonus": 1, "speed_bonus": 1.105, "hours": 10.86},
    {"name": "BlueClayPlanter", "nectar_bonus": 1, "speed_bonus": 1.0525, "hours": 5.71},
    {"name": "PlasticPlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 2},
    {"name": "CandyPlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 4},
    {"name": "PaperPlanter", "nectar_bonus": 0.75, "speed_bonus": 1, "hours": 1},
    {"name": "TicketPlanter", "nectar_bonus": 2, "speed_bonus": 1, "hours": 2}
]

# Rose Planters

RosePlanters = [
    {"name": "HeatTreatedPlanter", "nectar_bonus": 1.4, "speed_bonus": 1.41, "hours": 8.52},
    {"name": "PlanterOfPlenty", "nectar_bonus": 1.5, "speed_bonus": 1, "hours": 16},
    {"name": "PesticidePlanter", "nectar_bonus": 1.3, "speed_bonus": 1, "hours": 10},
    {"name": "RedClayPlanter", "nectar_bonus": 1, "speed_bonus": 1.205, "hours": 4.98},
    {"name": "CandyPlanter", "nectar_bonus": 1.2, "speed_bonus": 1, "hours": 4},
    {"name": "PetalPlanter", "nectar_bonus": 1, "speed_bonus": 1.09, "hours": 12.85},
    {"name": "PlasticPlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 2},
    {"name": "BlueClayPlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 6},
    {"name": "TackyPlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 8},
    {"name": "HydroponicPlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 12},
    {"name": "PaperPlanter", "nectar_bonus": 0.75, "speed_bonus": 1, "hours": 1},
    {"name": "TicketPlanter", "nectar_bonus": 2, "speed_bonus": 1, "hours": 2}
]

# Spider Planters

SpiderPlanters = [
    {"name": "PesticidePlanter", "nectar_bonus": 1.3, "speed_bonus": 1.6, "hours": 6.25},
    {"name": "PetalPlanter", "nectar_bonus": 1, "speed_bonus": 1.5, "hours": 9.33},
    {"name": "PlanterOfPlenty", "nectar_bonus": 1.5, "speed_bonus": 1, "hours": 16},
    {"name": "HeatTreatedPlanter", "nectar_bonus": 1.4, "speed_bonus": 1, "hours": 12},
    {"name": "CandyPlanter", "nectar_bonus": 1.2, "speed_bonus": 1, "hours": 4},
    {"name": "PlasticPlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 2},
    {"name": "BlueClayPlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 6},
    {"name": "RedClayPlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 6},
    {"name": "TackyPlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 8},
    {"name": "HydroponicPlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 12},
    {"name": "PaperPlanter", "nectar_bonus": 0.75, "speed_bonus": 1, "hours": 1},
    {"name": "TicketPlanter", "nectar_bonus": 2, "speed_bonus": 1, "hours": 2}
]

# Strawberry Planters

StrawberryPlanters = [
    {"name": "PesticidePlanter", "nectar_bonus": 1, "speed_bonus": 1.6, "hours": 6.25},
    {"name": "CandyPlanter", "nectar_bonus": 1, "speed_bonus": 1.5, "hours": 2.67},
    {"name": "PlanterOfPlenty", "nectar_bonus": 1.5, "speed_bonus": 1, "hours": 16},
    {"name": "HydroponicPlanter", "nectar_bonus": 1.4, "speed_bonus": 1, "hours": 12},
    {"name": "HeatTreatedPlanter", "nectar_bonus": 1, "speed_bonus": 1.345, "hours": 8.93},
    {"name": "BlueClayPlanter", "nectar_bonus": 1.2, "speed_bonus": 1, "hours": 6},
    {"name": "RedClayPlanter", "nectar_bonus": 1, "speed_bonus": 1.1725, "hours": 5.12},
    {"name": "PetalPlanter", "nectar_bonus": 1, "speed_bonus": 1.155, "hours": 12.13},
    {"name": "PlasticPlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 2},
    {"name": "TackyPlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 8},
    {"name": "PaperPlanter", "nectar_bonus": 0.75, "speed_bonus": 1, "hours": 1},
    {"name": "TicketPlanter", "nectar_bonus": 2, "speed_bonus": 1, "hours": 2}
]

# Stump Planters

StumpPlanters = [
    {"name": "PlanterOfPlenty", "nectar_bonus": 1.5, "speed_bonus": 1.5, "hours": 10.67},
    {"name": "HeatTreatedPlanter", "nectar_bonus": 1.4, "speed_bonus": 1.03, "hours": 11.65},
    {"name": "HydroponicPlanter", "nectar_bonus": 1, "speed_bonus": 1.375, "hours": 8.73},
    {"name": "PesticidePlanter", "nectar_bonus": 1.3, "speed_bonus": 1, "hours": 10},
    {"name": "CandyPlanter", "nectar_bonus": 1.2, "speed_bonus": 1, "hours": 4},
    {"name": "BlueClayPlanter", "nectar_bonus": 1, "speed_bonus": 1.1875, "hours": 5.06},
    {"name": "PetalPlanter", "nectar_bonus": 1, "speed_bonus": 1.095, "hours": 12.79},
    {"name": "RedClayPlanter", "nectar_bonus": 1, "speed_bonus": 1.015, "hours": 5.92},
    {"name": "PlasticPlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 2},
    {"name": "TackyPlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 8},
    {"name": "PaperPlanter", "nectar_bonus": 0.75, "speed_bonus": 1, "hours": 1},
    {"name": "TicketPlanter", "nectar_bonus": 2, "speed_bonus": 1, "hours": 2}
]

# Sunflower Planters

SunflowerPlanters = [
    {"name": "PetalPlanter", "nectar_bonus": 1.5, "speed_bonus": 1.3415, "hours": 10.44},
    {"name": "TackyPlanter", "nectar_bonus": 1.25, "speed_bonus": 1.5, "hours": 5.34},
    {"name": "PlanterOfPlenty", "nectar_bonus": 1.5, "speed_bonus": 1, "hours": 16},
    {"name": "PesticidePlanter", "nectar_bonus": 1.3, "speed_bonus": 1, "hours": 10},
    {"name": "RedClayPlanter", "nectar_bonus": 1.2, "speed_bonus": 1.04175, "hours": 5.76},
    {"name": "HeatTreatedPlanter", "nectar_bonus": 1, "speed_bonus": 1.0835, "hours": 11.08},
    {"name": "HydroponicPlanter", "nectar_bonus": 1, "speed_bonus": 1.075, "hours": 11.17},
    {"name": "BlueClayPlanter", "nectar_bonus": 1, "speed_bonus": 1.0375, "hours": 5.79},
    {"name": "PlasticPlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 2},
    {"name": "CandyPlanter", "nectar_bonus": 1, "speed_bonus": 1, "hours": 4},
    {"name": "PaperPlanter", "nectar_bonus": 0.75, "speed_bonus": 1, "hours": 1},
    {"name": "TicketPlanter", "nectar_bonus": 2, "speed_bonus": 1, "hours": 2}
]

###############
# Quest Data
###############

QuestBarGapSize = 10
QuestBarSize = 50
QuestBarInset = 16

# Quest Data for Bears

PolarBear = {
    "Aromatic Pie": [
        [3, "Kill", "Mantis"],
        [4, "Kill", "Ladybugs"],
        [1, "Collect", "Rose"],
        [2, "Collect", "Pine Tree"]
    ],
    "Beetle Brew": [
        [3, "Kill", "Ladybugs"],
        [4, "Kill", "RhinoBeetles"],
        [1, "Collect", "Pineapple"],
        [2, "Collect", "Dandelion"]
    ],
    "Candied Beetles": [
        [3, "Kill", "RhinoBeetles"],
        [1, "Collect", "Strawberry"],
        [2, "Collect", "Blue Flower"]
    ],
    "Exotic Salad": [
        [1, "Collect", "Cactus"],
        [2, "Collect", "Rose"],
        [3, "Collect", "Blue Flower"],
        [4, "Collect", "Clover"]
    ],
    "Extreme Stir-Fry": [
        [6, "Kill", "Werewolf"],
        [5, "Kill", "Scorpions"],
        [4, "Kill", "Spider"],
        [1, "Collect", "Cactus"],
        [2, "Collect", "Bamboo"],
        [3, "Collect", "Dandelion"]
    ],
    "High Protein": [
        [4, "Kill", "Spider"],
        [3, "Kill", "Scorpions"],
        [2, "Kill", "Mantis"],
        [1, "Collect", "Sunflower"]
    ],
    "Ladybug Poppers": [
        [2, "Kill", "Ladybugs"],
        [1, "Collect", "Blue Flower"]
    ],
    "Mantis Meatballs": [
        [2, "Kill", "Mantis"],
        [1, "Collect", "Pine Tree"]
    ],
    "Prickly Pears": [
        [1, "Collect", "Cactus"]
    ],
    "Pumpkin Pie": [
        [3, "Kill", "Mantis"],
        [1, "Collect", "Pumpkin"],
        [2, "Collect", "Sunflower"]
    ],
    "Scorpion Salad": [
        [2, "Kill", "Scorpions"],
        [1, "Collect", "Rose"]
    ],
    "Spiced Kebab": [
        [3, "Kill", "Werewolf"],
        [1, "Collect", "Clover"],
        [2, "Collect", "Bamboo"]
    ],
    "Spider Pot-Pie": [
        [2, "Kill", "Spider"],
        [1, "Collect", "Mushroom"]
    ],
    "Spooky Stew": [
        [4, "Kill", "Werewolf"],
        [3, "Kill", "Spider"],
        [1, "Collect", "Spider"],
        [2, "Collect", "Mushroom"]
    ],
    "Strawberry Skewers": [
        [3, "Kill", "Scorpions"],
        [1, "Collect", "Strawberry"],
        [2, "Collect", "Bamboo"]
    ],
    "Teriyaki Jerky": [
        [3, "Kill", "Werewolf"],
        [1, "Collect", "Pineapple"],
        [2, "Collect", "Spider"]
    ],
    "Thick Smoothie": [
        [1, "Collect", "Strawberry"],
        [2, "Collect", "Pumpkin"]
    ],
    "Trail Mix": [
        [1, "Collect", "Sunflower"],
        [2, "Collect", "Pineapple"]
    ]
}

BlackBear = { # Story quests
    "Sunflower Start": [
        [1, "Collect", "Sunflower"]
    ],
    "Dandilion Deed": [
        [1, "Collect", "Dandelion"]
    ],
    "Pollen Fetcher": [
        [1, "Collect", "Pollen"]
    ],
    "Red Request": [
        [1, "Collect", "Red"]
    ],
    "Into The Blue": [
        [1, "Collect", "Blue"]
    ],
    "Variety Fetcher": [
        [1, "Collect", "Red"],
        [2, "Collect", "Blue"],
        [3, "Collect", "White"]
    ],

    #congrats you got Silver Egg

    "Bamboo Boogie": [
        [1, "Collect", "Bamboo"]
    ],
    "Red Request 2": [
        [1, "Collect", "Red"]
    ],
    "Cobweb Sweeper": [
        [1, "Collect", "Spider"]
    ],
    "Leisure Loot": [
        [1, "Collect", "Sunflower"],
        [2, "Collect", "Dandelion"],
        [3, "Collect", "Mushroom"],
        [4, "Collect", "Blue Flower"]
    ],
    "White Pollen Wrangler": [
        [1, "Collect", "White"]
    ],
    "Pineapple Picking": [
        [1, "Collect", "Pineapple"]
    ],
    "Pollen Fetcher 2": [
        [1, "Collect", "Pollen"]
    ],
    "Weed Wacker": [
        [1, "Collect", "Strawberry"],
        [2, "Collect", "Bamboo"],
        [3, "Collect", "Clover"]
    ],
    "Red + Blue = Gold": [
        [1, "Collect", "Red"],
        [2, "Collect", "Blue"]
    ],

    #congrats you got a golden egg

    "Colorless Collection" : [
        [1, "Collect", "White"]
    ],
    "Spirit of Springtime": [
        [1, "Collect", "Strawberry"],
        [2,"Collect", "Sunflower"],
    ],
    "Weed Wacker 2": [
        [1, "Collect", "Dandelion"],
        [2, "Collect", "Bamboo"],
    ],
    "Pollen Fetcher 3": [
        [1, "Collect", "Pollen"]
    ],
    "Lucky Landscaping": [
        [1, "Collect", "Clover"],
    ],
    "Azure Adventure": {
        [1, "Collect", "Blue"],
    },
    "Pink Pineapples": [
        [1, "Collect", "Pineapple"],
        [2, "Collect", "Red"]
    ],
    "Blue Mushrooms": [
        [1, "Collect", "Blue"],
        [2, "Collect", "Mushroom"]
    ],
    "Cobweb Sweeper 2": [
        [1, "Collect", "Spider"],
    ],
    "Rojo-A-Go-Go": [
        [1, "Collect", "Red"],
        [2, "Collect", "Cactus"]
    ],
    "Pumpkin Plower": [
        [1, "Collect", "Pumpkin"],
    ],
    "Pollen Fetcher 4": [
        [1, "Collect", "Pollen"]
    ],
    "Bouncing Around Biomes": [
        [1, "Collect", "Pine tree"],
        [2, "Collect", "Cactus"],
    ],
    "Blue Pineapples": [
        [1, "Collect", "Blue"],
        [2, "Collect", "Pineapple"]
    ],
    "Rose Request": [
        [1, "Collect", "Rose"]
    ],
    "Search For The White Clover": [
        [1, "Collect", "White"],
    ],
    "Stomping Grounds": [
        [1, "Collect", "Sunflower"],
        [2, "Collect", "Dandelion"],
        [3, "Collect", "Mushroom"],
        [4, "Collect", "Blue Flower"]
    ],
    "Collecting Cliffside": [
        [1, "Collect", "Strawberry"],
        [2, "Collect", "Spider"],
        [3, "Collect", "Bamboo"]
    ],
    "Mountain Meandering": [
        [1, "Collect", "Rose"],
        [2, "Collect", "Pine tree"],
        [3, "Collect", "Pumpkin"],
        [4, "Collect", "Cactus"],
        [5, "Collect", "Pineapple"]
    ],
    "Quest Of Legends": [
        [1, "Collect", "White"],
        [2, "Collect", "Red"],
        [3, "Collect", "Blue"],

# congrats you got a diamond egg


    ],
    "High Altitude": [
        [1, "Collect", "Clover"],
        [2, "Collect", "Mountain Top"],
    ],
    "Blissfully Blue": [
        [1, "Collect", "Blue Flower"],
        [2, "Collect", "Pineapple"],
        [3, "Collect", "Blue"],
    ],
    "Rouge Round-up": [
        [1, "Collect", "Red"],
        [2, "Collect", "Rose"],
        [3, "Collect", "Strawberry"],
        [4, "Collect", "Cactus"],
    ],
    "White As Snow": [
        [1, "Collect", "White"],
        [2, "Collect", "Pineapple"],
        [3, "Collect", "Spider"],
        [4, "Collect", "Dandelion"]
    ],
    "Solo On The Stump": [
        [1, "Collect", "Stump"],
    ],
    "Colorful Craving": [
        [1, "Collect", "Red"],
        [2, "Collect", "Blue"],
        [3, "Collect", "Pine Tree"],
        [4, "Collect", "Mushroom"]
    ],
    "Pumpkins, Please!": [
        [1, "Collect", "Pumpkin"],
    ]
    "Smorgasbord": [
        [1, "Collect", "Sunflower"],
        [2, "Collect", "Clover"],
        [3, "Collect", "Bamboo"],
        [4, "Collect", "Pine apple"],
        [5, "Collect", "Cactus"],
        [6, "Collect", "Rose"],
        [7, "Collect", "Mountain Top"]
    ],
    "Pollen Fetcher 5": [
        [1, "Collect", "Pollen"]
    ],
    "White Clover Redux": [
        [1, "Collect", "White"],
        [2, "Collect", "Clover"
    ],
    "Strawberry Field Forever"  : [
        [1, "Collect", "Strawberry"],
    ],
    "Tasting The Sky": [
        [1, "Collect", "Blue"],
        [2, "Collect", "Mountain Top"],
        [3, "Collect", "Sunflower"]
    ],
    "Whispy and Crispy": [
        [1, "Collect", "Cactus"],
        [2, "Collect", "Dandelion"],
    ],
    "Walk Through The Woods": [
        [1, "Collect", "Pine Tree"],
        [2, "Collect", "Bamboo"],
    ],
    "Get Red-y": [
        [1, "Collect", "Red"],
        [2, "Collect", "Clover"],
        [3, "Collect", "Stump"],
    ],

###########################################################################
#new quests comming soon
###########################################################################



#################################
##loop quests below
#################################

    "Just White": [
        [1, "Collect", "White"]
    ],
    "Just Red": [
        [1, "Collect", "Red"]
    ],
    "Just Blue": [
        [1, "Collect", "Blue"]
    ],
    "A Bit Of Both": [
        [1, "Collect", "Red"],
        [2, "Collect", "Blue"]
    ],
    "Any Pollen": [
        [1, "Collect", "Any"]
    ],
    "The Whole Lot": [
        [1, "Collect", "Red"],
        [2, "Collect", "Blue"],
        [3, "Collect", "White"]
    ],
    "Between The Bamboo": [
        [2, "Collect", "Bamboo"],
        [1, "Collect", "Blue"]
    ],
    "Play In The Pumpkins": [
        [2, "Collect", "Pumpkin"],
        [1, "Collect", "White"]
    ],
    "Plundering Pineapples": [
        [2, "Collect", "Pineapple"],
        [1, "Collect", "Any"]
    ],
    "Stroll In The Strawberries": [
        [2, "Collect", "Strawberry"],
        [1, "Collect", "Red"]
    ],
    "Mid-Level Mission": [
        [1, "Collect", "Spider"],
        [2, "Collect", "Strawberry"],
        [3, "Collect", "Bamboo"]
    ],
    "Blue Flower Bliss": [
        [1, "Collect", "Blue Flower"]
    ],
    "Delve Into Dandelions": [
        [1, "Collect", "Dandelion"]
    ],
    "Fun In The Sunflowers": [
        [1, "Collect", "Sunflower"]
    ],
    "Mission For Mushrooms": [
        [1, "Collect", "Mushroom"]
    ],
    "Leisurely Lowlands": [
        [1, "Collect", "Sunflower"],
        [2, "Collect", "Dandelion"],
        [3, "Collect", "Mushroom"],
        [4, "Collect", "Blue Flower"]
    ],
    "Triple Trek": [
        [1, "Collect", "Mountain Top"],
        [2, "Collect", "Pepper"],
        [3, "Collect", "Coconut"]
    ],
    "Pepper Patrol": [
        [1, "Collect", "Pepper"]
    ]
}

BuckoBee = {
    "Abilities": [
        [1, "Collect", "Any"]
    ],
    "Bamboo": [
        [1, "Collect", "Bamboo"]
    ],
    "Bombard": [
        [4, "Get", "Ant"],
        [3, "Get", "Ant"],
        [2, "Kill", "RhinoBeetles"],
        [1, "Collect", "Any"]
    ],
    "Booster": [
        [2, "Get", "BlueBoost"],
        [1, "Collect", "Any"]
    ],
    "Clean-Up": [
        [1, "Collect", "Blue Flower"],
        [2, "Collect", "Bamboo"],
        [3, "Collect", "Pine Tree"]
    ],
    "Extraction": [
        [1, "Collect", "Clover"],
        [2, "Collect", "Cactus"],
        [3, "Collect", "Pumpkin"]
    ],
    "Flowers": [
        [1, "Collect", "Blue Flower"]
    ],
    "Goo": [
        [1, "Collect", "Blue"]
    ],
    "Medley": [
        [2, "Collect", "Bamboo"],
        [3, "Collect", "Pine Tree"],
        [1, "Collect", "Any"]
    ],
    "Picnic": [
        [5, "Get", "Ant"],
        [4, "Get", "Ant"],
        [3, "Feed", "Blueberry"],
        [1, "Collect", "Blue Flower"],
        [2, "Collect", "Blue"]
    ],
    "Pine Trees": [
        [1, "Collect", "Pine Tree"]
    ],
    "Pollen": [
        [1, "Collect", "Blue"]
    ],
    "Scavenge": [
        [1, "Collect", "Blue"],
        [3, "Collect", "Blue"],
        [2, "Collect", "Any"]
    ],
    "Skirmish": [
        [2, "Kill", "RhinoBeetles"],
        [1, "Collect", "Blue Flower"]
    ],
    "Tango": [
        [3, "Kill", "Mantis"],
        [1, "Collect", "Blue"],
        [2, "Collect", "Any"]
    ],
    "Tour": [
        [5, "Kill", "Mantis"],
        [4, "Kill", "RhinoBeetles"],
        [1, "Collect", "Blue Flower"],
        [2, "Collect", "Bamboo"],
        [3, "Collect", "Pine Tree"]
    ]
}

RileyBee = {
    "Abilities": [
        [1, "Collect", "Any"]
    ],
    "Booster": [
        [2, "Get", "RedBoost"],
        [1, "Collect", "Any"]
    ],
    "Clean-Up": [
        [1, "Collect", "Mushroom"],
        [2, "Collect", "Strawberry"],
        [3, "Collect", "Rose"]
    ],
    "Extraction": [
        [1, "Collect", "Clover"],
        [2, "Collect", "Cactus"],
        [3, "Collect", "Pumpkin"]
    ],
    "Goo": [
        [1, "Collect", "Red"]
    ],
    "Medley": [
        [2, "Collect", "Strawberry"],
        [3, "Collect", "Rose"],
        [1, "Collect", "Any"]
    ],
    "Mushrooms": [
        [1, "Collect", "Mushroom"]
    ],
    "Picnic": [
        [4, "Get", "Ant"],
        [3, "Feed", "Strawberry"],
        [1, "Collect", "Mushroom"],
        [2, "Collect", "Strawberry"]
    ],
    "Pollen": [
        [1, "Collect", "Red"]
    ],
    "Rampage": [
        [3, "Get", "Ant"],
        [2, "Kill", "Ladybugs"],
        [1, "Kill", "All"]
    ],
    "Roses": [
        [1, "Collect", "Rose"]
    ],
    "Scavenge": [
        [1, "Collect", "Red"],
        [3, "Collect", "Strawberry"],
        [2, "Collect", "Any"]
    ],
    "Skirmish": [
        [2, "Kill", "Ladybugs"],
        [1, "Collect", "Mushroom"]
    ],
    "Strawberries": [
        [1, "Collect", "Strawberry"]
    ],
    "Tango": [
        [3, "Kill", "Scorpions"],
        [1, "Collect", "Red"],
        [2, "Collect", "Any"]
    ],
    "Tour": [
        [5, "Kill", "Scorpions"],
        [4, "Kill", "Ladybugs"],
        [1, "Collect", "Mushroom"],
        [2, "Collect", "Strawberry"],
        [3, "Collect", "Rose"]
    ]
}

# Field Booster Data
FieldBooster = {
    "pine tree": {"booster": "blue", "stacks": 1},
    "bamboo": {"booster": "blue", "stacks": 1},
    "blue flower": {"booster": "blue", "stacks": 3},
    "stump": {"booster": "blue", "stacks": 1},
    "rose": {"booster": "red", "stacks": 1},
    "strawberry": {"booster": "red", "stacks": 1},
    "mushroom": {"booster": "red", "stacks": 3},
    "pepper": {"booster": "red", "stacks": 1},
    "sunflower": {"booster": "mountain", "stacks": 3},
    "dandelion": {"booster": "mountain", "stacks": 3},
    "spider": {"booster": "mountain", "stacks": 2},
    "clover": {"booster": "mountain", "stacks": 2},
    "pineapple": {"booster": "mountain", "stacks": 2},
    "pumpkin": {"booster": "mountain", "stacks": 1},
    "cactus": {"booster": "mountain", "stacks": 1},
    "mountain top": {"booster": "none", "stacks": 0},
    "coconut": {"booster": "none", "stacks": 0}
}

# Commando Chick Health
CommandoChickHealth = {
    3: 150,
    4: 2000,
    5: 10000,
    6: 15000,
    7: 25000,
    8: 50000,
    9: 100000,
    10: 150000,
    11: 200000,
    12: 300000,
    13: 400000,
    14: 500000,
    15: 750000,
    16: 1000000,
    17: 2500000,
    18: 5000000,
    19: 7500000
}

# Memory Match Data (to be included from a separate file or module)
# Note: The original AHK includes "data\memorymatch.ahk". In Python, this would need to be
# converted to a Python module (e.g., memorymatch.py) and imported or defined separately.
# For now, this is a placeholder comment.
# Example: from memorymatch import memory_match_data

# more code below 

# Field Default Overrides
field_default = {
    "Sunflower": {
        "pattern": "CornerXSnake",
        "size": "M",
        "width": 4,
        "camera": "None",
        "turns": 1,
        "sprinkler": "Upper Left",
        "distance": 8,
        "percent": 95,
        "gathertime": 10,
        "convert": "Walk",
        "drift": 0,
        "shiftlock": 0,
        "invertFB": 0,
        "invertLR": 1
    },
    "Dandelion": {
        "pattern": "CornerXSnake",
        "size": "M",
        "width": 6,
        "camera": "None",
        "turns": 1,
        "sprinkler": "Upper Left",
        "distance": 10,
        "percent": 95,
        "gathertime": 10,
        "convert": "Walk",
        "drift": 0,
        "shiftlock": 0,
        "invertFB": 0,
        "invertLR": 1
    },
    "Mushroom": {
        "pattern": "CornerXSnake",
        "size": "M",
        "width": 2,
        "camera": "None",
        "turns": 1,
        "sprinkler": "Upper Left",
        "distance": 8,
        "percent": 95,
        "gathertime": 10,
        "convert": "Walk",
        "drift": 0,
        "shiftlock": 0,
        "invertFB": 0,
        "invertLR": 1
    },
    "Blue Flower": {
        "pattern": "CornerXSnake",
        "size": "M",
        "width": 7,
        "camera": "Right",
        "turns": 2,
        "sprinkler": "Center",
        "distance": 1,
        "percent": 95,
        "gathertime": 10,
        "convert": "Walk",
        "drift": 0,
        "shiftlock": 0,
        "invertFB": 0,
        "invertLR": 0
    },
    "Clover": {
        "pattern": "Stationary",
        "size": "S",
        "width": 1,
        "camera": "None",
        "turns": 1,
        "sprinkler": "Center",
        "distance": 1,
        "percent": 95,
        "gathertime": 10,
        "convert": "Walk",
        "drift": 0,
        "shiftlock": 0,
        "invertFB": 0,
        "invertLR": 0
    },
    "Spider": {
        "pattern": "CornerXSnake",
        "size": "M",
        "width": 1,
        "camera": "None",
        "turns": 1,
        "sprinkler": "Upper Left",
        "distance": 6,
        "percent": 95,
        "gathertime": 10,
        "convert": "Walk",
        "drift": 0,
        "shiftlock": 0,
        "invertFB": 0,
        "invertLR": 1
    },
    "Strawberry": {
        "pattern": "CornerXSnake",
        "size": "M",
        "width": 1,
        "camera": "Right",
        "turns": 2,
        "sprinkler": "Upper Right",
        "distance": 6,
        "percent": 95,
        "gathertime": 10,
        "convert": "Walk",
        "drift": 0,
        "shiftlock": 0,
        "invertFB": 0,
        "invertLR": 1
    },
    "Bamboo": {
        "pattern": "CornerXSnake",
        "size": "M",
        "width": 3,
        "camera": "Left",
        "turns": 2,
        "sprinkler": "Upper Left",
        "distance": 4,
        "percent": 95,
        "gathertime": 10,
        "convert": "Walk",
        "drift": 0,
        "shiftlock": 0,
        "invertFB": 0,
        "invertLR": 1
    },
    "Pineapple": {
        "pattern": "CornerXSnake",
        "size": "M",
        "width": 1,
        "camera": "None",
        "turns": 1,
        "sprinkler": "Upper Left",
        "distance": 8,
        "percent": 95,
        "gathertime": 10,
        "convert": "Walk",
        "drift": 0,
        "shiftlock": 0,
        "invertFB": 0,
        "invertLR": 1
    },
    "Stump": {
        "pattern": "Stationary",
        "size": "S",
        "width": 1,
        "camera": "None",
        "turns": 1,
        "sprinkler": "Center",
        "distance": 1,
        "percent": 95,
        "gathertime": 10,
        "convert": "Walk",
        "drift": 0,
        "shiftlock": 0,
        "invertFB": 0,
        "invertLR": 0
    },
    "Cactus": {
        "pattern": "Stationary",
        "size": "S",
        "width": 1,
        "camera": "None",
        "turns": 1,
        "sprinkler": "Center",
        "distance": 1,
        "percent": 95,
        "gathertime": 10,
        "convert": "Walk",
        "drift": 0,
        "shiftlock": 0,
        "invertFB": 0,
        "invertLR": 0
    },
    "Pumpkin": {
        "pattern": "CornerXSnake",
        "size": "M",
        "width": 5,
        "camera": "Right",
        "turns": 2,
        "sprinkler": "Right",
        "distance": 8,
        "percent": 95,
        "gathertime": 10,
        "convert": "Walk",
        "drift": 0,
        "shiftlock": 0,
        "invertFB": 0,
        "invertLR": 1
    },
    "Pine Tree": {
        "pattern": "CornerXSnake",
        "size": "M",
        "width": 3,
        "camera": "Left",
        "turns": 2,
        "sprinkler": "Upper Left",
        "distance": 7,
        "percent": 95,
        "gathertime": 10,
        "convert": "Walk",
        "drift": 0,
        "shiftlock": 0,
        "invertFB": 0,
        "invertLR": 0
    },
    "Rose": {
        "pattern": "CornerXSnake",
        "size": "M",
        "width": 1,
        "camera": "Left",
        "turns": 4,
        "sprinkler": "Lower Right",
        "distance": 10,
        "percent": 95,
        "gathertime": 10,
        "convert": "Walk",
        "drift": 0,
        "shiftlock": 0,
        "invertFB": 0,
        "invertLR": 1
    },
    "Mountain Top": {
        "pattern": "CornerXSnake",
        "size": "M",
        "width": 3,
        "camera": "Left",
        "turns": 4,
        "sprinkler": "Lower Left",
        "distance": 5,
        "percent": 95,
        "gathertime": 10,
        "convert": "Walk",
        "drift": 0,
        "shiftlock": 0,
        "invertFB": 0,
        "invertLR": 0
    },
    "Coconut": {
        "pattern": "CornerXSnake",
        "size": "M",
        "width": 3,
        "camera": "Right",
        "turns": 2,
        "sprinkler": "Right",
        "distance": 6,
        "percent": 95,
        "gathertime": 10,
        "convert": "Walk",
        "drift": 0,
        "shiftlock": 0,
        "invertFB": 0,
        "invertLR": 1
    },
    "Pepper": {
        "pattern": "CornerXSnake",
        "size": "M",
        "width": 5,
        "camera": "None",
        "turns": 1,
        "sprinkler": "Upper Right",
        "distance": 7,
        "percent": 95,
        "gathertime": 10,
        "convert": "Walk",
        "drift": 0,
        "shiftlock": 0,
        "invertFB": 0,
        "invertLR": 0
    }
}

standard_field_default = copy.deepcopy(field_default)

inipath = os.path.join(os.getcwd(), "settings", "field_config.ini")

if os.path.exists(inipath):
    ini_config = configparser.ConfigParser()
    ini_config.read(inipath)
    for section in ini_config.sections():
        if section in field_default:
            for key in ini_config[section]:
                value = ini_config[section][key]
                try:
                    value = int(value)
                except ValueError:
                    try:
                        value = float(value)
                    except ValueError:
                        pass  # Keep as string
                field_default[section][key] = value

# Reset pattern to default if not in patternlist (assumes field_name1, field_pattern1, etc., are defined elsewhere)
for i in range(1, 4):
    field_name = globals().get(f"field_name{i}", "None")
    field_pattern = globals().get(f"field_pattern{i}")
    if field_name != "None" and field_pattern is not None:
        if field_pattern not in patternlist:
            globals()[f"field_pattern{i}"] = field_default[field_name]["pattern"]

ini_config = configparser.ConfigParser()
for field, settings in field_default.items():
    ini_config[field] = {k: str(v) for k, v in settings.items()}
with open(inipath, 'w') as configfile:
    ini_config.write(configfile)

# more code below

# Manual Planters
def nm_import_manual_planters():
    global manual_planters
    manual_planters = {
        "General": {
            "MHarvestInterval": "2 hours"
        },
        "Slot 1": {
            "MSlot1Cycle1Planter": "",
            "MSlot1Cycle2Planter": "",
            "MSlot1Cycle3Planter": "",
            "MSlot1Cycle4Planter": "",
            "MSlot1Cycle5Planter": "",
            "MSlot1Cycle6Planter": "",
            "MSlot1Cycle7Planter": "",
            "MSlot1Cycle8Planter": "",
            "MSlot1Cycle9Planter": "",
            "MSlot1Cycle1Field": "",
            "MSlot1Cycle2Field": "",
            "MSlot1Cycle3Field": "",
            "MSlot1Cycle4Field": "",
            "MSlot1Cycle5Field": "",
            "MSlot1Cycle6Field": "",
            "MSlot1Cycle7Field": "",
            "MSlot1Cycle8Field": "",
            "MSlot1Cycle9Field": "",
            "MSlot1Cycle1Glitter": 0,
            "MSlot1Cycle2Glitter": 0,
            "MSlot1Cycle3Glitter": 0,
            "MSlot1Cycle4Glitter": 0,
            "MSlot1Cycle5Glitter": 0,
            "MSlot1Cycle6Glitter": 0,
            "MSlot1Cycle7Glitter": 0,
            "MSlot1Cycle8Glitter": 0,
            "MSlot1Cycle9Glitter": 0,
            "MSlot1Cycle1AutoFull": "Timed",
            "MSlot1Cycle2AutoFull": "Timed",
            "MSlot1Cycle3AutoFull": "Timed",
            "MSlot1Cycle4AutoFull": "Timed",
            "MSlot1Cycle5AutoFull": "Timed",
            "MSlot1Cycle6AutoFull": "Timed",
            "MSlot1Cycle7AutoFull": "Timed",
            "MSlot1Cycle8AutoFull": "Timed",
            "MSlot1Cycle9AutoFull": "Timed"
        },
        "Slot 2": {
            "MSlot2Cycle1Planter": "",
            "MSlot2Cycle2Planter": "",
            "MSlot2Cycle3Planter": "",
            "MSlot2Cycle4Planter": "",
            "MSlot2Cycle5Planter": "",
            "MSlot2Cycle6Planter": "",
            "MSlot2Cycle7Planter": "",
            "MSlot2Cycle8Planter": "",
            "MSlot2Cycle9Planter": "",
            "MSlot2Cycle1Field": "",
            "MSlot2Cycle2Field": "",
            "MSlot2Cycle3Field": "",
            "MSlot2Cycle4Field": "",
            "MSlot2Cycle5Field": "",
            "MSlot2Cycle6Field": "",
            "MSlot2Cycle7Field": "",
            "MSlot2Cycle8Field": "",
            "MSlot2Cycle9Field": "",
            "MSlot2Cycle1Glitter": 0,
            "MSlot2Cycle2Glitter": 0,
            "MSlot2Cycle3Glitter": 0,
            "MSlot2Cycle4Glitter": 0,
            "MSlot2Cycle5Glitter": 0,
            "MSlot2Cycle6Glitter": 0,
            "MSlot2Cycle7Glitter": 0,
            "MSlot2Cycle8Glitter": 0,
            "MSlot2Cycle9Glitter": 0,
            "MSlot2Cycle1AutoFull": "Timed",
            "MSlot2Cycle2AutoFull": "Timed",
            "MSlot2Cycle3AutoFull": "Timed",
            "MSlot2Cycle4AutoFull": "Timed",
            "MSlot2Cycle5AutoFull": "Timed",
            "MSlot2Cycle6AutoFull": "Timed",
            "MSlot2Cycle7AutoFull": "Timed",
            "MSlot2Cycle8AutoFull": "Timed",
            "MSlot2Cycle9AutoFull": "Timed"
        },
        "Slot 3": {
            "MSlot3Cycle1Planter": "",
            "MSlot3Cycle2Planter": "",
            "MSlot3Cycle3Planter": "",
            "MSlot3Cycle4Planter": "",
            "MSlot3Cycle5Planter": "",
            "MSlot3Cycle6Planter": "",
            "MSlot3Cycle7Planter": "",
            "MSlot3Cycle8Planter": "",
            "MSlot3Cycle9Planter": "",
            "MSlot3Cycle1Field": "",
            "MSlot3Cycle2Field": "",
            "MSlot3Cycle3Field": "",
            "MSlot3Cycle4Field": "",
            "MSlot3Cycle5Field": "",
            "MSlot3Cycle6Field": "",
            "MSlot3Cycle7Field": "",
            "MSlot3Cycle8Field": "",
            "MSlot3Cycle9Field": "",
            "MSlot3Cycle1Glitter": 0,
            "MSlot3Cycle2Glitter": 0,
            "MSlot3Cycle3Glitter": 0,
            "MSlot3Cycle4Glitter": 0,
            "MSlot3Cycle5Glitter": 0,
            "MSlot3Cycle6Glitter": 0,
            "MSlot3Cycle7Glitter": 0,
            "MSlot3Cycle8Glitter": 0,
            "MSlot3Cycle9Glitter": 0,
            "MSlot3Cycle1AutoFull": "Timed",
            "MSlot3Cycle2AutoFull": "Timed",
            "MSlot3Cycle3AutoFull": "Timed",
            "MSlot3Cycle4AutoFull": "Timed",
            "MSlot3Cycle5AutoFull": "Timed",
            "MSlot3Cycle6AutoFull": "Timed",
            "MSlot3Cycle7AutoFull": "Timed",
            "MSlot3Cycle8AutoFull": "Timed",
            "MSlot3Cycle9AutoFull": "Timed"
        }
    }

    # Set global variables from manual_planters
    for section, settings in manual_planters.items():
        for key, value in settings.items():
            globals()[key] = value

    inipath = os.path.join(os.getcwd(), "settings", "manual_planters.ini")

    if os.path.exists(inipath):
        nm_read_ini(inipath)

    # Write current global values to INI
    ini_config = configparser.ConfigParser()
    for section, keys in manual_planters.items():
        ini_config[section] = {key: str(globals().get(key, '')) for key in keys}
    with open(inipath, 'w') as configfile:
        ini_config.write(configfile)

nm_import_manual_planters()

# Declare globals and prepare GUI
priority_list = []
default_priority_list = ["Night", "Mondo", "Planter", "Bugrun", "Collect", "QuestRotate", "Boost", "GoGather"]
for x in str(priority_list_numeric):  # Assuming priority_list_numeric is defined elsewhere
    priority_list.append(default_priority_list[int(x) - 1])

vb_state = 0
lost_planters = ""
quest_fields = ""
you_died = 0
game_frozen_counter = 0
afb_rolling_dice = 0
afb_use_glitter = 0
afb_use_booster = 0
macro_state = 0  # 0=stopped, 1=paused, 2=running
reset_time = macro_start_time = macro_reload_time = now_unix()  # Assuming now_unix is defined
paused_runtime = 0
field_guid_detected = 0
has_pop_star = 0
pop_star_active = 0
previous_action = "None"
current_action = "Startup"
field_name_list = ["Bamboo", "Blue Flower", "Cactus", "Clover", "Coconut", "Dandelion", "Mountain Top", "Mushroom", "Pepper", "Pine Tree", "Pineapple", "Pumpkin", "Rose", "Spider", "Strawberry", "Stump", "Sunflower"]
hotbar_while_list = ["Never", "Always", "At Hive", "Gathering", "Attacking", "Microconverter", "Whirligig", "Enzymes", "GatherStart", "Snowflake"]
sprinkler_images = ["saturator"]
reconnect_delay = 0
gather_start_time = convert_start_time = 0
quest_ant = 0
quest_blue_boost = 0
quest_red_boost = 0
hive_confirmed = 0
shift_lock_enabled = 0

# Ensure GUI will be visible
if gui_x and gui_y:  # Assuming gui_x and gui_y are defined
    monitor_count = monitor_get_count()  # Assuming monitor_get_count is defined
    for i in range(1, monitor_count + 1):
        mon_left, mon_top, mon_right, mon_bottom = monitor_get_work_area(i)  # Assuming monitor_get_work_area is defined
        if mon_left < gui_x < mon_right and mon_top < gui_y < mon_bottom:
            break
    else:
        gui_x = gui_y = 0
else:
    gui_x = gui_y = 0

backpack_percent = backpack_percent_filtered = 0
active_hotkeys = []

# more code below

# Manual Planters
def nm_import_manual_planters():
    global manual_planters
    manual_planters = {
        "General": {
            "MHarvestInterval": "2 hours"
        },
        "Slot 1": {
            "MSlot1Cycle1Planter": "",
            "MSlot1Cycle2Planter": "",
            "MSlot1Cycle3Planter": "",
            "MSlot1Cycle4Planter": "",
            "MSlot1Cycle5Planter": "",
            "MSlot1Cycle6Planter": "",
            "MSlot1Cycle7Planter": "",
            "MSlot1Cycle8Planter": "",
            "MSlot1Cycle9Planter": "",
            "MSlot1Cycle1Field": "",
            "MSlot1Cycle2Field": "",
            "MSlot1Cycle3Field": "",
            "MSlot1Cycle4Field": "",
            "MSlot1Cycle5Field": "",
            "MSlot1Cycle6Field": "",
            "MSlot1Cycle7Field": "",
            "MSlot1Cycle8Field": "",
            "MSlot1Cycle9Field": "",
            "MSlot1Cycle1Glitter": 0,
            "MSlot1Cycle2Glitter": 0,
            "MSlot1Cycle3Glitter": 0,
            "MSlot1Cycle4Glitter": 0,
            "MSlot1Cycle5Glitter": 0,
            "MSlot1Cycle6Glitter": 0,
            "MSlot1Cycle7Glitter": 0,
            "MSlot1Cycle8Glitter": 0,
            "MSlot1Cycle9Glitter": 0,
            "MSlot1Cycle1AutoFull": "Timed",
            "MSlot1Cycle2AutoFull": "Timed",
            "MSlot1Cycle3AutoFull": "Timed",
            "MSlot1Cycle4AutoFull": "Timed",
            "MSlot1Cycle5AutoFull": "Timed",
            "MSlot1Cycle6AutoFull": "Timed",
            "MSlot1Cycle7AutoFull": "Timed",
            "MSlot1Cycle8AutoFull": "Timed",
            "MSlot1Cycle9AutoFull": "Timed"
        },
        "Slot 2": {
            "MSlot2Cycle1Planter": "",
            "MSlot2Cycle2Planter": "",
            "MSlot2Cycle3Planter": "",
            "MSlot2Cycle4Planter": "",
            "MSlot2Cycle5Planter": "",
            "MSlot2Cycle6Planter": "",
            "MSlot2Cycle7Planter": "",
            "MSlot2Cycle8Planter": "",
            "MSlot2Cycle9Planter": "",
            "MSlot2Cycle1Field": "",
            "MSlot2Cycle2Field": "",
            "MSlot2Cycle3Field": "",
            "MSlot2Cycle4Field": "",
            "MSlot2Cycle5Field": "",
            "MSlot2Cycle6Field": "",
            "MSlot2Cycle7Field": "",
            "MSlot2Cycle8Field": "",
            "MSlot2Cycle9Field": "",
            "MSlot2Cycle1Glitter": 0,
            "MSlot2Cycle2Glitter": 0,
            "MSlot2Cycle3Glitter": 0,
            "MSlot2Cycle4Glitter": 0,
            "MSlot2Cycle5Glitter": 0,
            "MSlot2Cycle6Glitter": 0,
            "MSlot2Cycle7Glitter": 0,
            "MSlot2Cycle8Glitter": 0,
            "MSlot2Cycle9Glitter": 0,
            "MSlot2Cycle1AutoFull": "Timed",
            "MSlot2Cycle2AutoFull": "Timed",
            "MSlot2Cycle3AutoFull": "Timed",
            "MSlot2Cycle4AutoFull": "Timed",
            "MSlot2Cycle5AutoFull": "Timed",
            "MSlot2Cycle6AutoFull": "Timed",
            "MSlot2Cycle7AutoFull": "Timed",
            "MSlot2Cycle8AutoFull": "Timed",
            "MSlot2Cycle9AutoFull": "Timed"
        },
        "Slot 3": {
            "MSlot3Cycle1Planter": "",
            "MSlot3Cycle2Planter": "",
            "MSlot3Cycle3Planter": "",
            "MSlot3Cycle4Planter": "",
            "MSlot3Cycle5Planter": "",
            "MSlot3Cycle6Planter": "",
            "MSlot3Cycle7Planter": "",
            "MSlot3Cycle8Planter": "",
            "MSlot3Cycle9Planter": "",
            "MSlot3Cycle1Field": "",
            "MSlot3Cycle2Field": "",
            "MSlot3Cycle3Field": "",
            "MSlot3Cycle4Field": "",
            "MSlot3Cycle5Field": "",
            "MSlot3Cycle6Field": "",
            "MSlot3Cycle7Field": "",
            "MSlot3Cycle8Field": "",
            "MSlot3Cycle9Field": "",
            "MSlot3Cycle1Glitter": 0,
            "MSlot3Cycle2Glitter": 0,
            "MSlot3Cycle3Glitter": 0,
            "MSlot3Cycle4Glitter": 0,
            "MSlot3Cycle5Glitter": 0,
            "MSlot3Cycle6Glitter": 0,
            "MSlot3Cycle7Glitter": 0,
            "MSlot3Cycle8Glitter": 0,
            "MSlot3Cycle9Glitter": 0,
            "MSlot3Cycle1AutoFull": "Timed",
            "MSlot3Cycle2AutoFull": "Timed",
            "MSlot3Cycle3AutoFull": "Timed",
            "MSlot3Cycle4AutoFull": "Timed",
            "MSlot3Cycle5AutoFull": "Timed",
            "MSlot3Cycle6AutoFull": "Timed",
            "MSlot3Cycle7AutoFull": "Timed",
            "MSlot3Cycle8AutoFull": "Timed",
            "MSlot3Cycle9AutoFull": "Timed"
        }
    }

    # Set global variables from manual_planters
    for section, settings in manual_planters.items():
        for key, value in settings.items():
            globals()[key] = value

    inipath = os.path.join(os.getcwd(), "settings", "manual_planters.ini")

    if os.path.exists(inipath):
        nm_read_ini(inipath)

    # Write current global values to INI
    ini_config = configparser.ConfigParser()
    for section, keys in manual_planters.items():
        ini_config[section] = {key: str(globals().get(key, '')) for key in keys}
    with open(inipath, 'w') as configfile:
        ini_config.write(configfile)

nm_import_manual_planters()

# Declare globals and prepare GUI
priority_list = []
default_priority_list = ["Night", "Mondo", "Planter", "Bugrun", "Collect", "QuestRotate", "Boost", "GoGather"]
for x in str(priority_list_numeric):  # Assuming priority_list_numeric is defined elsewhere
    priority_list.append(default_priority_list[int(x) - 1])

vb_state = 0
lost_planters = ""
quest_fields = ""
you_died = 0
game_frozen_counter = 0
afb_rolling_dice = 0
afb_use_glitter = 0
afb_use_booster = 0
macro_state = 0  # 0=stopped, 1=paused, 2=running
reset_time = macro_start_time = macro_reload_time = now_unix()  # Assuming now_unix is defined
paused_runtime = 0
field_guid_detected = 0
has_pop_star = 0
pop_star_active = 0
previous_action = "None"
current_action = "Startup"
field_name_list = ["Bamboo", "Blue Flower", "Cactus", "Clover", "Coconut", "Dandelion", "Mountain Top", "Mushroom", "Pepper", "Pine Tree", "Pineapple", "Pumpkin", "Rose", "Spider", "Strawberry", "Stump", "Sunflower"]
hotbar_while_list = ["Never", "Always", "At Hive", "Gathering", "Attacking", "Microconverter", "Whirligig", "Enzymes", "GatherStart", "Snowflake"]
sprinkler_images = ["saturator"]
reconnect_delay = 0
gather_start_time = convert_start_time = 0
quest_ant = 0
quest_blue_boost = 0
quest_red_boost = 0
hive_confirmed = 0
shift_lock_enabled = 0

# Ensure GUI will be visible
if gui_x and gui_y:  # Assuming gui_x and gui_y are defined
    monitor_count = monitor_get_count()  # Assuming monitor_get_count is defined
    for i in range(1, monitor_count + 1):
        mon_left, mon_top, mon_right, mon_bottom = monitor_get_work_area(i)  # Assuming monitor_get_work_area is defined
        if mon_left < gui_x < mon_right and mon_top < gui_y < mon_bottom:
            break
    else:
        gui_x = gui_y = 0
else:
    gui_x = gui_y = 0

backpack_percent = backpack_percent_filtered = 0
active_hotkeys = []

# more code below

# Main GUI Window Setup
main_gui = tk.Tk()
main_gui.title("Natro Macro (Loading 0%)")
main_gui.geometry(f"490x275+{GuiX}+{GuiY}")
main_gui.attributes('-alpha', 1 - (GuiTransparency / 100))  # Transparency from 0-100 scale
if AlwaysOnTop:
    main_gui.attributes('-topmost', 1)

def set_loading_progress(percent):
    main_gui.title(f"Natro Macro (Loading {round(percent)}%)")

main_gui.protocol("WM_DELETE_WINDOW", lambda: exit())  # Close event

# Font Settings
default_font = ("Tahoma", 8)
bold_font = ("Tahoma", 8, "bold")
bold_underline_font = ("Tahoma", 8, "bold underline")

# Bottom Section: Current Field and Status
tk.Label(main_gui, text="Current Field:", font=default_font, bg=main_gui.cget('bg')).place(x=5, y=241, width=80)
tk.Label(main_gui, text="Status:", font=default_font, bg=main_gui.cget('bg')).place(x=177, y=241, width=30)

current_field_up = tk.Button(main_gui, text="<", state='disabled', command=nm_currentFieldUp)
current_field_up.place(x=82, y=240, width=10, height=15)

current_field_down = tk.Button(main_gui, text=">", state='disabled', command=nm_currentFieldDown)
current_field_down.place(x=165, y=240, width=10, height=15)

current_field = tk.Label(main_gui, text=globals()[f'FieldName{CurrentFieldNum}'], font=default_font, borderwidth=1, relief='solid', justify='center', bg=main_gui.cget('bg'))
current_field.place(x=92, y=240, width=73)

state_label = tk.Label(main_gui, text="Startup: UI", font=default_font, borderwidth=1, relief='solid', bg=main_gui.cget('bg'))
state_label.place(x=220, y=240, width=275)

# Version Label and Links
version_text = tk.Label(main_gui, text=f"v{versionID}", font=default_font, bg=main_gui.cget('bg'))
version_text.place(x=494 - TextExtent(f"v{versionID}", version_text), y=264)
version_text.bind("<Button-1>", nm_showAdvancedSettings)

# Assuming images are loaded elsewhere as PhotoImage objects
warning_gui_image = bitmaps["warninggui"]  # Placeholder for image
image_update_link = tk.Label(main_gui, image=warning_gui_image, bg=main_gui.cget('bg'))
image_update_link.place(x=482, y=264, width=14, height=14)
image_update_link.bind("<Button-1>", nm_AutoUpdateGUI)
image_update_link.place_forget()  # Hidden initially

github_gui_image = bitmaps["githubgui"]
image_github_link = tk.Label(main_gui, image=github_gui_image, bg=main_gui.cget('bg'))
image_github_link.place(x=494 - TextExtent(f"v{versionID}", version_text) - 23, y=262, width=18, height=18)

discord_gui_image = bitmaps["discordgui"]  # Assuming grayscale conversion elsewhere
image_discord_link = tk.Label(main_gui, image=discord_gui_image, bg=main_gui.cget('bg'))
image_discord_link.place(x=494 - TextExtent(f"v{versionID}", version_text) - 48, y=263, width=21, height=16)

# Control Buttons
start_button = tk.Button(main_gui, text=f" Start ({StartHotkey})", state='disabled', command=nm_StartButton)
start_button.place(x=5, y=260, width=65, height=20)

pause_button = tk.Button(main_gui, text=f" Pause ({PauseHotkey})", state='disabled', command=nm_PauseButton)
pause_button.place(x=75, y=260, width=65, height=20)

stop_button = tk.Button(main_gui, text=f" Stop ({StopHotkey})", state='disabled', command=nm_StopButton)
stop_button.place(x=145, y=260, width=65, height=20)

# Tabs Setup
notebook = ttk.Notebook(main_gui, width=500, height=240)
notebook.place(x=0, y=-1)

tab_arr = ["Gather", "Collect/Kill", "Boost", "Quests", "Planters", "Status", "Settings", "Misc", "Credits"]
if BuffDetectReset == 1:
    tab_arr.append("Advanced")

tabs = {}
for tab_name in tab_arr:
    frame = ttk.Frame(notebook)
    notebook.add(frame, text=tab_name)
    tabs[tab_name.lower()] = frame

notebook.bind("<<NotebookTabChanged>>", lambda e: notebook.focus_set())

# GATHER TAB
gather_frame = tabs["gather"]

# Headers
tk.Label(gather_frame, text="Gathering", font=bold_underline_font, bg=gather_frame.cget('bg')).place(x=0, y=25, width=126, anchor='center')
tk.Label(gather_frame, text="Pattern", font=bold_underline_font, bg=gather_frame.cget('bg')).place(x=126, y=25, width=205, anchor='center')
tk.Label(gather_frame, text="Until", font=bold_underline_font, bg=gather_frame.cget('bg')).place(x=331, y=25, width=83, anchor='center')
tk.Label(gather_frame, text="Sprinkler", font=bold_underline_font, bg=gather_frame.cget('bg')).place(x=414, y=25, width=86, anchor='center')

# Sub-headers
tk.Label(gather_frame, text="Field Rotation", font=default_font, bg=gather_frame.cget('bg')).place(x=2, y=39, width=124, anchor='center')
tk.Label(gather_frame, text="Pattern Shape", font=default_font, bg=gather_frame.cget('bg')).place(x=130, y=39, width=112, anchor='center')
tk.Label(gather_frame, text="Length", font=default_font, bg=gather_frame.cget('bg')).place(x=253, y=39)
tk.Label(gather_frame, text="Width", font=default_font, bg=gather_frame.cget('bg')).place(x=295, y=39)
tk.Label(gather_frame, text="Mins", font=default_font, bg=gather_frame.cget('bg')).place(x=342, y=39)
tk.Label(gather_frame, text="Pack%", font=default_font, bg=gather_frame.cget('bg')).place(x=376, y=39)
tk.Label(gather_frame, text="Start Location", font=default_font, bg=gather_frame.cget('bg')).place(x=423, y=39)

# Lines
tk.Frame(gather_frame, height=2, width=492, bg='black').place(x=5, y=53)
tk.Frame(gather_frame, height=1, width=492, bg='black').place(x=5, y=115)
tk.Frame(gather_frame, height=1, width=492, bg='black').place(x=5, y=175)
tk.Frame(gather_frame, height=1, width=492, bg='black').place(x=5, y=235)
tk.Frame(gather_frame, height=206, width=1, bg='black').place(x=126, y=25)
tk.Frame(gather_frame, height=206, width=1, bg='black').place(x=331, y=25)
tk.Frame(gather_frame, height=206, width=1, bg='black').place(x=412, y=25)

# Field Numbers
tk.Label(gather_frame, text="1:", font=bold_font, bg=gather_frame.cget('bg')).place(x=4, y=61)
tk.Label(gather_frame, text="2:", font=bold_font, bg=gather_frame.cget('bg')).place(x=4, y=121)
tk.Label(gather_frame, text="3:", font=bold_font, bg=gather_frame.cget('bg')).place(x=4, y=181)

# Field Dropdowns
field_name1 = ttk.Combobox(gather_frame, values=fieldnamelist, state='disabled')
field_name1.place(x=18, y=57, width=106)
field_name1.set(FieldName1)
field_name1.bind('<<ComboboxSelected>>', nm_FieldSelect1)
set_loading_progress(3)

field_name2 = ttk.Combobox(gather_frame, values=["None"] + fieldnamelist, state='disabled')
field_name2.place(x=18, y=117, width=106)
field_name2.set(FieldName2)
field_name2.bind('<<ComboboxSelected>>', nm_FieldSelect2)
set_loading_progress(6)

field_name3 = ttk.Combobox(gather_frame, values=["None"] + fieldnamelist, state='disabled')
field_name3.place(x=18, y=177, width=106)
field_name3.set(FieldName3)
field_name3.bind('<<ComboboxSelected>>', nm_FieldSelect3)
set_loading_progress(9)

# Save Field Default Buttons
save_field_default1 = tk.Button(gather_frame, image=savefielddisabled_image, state='disabled', command=nm_SaveFieldDefault)
save_field_default1.place(x=2, y=86, width=18, height=18)

save_field_default2 = tk.Button(gather_frame, image=savefielddisabled_image, state='disabled', command=nm_SaveFieldDefault)
save_field_default2.place(x=2, y=146, width=18, height=18)

save_field_default3 = tk.Button(gather_frame, image=savefielddisabled_image, state='disabled', command=nm_SaveFieldDefault)
save_field_default3.place(x=2, y=206, width=18, height=18)

# Drift Compensation Checkboxes
field_drift_check1 = tk.Checkbutton(gather_frame, text="Drift\nComp", variable=tk.BooleanVar(value=FieldDriftCheck1), state='disabled', command=nm_saveConfig, justify='center')
field_drift_check1.place(x=65, y=83, width=50)

field_drift_check2 = tk.Checkbutton(gather_frame, text="Drift\nComp", variable=tk.BooleanVar(value=FieldDriftCheck2), state='disabled', command=nm_saveConfig, justify='center')
field_drift_check2.place(x=65, y=143, width=50)

field_drift_check3 = tk.Checkbutton(gather_frame, text="Drift\nComp", variable=tk.BooleanVar(value=FieldDriftCheck3), state='disabled', command=nm_saveConfig, justify='center')
field_drift_check3.place(x=65, y=203, width=50)

# Help Buttons
fdc_help1 = tk.Button(gather_frame, text="?", state='disabled', command=nm_FDCHelp)
fdc_help1.place(x=115, y=89, width=9, height=14)

fdc_help2 = tk.Button(gather_frame, text="?", state='disabled', command=nm_FDCHelp)
fdc_help2.place(x=115, y=149, width=9, height=14)

fdc_help3 = tk.Button(gather_frame, text="?", state='disabled', command=nm_FDCHelp)
fdc_help3.place(x=115, y=209, width=9, height=14)

# Copy/Paste Buttons
copy_gather1 = tk.Button(gather_frame, text="Copy", state='disabled', command=nm_CopyGatherSettings)
copy_gather1.place(x=22, y=82, width=40, height=14)

paste_gather1 = tk.Button(gather_frame, text="Paste", state='disabled', command=nm_PasteGatherSettings)
paste_gather1.place(x=22, y=97, width=40, height=14)

copy_gather2 = tk.Button(gather_frame, text="Copy", state='disabled', command=nm_CopyGatherSettings)
copy_gather2.place(x=22, y=142, width=40, height=14)

paste_gather2 = tk.Button(gather_frame, text="Paste", state='disabled', command=nm_PasteGatherSettings)
paste_gather2.place(x=22, y=157, width=40, height=14)

copy_gather3 = tk.Button(gather_frame, text="Copy", state='disabled', command=nm_CopyGatherSettings)
copy_gather3.place(x=22, y=202, width=40, height=14)

paste_gather3 = tk.Button(gather_frame, text="Paste", state='disabled', command=nm_PasteGatherSettings)
paste_gather3.place(x=22, y=217, width=40, height=14)

# Pattern Dropdowns
field_pattern1 = ttk.Combobox(gather_frame, values=patternlist, state='disabled')
field_pattern1.place(x=129, y=57, width=112)
field_pattern1.set(FieldPattern1)
field_pattern1.bind('<<ComboboxSelected>>', nm_saveConfig)
set_loading_progress(12)

field_pattern2 = ttk.Combobox(gather_frame, values=patternlist, state='disabled')
field_pattern2.place(x=129, y=117, width=112)
field_pattern2.set(FieldPattern2)
field_pattern2.bind('<<ComboboxSelected>>', nm_saveConfig)
set_loading_progress(15)

field_pattern3 = ttk.Combobox(gather_frame, values=patternlist, state='disabled')
field_pattern3.place(x=129, y=177, width=112)
field_pattern3.set(FieldPattern3)
field_pattern3.bind('<<ComboboxSelected>>', nm_saveConfig)
set_loading_progress(18)

# Pattern Size
field_pattern_size_arr = {"XS": 1, "S": 2, "M": 3, "L": 4, "XL": 5}
field_pattern_size1 = tk.Label(gather_frame, text=FieldPatternSize1, font=default_font, bg=gather_frame.cget('bg'), justify='center')
field_pattern_size1.place(x=254, y=60, width=12, height=16)
field_pattern_size1_updown = tk.Spinbox(gather_frame, from_=1, to=5, textvariable=tk.IntVar(value=field_pattern_size_arr[FieldPatternSize1]), state='disabled', command=nm_FieldPatternSize)
field_pattern_size1_updown.place(x=268, y=60, width=20, height=16)

field_pattern_size2 = tk.Label(gather_frame, text=FieldPatternSize2, font=default_font, bg=gather_frame.cget('bg'), justify='center')
field_pattern_size2.place(x=254, y=120, width=12, height=16)
field_pattern_size2_updown = tk.Spinbox(gather_frame, from_=1, to=5, textvariable=tk.IntVar(value=field_pattern_size_arr[FieldPatternSize2]), state='disabled', command=nm_FieldPatternSize)
field_pattern_size2_updown.place(x=268, y=120, width=20, height=16)

field_pattern_size3 = tk.Label(gather_frame, text=FieldPatternSize3, font=default_font, bg=gather_frame.cget('bg'), justify='center')
field_pattern_size3.place(x=254, y=180, width=12, height=16)
field_pattern_size3_updown = tk.Spinbox(gather_frame, from_=1, to=5, textvariable=tk.IntVar(value=field_pattern_size_arr[FieldPatternSize3]), state='disabled', command=nm_FieldPatternSize)
field_pattern_size3_updown.place(x=268, y=180, width=20, height=16)

# Pattern Reps
field_pattern_reps1 = tk.Spinbox(gather_frame, from_=1, to=9, textvariable=tk.IntVar(value=FieldPatternReps1), state='disabled', command=nm_saveConfig)
field_pattern_reps1.place(x=294, y=60, width=28, height=16)

field_pattern_reps2 = tk.Spinbox(gather_frame, from_=1, to=9, textvariable=tk.IntVar(value=FieldPatternReps2), state='disabled', command=nm_saveConfig)
field_pattern_reps2.place(x=294, y=120, width=28, height=16)

field_pattern_reps3 = tk.Spinbox(gather_frame, from_=1, to=9, textvariable=tk.IntVar(value=FieldPatternReps3), state='disabled', command=nm_saveConfig)
field_pattern_reps3.place(x=294, y=180, width=28, height=16)

# Shift-Lock Checkboxes
field_pattern_shift1 = tk.Checkbutton(gather_frame, text="Gather w/Shift-Lock", variable=tk.BooleanVar(value=FieldPatternShift1), state='disabled', command=nm_saveConfig)
field_pattern_shift1.place(x=129, y=82)

field_pattern_shift2 = tk.Checkbutton(gather_frame, text="Gather w/Shift-Lock", variable=tk.BooleanVar(value=FieldPatternShift2), state='disabled', command=nm_saveConfig)
field_pattern_shift2.place(x=129, y=142)

field_pattern_shift3 = tk.Checkbutton(gather_frame, text="Gather w/Shift-Lock", variable=tk.BooleanVar(value=FieldPatternShift3), state='disabled', command=nm_saveConfig)
field_pattern_shift3.place(x=129, y=202)

# Invert Checkboxes
tk.Label(gather_frame, text="Invert:", font=default_font, bg=gather_frame.cget('bg')).place(x=132, y=97)
tk.Label(gather_frame, text="Invert:", font=default_font, bg=gather_frame.cget('bg')).place(x=132, y=157)
tk.Label(gather_frame, text="Invert:", font=default_font, bg=gather_frame.cget('bg')).place(x=132, y=217)

field_pattern_invert_fb1 = tk.Checkbutton(gather_frame, text="F/B", variable=tk.BooleanVar(value=FieldPatternInvertFB1), state='disabled', command=nm_saveConfig)
field_pattern_invert_fb1.place(x=171, y=97)

field_pattern_invert_fb2 = tk.Checkbutton(gather_frame, text="F/B", variable=tk.BooleanVar(value=FieldPatternInvertFB2), state='disabled', command=nm_saveConfig)
field_pattern_invert_fb2.place(x=171, y=157)

field_pattern_invert_fb3 = tk.Checkbutton(gather_frame, text="F/B", variable=tk.BooleanVar(value=FieldPatternInvertFB3), state='disabled', command=nm_saveConfig)
field_pattern_invert_fb3.place(x=171, y=217)

field_pattern_invert_lr1 = tk.Checkbutton(gather_frame, text="L/R", variable=tk.BooleanVar(value=FieldPatternInvertLR1), state='disabled', command=nm_saveConfig)
field_pattern_invert_lr1.place(x=208, y=97)

field_pattern_invert_lr2 = tk.Checkbutton(gather_frame, text="L/R", variable=tk.BooleanVar(value=FieldPatternInvertLR2), state='disabled', command=nm_saveConfig)
field_pattern_invert_lr2.place(x=208, y=157)

field_pattern_invert_lr3 = tk.Checkbutton(gather_frame, text="L/R", variable=tk.BooleanVar(value=FieldPatternInvertLR3), state='disabled', command=nm_saveConfig)
field_pattern_invert_lr3.place(x=208, y=217)
set_loading_progress(22)

# Rotate Camera
tk.Label(gather_frame, text="Rotate Camera:", font=default_font, bg=gather_frame.cget('bg'), justify='center').place(x=251, y=79)
tk.Label(gather_frame, text="Rotate Camera:", font=default_font, bg=gather_frame.cget('bg'), justify='center').place(x=251, y=139)
tk.Label(gather_frame, text="Rotate Camera:", font=default_font, bg=gather_frame.cget('bg'), justify='center').place(x=251, y=199)

field_rotate_direction1 = tk.Label(gather_frame, text=FieldRotateDirection1, font=default_font, bg=gather_frame.cget('bg'), justify='center')
field_rotate_direction1.place(x=258, y=96, width=31)
frd1_left = tk.Button(gather_frame, text="<", state='disabled', command=nm_FieldRotateDirection)
frd1_left.place(x=246, y=95, width=12, height=16)
frd1_right = tk.Button(gather_frame, text=">", state='disabled', command=nm_FieldRotateDirection)
frd1_right.place(x=288, y=95, width=12, height=16)

field_rotate_direction2 = tk.Label(gather_frame, text=FieldRotateDirection2, font=default_font, bg=gather_frame.cget('bg'), justify='center')
field_rotate_direction2.place(x=258, y=156, width=31)
frd2_left = tk.Button(gather_frame, text="<", state='disabled', command=nm_FieldRotateDirection)
frd2_left.place(x=246, y=155, width=12, height=16)
frd2_right = tk.Button(gather_frame, text=">", state='disabled', command=nm_FieldRotateDirection)
frd2_right.place(x=288, y=155, width=12, height=16)

field_rotate_direction3 = tk.Label(gather_frame, text=FieldRotateDirection3, font=default_font, bg=gather_frame.cget('bg'), justify='center')
field_rotate_direction3.place(x=258, y=216, width=31)
frd3_left = tk.Button(gather_frame, text="<", state='disabled', command=nm_FieldRotateDirection)
frd3_left.place(x=246, y=215, width=12, height=16)
frd3_right = tk.Button(gather_frame, text=">", state='disabled', command=nm_FieldRotateDirection)
frd3_right.place(x=288, y=215, width=12, height=16)

field_rotate_times1 = tk.Spinbox(gather_frame, from_=1, to=4, textvariable=tk.IntVar(value=FieldRotateTimes1), state='disabled', command=nm_saveConfig)
field_rotate_times1.place(x=301, y=95, width=28, height=16)

field_rotate_times2 = tk.Spinbox(gather_frame, from_=1, to=4, textvariable=tk.IntVar(value=FieldRotateTimes2), state='disabled', command=nm_saveConfig)
field_rotate_times2.place(x=301, y=155, width=28, height=16)

field_rotate_times3 = tk.Spinbox(gather_frame, from_=1, to=4, textvariable=tk.IntVar(value=FieldRotateTimes3), state='disabled', command=nm_saveConfig)
field_rotate_times3.place(x=301, y=215, width=28, height=16)

# Until Mins
field_until_mins1 = tk.Entry(gather_frame, textvariable=tk.StringVar(value=ValidateInt(FieldUntilMins1, 10)), state='disabled', justify='center')
field_until_mins1.place(x=334, y=58, width=36, height=20)
field_until_mins1.bind("<FocusOut>", nm_saveConfig)

field_until_mins2 = tk.Entry(gather_frame, textvariable=tk.StringVar(value=ValidateInt(FieldUntilMins2, 10)), state='disabled', justify='center')
field_until_mins2.place(x=334, y=118, width=36, height=20)
field_until_mins2.bind("<FocusOut>", nm_saveConfig)

field_until_mins3 = tk.Entry(gather_frame, textvariable=tk.StringVar(value=ValidateInt(FieldUntilMins3, 10)), state='disabled', justify='center')
field_until_mins3.place(x=334, y=178, width=36, height=20)
field_until_mins3.bind("<FocusOut>", nm_saveConfig)

# Until Pack%
field_until_pack1 = tk.Label(gather_frame, text=FieldUntilPack1, font=default_font, bg=gather_frame.cget('bg'), justify='center')
field_until_pack1.place(x=375, y=60, width=16, height=16)
field_until_pack1_updown = tk.Spinbox(gather_frame, from_=1, to=20, textvariable=tk.IntVar(value=FieldUntilPack1//5), state='disabled', command=nm_FieldUntilPack)
field_until_pack1_updown.place(x=393, y=60, width=20, height=16)

field_until_pack2 = tk.Label(gather_frame, text=FieldUntilPack2, font=default_font, bg=gather_frame.cget('bg'), justify='center')
field_until_pack2.place(x=375, y=120, width=16, height=16)
field_until_pack2_updown = tk.Spinbox(gather_frame, from_=1, to=20, textvariable=tk.IntVar(value=FieldUntilPack2//5), state='disabled', command=nm_FieldUntilPack)
field_until_pack2_updown.place(x=393, y=120, width=20, height=16)

field_until_pack3 = tk.Label(gather_frame, text=FieldUntilPack3, font=default_font, bg=gather_frame.cget('bg'), justify='center')
field_until_pack3.place(x=375, y=180, width=16, height=16)
field_until_pack3_updown = tk.Spinbox(gather_frame, from_=1, to=20, textvariable=tk.IntVar(value=FieldUntilPack3//5), state='disabled', command=nm_FieldUntilPack)
field_until_pack3_updown.place(x=393, y=180, width=20, height=16)
set_loading_progress(24)

# To Hive By
tk.Label(gather_frame, text="To Hive By:", font=default_font, bg=gather_frame.cget('bg'), justify='center').place(x=327, y=79, width=93)
tk.Label(gather_frame, text="To Hive By:", font=default_font, bg=gather_frame.cget('bg'), justify='center').place(x=327, y=139, width=93)
tk.Label(gather_frame, text="To Hive By:", font=default_font, bg=gather_frame.cget('bg'), justify='center').place(x=327, y=199, width=93)

field_return_type1 = tk.Label(gather_frame, text=FieldReturnType1, font=default_font, bg=gather_frame.cget('bg'), justify='center')
field_return_type1.place(x=356, y=96, width=33)
frt1_left = tk.Button(gather_frame, text="<", state='disabled', command=nm_FieldReturnType)
frt1_left.place(x=340, y=95, width=12, height=16)
frt1_right = tk.Button(gather_frame, text=">", state='disabled', command=nm_FieldReturnType)
frt1_right.place(x=392, y=95, width=12, height=16)

field_return_type2 = tk.Label(gather_frame, text=FieldReturnType2, font=default_font, bg=gather_frame.cget('bg'), justify='center')
field_return_type2.place(x=356, y=156, width=33)
frt2_left = tk.Button(gather_frame, text="<", state='disabled', command=nm_FieldReturnType)
frt2_left.place(x=340, y=155, width=12, height=16)
frt2_right = tk.Button(gather_frame, text=">", state='disabled', command=nm_FieldReturnType)
frt2_right.place(x=392, y=155, width=12, height=16)

field_return_type3 = tk.Label(gather_frame, text=FieldReturnType3, font=default_font, bg=gather_frame.cget('bg'), justify='center')
field_return_type3.place(x=356, y=216, width=33)
frt3_left = tk.Button(gather_frame, text="<", state='disabled', command=nm_FieldReturnType)
frt3_left.place(x=340, y=215, width=12, height=16)
frt3_right = tk.Button(gather_frame, text=">", state='disabled', command=nm_FieldReturnType)
frt3_right.place(x=392, y=215, width=12, height=16)

# Sprinkler Location
field_sprinkler_loc1 = tk.Label(gather_frame, text=FieldSprinklerLoc1, font=default_font, bg=gather_frame.cget('bg'), justify='center')
field_sprinkler_loc1.place(x=427, y=61, width=60)
fsl1_left = tk.Button(gather_frame, text="<", state='disabled', command=nm_FieldSprinklerLoc)
fsl1_left.place(x=415, y=60, width=12, height=16)
fsl1_right = tk.Button(gather_frame, text=">", state='disabled', command=nm_FieldSprinklerLoc)
fsl1_right.place(x=486, y=60, width=12, height=16)

field_sprinkler_loc2 = tk.Label(gather_frame, text=FieldSprinklerLoc2, font=default_font, bg=gather_frame.cget('bg'), justify='center')
field_sprinkler_loc2.place(x=427, y=121, width=60)
fsl2_left = tk.Button(gather_frame, text="<", state='disabled', command=nm_FieldSprinklerLoc)
fsl2_left.place(x=415, y=120, width=12, height=16)
fsl2_right = tk.Button(gather_frame, text=">", state='disabled', command=nm_FieldSprinklerLoc)
fsl2_right.place(x=486, y=120, width=12, height=16)

field_sprinkler_loc3 = tk.Label(gather_frame, text=FieldSprinklerLoc3, font=default_font, bg=gather_frame.cget('bg'), justify='center')
field_sprinkler_loc3.place(x=427, y=181, width=60)
fsl3_left = tk.Button(gather_frame, text="<", state='disabled', command=nm_FieldSprinklerLoc)
fsl3_left.place(x=415, y=180, width=12, height=16)
fsl3_right = tk.Button(gather_frame, text=">", state='disabled', command=nm_FieldSprinklerLoc)
fsl3_right.place(x=486, y=180, width=12, height=16)

# Sprinkler Distance
tk.Label(gather_frame, text="Distance:", font=default_font, bg=gather_frame.cget('bg'), justify='center').place(x=415, y=79, width=86)
tk.Label(gather_frame, text="Distance:", font=default_font, bg=gather_frame.cget('bg'), justify='center').place(x=415, y=139, width=86)
tk.Label(gather_frame, text="Distance:", font=default_font, bg=gather_frame.cget('bg'), justify='center').place(x=415, y=199, width=86)

field_sprinkler_dist1 = tk.Spinbox(gather_frame, from_=1, to=10, textvariable=tk.IntVar(value=FieldSprinklerDist1), state='disabled', command=nm_saveConfig)
field_sprinkler_dist1.place(x=440, y=95, width=32, height=16)

field_sprinkler_dist2 = tk.Spinbox(gather_frame, from_=1, to=10, textvariable=tk.IntVar(value=FieldSprinklerDist2), state='disabled', command=nm_saveConfig)
field_sprinkler_dist2.place(x=440, y=155, width=32, height=16)

field_sprinkler_dist3 = tk.Spinbox(gather_frame, from_=1, to=10, textvariable=tk.IntVar(value=FieldSprinklerDist3), state='disabled', command=nm_saveConfig)
field_sprinkler_dist3.place(x=440, y=215, width=32, height=16)
set_loading_progress(26)

# CREDITS TAB
credits_frame = tabs["credits"]

contributors_dev_image = tk.Label(credits_frame, image=None, bg=credits_frame.cget('bg'))
contributors_dev_image.place(x=5, y=24)

contributors_image = tk.Label(credits_frame, image=None, bg=credits_frame.cget('bg'))
contributors_image.place(x=253, y=24)

tk.Label(credits_frame, text="Development", font=bold_font, fg="white", bg=credits_frame.cget('bg'), wraplength=225).place(x=15, y=28, width=225)
tk.Label(credits_frame, text="Supporters", font=bold_font, fg="white", bg=credits_frame.cget('bg'), wraplength=225).place(x=261, y=28, width=225)

tk.Label(credits_frame, text="Special Thanks to the developers and testers!\nClick the names to view their Discord profiles!", font=default_font, fg="white", bg=credits_frame.cget('bg'), wraplength=225).place(x=18, y=43, width=225)
tk.Label(credits_frame, text="Thank you for your donations and contributions to this project!", font=default_font, fg="white", bg=credits_frame.cget('bg'), wraplength=180).place(x=264, y=43, width=180)

contributors_left = tk.Button(credits_frame, text="<", state='disabled', command=nm_ContributorsPageButton)
contributors_left.place(x=440, y=46, width=18, height=18)

contributors_right = tk.Button(credits_frame, text=">", state='disabled', command=nm_ContributorsPageButton)
contributors_right.place(x=464, y=46, width=18, height=18)
set_loading_progress(27)

# MISC TAB
misc_frame = tabs["misc"]

tk.LabelFrame(misc_frame, text="Hive Tools", font=bold_font).place(x=5, y=24, width=160, height=144)
tk.LabelFrame(misc_frame, text="Other Tools", font=bold_font).place(x=5, y=168, width=160, height=62)
tk.LabelFrame(misc_frame, text="Calculators", font=bold_font).place(x=170, y=24, width=160, height=144)
auto_clicker_frame = tk.LabelFrame(misc_frame, text=f"AutoClicker ({AutoClickerHotkey})", font=bold_font)
auto_clicker_frame.place(x=170, y=168, width=160, height=62)
tk.LabelFrame(misc_frame, text="Macro Tools", font=bold_font).place(x=335, y=24, width=160, height=84)
tk.LabelFrame(misc_frame, text="Discord Tools", font=bold_font).place(x=335, y=108, width=160, height=60)
tk.LabelFrame(misc_frame, text="Bugs and Suggestions", font=bold_font).place(x=335, y=168, width=160, height=62)

basic_egg_hatcher_button = tk.Button(misc_frame, text="Gifted Basic Bee\nAuto-Hatcher", font=("Tahoma", 9), state='disabled', command=nm_BasicEggHatcher)
basic_egg_hatcher_button.place(x=10, y=40, width=150, height=40)

bitterberry_feeder_button = tk.Button(misc_frame, text="Bitterberry\nAuto-Feeder", font=("Tahoma", 9), state='disabled', command=nm_BitterberryFeeder)
bitterberry_feeder_button.place(x=10, y=82, width=150, height=40)

auto_mutator_button = tk.Button(misc_frame, text="Auto-Jelly", font=("Tahoma", 9), state='disabled', command=blc_mutations)
auto_mutator_button.place(x=10, y=124, width=150, height=40)

generate_bee_list_button = tk.Button(misc_frame, text="Export Hive Bee List\n(for Hive Builder)", font=("Tahoma", 9), state='disabled', command=nm_GenerateBeeList)
generate_bee_list_button.place(x=10, y=184, width=150, height=42)

ticket_shop_calculator_button = tk.Button(misc_frame, text="Ticket Shop Calculator\n(Google Sheets)", font=("Tahoma", 9), state='disabled', command=nm_TicketShopCalculatorButton)
ticket_shop_calculator_button.place(x=175, y=40, width=150, height=40)

ssa_calculator_button = tk.Button(misc_frame, text="SSA Calculator\n(Google Sheets)", font=("Tahoma", 9), state='disabled', command=nm_SSACalculatorButton)
ssa_calculator_button.place(x=175, y=82, width=150, height=40)

bond_calculator_button = tk.Button(misc_frame, text="Bond Calculator\n(Google Sheets)", font=("Tahoma", 9), state='disabled', command=nm_BondCalculatorButton)
bond_calculator_button.place(x=175, y=124, width=150, height=40)

auto_clicker_gui = tk.Button(auto_clicker_frame, text="AutoClicker\nSettings", font=("Tahoma", 9), state='disabled', command=nm_AutoClickerButton)
auto_clicker_gui.place(x=175, y=184, width=150, height=42)

hotkey_gui = tk.Button(misc_frame, text="Change Hotkeys", font=("Tahoma", 9), state='disabled', command=nm_HotkeyGUI)
hotkey_gui.place(x=340, y=40, width=150, height=20)

debug_log_gui = tk.Button(misc_frame, text="Debug Log Options", font=("Tahoma", 9), state='disabled', command=nm_DebugLogGUI)
debug_log_gui.place(x=340, y=62, width=150, height=20)

auto_start_manager_gui = tk.Button(misc_frame, text="Auto-Start Manager", font=("Tahoma", 9), state='disabled', command=nm_AutoStartManager)
auto_start_manager_gui.place(x=340, y=84, width=150, height=20)

night_announcement_gui = tk.Button(misc_frame, text="Night Detection\nAnnouncement", font=("Tahoma", 9), state='disabled', command=nm_NightAnnouncementGUI)
night_announcement_gui.place(x=340, y=124, width=150, height=40)

report_bug_button = tk.Button(misc_frame, text="Report Bugs", font=("Tahoma", 9), state='disabled', command=nm_ReportBugButton)
report_bug_button.place(x=340, y=184, width=150, height=20)

make_suggestion_button = tk.Button(misc_frame, text="Make Suggestions", font=("Tahoma", 9), state='disabled', command=nm_MakeSuggestionButton)
make_suggestion_button.place(x=340, y=206, width=150, height=20)

# STATUS TAB
status_frame = tabs["status"]

tk.LabelFrame(status_frame, text="Status Log", font=bold_font).place(x=5, y=23, width=240, height=210)
tk.LabelFrame(status_frame, text="Stats", font=bold_font).place(x=250, y=23, width=245, height=160)
tk.LabelFrame(status_frame, text="Discord Integration", font=bold_font).place(x=250, y=185, width=245, height=48)

status_log_reverse = tk.Checkbutton(status_frame, text="Reverse Order", variable=tk.BooleanVar(value=StatusLogReverse), state='disabled', command=nm_StatusLogReverseCheck)
status_log_reverse.place(x=85, y=23)

status_log = tk.Text(status_frame, height=15, width=30, font=default_font, bg=status_frame.cget('bg'), wrap='none', state='disabled')
status_log.place(x=10, y=37)

tk.Label(status_frame, text="Total", font=bold_font).place(x=255, y=40)
tk.Label(status_frame, text="Session", font=bold_font).place(x=375, y=40)

total_stats = tk.Label(status_frame, text="", font=default_font, wraplength=119)
total_stats.place(x=255, y=55, width=119, height=120)

session_stats = tk.Label(status_frame, text="", font=default_font, wraplength=119)
session_stats.place(x=375, y=55, width=119, height=120)

reset_total_stats = tk.Button(status_frame, text="Reset", state='disabled', command=nm_ResetTotalStats)
reset_total_stats.place(x=290, y=39, width=50, height=15)

webhook_gui = tk.Button(status_frame, text="Change Discord Settings", state='disabled', command=nm_WebhookGUI)
webhook_gui.place(x=265, y=202, width=215, height=24)

nm_setStats()
set_loading_progress(28)

# SETTINGS TAB line 2544
