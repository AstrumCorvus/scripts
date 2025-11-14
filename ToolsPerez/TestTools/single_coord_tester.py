import pyautogui
import sys
import time

# --- Configuration ---
MOVE_DURATION = 0.5  # Time in seconds for the mouse to move, for smooth transition

def get_integer_input(prompt):
    """Safely handles user input, ensuring it is a valid integer."""
    while True:
        try:
            # Get input from the user
            value_str = input(prompt).strip()
            # Check for quit command
            if value_str.lower() in ('q', 'quit'):
                return None # Signal to exit the main loop
            
            # Attempt to convert to integer
            value = int(value_str)
            if value < 0:
                print("⚠️ Please enter a non-negative coordinate value.")
                continue
            return value
        except ValueError:
            print("❌ Invalid input. Please enter a whole number (integer) or 'q' to quit.")
        except EOFError:
            # Handle closing terminal gracefully
            return None


def main():
    """Main function to prompt for coordinates and move the mouse."""
    print("\n--- Single Coordinate Tester Activated ---")
    print(f"Movement Duration: {MOVE_DURATION} seconds.")
    print("Enter 'q' or 'quit' at any prompt to exit.")
    
    # Get screen resolution for informational purposes
    screen_w, screen_h = pyautogui.size()
    print(f"Screen Resolution Detected: {screen_w}x{screen_h}")

    try:
        while True:
            # 1. Get X Coordinate
            x = get_integer_input("\n-> Enter X Coordinate: ")
            if x is None:
                break # Exit if user typed 'q'

            # 2. Get Y Coordinate
            y = get_integer_input("-> Enter Y Coordinate: ")
            if y is None:
                break # Exit if user typed 'q'

            # 3. Move the mouse
            print(f"🚀 Moving mouse to X={x}, Y={y}...")
            
            # Move the mouse smoothly to the target (X, Y)
            pyautogui.moveTo(x, y, duration=MOVE_DURATION)
            
            # 4. Confirmation
            current_x, current_y = pyautogui.position()
            
            # Wait briefly for the move to complete
            time.sleep(0.1) 
            
            print(f"✅ Mouse arrived at X={current_x}, Y={current_y}.")
            
    except KeyboardInterrupt:
        pass # Catch Ctrl+C to exit gracefully

    print("\n--- Tester Exited ---")
    sys.exit(0)

if __name__ == "__main__":
    main()