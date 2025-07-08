import pyautogui
import time

# Key mappings (adjust based on game controls)
TCFBKey = 'w'  # Forward
TCLRKey = 'a'  # Left
AFCFBKey = 's' # Backward
AFCLRKey = 'd' # Right

# Parameters
reps = 1  # Number of repetitions, adjust as needed
size = 1  # Size factor for movement duration, adjust as needed

def walk(key, duration):
    """
    Press and hold a key for a specified duration.
    
    :param key: The key to press.
    :param duration: Duration to hold the key in seconds.
    """
    pyautogui.keyDown(key)
    time.sleep(duration)
    pyautogui.keyUp(key)

try:
    # First loop: towards center
    for _ in range(reps):
        walk(TCFBKey, 11 * size)
        walk(TCLRKey, 1)
        walk(AFCFBKey, 11 * size)
        walk(TCLRKey, 1)
    
    # Second loop: away from center
    for _ in range(reps):
        walk(TCFBKey, 11 * size)
        walk(AFCLRKey, 1)
        walk(AFCFBKey, 11 * size)
        walk(AFCLRKey, 1)
    
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    # Ensure all keys are released
    for key in [TCFBKey, TCLRKey, AFCFBKey, AFCLRKey]:
        pyautogui.keyUp(key)