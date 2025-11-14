import fitz
import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ===============================================
# --- Configuration (Your Final Settings) ---
# ===============================================

# 📂 Directory to WATCH for new PDF files
INPUT_DIRECTORY = r"C:\Users\User\Desktop\Pdf.Test" 

# 🗄️ Directory where all output JPG files should be saved
OUTPUT_DIRECTORY = r"C:\Users\User\Desktop\Pdf.Test\Fotos"

# 📐 Your manual coordinates: (X_left, Y_top_down, X_right, Y_bottom_down)
CROP_COORDS = (70, 170, 270, 330)

# 🔎 Optional: Resolution zoom factor
RESOLUTION_ZOOM = 3 

# --- 1. CORE PROCESSING FUNCTION (with File Opening Retry Logic) ---

def crop_pdf_to_jpg(input_pdf_path, output_dir, coords, zoom_factor):
    """
    Reads a single PDF with retries, targets the second-to-last page, crops it, saves 
    the JPG, and returns the path of the processed PDF.
    """
    input_filename = os.path.basename(input_pdf_path)
    doc = None
    max_open_attempts = 5

    # File Opening Retry Loop to handle incomplete/locked files
    for attempt in range(1, max_open_attempts + 1):
        try:
            doc = fitz.open(input_pdf_path)
            total_pages = len(doc)
            
            if total_pages > 1:
                # Success! File opened and has pages. Break the retry loop.
                print(f"File successfully opened (Attempt {attempt}/{max_open_attempts}). Pages found: {total_pages}.")
                break
            else:
                # File opened, but reported 0 or 1 page (likely still being written).
                if doc: doc.close()
                print(f"File opened but reported {total_pages} pages (Attempt {attempt}/{max_open_attempts}). Retrying in 2 seconds...")
                time.sleep(2)

        except Exception as e:
            print(f"Error opening file (Attempt {attempt}/{max_open_attempts}): {e}. Retrying in 2 seconds...")
            time.sleep(2)

        if attempt == max_open_attempts:
            print(f"🛑 FINAL FAILURE: Could not open/read '{input_filename}' after {max_open_attempts} attempts.")
            return None # Indicate failure

    # Check if processing is possible after retries
    if total_pages < 2:
        print(f"Skipping '{input_filename}': PDF has only {total_pages} pages or failed to open.")
        if doc: doc.close()
        return None 

    # --- Processing Logic ---
    TARGET_PAGE_INDEX = total_pages - 2 
    output_filename = "cropped_" + input_filename.replace(".pdf", ".jpg")
    output_full_path = os.path.join(output_dir, output_filename)

    try:
        print(f"Processing: {input_filename} (Page {TARGET_PAGE_INDEX + 1})...")

        page = doc[TARGET_PAGE_INDEX]
        
        # Define Crop Area (PyMuPDF uses Top-Down Y)
        X_left, Y_top_down, X_right, Y_bottom_down = coords[0], coords[1], coords[2], coords[3]
        crop_rect = fitz.Rect(X_left, Y_top_down, X_right, Y_bottom_down)
        
        # Render and Save as JPG
        mat = fitz.Matrix(zoom_factor, zoom_factor)
        pix = page.get_pixmap(matrix=mat, clip=crop_rect) 
        pix.save(output_full_path) 
        
        doc.close()
            
        print(f"✅ Saved JPG: '{output_filename}'")
        return input_pdf_path 
        
    except Exception as e:
        print(f"❌ An error occurred while processing {input_filename}: {e}")
        if doc:
            doc.close()
        return None


# --- 2. WATCHDOG EVENT HANDLER (Deletetion temporarily disabled) ---

class PdfHandler(FileSystemEventHandler):
    """Custom handler to process new PDF files detected by watchdog."""

    def on_created(self, event):
        """Called when a file or directory is created."""
        
        if not event.is_directory and event.src_path.lower().endswith('.pdf'):
            
            print(f"File detected: {os.path.basename(event.src_path)}. Waiting 2 seconds before processing...")
            time.sleep(2) # Initial waiting time
            
            pdf_path_to_delete = crop_pdf_to_jpg(
                event.src_path, 
                OUTPUT_DIRECTORY, 
                CROP_COORDS, 
                RESOLUTION_ZOOM
            )

            # --- DELETION PROCESS CUT (TEMPORARY SOLUTION) ---
            if pdf_path_to_delete:
                print(f"⚠️ TEMPORARY: Skipping deletion of '{os.path.basename(pdf_path_to_delete)}'.")
                print("   Please delete this PDF manually after verifying the JPG output.")
                
            # If you resolve the 'Access Denied' issue, you can uncomment the robust deletion loop here.
            # (See previous steps for the full robust deletion code)


# --- 3. MAIN EXECUTION LOOP ---

if __name__ == "__main__":
    # 1. Ensure the output directory exists
    if not os.path.exists(OUTPUT_DIRECTORY):
        os.makedirs(OUTPUT_DIRECTORY)
        print(f"Created output directory: {OUTPUT_DIRECTORY}")

    # 2. Start the monitor
    print(f"✨ Starting PDF file monitor on: {INPUT_DIRECTORY}")
    print("-----------------------------------------------------")
    
    event_handler = PdfHandler()
    observer = Observer()
    observer.schedule(event_handler, INPUT_DIRECTORY, recursive=False)
    observer.start()

    try:
        while True:
            # Keep the main thread alive so the observer can run
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nMonitor stopped by user.")
    
    observer.join()