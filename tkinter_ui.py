import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
# from tkinter import ttk
# import threading
# import time
# Later on we will restore the threading and progress bar functionality, but for now, we will focus on the core functionality of the GUI.
from generator import generate_barcodes
from config import config

class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command=None, radius=20, padding=10, bg_color="#4CAF50", 
                 hover_color="#45a049", active_color="#ff0000", text_color="white", 
                 font=("Arial", 11, "bold"), **kwargs):
        tk.Canvas.__init__(self, parent, borderwidth=0, relief="flat", 
                          highlightthickness=0, bg=parent.cget("bg"), **kwargs)
        self.command = command
        self.radius = radius
        self.padding = padding
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.active_color = active_color
        self.text_color = text_color
        self.font = font
        self.text = text
        
        # Calculate button size based on text
        temp_label = tk.Label(self, text=text, font=font)
        temp_label.update_idletasks()
        text_width = temp_label.winfo_reqwidth()
        text_height = temp_label.winfo_reqheight()
        temp_label.destroy()
        
        self.width = text_width + padding * 2
        self.height = text_height + padding * 2
        
        self.config(width=self.width, height=self.height)
        
        self.draw_button(self.bg_color)
        
        # Bind events
        self.bind("<Button-1>", self.on_click)
        self.bind("<ButtonRelease-1>", self.on_release)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
    
    def draw_button(self, color):
        self.delete("all")
        # Draw rounded rectangle
        x1, y1 = 0, 0
        x2, y2 = self.width, self.height
        r = self.radius
        
        # Create rounded rectangle using arcs and lines
        self.create_arc(x1, y1, x1 + 2*r, y1 + 2*r, start=90, extent=90, fill=color, outline=color)
        self.create_arc(x2 - 2*r, y1, x2, y1 + 2*r, start=0, extent=90, fill=color, outline=color)
        self.create_arc(x1, y2 - 2*r, x1 + 2*r, y2, start=180, extent=90, fill=color, outline=color)
        self.create_arc(x2 - 2*r, y2 - 2*r, x2, y2, start=270, extent=90, fill=color, outline=color)
        self.create_rectangle(x1 + r, y1, x2 - r, y2, fill=color, outline=color)
        self.create_rectangle(x1, y1 + r, x2, y2 - r, fill=color, outline=color)
        
        # Draw text
        self.create_text(self.width/2, self.height/2, text=self.text, 
                        fill=self.text_color, font=self.font, tags="text")
    
    def on_enter(self, event):
        self.draw_button(self.hover_color)
        self.config(cursor="hand2")
    
    def on_leave(self, event):
        self.draw_button(self.bg_color)
        self.config(cursor="")
    
    def on_click(self, event):
        self.draw_button(self.active_color)
    
    def on_release(self, event):
        self.draw_button(self.hover_color)
        if self.command:
            self.command()

def only_integer(char):
    return char.isdigit()

def select_folder():
    folder_selected = filedialog.askdirectory(title="Select Folder")
    if folder_selected:
        config["target_folder"] = folder_selected
        label_folder.config(text=f"Selected Folder:\n {shorten_path(config['target_folder'])}")

def update_values():
    config["input_value"] = title_entry.get()
    # print(f"Updated config: {config} ")  # Debugging line
    if not config["target_folder"]:
        messagebox.showerror("Error", "Please select a target folder.")
        return
    if not config["input_value"].isdigit() or int(config["input_value"]) <= 0:
        messagebox.showerror("Error", "Please enter a valid positive number for the quantity of barcodes.")
        return
    
    if messagebox.askokcancel("Configuration Updated", f"Barcode(s) to generate: {config['input_value']}\nFolder selected: {config['target_folder']}"):
        generate_barcodes(config["input_value"], config["target_folder"],
                    on_progress = lambda current, total: print(f"Progress: {current}/{total} barcodes generated."),
                    on_complete = lambda folder: messagebox.showinfo("Completed", f"Barcodes generated successfully in:\n{folder}"),
                    on_error = lambda msg: messagebox.showerror("Error", msg))
    else:
        return
    
def shorten_path(path, max_length=30):
    if len(path) <= max_length:
        return path
    else:
        part_length = (max_length - 3) // 2
        return f"{path[:part_length]}...{path[-part_length:]}"

# Main window
root = tk.Tk()
root.title("Barcode Generator-beta")
root.geometry("450x580")
root.resizable(False, False)

# Title
title_frame = tk.Frame(root, bg="#4CAF50", height=120)
title_frame.pack(fill=tk.X, pady=0)
title_frame.pack_propagate(False)

icon_label = tk.Label(title_frame, text="📊", font=("Arial", 30), 
                      fg="white",
                      bg="#4CAF50")
icon_label.pack(pady=(15, 0))

title_label = tk.Label(title_frame, text="Barcode Generator", 
                      font=("Arial", 18, "bold"), 
                      fg="white", 
                      bg="#4CAF50")
title_label.pack(pady=(0, 15))

# Quantity section
quantity_frame = tk.Frame(root, bg="#f5f7fa", height=100)
quantity_frame.pack(fill=tk.X,)
quantity_frame.pack_propagate(False)

quantity_label = tk.Label(quantity_frame, 
                         text="Quantity of barcodes to generate:", 
                         font=("Arial", 11, "bold"),
                         fg="#2c3e50",
                         bg="#f5f7fa")
quantity_label.pack(anchor="w", pady=(10, 0))

# Entry with border
entry_container = tk.Frame(quantity_frame, 
                          bg="white", 
                          highlightbackground="#dcdde1",
                          highlightthickness=2)
entry_container.pack(fill=tk.X)

title_entry = tk.Entry(entry_container, 
                      font=("Arial", 12), 
                      fg="#2c3e50",
                      bg="white",
                      relief=tk.FLAT,
                      bd=8)
title_entry.pack(fill=tk.X, padx=5, pady=5)
title_entry.insert(0, config["input_value"])

# Validate that only integers can be entered
vcmd = (root.register(only_integer), '%S')
title_entry.config(validate='key', validatecommand=vcmd)

# Folder selection section
folder_frame = tk.Frame(root, bg="#f5f7fa")
folder_frame.pack(fill=tk.X, padx=30, pady=20)

folder_label_title = tk.Label(folder_frame, 
                             text="Destination Folder:", 
                             font=("Arial", 11, "bold"),
                             fg="#2c3e50",
                             bg="#f5f7fa")
folder_label_title.pack(anchor="w", pady=(0, 8))

# Button with modern style
folder_button = RoundedButton(folder_frame, 
                         text="📁 Select Folder", 
                         command=select_folder,
                         radius=15,
                         padding=15,
                         bg_color="#4CAF50",
                         hover_color="#45a049",
                         active_color="#3d8b40",
                         text_color="white",
                         font=("Arial", 11, "bold"))
folder_button.pack(pady=(0, 10))

label_folder = tk.Label(folder_frame, 
                       text="No folder selected", 
                       font=("Arial", 9),
                       fg="#000000",
                       bg="#f5f7fa",
                       wraplength=400)
label_folder.pack(pady=(0, 20))

# Update button
update_button = RoundedButton(folder_frame, 
                         text="✓ Generate Barcodes", 
                         command=update_values,
                         radius=15,
                         padding=15,
                         bg_color="#4CAF50",
                         hover_color="#45a049",
                         active_color="#3d8b40",
                         text_color="white",
                         font=("Arial", 11, "bold"))
update_button.pack()

# Instructions
instructions = tk.Label(root, text="\nInstructions:\n1. Enter the number of barcodes to generate\n2. Select destination folder\n3. Click 'Generate Barcodes'", 
                       font=("Arial", 9), justify="left", fg="gray")
instructions.pack(pady=20)

def Run():
    root.mainloop()