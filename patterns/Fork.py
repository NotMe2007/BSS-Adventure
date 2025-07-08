import pyautogui
import time
import math

# Key mappings
FwdKey = 'w'      # Forward
TCLRKey = 'a'     # Left
AFCLRKey = 'd'    # Right
AFCFBKey = 's'    # Backward
TCFBKey = 'w'     # Alias for forward key (assumed from context)

# Example input values (adjust as needed)
reps = 1          # Number of loop repetitions
size = 1          # Scaling factor for movement length
facingcorner = True  # Whether facing a corner initially

# Movement calculations
CForkGap = 0.75
CForkDiagonal = CForkGap * math.sqrt(2)
CForkLength = (40 - CForkGap * 16 - CForkDiagonal * 4) / 6

# Initial movement if facing a corner
if facingcorner:
    pyautogui.keyDown(FwdKey)
    time.sleep(1.5)
    pyautogui.keyUp(FwdKey)

# Start movement sequence
pyautogui.keyDown(TCLRKey)    # Press left
pyautogui.keyDown(AFCFBKey)   # Press backward
time.sleep(CForkDiagonal * 2) # Walk diagonally

pyautogui.keyUp(AFCFBKey)     # Release backward
time.sleep(((reps - 1) * 4 + 2) * CForkGap)  # Walk with left

pyautogui.keyDown(TCFBKey)    # Press forward
time.sleep(CForkDiagonal * 2) # Walk diagonally

pyautogui.keyUp(TCLRKey)      # Release left, now only forward is pressed

# Repeat movement pattern 'reps' times
for _ in range(reps):
    time.sleep(CForkLength * size)  # Walk forward
    
    pyautogui.keyUp(TCFBKey)        # Release forward
    pyautogui.keyDown(AFCLRKey)     # Press right
    time.sleep(CForkGap * 2)        # Walk right
    
    pyautogui.keyUp(AFCLRKey)       # Release right
    pyautogui.keyDown(AFCFBKey)     # Press backward
    time.sleep(CForkLength * size)  # Walk backward
    
    pyautogui.keyUp(AFCFBKey)       # Release backward
    pyautogui.keyDown(AFCLRKey)     # Press right
    time.sleep(CForkGap * 2)        # Walk right
    
    pyautogui.keyUp(AFCLRKey)       # Release right
    pyautogui.keyDown(TCFBKey)      # Press forward

# Final movement sequence after loop
time.sleep(CForkLength * size)      # Walk forward

pyautogui.keyUp(TCFBKey)            # Release forward
pyautogui.keyDown(AFCLRKey)         # Press right
time.sleep(CForkGap * 2)            # Walk right

pyautogui.keyUp(AFCLRKey)           # Release right
pyautogui.keyDown(AFCFBKey)         # Press backward
time.sleep(CForkLength * size)      # Walk backward

pyautogui.keyUp(AFCFBKey)           # Release backward