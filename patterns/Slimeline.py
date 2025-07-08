import pyautogui
import time

# Define keys (customize based on your game's controls)
TCLRKey = 'a'  # Left movement key
AFCLRKey = 'd' # Right movement key

# Define parameters (adjust these values as needed)
size = 1  # Base duration multiplier
reps = 1  # Repetition factor

# Calculate durations in seconds
first_duration = (4 * size) + (reps * 0.1) - 0.1
second_duration = 8 * size
third_duration = 4 * size

def walk(key, duration):
    """
    Simulates holding a key down for a specified duration.
    
    Args:
        key (str): The key to press.
        duration (float): Duration to hold the key in seconds.
    """
    pyautogui.keyDown(key)
    time.sleep(duration)
    pyautogui.keyUp(key)

# Execute the movement sequence
try:
    walk(TCLRKey, first_duration)   # Move left
    walk(AFCLRKey, second_duration) # Move right
    walk(TCLRKey, third_duration)   # Move left again
finally:
    # Ensure all keys are released if the script is interrupted
    pyautogui.keyUp(TCLRKey)
    pyautogui.keyUp(AFCLRKey)