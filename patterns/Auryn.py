import pyautogui
import time

# Configuration
reps = 1  # Number of repetitions, adjust as needed
size = 1  # Size factor, adjust as needed
AurynDelay = 175  # Base delay in milliseconds

# Key bindings (customize based on your game controls)
TCFBKey = 'w'  # Forward
TCLRKey = 'a'  # Left
AFCFBKey = 's'  # Backward
AFCLRKey = 'd'  # Right

for i in range(1, reps + 1):
    # Base duration for this iteration
    base = AurynDelay * 9 / 2000 * size * i * 1.1
    
    # Infinity pattern
    pyautogui.keyDown(TCFBKey)
    time.sleep(base)
    pyautogui.keyDown(TCLRKey)
    time.sleep(base * 1.4)
    pyautogui.keyUp(TCFBKey)
    time.sleep(base)
    pyautogui.keyDown(AFCFBKey)
    time.sleep(base * 3 * 1.4)
    pyautogui.keyUp(AFCFBKey)
    time.sleep(base)
    pyautogui.keyDown(TCFBKey)
    time.sleep(base * 1.4)
    pyautogui.keyUp(TCLRKey)
    time.sleep(base)
    pyautogui.keyDown(AFCLRKey)
    time.sleep(base * 1.4)
    pyautogui.keyUp(TCFBKey)
    time.sleep(base)
    pyautogui.keyDown(AFCFBKey)
    time.sleep(base * 3 * 1.4)
    pyautogui.keyUp(AFCFBKey)
    time.sleep(base)
    pyautogui.keyDown(TCFBKey)
    time.sleep(base * 1.4)
    pyautogui.keyUp(AFCLRKey)
    
    # Big circle
    time.sleep(base * 2)
    pyautogui.keyDown(TCLRKey)
    time.sleep(base * 2 * 1.4)
    pyautogui.keyUp(TCFBKey)
    time.sleep(base * 2)
    pyautogui.keyDown(AFCFBKey)
    time.sleep(base * 2 * 1.4)
    pyautogui.keyUp(TCLRKey)
    time.sleep(base * 2)
    pyautogui.keyDown(AFCLRKey)
    time.sleep(base * 2 * 1.4)
    pyautogui.keyUp(AFCFBKey)
    time.sleep(base * 2)
    pyautogui.keyDown(TCFBKey)
    time.sleep(base * 2 * 1.4)
    pyautogui.keyUp(AFCLRKey)
    
    # FLIP!! (move to other side - half circle)
    time.sleep(base * 2)
    pyautogui.keyDown(TCLRKey)
    time.sleep(base * 2 * 1.4)
    pyautogui.keyUp(TCFBKey)
    time.sleep(base * 2)
    pyautogui.keyDown(AFCFBKey)
    time.sleep(base * 2 * 1.4)
    pyautogui.keyUp(TCLRKey)
    pyautogui.keyUp(AFCFBKey)
    time.sleep(0.05)  # HyperSleep(50)
    
    # Reverse infinity
    pyautogui.keyDown(AFCFBKey)
    time.sleep(base)
    pyautogui.keyDown(AFCLRKey)
    time.sleep(base * 1.4)
    pyautogui.keyUp(AFCFBKey)
    time.sleep(base)
    pyautogui.keyDown(TCFBKey)
    time.sleep(base * 3 * 1.4)
    pyautogui.keyUp(TCFBKey)
    time.sleep(base)
    pyautogui.keyDown(AFCFBKey)
    time.sleep(base * 1.4)
    pyautogui.keyUp(AFCLRKey)
    time.sleep(base)
    pyautogui.keyDown(TCLRKey)
    time.sleep(base * 1.4)
    pyautogui.keyUp(AFCFBKey)
    time.sleep(base)
    pyautogui.keyDown(TCFBKey)
    time.sleep(base * 1.4)
    pyautogui.keyUp(TCFBKey)
    time.sleep(base)
    pyautogui.keyDown(AFCFBKey)
    time.sleep(base * 1.4)
    pyautogui.keyUp(TCLRKey)
    
    # Big circle
    time.sleep(base * 2)
    pyautogui.keyDown(AFCLRKey)
    time.sleep(base * 2 * 1.4)
    pyautogui.keyUp(AFCFBKey)
    time.sleep(base * 2)
    pyautogui.keyDown(TCFBKey)
    time.sleep(base * 2 * 1.4)
    pyautogui.keyUp(AFCLRKey)
    time.sleep(base * 2)
    pyautogui.keyDown(TCLRKey)
    time.sleep(base * 2 * 1.4)
    pyautogui.keyUp(TCFBKey)
    time.sleep(base * 2)
    pyautogui.keyDown(AFCFBKey)
    time.sleep(base * 2 * 1.4)
    pyautogui.keyUp(TCLRKey)
    
    # FLIP!! (move to other side - half circle)
    time.sleep(base * 2)
    pyautogui.keyDown(AFCLRKey)
    time.sleep(base * 2 * 1.4)
    pyautogui.keyUp(AFCFBKey)
    time.sleep(base * 2)
    pyautogui.keyDown(TCFBKey)
    time.sleep(base * 2 * 1.4)
    pyautogui.keyUp(AFCLRKey)
    pyautogui.keyUp(TCFBKey)
