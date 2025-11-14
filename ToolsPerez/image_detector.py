import pyautogui
import os
import sys
import time

# --- Configuration ---
# The default path is now UNCOMMENTED and set to the path you were trying to use.
# Ensure this path is correct for your image!
DEFAULT_IMAGE_PATH = r"C:\Users\User\Downloads\scripts\Fotos\Pdf_Carpeta.png"
CLICK_CONFIDENCE = 0.70  # Increased confidence for more accurate matches (90%)
MOVE_DURATION = 0.3      # Seconds for the mouse to move
POST_CLICK_DELAY = 1.0   # Seconds to wait after a successful click

def main():
    """
    Checks if a target image is visible on the screen and clicks its center if found.
    """
    print("\n--- Image Detector & Clicker Activated ---")
    print(f"Target Image: {os.path.basename(DEFAULT_IMAGE_PATH)}")
    print("This program runs continuously, searching for the image and clicking it.")
    print("Press Ctrl+C to exit.")

    while True:
        try:
            # 1. Always assign the path from the global variable
            image_path = DEFAULT_IMAGE_PATH
            
            if not os.path.exists(image_path):
                print(f"❌ Critical Error: Image file not found at '{image_path}'. Check the DEFAULT_IMAGE_PATH.")
                # We don't delete the variable, so it will be available on the next loop iteration
                time.sleep(5) 
                continue

            # 2. Search the screen for the image
            print(f"\n🔎 Searching screen...")
            
            # --- ADDED DELAY ---
            print("⏳ Waiting 5 seconds before checking the screen...")
            time.sleep(5)
            
            # pyautogui.locateOnScreen returns a Box object (left, top, width, height) 
            location = pyautogui.locateOnScreen(image_path, confidence=CLICK_CONFIDENCE) 
            
            # 3. Process Result
            if location:
                # Calculate the center (x, y) coordinates of the located box
                center_x, center_y = pyautogui.center(location)
                
                print("✅ IMAGE FOUND! Moving mouse and clicking...")
                print(f"   Center Coords: X={center_x}, Y={center_y}")
                
                # Move the mouse smoothly to the center
                pyautogui.moveTo(center_x, center_y, duration=MOVE_DURATION)
                
                # Perform the click
                pyautogui.click() 
                
                print(f"👍 Click successful. Waiting {POST_CLICK_DELAY}s...")
                time.sleep(POST_CLICK_DELAY) 
                
            else:
                print("❌ Image NOT found on screen. Looping...")
                # Wait a bit longer if not found to reduce CPU usage
                time.sleep(2) 
                
        except KeyboardInterrupt:
            break
        #except Exception as e:
            print(f"An unexpected error occurred: {e}")
            # Ensure error handling doesn't immediately crash the loop
            time.sleep(2)

    print("\n--- Detector & Clicker Exited ---")
    sys.exit(0)

if __name__ == "__main__":
    main()