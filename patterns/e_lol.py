import pyautogui
import time

# Configuration
spacingDelay = 274  # in milliseconds
reps = 1            # number of repetitions
size = 1            # size factor
facingcorner = 0    # adjust based on context

# Key bindings
TCLRKey = 'a'    # left
AFCFBKey = 's'   # backward
AFCLRKey = 'd'   # right
TCFBKey = 'w'    # forward

def walk(key, duration):
    pyautogui.keyDown(key)
    time.sleep(duration)
    pyautogui.keyUp(key)

# Initial movement
walk(TCLRKey, spacingDelay * 9 / 2000 * (reps * 2 + 1))
walk(AFCFBKey, 5 * size)

# First loop
for _ in range(reps):
    walk(AFCLRKey, spacingDelay * 9 / 2000)
    walk(TCFBKey, 5 * size)
    walk(AFCLRKey, spacingDelay * 9 / 2000)
    walk(AFCFBKey, (1094 + 25 * facingcorner) * 9 / 2000 * size)

# Intermediate movement
walk(TCLRKey, spacingDelay * 9 / 2000 * (reps * 2 + 0.5))
walk(TCFBKey, 5 * size)

# Second loop
for _ in range(reps):
    walk(AFCLRKey, spacingDelay * 9 / 2000)
    walk(AFCFBKey, (1094 + 25 * facingcorner) * 9 / 2000 * size)
    walk(AFCLRKey, spacingDelay * 9 / 2000 * 1.5)
    walk(TCFBKey, 5 * size)