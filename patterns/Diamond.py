import pyautogui
import time

# Configuration
reps = 1  # Number of repetitions, adjust as needed
size = 1  # Size factor, adjust as needed

# Key bindings (customize based on your game controls)
TCFBKey = 'w'  # Forward
TCLRKey = 'a'  # Left
AFCLRKey = 'd' # Right
AFCFBKey = 's' # Backward

for i in range(1, reps + 1):
    duration = 5 * size + i
    duration_sec = duration / 1000.0  # Convert milliseconds to seconds
    
    # Step 1: Press forward and left (diagonal forward-left)
    pyautogui.keyDown(TCFBKey)
    pyautogui.keyDown(TCLRKey)
    time.sleep(duration_sec)
    
    # Step 2: Release left, press right (diagonal forward-right)
    pyautogui.keyUp(TCLRKey)
    pyautogui.keyDown(AFCLRKey)
    time.sleep(duration_sec)
    
    # Step 3: Release forward, press backward (diagonal backward-right)
    pyautogui.keyUp(TCFBKey)
    pyautogui.keyDown(AFCFBKey)
    time.sleep(duration_sec)
    
    # Step 4: Release right, press left (diagonal backward-left)
    pyautogui.keyUp(AFCLRKey)
    pyautogui.keyDown(TCLRKey)
    time.sleep(duration_sec)
    
    # Step 5: Release left and backward to stop movement
    pyautogui.keyUp(TCLRKey)
    pyautogui.keyUp(AFCFBKey)