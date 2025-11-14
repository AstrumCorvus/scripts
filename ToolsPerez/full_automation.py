import pyautogui
import os
import sys
import time
import glob
# --- NEW: Import for global keyboard listener ---
from pynput import keyboard

# ===============================================
# --- 1. CONFIGURATION (REQUIRED UPDATES) ---
# ===============================================

# --- Image Paths for Dynamic Detection (Provided by User) ---
# NOTE: Ensure these paths exist on your system and contain clear screenshots.
IMAGE_SIN_IMAGEN = r"C:\Users\User\Downloads\scripts\Fotos\SinImagen.png"
IMAGE_METAMAP_VERIFICATION = r"C:\Users\User\Downloads\scripts\Fotos\MetamapVerificactiion.png"
IMAGE_PDF_TEST_JP = r"C:\Users\User\Downloads\scripts\Fotos\Pdf.TestJp.png"
IMAGE_GUARDAR = r"C:\Users\User\Downloads\scripts\Fotos\Guardar.png"
IMAGE_PDF_CARPETA = r"C:\Users\User\Downloads\scripts\Fotos\Pdf_Carpeta.png"
IMAGE_COPIAR_LOCAL = r"C:\Users\User\Downloads\scripts\Fotos\Copiar_Local.png"


SIGNATURE_OUTPUT_DIR = r"C:\Users\User\Desktop\Pdf.Test\Fotos"

# --- General Configuration ---
STARTUP_DELAY = 10       # Seconds to wait before starting the loop (Requested: 10s)
TEST_LOOP_COUNT = 3      # Number of times to run the main process (Requested: 3)
POST_CLICK_DELAY = 1.5   # Seconds to wait after most clicks/key presses (Increased)
MOVE_DURATION = 0.2      # Time in seconds for the mouse to move
CONFIDENCE_LEVEL = 0.70  # IMPORTANT: Adjusted confidence to 70% for robust image detection

# ===============================================
# --- 2. COORDINATE MAP (Fixed Clicks/Actions) ---
# ===============================================

COORDS = {
    # [1A] Initial Table Selection (Only runs once at start)
    "[1A] Initial Selection": (1101, 276),
    # Standard Procedure Inside Loan Object
    "[2] Right-Click for Options": (1247, 201), 
    "[3] Click Save As": (1287, 401),
    "[4] Click cropdf path": (1373, 129),
    "[5] Select pdf folder": (1357, 243),
    "[7] Click Save": (1683, 634), # This coordinate is still used
    "[9] Hold Scroll Down": (1910, 986),
    "[10] Select File Manager Folder": (1240, 972),
    "[11] Hold Scroll Up": (1911, 49),
    # --- File Management (Cut/Paste Cropped Signature) ---
    "[12] Click cropdf path (File Mngr)": (1360, 116),
    "[13] Select pdf folder (File Mngr)": (1354, 185),
    "[15] Right-Click on PDF": (1354, 185),
    "[16] Select Cut Option": (1120, 644), 
    # [17] Removed - Now Dynamic
    # [18] Removed - Now Dynamic
    # [19] Removed - Now Dynamic
    "[20] Click Fotos folder": (377, 235),
    # --- Cut Cropped Image back to Target Folder ---
    "[22] Right-Click on Newest PNG": (278, 244),
    "[23] Select Cut Option (PNG)": (331, 50),
    "[24] Click cropdf path (PNG Target)": (1360, 115),
    "[25] Select PNG Target Folder": (1267, 225),
    "[27] Right-Click in PNG Folder": (1224, 187),
    "[28] Select Paste Option (PNG)": (1187, 355),
    # --- Final Upload & Next Object ---
    "[29] Hold Scroll Down": (1910, 986),
    "[30] Click Celesol": (1364, 966),
    "[31] Hold Scroll Up": (1911, 49),
    "[32] Close Loan Tab": (1516, 139), 
    "[33] Right-Click Signature Field": (1510, 332),
    "[34] Open PNG Folder": (1557, 470),
    "[35] Select Newest PNG": (1564, 435), 
    "[36] Save and Close": (1064, 110),
}


# ===============================================
# --- 3. GLOBAL CONTROL & HELPER FUNCTIONS ---
# ===============================================
# ... (Global 'running' flag and helper functions: on_press, find_newest_file, wait_for_new_signature, check_for_image, move_and_click, hold_mouse, press_key)
# Global flag for non-console interruption
running = True 

def on_press(key):
    """
    Callback function for the global keyboard listener.
    Stops the script when the ESC key is pressed.
    """
    global running
    try:
        # Check for the Escape key press (reliable global interrupt)
        if key == keyboard.Key.esc:
            print("\n!!! Global STOP signal received (ESC key detected). Halting script...")
            running = False
            return False # Stop listener thread
    except AttributeError:
        pass # Ignore key.char errors

def find_newest_file(directory, extension="jpg"):
    """Finds the path of the newest file with a given extension in a directory."""
    try:
        list_of_files = glob.glob(os.path.join(directory, f'*.{extension}'))
        if not list_of_files:
            return None
        latest_file = max(list_of_files, key=os.path.getctime)
        return latest_file
    except Exception as e:
        print(f"Error finding newest file in {directory}: {e}")
        return None

def wait_for_new_signature(signature_dir, timeout=30):
    """Waits for a new JPG file to appear in the signature directory."""
    print(f"⏳ Waiting for new cropped signature in '{os.path.basename(signature_dir)}'...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if not running: return None # Check interrupt flag during wait
        
        newest_file = find_newest_file(signature_dir, extension="jpg")
        if newest_file and os.path.exists(newest_file):
            try:
                # Check if the file is still being written
                with open(newest_file, 'rb') as f:
                    f.seek(-1, 2)
                return newest_file
            except Exception:
                pass 
        time.sleep(1) # Poll every second

    print(f"❌ Timeout ({timeout}s) reached. Cropped signature did not appear.")
    return None

def check_for_image(image_path):
    """Searches the screen for the given image path."""
    image_name = os.path.basename(image_path)
    print(f"   🔎 Searching for '{image_name}'...")
    try:
        location = pyautogui.locateOnScreen(image_path, confidence=CONFIDENCE_LEVEL, grayscale=True) 
        return location
    except Exception as e:
        print(f"   Error during image search for {image_name}: {e}") 
        return None

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
# --- 4. MAIN AUTOMATION LOGIC ---
# ===============================================

def run_main_loop():
    """Executes the full automation workflow."""
    global running
    
    # ----------------------------------------------------
    # Setup Global Keyboard Listener
    # ----------------------------------------------------
    # Start the listener thread to monitor for the ESC key globally
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    try:
        # --- INITIAL SETUP ---
        print("\n" + "="*50)
        print(f"✨ FULL AUTOMATION STARTING IN {STARTUP_DELAY} SECONDS...")
        print(f"   Will run for {TEST_LOOP_COUNT} cycles. Press ESC key to stop.")
        print("   Please ensure the application window is focused.")
        print("="*50)
        time.sleep(STARTUP_DELAY)
        
        if not running: return # Check interrupt flag

        # [1A] Initial Selection (Runs only once at the start)
        x1a, y1a = COORDS["[1A] Initial Selection"]
        move_and_click(x1a, y1a, "[1A] Selecting first element in the table")
        
        # --- ADDED: Enter key press after the initial selection ---
        press_key('enter', "Pressing Enter after initial selection to open object")
        
        # --- MAIN LOOP (Modified to run TEST_LOOP_COUNT times) ---
        for i in range(1, TEST_LOOP_COUNT + 1):
            if not running:
                break # Exit loop if interrupt flag is set
                
            print(f"\n--- CYCLE {i}/{TEST_LOOP_COUNT} ---")
            
            # 1. Check for "Sin Imagen" (Is the signature missing?)
            if not running: break
            print("   [2A] Checking for 'Sin Imagen'...")
            time.sleep(1.0) 
            
            # If 'Sin Imagen' is NOT found, it means the signature is already there.
            if not check_for_image(IMAGE_SIN_IMAGEN):
                # --- Logic: Signature is present/object is complete ---
                print("   -> 'Sin Imagen' NOT found. Assuming signature is complete. Skipping object.")
                
                # Close current object and move to the next one
                move_and_click(1323, 143, "   -> Closing loan object (Complete)")
                press_key('down', "   -> Moving to next item in list")
                press_key('enter', "   -> Opening next item")
                
                continue 

            else:
                # --- Logic: Signature is missing, proceed with full sequence ---
                print("   -> 'Sin Imagen' FOUND. Object is INCOMPLETE. Proceeding to verification.")

                # 2. Check for "metamap-verification" link
                if not running: break
                print("   [2B] Checking for 'metamap-verification'...")
                time.sleep(1.0) 
                metamap_loc = check_for_image(IMAGE_METAMAP_VERIFICATION)
                
                if not metamap_loc:
                    print("   ❌ 'metamap-verification' NOT found. Cannot proceed with download.")
                    
                    # Close current object and move to the next one
                    move_and_click(1323, 143, "   -> Closing loan object (Verification file missing)")
                    press_key('down', "   -> Moving to next item in list")
                    press_key('enter', "   -> Opening next item")
                    
                    continue 
                
                # --- Standard Procedure: Steps [1] through [36] ---
                
                # [1] Click verification link (Dynamic Coords)
                metamap_x, metamap_y = pyautogui.center(metamap_loc)
                move_and_click(metamap_x, metamap_y, "[1] Clicking 'metamap-verification' link")
                
                # [1.5] Added: Press Enter key after clicking the link 
                press_key('enter', "[1.5] Pressing Enter to confirm/open verification file")
                
                if not running: break

                # [2] Right-click PDF location
                x2, y2 = COORDS["[2] Right-Click for Options"]
                pyautogui.moveTo(x2, y2, duration=MOVE_DURATION)
                pyautogui.rightClick()
                time.sleep(POST_CLICK_DELAY)

                # [3] Click 'Save As'
                x3, y3 = COORDS["[3] Click Save As"]
                move_and_click(x3, y3, "[3] Clicking 'Save As'")

                # [4] Navigate to PDF save folder (Path: cropdf)
                x4, y4 = COORDS["[4] Click cropdf path"]
                move_and_click(x4, y4, "[4] Clicking 'cropdf' in path bar")

                # [5] Select 'pdf' folder
                x5, y5 = COORDS["[5] Select pdf folder"]
                move_and_click(x5, y5, "[5] Selecting 'pdf' folder")

                # [6] Press Enter (to enter 'pdf' folder)
                press_key('enter', "[6] Entering 'pdf' folder")

                # [7] Click Save
                x7, y7 = COORDS["[7] Click Save"]
                move_and_click(x7, y7, "[7] Clicking Save button (Triggers PDF download)")
                
                # --- FILE MANAGEMENT: Wait for Cropper ---
                
                # [7.1] *** CRITICAL: UN-COMMENTED THIS BLOCK ***
                # This block is required to wait for pdf_monitor.py to finish.
                #cropped_signature_path = wait_for_new_signature(SIGNATURE_OUTPUT_DIR)
                
                #if not running: break # Check interrupt flag during wait
                
                #if not cropped_signature_path:
                    #print("   ❌ Failed to find cropped signature after waiting. Aborting cycle.")
                    #break 

               # print(f"   -> Found new cropped signature: {os.path.basename(cropped_signature_path)}")

                # --- Move PDF to 'Processed' and PNG back to target location ---
                
                # [9] Hold Scroll Down
                x9, y9 = COORDS["[9] Hold Scroll Down"]
                hold_mouse(x9, y9, 1.304, "[9] Scrolling down remote desktop")

                # [10] Select File Manager Folder
                x10, y10 = COORDS["[10] Select File Manager Folder"]
                move_and_click(x10, y10, "[10] Selecting File Manager Folder")

                # [11] Hold Scroll Up
                x11, y11 = COORDS["[11] Hold Scroll Up"]
                hold_mouse(x11, y11, 1.304, "[11] Scrolling up remote desktop")
                
                if not running: break

                # [12] Navigate to PDF folder (remote desk) (Path: cropdf)
                x12, y12 = COORDS["[12] Click cropdf path (File Mngr)"]
                move_and_click(x12, y12, "[12] Clicking 'cropdf' in path bar")

                # [13] Select 'pdf' folder & [14] Press Enter (Combined: Double Click)
                x13, y13 = COORDS["[13] Select pdf folder (File Mngr)"]
                print(f"   -> Double Clicking to select and enter 'pdf' folder at X={x13}, Y={y13}")
                pyautogui.moveTo(x13, y13, duration=MOVE_DURATION)
                pyautogui.doubleClick()
                time.sleep(POST_CLICK_DELAY)
                
                # [15] Right-click on PDF (to open menu)
                x15, y15 = COORDS["[15] Right-Click on PDF"]
                pyautogui.moveTo(x15, y15, duration=MOVE_DURATION)
                pyautogui.rightClick()
                time.sleep(POST_CLICK_DELAY)
                
                # [16] Select 'Cut'
                x16, y16 = COORDS["[16] Select Cut Option"]
                move_and_click(x16, y16, "[16] Selecting 'Cut' option")

                # [17] Navigate to PDF.Test (Path) (local desk) - DYNAMIC
                if not running: break
                print("   [17] Searching for 'Pdf.TestJp.png' to click path...")
                pdf_test_loc = check_for_image(IMAGE_PDF_TEST_JP)
                
                if not pdf_test_loc:
                    print("   ❌ ERROR: 'Pdf.TestJp.png' image NOT found. Aborting cycle.")
                    break 
                
                x17, y17 = pyautogui.center(pdf_test_loc)
                move_and_click(x17, y17, "[17] Clicking 'pdf.test' path (Dynamic)") 

                # [18] Right-click in empty space // DYNAMIC using PDF_CARPETA image
                if not running: break
                print("   [18] Searching for 'Pdf_Carpeta.png' to click path...")
                pdf_carpeta_loc = check_for_image(IMAGE_PDF_CARPETA)
                
                if not pdf_carpeta_loc:
                    print("   ❌ ERROR: 'Pdf_Carpeta.png' image NOT found. Aborting cycle.")
                    break 
                
                # --- FIX: Changed to moveTo + rightClick ---
                x18, y18 = pyautogui.center(pdf_carpeta_loc)
                print(f"   -> Moving mouse to X={x18}, Y={y18}... [18] Clicking 'Carpeta Pdf' (Dynamic)")
                pyautogui.moveTo(x18, y18, duration=MOVE_DURATION)
                pyautogui.rightClick()
                time.sleep(POST_CLICK_DELAY)

                # [19] Select 'Paste' (moves PDF) - DYNAMIC
                if not running: break
                print("   [19] Searching for 'copiar_local.png' to click path...")
                
                # --- FIX: Corrected variable name ---
                copiar_local_loc = check_for_image(IMAGE_COPIAR_LOCAL)
                
                if not copiar_local_loc:
                    print("   ❌ ERROR: 'COPIAR_LOCAL' (Paste) image NOT found. Aborting cycle.")
                    break 
                
                x19, y19 = pyautogui.center(copiar_local_loc)
                move_and_click(x19, y19, "[19] Clicking 'copiar' (Paste) button (Dynamic)") 
                
                # Added delay to let OS finish pasting the file
                time.sleep(1.0) 

                # [20] Click 'Fotos' folder (where the signature JPG is now)
                x20, y20 = COORDS["[20] Click Fotos folder"]
                move_and_click(x20, y20, "[20] Clicking 'Fotos' folder")

                # [21] Press Enter (to open 'Fotos' folder)
                press_key('enter', "[21] Entering 'Fotos' folder")
                
                # [22] Right-click on newest PNG/JPG
                x22, y22 = COORDS["[22] Right-Click on Newest PNG"]
                pyautogui.moveTo(x22, y22, duration=MOVE_DURATION)
                pyautogui.rightClick()
                time.sleep(POST_CLICK_DELAY)

                # [23] Select 'Cut'
                x23, y23 = COORDS["[23] Select Cut Option (PNG)"]
                move_and_click(x23, y23, "[23] Selecting 'Cut' option for PNG")

                # [24] Navigate back to 'cropdf' path
                x24, y24 = COORDS["[24] Click cropdf path (PNG Target)"]
                move_and_click(x24, y24, "[24] Clicking 'cropdf' path")

                # [25] Select target PNG folder
                x25, y25 = COORDS["[25] Select PNG Target Folder"]
                move_and_click(x25, y25, "[25] Selecting PNG target folder")

                # [26] Press Enter (to open PNG folder)
                press_key('enter', "[26] Entering PNG target folder")

                # [27] Right-click in PNG folder
                x27, y27 = COORDS["[27] Right-Click in PNG Folder"]
                pyautogui.moveTo(x27, y27, duration=MOVE_DURATION)
                pyautogui.rightClick()
                time.sleep(POST_CLICK_DELAY)
                
                # [28] Select 'Paste' (moves PNG back)
                x28, y28 = COORDS["[28] Select Paste Option (PNG)"]
                move_and_click(x28, y28, "[28] Pasting PNG/JPG signature file")
                
                if not running: break

                # [29] Hold Scroll Down
                x29, y29 = COORDS["[29] Hold Scroll Down"]
                hold_mouse(x29, y29, 1.304, "[29] Scrolling down remote desktop")

                # [30] Click Celesol
                x30, y30 = COORDS["[30] Click Celesol"]
                move_and_click(x30, y30, "[30] Clicking Celesol application")

                # [31] Hold Scroll Up
                x31, y31 = COORDS["[31] Hold Scroll Up"]
                hold_mouse(x31, y31, 1.304, "[31] Scrolling up remote desktop")

                # [32] Close Loan Tab
                x32, y32 = COORDS["[32] Close Loan Tab"]
                move_and_click(x32, y32, "[32] Closing loan object tab") 

                # [33] Right-click signature field
                x33, y33 = COORDS["[33] Right-Click Signature Field"]
                pyautogui.moveTo(x33, y33, duration=MOVE_DURATION)
                pyautogui.rightClick()
                time.sleep(POST_CLICK_DELAY)
                
                # [34] Open PNG Folder
                x34, y34 = COORDS["[34] Open PNG Folder"]
                move_and_click(x34, y34, "[34] Clicking to open PNG folder")

                # [35] Select newest PNG (to select)
                x35, y35 = COORDS["[35] Select Newest PNG"]
                move_and_click(x35, y35, "[35] Selecting newest PNG")
                press_key('enter', "Pressing enter to confirm upload")

                # [36] Save and Close
                x36, y36 = COORDS["[36] Save and Close"]
                move_and_click(x36, y36, "[36] Clicking 'Save and Close'")
            
            # --- NEXT ITEM (Applies to both paths) ---
            
            # [37] Press down arrow key (Moves to next item in the main list)
            press_key('down', "[37] Moving to next object in the main list")

            # [38] Press enter (Opens the next item)
            press_key('enter', "[38] Opening the next object")

        print("\n--- TEST RUN COMPLETE ---")

    finally:
        # Crucial: Stop the listener thread cleanly upon exit
        if listener.is_alive():
            listener.stop()
        
        # Exit the system cleanly
        sys.exit(0)

# ===============================================
# --- 5. SCRIPT EXECUTION ---
# ===============================================

if __name__ == "__main__":
    # Standard KeyboardInterrupt remains as a console fallback
    try:
        run_main_loop()
    except KeyboardInterrupt:
        print("\nAutomation stopped by user (Ctrl+C). Exiting.")
        # The finally block in run_main_loop handles listener stop and exit.