import os
import random
import threading
from barcode import EAN13, EAN8, JAN, UPCA
from barcode.writer import ImageWriter
from datetime import datetime

CODEBAR_CONFIG = { 
    "EAN13": {"class": EAN13, "length": 12},
    "EAN8": {"class": EAN8, "length": 7,},
    "UPC-A": {"class": UPCA, "length": 11},
    "JAN13": {"class": JAN, "length": 12, "prefix": "45"}
}

def generate_unique_number(barcode_type, target_folder, used_numbers, idx):
    
    config = CODEBAR_CONFIG.get(barcode_type)

    if not config:
        raise ValueError(f"Codebar type: {barcode_type} is not supported")

    barcode_class = config["class"]
    len_code = config["length"]
    prefix = config.get("prefix", "")

    random_len = len_code - len(prefix)
    random_part = ''.join([str(random.randint(0, 9)) for _ in range(random_len)])
    while random_part in used_numbers:
        random_part = ''.join([str(random.randint(0, 9)) for _ in range(random_len)])
    used_numbers.add(random_part)

    number = prefix + random_part

    barcode = barcode_class(number, writer=ImageWriter())
    archive_name = f"{idx+1:03d}_{barcode.get_fullcode()}"
    barcode.save(os.path.join(target_folder, archive_name))

def _barcode_gen_thread(n, target_folder, barcode_type, on_progress, on_complete, on_error):
    """Function to run barcode generation in a thread"""
    try:
        used_numbers = set()

        for i in range(n):
                generate_unique_number(barcode_type, target_folder, used_numbers, i)
                if on_progress:
                    on_progress(i + 1, n)  # Update progress

        if on_complete:
            on_complete(target_folder)  # Notify completion
            
    except Exception as e:
        if on_error:
            on_error("Error during barcode generation: " + str(e))

def generate_barcodes(n, target_folder, barcode_type, on_progress=None, on_complete=None, on_error=None):
    """Validates config, creates output folder, spawns generation thread."""
    if not target_folder:
        if on_error:
            on_error("Error: Please select a target folder.")
        return

    if not barcode_type:
        if on_error:
            on_error("Error: Please select a barcode type.")
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
    thread = threading.Thread(target=_barcode_gen_thread, args=(nm, final_destination, barcode_type, on_progress, on_complete, on_error), daemon=False)
    thread.start()