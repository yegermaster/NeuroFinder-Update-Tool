"""
This module provides a GUI for uploading CSV and Excel files.
"""
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import customtkinter as ctk
import pandas as pd
from tkinterdnd2 import TkinterDnD, DND_FILES
from db_handler import DbHandler
from dotenv import load_dotenv
import datetime as dt
import os


#TODO: srearch both sites when fiding new comapnies
#TODO: add updating data

# Constants
load_dotenv()
MAIN_DB_PATH = os.getenv('MAIN_DB_PATH')
NOT_NEUROTECH_DB_PATH = os.getenv('NOT_NEUROTECH_DB_PATH')
NEW_COMPANIES_PATH = os.getenv('NEW_COMPANIES_PATH')


print(f"MAIN_DB_PATH: {MAIN_DB_PATH}")  # Debugging line
print(f"NOT_NEUROTECH_DB_PATH: {NOT_NEUROTECH_DB_PATH}")  # Debugging line

FILE_TYPES = ["tsun", "cb", "pb", "other"]
loading_files = []
loaded_files = []
db_handler = DbHandler(MAIN_DB_PATH, NOT_NEUROTECH_DB_PATH )


def read_file(filepath:str):
    """Reads a file and updates the loading file list. """
    try:
        if filepath.endswith('.csv'):
            pd.read_csv(filepath)
        elif filepath.endswith('.xlsx'):
            pd.read_excel(filepath)
        else:
            messagebox.showerror("Error", "Unsupported file format.")
            return
        loading_files.append({"path": filepath, "data_type": tk.StringVar(value="tsun")})
        update_loading_list()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read file: {e}")

def update_loading_list():
    """Updates the displayed list of loading files."""
    for widget in loading_list_frame.winfo_children():
        widget.destroy()

    for i, file_info in enumerate(loading_files):
        file_path = file_info["path"]
        file_type_var = file_info["data_type"]

        file_label = ttk.Label(loading_list_frame, text=file_path.split('/')[-1])
        file_label.grid(row=i, column=0, padx=5, pady=5)

        type_menu = ttk.OptionMenu(loading_list_frame,
                                file_type_var, file_type_var.get(),
                                *FILE_TYPES)
        type_menu.grid(row=i, column=1, padx=5, pady=5)

        delete_button = ttk.Button(loading_list_frame,
                                    text="Delete",
                                    command=lambda idx=i: delete_loading_file(idx))
        delete_button.grid(row=i, column=2, padx=5, pady=5)

def delete_loading_file(index: int):
    """Deletes a file from the loading file list."""
    del loading_files[index]
    update_loading_list()

def open_file_dialog():
    """Opens a file dialog to select a file for uploading."""
    filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"),
                                                      ("Excel files", "*.xlsx")])
    if filepath:
        read_file(filepath)

def drop(event: any):
    """Handles file drop events."""
    filepath = event.data
    if filepath:
        filepath = filepath.strip('{}')  # Strip curly braces if present
        read_file(filepath)

def upload_all_files():
    """Handles the final upload of all files."""
    if not loading_files:
        messagebox.showerror("Error", "No files to upload.")
        return

    valid_files = []
    for file_info in loading_files:
        data_type = file_info['data_type'].get()
        file_path = file_info['path']
        if not db_handler.validate_file_type(file_path, data_type):
            messagebox.showerror("Error", f"File '{file_path.split('/')[-1]}' does not match the specified type '{data_type}'. Please try again.")
        else:
            valid_files.append(file_info)

    if not valid_files:
        return

    for file_info in valid_files:
        db_handler.start_searching_process(file_info['path'], file_info['data_type'].get())
        loaded_files.append(file_info)

    loading_files.clear()
    update_loading_list()
    update_loaded_list()
    messagebox.showinfo("Success", "All valid files uploaded successfully!")

def export_all_files():
    """Exports files to Excel."""
    if not loaded_files:
        messagebox.showerror("Error", "No files to export.")
        return
    db_handler.export(NEW_COMPANIES_PATH)
    messagebox.showinfo("Success", "All files exported successfully!")


def update_loaded_list():
    """Updates the displayed list of loaded files."""
    for widget in loaded_list_frame.winfo_children():
        widget.destroy()

    for i, file_info in enumerate(loaded_files):
        file_path = file_info["path"]

        file_label = ttk.Label(loaded_list_frame, text=file_path.split('/')[-1])
        file_label.grid(row=i, column=0, padx=5, pady=5)

def upload_image():
    """Opens the upload image gui"""
    pass

# Initialize the root window with customtkinter style
ctk.set_appearance_mode("System")  # Modes: "System" (default), "Light", "Dark"
ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue"

root = TkinterDnD.Tk()
root.title("File Upload GUI")
root.geometry("600x600")

# Main header
header = ctk.CTkLabel(root, text="Upload Files", font=("Arial", 16), fg_color="green", text_color="white", anchor="center")
header.pack(fill="x", pady=10)

# Img uploader
img_button = ctk.CTkButton(root, text="Upload Images", command=upload_image)
img_button.pack(pady=10)

# Drag and drop frame
drag_frame = ctk.CTkFrame(root, width=400, height=200, corner_radius=10)
drag_frame.pack(pady=20)
drag_frame.pack_propagate(False)

upload_button = ctk.CTkButton(drag_frame, text="Upload File or Drag files here", command=open_file_dialog)
upload_button.pack(pady=10)

# Button frame
button_frame = ctk.CTkFrame(root, width=600, height=100, corner_radius=10)
button_frame.pack(pady=20)
button_frame.pack_propagate(False)

final_upload_button = ctk.CTkButton(button_frame, text="Load All Files", command=upload_all_files)
final_upload_button.pack(pady=5)

export_button = ctk.CTkButton(button_frame, text="Export", command=export_all_files)
export_button.pack(pady=5)

# Section for files ready to load
loading_label = ctk.CTkLabel(root, text="Files ready to Load:", anchor="w")
loading_label.pack(anchor="w", padx=20)

loading_list_frame = ctk.CTkFrame(root)
loading_list_frame.pack(pady=10, padx=20, fill="both", expand=True)

# Section for files already loaded
loaded_label = ctk.CTkLabel(root, text="Files Already Loaded:", anchor="w")
loaded_label.pack(anchor="w", padx=20)

loaded_list_frame = ctk.CTkFrame(root)
loaded_list_frame.pack(pady=10, padx=20, fill="both", expand=True)

drag_frame.drop_target_register(DND_FILES)
drag_frame.dnd_bind('<<Drop>>', drop)

root.mainloop()