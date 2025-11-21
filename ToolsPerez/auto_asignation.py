import pyautogui
import os
import time
import sys
from pynput import keyboard

# ===============================================
# --- 1. CONFIGURATION ---
# ===============================================

# --- Image Paths for Dynamic Detection ---
IMAGE_INGRESO = r"C:\Users\User\Downloads\scripts\Fotos\INGRESO.png"
IMAGE_CBU1 = r"C:\Users\User\Downloads\scripts\Fotos\LINEACOMERCIALIZADORESCBU.png"
IMAGE_CBU2 = r"C:\Users\User\Downloads\scripts\Fotos\LINEACOMERSNUEVOSCBU.png"
IMAGE_CBU3 = r"C:\Users\User\Downloads\scripts\Fotos\LINEAPROPIACBU.png"
IMAGE_CANC = r"C:\Users\User\Downloads\scripts\Fotos\CANC.png"
IMAGE_CANCE = r"C:\Users\User\Downloads\scripts\Fotos\Cance.png"
IMAGE_CAMBIAR_EJECUTIVO = r"C:\Users\User\Downloads\scripts\Fotos\CambiarEjecutivo.png"
IMAGE_ARIEL_ORTEGA = r"C:\Users\User\Downloads\scripts\Fotos\ArielOrtega.png"
IMAGE_DANIEL_MONTANA = r"C:\Users\User\Downloads\scripts\Fotos\DanielMontana.png"
IMAGE_JORGELINA_MARIN = r"C:\Users\User\Downloads\scripts\Fotos\JorgelinaMarin.png"
IMAGE_STEFANIA_SALGUERO = r"C:\Users\User\Downloads\scripts\Fotos\StefaniaSalguero.png" 

# Dictionary to map analyst names to their image files
ANALYST_IMAGES = {
    "Ariel Ortega": IMAGE_ARIEL_ORTEGA,
    "Daniel Montaña": IMAGE_DANIEL_MONTANA,
    "Jorgelina Marin": IMAGE_JORGELINA_MARIN,
    # Stefania is included here so the CBU logic can find her image
    "Stefania Salguero": IMAGE_STEFANIA_SALGUERO, 
}

# --- General Configuration ---
STARTUP_DELAY = 5        # Seconds to wait before starting the loop
POST_CLICK_DELAY = 0.5   # Seconds to pause after every click/key press
MOVE_DURATION = 0.3      # Duration (seconds) for mouse movements
CONFIDENCE_LEVEL = 0.70  # Confidence level for image detection

# ===============================================
# --- 2. COORDINATE MAP (Fixed Clicks) ---
# ===============================================

COORDS = {
    # [2.3] / [3.3] / [4.2] Click to open analyst selection dropdown
    "Open Selection": (670, 96), 
    # [2.4] Click and hold to scroll down the analyst list
    "Scroll Analysts": (684, 473),
    # [2.6] / [3.5] / [4.4] Click to accept the new analyst assignment
    "Accept Change": (520, 518),
}

# ===============================================
# --- 3. ROUND-ROBIN ASSIGNMENT LOGIC ---
# ===============================================

class AnalystAssigner:
    """Manages the round-robin assignment for a list of analysts."""
    def __init__(self, analysts):
        # The list contains ONLY the analysts for the rotation queue (CANC/INGRESO)
        self.analysts = analysts
        self.index = 0

    def get_next_analyst(self):
        """Gets the next analyst in the list and loops back to the start."""
        # Get the analyst name at the current index
        analyst_name = self.analysts[self.index]
        
        # Increment the index for the next call
        # The % (modulo) operator ensures it wraps around to 0
        self.index = (self.index + 1) % len(self.analysts)
        
        print(f"   -> Assigning to next analyst: {analyst_name}")
        return analyst_name

# ===============================================
# --- 4. GLOBAL CONTROL & HELPER FUNCTIONS ---
# ===============================================

# Global flag for non-console interruption (using ESC key)
running = True 

def on_press(key):
    """Callback function to stop the script when the ESC key is pressed."""
    global running
    try:
        if key == keyboard.Key.esc:
            print("\n!!! Global STOP signal received (ESC key detected). Halting script...")
            running = False
            return False # Stop listener thread
    except AttributeError:
        pass # Ignore other key presses

def check_for_image(image_path, region=None):
    """
    Searches the screen (or a specific region) for the given image path.
    Returns the location Box object or None.
    """
    image_name = os.path.basename(image_path)
    print(f"   🔎 Searching for '{image_name}'..." + (f" in region {region}" if region else ""))
    try:
        location = pyautogui.locateOnScreen(
            image_path, 
            confidence=CONFIDENCE_LEVEL, 
            grayscale=True,
            region=region  # Search only within the specified region
        ) 
        return location
    except Exception as e:
        print(f"   Error during image search for {image_name}: {e}") 
        return None

def find_and_click_analyst(analyst_name):
    """
    Finds the image for the given analyst and clicks it.
    Handles the special case for "Jorgelina Marin".
    """
    if analyst_name not in ANALYST_IMAGES:
        print(f"   ❌ ERROR: No image path defined for analyst '{analyst_name}'.")
        return False

    image_path = ANALYST_IMAGES[analyst_name]
    target_loc = None

    if analyst_name == "Jorgelina Marin":
        print("   -> Applying special rule for 'Jorgelina Marin' (finding highest Y-axis)...")
        try:
            # Find all instances of Jorgelina
            locations = list(pyautogui.locateAllOnScreen(image_path, confidence=CONFIDENCE_LEVEL, grayscale=True))
            if not locations:
                print("   ❌ ERROR: Could not find 'Jorgelina Marin' on screen.")
                return False
            
            # Find the one with the lowest 'top' value (highest on the screen)
            target_loc = min(locations, key=lambda loc: loc.top)
            
        except Exception as e:
            print(f"   Error locating all 'Jorgelina Marin': {e}")
            return False
    else:
        # For all other analysts, just find the first instance
        target_loc = check_for_image(image_path)

    if target_loc:
        x, y = pyautogui.center(target_loc)
        move_and_click(x, y, f"[Clicking {analyst_name}]")
        return True
    else:
        print(f"   ❌ ERROR: Could not find '{analyst_name}' on screen.")
        return False

def move_and_click(x, y, desc=""):
    """Moves the mouse to (X, Y) and performs a LEFT click."""
    print(f"   -> Moving mouse to X={x}, Y={y}... {desc}")
    pyautogui.moveTo(x, y, duration=MOVE_DURATION)
    pyautogui.click()
    time.sleep(POST_CLICK_DELAY)

def hold_mouse(x, y, hold_time, desc=""):
    """Moves the mouse, holds the left button down, and releases it."""
    print(f"   -> Holding mouse button at X={x}, Y={y} for {hold_time:.3f}s... {desc}")
    pyautogui.moveTo(x, y, duration=MOVE_DURATION)
    pyautogui.mouseDown()
    time.sleep(hold_time)
    pyautogui.mouseUp()
    time.sleep(POST_CLICK_DELAY)

def press_key(key, desc=""):
    """Presses a single key."""
    print(f"   -> Pressing key '{key}'... {desc}")
    pyautogui.press(key)
    time.sleep(POST_CLICK_DELAY)

# ===============================================
# --- 5. MAIN AUTOMATION LOGIC ---
# ===============================================

def run_main_loop():
    """Executes the full assignment automation workflow."""
    global running
    
    # --- Setup Global Keyboard Listener ---
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    # --- Setup Analyst Queues ---
    # This list is used for the round-robin assignment for CANC and default INGRESO.
    # Stefania Salguero is explicitly excluded here.
    analyst_list = ["Ariel Ortega", "Daniel Montaña", "Jorgelina Marin"]
    canc_assigner = AnalystAssigner(analyst_list)
    asig_assigner = AnalystAssigner(analyst_list)
    
    # --- Get screen dimensions ---
    screen_width, screen_height = pyautogui.size()

    try:
        print("\n" + "="*50)
        print(f"✨ ASSIGNMENT BOT STARTING IN {STARTUP_DELAY} SECONDS...")
        print("   Press ESC key (any time) to stop.")
        print("="*50)
        time.sleep(STARTUP_DELAY)
        
        # --- Main Infinite Loop ---
        while running:
            print("\n--- Top of Loop: Searching for new 'INGRESO' item ---")
            
            # [1] Check for "INGRESO"
            ingreso_loc = check_for_image(IMAGE_INGRESO)
            
            if not ingreso_loc:
                # [1.1] Not found, wait 1 min and refresh
                print("   -> No 'INGRESO' found. Waiting 1 minute...")
                # Sleep in 1-second intervals to check 'running' flag
                for _ in range(60):
                    if not running:
                        break
                    time.sleep(1)
                
                if not running:
                    break
                    
                press_key('f5', "Refreshing screen")
                continue # Restart the loop
            
            # --- INGRESO was found ---
            print(f"   ✅ 'INGRESO' found at {ingreso_loc}. Analyzing row...")
            
            # Define the search region: from the right of "INGRESO" to the edge 
            # of the screen, in the same row (same height).
            search_region = (
                ingreso_loc.left + ingreso_loc.width, 
                ingreso_loc.top, 
                screen_width - (ingreso_loc.left + ingreso_loc.width), 
                ingreso_loc.height
            )

            # [2] Check for "CBU" in the same row
            cbu_loc = check_for_image(IMAGE_CBU1, region=search_region)
            if not cbu_loc:
                cbu_loc = check_for_image(IMAGE_CBU2, region=search_region)
            if not cbu_loc:
                cbu_loc = check_for_image(IMAGE_CBU3, region=search_region)
            
            # [3] Check for "CANC" or "Cance" in the same row
            canc_loc = check_for_image(IMAGE_CANC, region=search_region)
            if not canc_loc:
                canc_loc = check_for_image(IMAGE_CANCE, region=search_region)
                
            # --- Assignment Logic ---

            if cbu_loc:
                # --- CBU LOGIC (Explicitly Stefania Salguero) ---
                print("   -> 'CBU' found. Assigning to Stefania Salguero.")
                
                # [2.1] Right click "CBU"
                cbu_x, cbu_y = pyautogui.center(cbu_loc)
                print("   -> Right-clicking CBU...")
                pyautogui.moveTo(cbu_x, cbu_y, duration=MOVE_DURATION)
                pyautogui.rightClick()
                time.sleep(POST_CLICK_DELAY)
                
                # [2.2] Click "Cambiar Ejecutivo"
                cambiar_loc = check_for_image(IMAGE_CAMBIAR_EJECUTIVO)
                if not cambiar_loc:
                    print("   ❌ ERROR: Found CBU but could not find 'Cambiar Ejecutivo'. Skipping.")
                    continue
                cambiar_x, cambiar_y = pyautogui.center(cambiar_loc)
                move_and_click(cambiar_x, cambiar_y, "[2.2] Clicking 'Cambiar Ejecutivo'")
                
                # [2.3] Open selection
                x_open, y_open = COORDS["Open Selection"]
                move_and_click(x_open, y_open, "[2.3] Opening analyst selection")
                
                # [2.4] Scroll down (If needed to see Stefania)
                x_scroll, y_scroll = COORDS["Scroll Analysts"]
                hold_mouse(x_scroll, y_scroll, 1.120, "[2.4] Scrolling analyst list")
                
                # [2.5] Find and click Stefania
                if not find_and_click_analyst("Stefania Salguero"):
                    print("   ❌ ERROR: Could not find 'Stefania Salguero'. Skipping.")
                    continue
                
                # [2.6] Accept change
                x_accept, y_accept = COORDS["Accept Change"]
                move_and_click(x_accept, y_accept, "[2.6] Accepting change")
                # --- 5 SECOND DELAY ---
                print("   -> Waiting 5 seconds for change to process...")
                time.sleep(5.0)

            elif canc_loc:
                # --- CANCELACION LOGIC (Round-Robin excluding Stefania) ---
                print("   -> 'CANC'/'Cance' found. Assigning from Cancelation queue.")
                
                # [3.1] Right click "CANC"
                canc_x, canc_y = pyautogui.center(canc_loc)
                print("   -> Right-clicking CANC...")
                pyautogui.moveTo(canc_x, canc_y, duration=MOVE_DURATION)
                pyautogui.rightClick()
                time.sleep(POST_CLICK_DELAY)

                # [3.2] Click "Cambiar Ejecutivo"
                cambiar_loc = check_for_image(IMAGE_CAMBIAR_EJECUTIVO)
                if not cambiar_loc:
                    print("   ❌ ERROR: Found CANC but could not find 'Cambiar Ejecutivo'. Skipping.")
                    continue
                cambiar_x, cambiar_y = pyautogui.center(cambiar_loc)
                move_and_click(cambiar_x, cambiar_y, "[3.2] Clicking 'Cambiar Ejecutivo'")
                
                # [3.3] Open selection
                x_open, y_open = COORDS["Open Selection"]
                move_and_click(x_open, y_open, "[3.3] Opening analyst selection")
                
                # [3.4] Find and click next analyst from "Canc Array"
                next_analyst = canc_assigner.get_next_analyst()
                if not find_and_click_analyst(next_analyst):
                    print(f"   ❌ ERROR: Could not find '{next_analyst}'. Skipping.")
                    continue
                
                # [3.5] Accept change
                x_accept, y_accept = COORDS["Accept Change"]
                move_and_click(x_accept, y_accept, "[3.5] Accepting change")
                # --- 5 SECOND DELAY ---
                print("   -> Waiting 5 seconds for change to process...")
                time.sleep(5.0)

            else:
                # --- DEFAULT ASIGNACION LOGIC (Round-Robin excluding Stefania) ---
                print("   -> Standard 'INGRESO'. Assigning from Asignation queue.")
                
                # [4] Right click "INGRESO"
                ingreso_x, ingreso_y = pyautogui.center(ingreso_loc)
                print("   -> Right-clicking INGRESO...")
                pyautogui.moveTo(ingreso_x, ingreso_y, duration=MOVE_DURATION)
                pyautogui.rightClick()
                time.sleep(POST_CLICK_DELAY)
                
                # [4.1] Click "Cambiar Ejecutivo"
                cambiar_loc = check_for_image(IMAGE_CAMBIAR_EJECUTIVO)
                if not cambiar_loc:
                    print("   ❌ ERROR: Found INGRESO but could not find 'Cambiar Ejecutivo'. Skipping.")
                    continue
                cambiar_x, cambiar_y = pyautogui.center(cambiar_loc)
                move_and_click(cambiar_x, cambiar_y, "[4.1] Clicking 'Cambiar Ejecutivo'")

                # [4.2] Open selection
                x_open, y_open = COORDS["Open Selection"]
                move_and_click(x_open, y_open, "[4.2] Opening analyst selection")

                # [4.3] Find and click next analyst from "Asignation Array"
                next_analyst = asig_assigner.get_next_analyst()
                if not find_and_click_analyst(next_analyst):
                    print(f"   ❌ ERROR: Could not find '{next_analyst}'. Skipping.")
                    continue
                
                # [4.4] Accept change
                x_accept, y_accept = COORDS["Accept Change"]
                move_and_click(x_accept, y_accept, "[4.4] Accepting change")
                # --- 5 SECOND DELAY ---
                print("   -> Waiting 5 seconds for change to process...")
                time.sleep(5.0)
            
            # Short pause before starting the next loop
            time.sleep(2) 

        print("\n--- Loop finished ---")

    finally:
        # Crucial: Stop the listener thread cleanly upon exit
        if listener.is_alive():
            listener.stop()
        
        print("Assignment Bot has been stopped.")
        sys.exit(0)

# ===============================================
# --- 6. SCRIPT EXECUTION ---
# ===============================================

if __name__ == "__main__":
    # Standard KeyboardInterrupt remains as a console fallback
    try:
        run_main_loop()
    except KeyboardInterrupt:
        print("\nAutomation stopped by user (Ctrl+C). Exiting.")
        sys.exit(0)