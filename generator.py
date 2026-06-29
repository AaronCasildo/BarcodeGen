import os
import random
import threading
from barcode import EAN13
from barcode.writer import ImageWriter
from datetime import datetime

# Single function to generate a single barcode and save it as an image
def barcode_rendering(target_folder, used_numbers, index):
    # Generate a unique 12-digit number for EAN13 barcode
    number = ''.join([str(random.randint(0, 9)) for _ in range(12)])
    while number in used_numbers:
        number = ''.join([str(random.randint(0, 9)) for _ in range(12)])
    used_numbers.add(number)

    # Create EAN13 barcode with PNG image
    barcode = EAN13(number, writer=ImageWriter())

    # Save to specified folder
    archive_name = f"{index+1:03d}_{barcode.get_fullcode()}"
    barcode.save(os.path.join(target_folder, archive_name))
    # print(f"Generated barcode {index+1}: {archive_name}.png")

def _barcode_gen_thread(n, target_folder, on_progress, on_complete, on_error):
    """Function to run barcode generation in a thread"""
    try:
        used_numbers = set()
        for i in range(n):
            barcode_rendering(target_folder, used_numbers, i)

            if on_progress:
                on_progress(i + 1, n)  # Update progress

        if on_complete:
            on_complete(target_folder)  # Notify completion
            
    except Exception as e:
        if on_error:
            on_error("Error during barcode generation: " + str(e))

def generate_barcodes(n, target_folder, on_progress=None, on_complete=None, on_error=None):
    """Validates config, creates output folder, spawns generation thread."""
    if not target_folder:
        if on_error:
            on_error("Error: Please select a target folder.")
        return
        
    try:
        nm = int(n)
        if nm <= 0:
            if on_error:
                on_error("Error: Please enter a positive number.")
            return
    except ValueError:
        if on_error:
            on_error("Error: Please enter a valid number.")
        return

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    final_destination = os.path.join(target_folder, f"Barcodes_{timestamp}")
    
    try:
        os.makedirs(final_destination, exist_ok=True)
    except Exception as e:
        if on_error:
            on_error(f"Error: Could not create subfolder: {str(e)}")
        return
    
    # Start the barcode generation in a separate thread
    thread = threading.Thread(target=_barcode_gen_thread, args=(nm, final_destination, on_progress, on_complete, on_error), daemon=False)
    thread.start()