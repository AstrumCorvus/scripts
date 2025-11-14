import pyautogui
import os
import sys
import time

# --- Configuration ---
COORDS_LOG_FILE = "coords_log.txt"
MOVE_DURATION = 0.3  # Time in seconds for the mouse to move to each point

# --- Functions ---
def load_coordinates():
    """Loads clean (X, Y) coordinates from the log file."""
    if not os.path.exists(COORDS_LOG_FILE):
        print(f"❌ Error: Coordinate log file not found at '{COORDS_LOG_FILE}'")
        print("Please run click_tracker.py first to generate the coordinates.")
        sys.exit(1)
    
    coords = []
    try:
        with open(COORDS_LOG_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        x, y = map(int, line.split(','))
                        coords.append((x, y))
                    except ValueError:
                        print(f"Skipping malformed line in log: {line}")
        return coords
    except Exception as e:
        print(f"❌ Error reading coordinate file: {e}")
        sys.exit(1)

def validate_coordinates(coords):
    """
    Iterates through coordinates, moves the mouse, and validates with keyboard input.
    """
    if not coords:
        print("No coordinates to validate. Exiting.")
        return 0, 0
    
    correct_count = 0
    wrong_count = 0
    
    print(f"--- Starting Coordinate Validation ({len(coords)} points) ---")
    print("Instructions: Press 'a' (correct) or 'x' (wrong) after the mouse moves.")
    
    for i, (x, y) in enumerate(coords):
        coord_number = i + 1
        
        # 1. Move the mouse to the target coordinate
        print(f"\n[{coord_number}/{len(coords)}] Moving mouse to X={x}, Y={y}...")
        pyautogui.moveTo(x, y, duration=MOVE_DURATION)
        
        # 2. Wait for input
        while True:
            try:
                # Use standard input() for blocking input
                validation_input = input(f"Coordinates X={x}, Y={y} reached. Is this correct? (a/x): ").strip().lower()
            except EOFError:
                # Handle cases where the input stream is closed
                validation_input = 'x'
            
            if validation_input == 'a':
                print("   -> Marked as CORRECT.")
                correct_count += 1
                break
            elif validation_input == 'x':
                print("   -> Marked as WRONG.")
                wrong_count += 1
                break
            else:
                print("   Invalid input. Please enter 'a' or 'x'.")

    return correct_count, wrong_count

# --- Main Execution ---
if __name__ == "__main__":
    
    # 1. Load Data
    all_coords = load_coordinates()
    
    # 2. Run Validation Loop
    if all_coords:
        try:
            total_correct, total_wrong = validate_coordinates(all_coords)
            
            # 3. Output Final Summary
            print("\n" + "="*40)
            print("         VALIDATION COMPLETE")
            print("="*40)
            print(f"Total Coordinates Tested: {len(all_coords)}")
            print(f"Correct: {total_correct}")
            print(f"Wrong:   {total_wrong}")
            print("="*40)
        
        except KeyboardInterrupt:
            # Allows user to press Ctrl+C during validation
            print("\nValidation interrupted by user. Exiting.")
            sys.exit(0)
    else:
        print("No coordinates were loaded from the file.")