import pyautogui
import time
import math

# Define movement keys (adjust based on game controls)
TCLRKey = 'a'    # Left
TCFBKey = 'w'    # Forward
AFCLRKey = 'd'   # Right
AFCFBKey = 's'   # Backward

# Define variables (adjust as needed)
size = 1  # Scaling factor
reps = 1  # Repetition factor

def walk(distance, keys):
    for key in keys:
        pyautogui.keyDown(key)
    time.sleep(distance)  # Duration in seconds; may need adjustment
    for key in keys:
        pyautogui.keyUp(key)

# Movement sequence
walk(4 * size, [TCLRKey])
walk(2 * size, [TCFBKey])
walk(8 * size, [AFCLRKey])
walk(2 * size, [TCFBKey])
walk(8 * size, [TCLRKey])
walk(8 * size * math.sqrt(2), [AFCLRKey, AFCFBKey])  # Diagonal right-backward
walk(8 * size, [TCLRKey])
walk(2 * size, [TCFBKey])
walk(8 * size, [AFCLRKey])
walk(6.7 * size + 10, [TCFBKey])
walk(6 + reps, [AFCLRKey])
walk(3, [AFCLRKey, TCFBKey])  # Diagonal right-forward
walk(2 + reps, [TCLRKey])
walk(5, [AFCFBKey])
walk(8 * size, [TCLRKey])
walk(2 * size, [AFCFBKey])
walk(8 * size, [AFCLRKey])
walk(2 * size, [AFCFBKey])
walk(8 * size, [TCLRKey])
walk(2 * size, [AFCFBKey])
walk(8 * size, [AFCLRKey])
walk(3 * size, [AFCFBKey])
walk(8 * size, [TCLRKey])
walk(4 * size * math.sqrt(2), [TCFBKey, AFCLRKey])  # Diagonal forward-right