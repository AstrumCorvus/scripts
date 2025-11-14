#output is a single jpg file 

import fitz  # PyMuPDF library for rendering and cropping
import os

def crop_pdf_to_jpg(input_pdf_path, output_dir, output_filename, coords, zoom_factor=3):
    """
    Reads a PDF, targets the second-to-last page, crops it using manual coordinates,
    and saves the resulting area as a high-resolution JPG file.
    """
    try:
        # --- 1. Preparation ---
        doc = fitz.open(input_pdf_path)
        
        total_pages = len(doc)
        
        if total_pages < 2:
            print(f"Error: PDF has only {total_pages} pages. Cannot access 'last page - 1'.")
            return
            
        # Dynamically calculate the target page index (last page - 1)
        TARGET_PAGE_INDEX = total_pages - 2 

        # Create the full output path
        output_full_path = os.path.join(output_dir, output_filename)

        print(f"Total pages: {total_pages}. Targeting page index {TARGET_PAGE_INDEX} (Page {TARGET_PAGE_INDEX + 1}).")

        page = doc[TARGET_PAGE_INDEX]
        
        # --- 2. Define Crop Area (PyMuPDF uses Top-Down Y) ---
        X_left, Y_top_down, X_right, Y_bottom_down = coords[0], coords[1], coords[2], coords[3]
        
        # PyMuPDF Rect format: (x0, y0, x1, y1), uses top-down Y
        crop_rect = fitz.Rect(X_left, Y_top_down, X_right, Y_bottom_down)
        
        print(f"Crop area (PyMuPDF Rect): {crop_rect}")
        
        # --- 3. Render the Cropped Area to Pixels (Rasterize) ---
        
        # 'zoom_factor' increases resolution (DPI)
        mat = fitz.Matrix(zoom_factor, zoom_factor)
        
        # get_pixmap renders ONLY the area specified by 'clip'
        pix = page.get_pixmap(matrix=mat, clip=crop_rect) 

        # --- 4. Save the Pixmap as JPG (FIXED) ---
        # Removed the unexpected 'format="jpeg"' argument
        pix.save(output_full_path) 
        
        doc.close()
            
        print(f"\n✅ Successfully cropped page and saved JPG to '{output_full_path}'")
        
    except Exception as e:
        print(f"\nAn error occurred: {e}")

# ===============================================
# --- Configuration (Your Final Settings) ---
# ===============================================

INPUT_FILE = r"C:\Users\User\Desktop\Pdf.Test\metamap-verification-68a48d600fced7c05290bb27.pdf"
OUTPUT_DIRECTORY = r"C:\Users\User\Desktop\Pdf.Test\Fotos"
OUTPUT_JPG_FILENAME = "cropped_signature.jpg" 

# Your manual coordinates: (X_left, Y_top_down, X_right, Y_bottom_down)
CROP_COORDS = (70, 170, 270, 330)

# Optional: Increase this number (e.g., 4, 5) if you need higher quality/resolution
RESOLUTION_ZOOM = 3 

# --- Run the script ---
crop_pdf_to_jpg(INPUT_FILE, OUTPUT_DIRECTORY, OUTPUT_JPG_FILENAME, CROP_COORDS, RESOLUTION_ZOOM)