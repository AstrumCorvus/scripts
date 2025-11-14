import pyautogui
import time

# Wait a few seconds to give you time to switch to the target application
print("Starting in 3 seconds...")
time.sleep(3) 

# 1. Define the path to your button image
button_image_path = r'C:\Users\User\Pictures\Captura de pantalla 2025-11-03 112518.png'

print(f"Searching for '{button_image_path}' on screen...")

try:
    # 2. Locate the image on the screen
    # The result is a Box object (left, top, width, height) of the detected image.
    button_location = pyautogui.locateOnScreen(
        button_image_path, 
        confidence=0.8,   # Set a confidence level (80%) for a more robust match
        grayscale=False   # Keep it colored for better distinction
    )

    if button_location is not None:
        print(f"Button found at: {button_location}")
        
        # 3. Calculate the center of the found area
        center_x, center_y = pyautogui.center(button_location)
        
        # 4. Move the mouse to the center and click
        pyautogui.click(center_x, center_y)
        print("Successfully clicked the button.")
        
    else:
        print("Button image was not found on the screen.")
        
except Exception as e:
    print(f"An error occurred: {e}")