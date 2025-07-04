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
    "festiveplanter": {
        "bitmap": "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"
	,    "name": "Festive Planter", 
         "color": 12368237
    },
    "heattreatedplanter": {
        "bitmap": "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"
	    "name": "Heat-Treated Planter", 
        "color": 10172428
    },
    "hydroponicplanter": {
    "bitmap": "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"
	"name": "Ticket Planter", 
    "color": 14668392
    },
    "paperplanter": {
    "bitmap": "iVBORw0KGgoAAAANSUhEUgAAACgAAAAoCAMAAAC7IEhfAAAB+1BMVEUAAAA2NTUhISElJSUkJCQ1NTU1NTUcHBw2NjY0NDQwMDAzMzMwMTEvLy81NTU0NDQyMjI0NDQzMzMYGBg2NjY0NDQzMzM0NDQzMzMxMTEvLy8yMjIvLy81NTU1NTU1NTU0NDMxMjIwMDAuLi4uLi4mJiYkJCQ1NTU1NzYwMC8wMDDRqmO6m13PqWPMqGK6m143NjbDoF+4mlw8OTbFoV/Cn126m1y2mFusj1bOqWPOqGK7m1y1lluafknJpWC4mVypjFSnilOliFFAPDaukVl0uyjLp2Gxk1mojFaOdUU5ODbHomDBnl+7nF6+nFylild3ZUaMc0WUbT6Tajw1NjTBnly3llyylVqqjVerjVShg1CHcUt7aUmNdUeeeUZzYkNlWD5jVT2PaDtWSztKRDh8XTdxtyhqpydopibVr2nSq2TRq2TLp2K3mmG/nWDIo1+iiFSfhVKfgUyMdEyDcEuddUSGb0RuXkJqXEGCXziBzTJjmS1rridpqiasjVScgVKWflGafEiYdESDbUOPdD2SaDxeUjtRRztNRThHQThEPziBmTeLfzeH1TV5pTJTezBqpi12wCpwtSamjl62kFWNeU6gfUqNa0KGhT+FhTY7RTZ7qjROcjFLaTFoozBYhzBIZzB3lS98qy54nC5Zhi55xC14ni10uClnpiiaiWq0AAAAK3RSTlMA+xIhCf3zBffIdW9kP+O7tqWVDOqtoaB9aF47M+bZzsFXUTcrGRbr0IRzNB0GUAAAA0xJREFUOMuF1HdTGkEYBnAOETGiRo0ajek9LFwHjl4FFBAEe+8l9hZj7z229N7Lx8zdrsAZx/D8czPcb95375kdJP8kLSUXi8pzZZIkkRVg0Y+zX7CbyVwOcfB5du7wXX4SeBs7mPnZPdfz4WqS3ZnRT89m3Me9P7CHykyZVJp23uZC4pCH3T2zdBmtuK5QZF+5VVx85zTKk94qSCc23h8d8XDfN9W05WxtLcMIJ30pU+yU9xUYTbf5dt1u91zvvtlsnmoym1dbxgcrdq7L4uXJihRbbR1TTU3hN7/d3fO9u8vLZj5jC3V+ozaUmhJzhXKsM+zz+cLh8Nq34/k/PXuRyvaVV2NDRi0AoDEOM7HG54MLvvqVykgksvZ1vvd7ZfvT1wFrtRHwwVuu5Z3AImKwr089zL3g3z/t6nr7a299fbJaqwVCdPaO9NgRS1JH+/tVKpWmqo9pnmyOtHd11Q8hRukd+u3cGLyHjfc/VsGoOTXZXDnZPCQoq8fucFm99IV4hVenObUqFo61WEAABx6Hw6WjKGqEeBQvsZB2kSTJlMasBsdr7HpXDdy+lJoovARr4F8bLCRLlnIC1Nn0VlxvgrABtoMixSbQKIYpZ/1+MqjXaQFeR0E4LobyEDpjFXyoSQHE4BJRnLj/N6YN8GwsGuyH0IZgBfpqlItP4ChLOXQGI4JWCF3Os5AZEEEAP0YLvGVi2AIhqUHtQId7PGi1COZlNUJBok8qRdBhh8/FqFJUTwMUrBiavEhOiOq5g43AlUbxapuOqvcEAAjJ78ahktAL9fktbALq7IGAacwKqNZ0STxFdDXvWI2qSgOhloe1JqGhUauuUwTznQx0j8uHUT3CQC3cX+915iRgducAxwrDuKD6BNaZAEztKqEUwQ4La4BXt5wRVgsDAYqrVZ4i6nunmju54VUWCPU1iDVsY5fTEjAD21zUIGkIGgTowIUjjmwSWTeRQ0nLuEaETCdtB9UWoPPiAHganZcypJLTkRbI6SdehhOOSQ7DzaMdqelXJGdTkiOPdoZspSp1kAEOinrJjzvnTzIl44acaKsdYIymWusE/QCNO8deziprqzDZKlqIbKnkv7nH0+kNpyKHd0lyN59Q5N4+8/NfEj3vSXiPm+wAAAAASUVORK5CYII="
    "name": "Paper Planter",
    "color": 15844367
    },
    "plasticplanter ": {
    "bitmap": "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"
	"name": "Ticket Planter", 
    "color": 14668392
    },
    "petalplanter" : {
    "bitmap": "VBORw0KGgoAAAANSUhEUgAAACgAAAAoCAMAAAC7IEhfAAAC+lBMVEUAAAAmJiYvLy8uLi4tLS00NDU9PDs1NjY1NTUzMzMvLy8yMjItLS01NTVOTU06OjksLCxFRUU2NjY2NjY3Nzc0NDU0NDQxMTEzMzMyMjIzMzMxMTEzMzMyMjIwMDA/Pz81NTQ1NTUzMzMyMjJGRkdFQzkzMzQ1NTU0NDQ0NDQvLy8uLi4xMTEvLy80NDQzMzM0NDQzMzPj25ru7e3w7u7q6eno6Ojq6urx7+/s6+vLy8vt7Ow1NTXi4eHR0NDNzc1TU1Py8PDk4+Pu6tvAvr7i2pfc1ZWRkZHCu4P15WtjY2La2tnW1dXFxcTx7MHY0ZDx7d7f3czJyMiY3arm36mb3amtrKnj25TTzIs3ODb08vHm5eXw7OPy7L25uLjk37Tw6qzY0qPl3Zjo35DRyonMxYbf03/r3W9KSkru7u7u7Ojw7NHBxMLU0b/o5L3x67ap3LPz7LClpKTk3Z/l35Ta05Hg15DFv4X87HBubm1nZ2fFuWVfXl5aWlp6c0lUUTszMzTq5+De3t3079jq5tDNzsm8vLvm37CxsLDo4q/Qzamn3KXs5aK33qKu16Df2p/t5p2bm5v88JfI0ZLUzY7X0IqJiInXzoF8fHt0c3Ph0nHw43D252/e0G6UkWze0WbTxWJCQkLm5NfT39XK3szY1cnKy8O70cLd2cDe2rfHxrPs5rLM27Lr5a+i16/+867f2qyb2qz/9KPI3KLB3KLN3KCgoKDa2pjq5JaXl5bk2Yrk44nf1IXz54T77YGPjYHn23nIzXnw4njcz3VslHTazW/j1WqCfl/CtlyAelBYXElASkJKRzfS0tLa2M/l4cbC0sbA0cXW3sTGzMSw3bqu0LavyLXr5rTB0LDBv6ilsKja1qe3taSUy6Hw5Z6Oy56x1pe/upGopo6fnYyMjIz/8IiAr4jw44aDg4Pr3n6hnHusp3nr3nfQxnavqnaNl3LEuXFohWlbfmWrpGSHg2JmZWGPiV6xp1uellJxblBGVkpVVERrZkFgWz6Xs/S3AAAAMnRSTlMABGwlCNH7+7euMCsN8f7+Fv749Orevod2XllPQzsS+NnIoEn+++vMqJNnHxq3moqAcBcpbV4AAASCSURBVDjLdZRlVBRRGIZn2aKWBgkRAbudOz1ssCys7LKklLSCdKMIgmJ3KyFSdnd3d3d3d7fneJdQQXj+zJ9n3u++57vnIg20se+io6Nj25tvXGNaY2yhp1OLXTcO0hgDJwtTIyNTgZmsTDlDWaoSCNvJZDJTc13brpxGnp4gT7l587Y9e26m+vktTb1WeeRBUFCWMi9BpGf/1+To6zmURjKS035pUVdWrFo1efJkd4++E6KWpo6doRLqchs8fWsrwdOx0kVn0iZke8wOiQ2Z4zNocHBOztbpfZeNCSoUOenXZZp0NjcqVniNHB09PXhOXG6fWnJz42ZPW5Ee7eeVZWSma1Arcrurghg5DZKSo6dvzckJnrb2RkxMzNqoNO+IiOQkUq7IE3Y2qRPzx4YBFrB0eHJ6dHp0ZoQ3JCI9MzPCDcdxGlcUiOy0w/WtEhQ0SQMSZ/ER4Unh4b6+br6+o7yTfZMIAgcAEytdrHkI0q2XqHgkzWIYS9ByAhA4SeIEQVOAoFicBBiGgfGmndogPB2HPA0JPUATpJim8VoIPDGRoDCKoqBIKWR6bRBDJ9l4ggYYIAlcLgYkCSA0QbCkmKX69XN1hXqkERS5jrJIFgAWxsglatgJgwCcoMUMoya0KgaCaqBo41CsTgQsESYf6R/pBTUtNDypOiWFkagJ134ULNPDENExyvI6JfFS+y08q9HUi4DESbFEI5Uy/l44BfxVQhse0kUgUxUU5N9fmbFEykhICgPwvCwbpmYYrThmQaJ4W2hHuBoDXUtLC6Hxm0mrz0kZhqAAScPIsAVLUhjoLb56Ua6QmVkbwptjaMJtZfH9cUDGBc3y5fMxGtYmxQsz1l3WSJnFE6feul7mUr9rxJ5/4uCdSRsmToxBR8PJgJh/PiMgYHXKmNSYOXffhbrwnetvZOu2J94f3Fe+fwCaPdrNd9Qo79s7pgQGrLu0cprP3n3Hza1sDJE6unXuUHSy2tNz/4DsqAmZa9bMnOepNQM3euwsrz5p6cxDGujq3LP90fj4+O0o2n/m+vVQfLllChR99npWDW+rj/yDncWwoRUVO93R/rt2P9odf3ig+4bASbNK4j2rfjUWuR0Fw4YeGuiOogOGDJk398BgdFPg1NgDh6uONknktOZDc2AwCiOHeM6Ff2yaOqukovrrcKEjF2lsdjQe9nYwCiOhCL9bZpUcGnqsvbmjDQdpYjq6fPZBYeSTcu0RBsW++vIztEMP7eAmpjP/eC6qjXwG27uHxH0YXsS3NkH+x7BV6AsPbWRwsDawz7ciKzse0hy2HSoHofX4xL5ub2nLadaDOz/iU+/ByZUu8C1pHjvLjw2iR0jcMWHPFgINrNo99/gj9vkh6t28x+viMGPRuOx6cfa9T2atYJVmSxf4U25p4/pCxkUt8xsfqte1BbFQg1FYuBtkxAi5ODK0hTI8a4FSQgDKFQLCxJKHRZ1MmhU59vx2ZcogBSOVSBhFVmmCeS9OC21s+WbGCYUqVX6+qjDBWNTJAGkBHtfGSeRSh1C3tUmjwN/oJXePXBRgLQAAAABJRU5ErkJggg=="
    "name": "Petal Planter",
    "color": 15856111
    },
    "planterofplenty": {
    "bitmap": "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"
    "name": "The Planter Of Plenty",
    "color": 15770372
    }    
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
        if 'color_index' not in globals():
            globals()['color_index'] = 0
        else:
            globals()['color_index'] = (globals()['color_index'] % 7) + 1
        return colors[globals()['color_index']]
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
      #     Discord.get_commands(MainChannelID)
      #  if not command_buffer.empty():
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
