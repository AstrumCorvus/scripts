import pynput
import sys
import time
import os # Import os for file path handling

# --- Configuration ---
COORDS_LOG_FILE = "coords_log.txt"

# --- Global State ---
click_count = 0
mouse_press_times = {}
clean_coords_log = [] # New list to store clean (x, y) tuples for the mover script

# --- Helper Functions ---
def save_coords_to_file():
    """Writes the clean coordinate log to a file."""
    if not clean_coords_log:
        print("\n(No coordinates were logged to save.)")
        return

    with open(COORDS_LOG_FILE, 'w') as f:
        for x, y in clean_coords_log:
            f.write(f"{x},{y}\n")
    print(f"\n✅ Saved {len(clean_coords_log)} coordinates to: {os.path.abspath(COORDS_LOG_FILE)}")


# --- Mouse Callback Function ---
def on_click(x, y, button, pressed):
    """
    Logs the position and button press/release, and calculates the hold duration.
    Also logs clean coordinates for the mover script.
    """
    global click_count
    global mouse_press_times
    
    # --- BUTTON PRESS (Click Start) ---
    if pressed:
        mouse_press_times[button] = time.time()
        
    # --- BUTTON RELEASE (Click End) ---
    else:
        if button in mouse_press_times:
            # 1. Calculate Duration
            stop_time = time.time()
            start_time = mouse_press_times.pop(button) 
            duration = stop_time - start_time
            
            # 2. Increment Counter (The click is complete upon release)
            click_count += 1
            
            # 3. Log Clean Coordinate
            clean_coords_log.append((x, y))

            # 4. Print Output (detailed version)
            duration_str = f"{duration:.3f}s" 
            print(f"CLICK n°{click_count:<4} X={x:<6} Y={y:<6} | Button: {button:<15} | Hold Time: {duration_str}")


# --- Keyboard Callback Function ---
def on_press(key):
    """Prints the key that was pressed."""
    try:
        print(f"KEY PRESS: {key.char}")
    except AttributeError:
        print(f"KEY PRESS: {key}")

# --- Main Execution ---
print("--- Mouse & Keyboard Listener Activated ---")
print(f"Coordinates will be saved to {COORDS_LOG_FILE} on exit.")
print("Click anywhere (and hold) or press keys to log them.")
print("Press Ctrl+C in this terminal window to stop the listener and quit.")

# Create listeners
mouse_listener = pynput.mouse.Listener(on_click=on_click)
keyboard_listener = pynput.keyboard.Listener(on_press=on_press)

# Start listeners
mouse_listener.start()
keyboard_listener.start()

try:
    while mouse_listener.is_alive() and keyboard_listener.is_alive():
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n--- Ctrl+C detected. Stopping listeners... ---")
    mouse_listener.stop()
    keyboard_listener.stop()
    save_coords_to_file() # NEW: Save coordinates before exiting
    print("--- Listeners Stopped ---")
    sys.exit(0)