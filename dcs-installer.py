#!/usr/bin/env python3
"""
DCS_Installer.py  Copyright (C) <2025>  J Ryan Cole

Author:  J Ryan Cole
Date:    August 22, 2025
Version: 1.0
Repository: https://github.com/mowerman1708/Linux-installer-for-DCS-World

Description:    This script downloads the files needed for a DCS installation on GNU/Linux.
                Creates the wine prefix at your choice of location. Proceeds to run the DCS World installer.

"""
import os
import subprocess
import requests
import chardet
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import time
# Check for root account
if os.geteuid() == 0:
    print("This script is not supposed to be run as root!")
    exit(1)
# Global stack to hold messages
message_stack = []
displaying_message = False
# Global variables
is_blinking = True  #to control the blinking
script_dir = os.path.dirname(os.path.realpath(__file__))  # Sets a path to this script
install_dir = ""
wine_path = ""
dcs_url = "https://www.digitalcombatsimulator.com/upload/iblock/959/d33ul8g3arxnzc1ejgdaa8uev8gvmew2"
dcs_installer = "DCS_World_web.exe"
wine_git = "https://dl.winehq.org/wine/source/8.0/wine-8.0.1.tar.xz"
wine_file = "wine-8.0.1.tar.xz"
wine_directory = "wine-lutris-GE-Proton8-26-x86_64"
#####################################################
#####################################################
def check_file_encoding(file_path):
    with open(file_path, 'rb') as file:
        raw_data = file.read(10000)  # Read the first 10,000 bytes
        result = chardet.detect(raw_data)  # Detect encoding
        encoding = result['encoding']
        confidence = result['confidence']
        if encoding is None:
            print("Could not detect encoding. Defaulting to 'utf-8'.")
            return 'utf-8'  # Default to 'utf-8' or handle as needed
        print(f"Detected encoding: {encoding} (Confidence: {confidence * 100:.2f}%)")
        return encoding

#####################################################
def convert_file_encoding(file_path, target_encoding='utf-8'):
    current_encoding = check_file_encoding(file_path)
    if current_encoding is None:
        print("Encoding detection failed. Cannot convert file.")
        return  # Exit the function if encoding detection fails
    if current_encoding.lower() != target_encoding.lower():
        print(f"Converting file from {current_encoding} to {target_encoding}...")
        with open(file_path, 'r', encoding=current_encoding) as file:
            content = file.read()
        with open(file_path, 'w', encoding=target_encoding) as file:
            file.write(content)
        print("File encoding conversion completed.")
    else:
        print(f"No conversion needed. The file is already in {target_encoding} encoding.")

#####################################################
def download_file(url, dest, progress_var, status_bar, root):
    try:
        update_progress(progress_var, status_bar, 0, "Starting download...")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0
        with open(dest, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)
                downloaded_size += len(chunk)
                if total_size > 0:  # stop possible divide by zero
                    progress = (downloaded_size / total_size) * 100
                    update_progress(progress_var, status_bar, progress, f"Downloaded {downloaded_size} of {total_size} bytes...")
        update_progress(progress_var, status_bar, 100, "Download completed successfully!")
        return True
    except requests.RequestException as e:
        messagebox.showerror("Download Error", f"Download failed: {e}")
        return False

#####################################################
def update_progress(progress_var, status_bar, progress, message):
    progress_var.set(progress)
    status_bar.config(text=message)
    status_bar.update()  # Ensure the status bar updates immediately

#####################################################
def extract_wine_files(wine_file_path, runner_dir, progress_var, status_bar):
    # Check the file type
    file_type = subprocess.run(['file', wine_file_path], capture_output=True, text=True)
    if "gzip compressed data" in file_type.stdout:
        # It's a .tar.gz file
        update_progress(progress_var, status_bar, 10, "Extracting .tar.gz files...")
        try:
            subprocess.run(f"tar -xzvf {wine_file_path} -C {runner_dir}", shell=True, check=True)
            update_progress(progress_var, status_bar, 100, "Extraction completed successfully!")
            return True
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Extraction Error", f"Extraction failed: {e}")
            return False
    elif "XZ compressed data" in file_type.stdout:
        # It's a .tar.xz file
        update_progress(progress_var, status_bar, 10, "Extracting .tar.xz files...")
        try:
            subprocess.run(f"tar -xJvf {wine_file_path} -C {runner_dir}", shell=True, check=True)
            update_progress(progress_var, status_bar, 100, "Extraction completed successfully!")
            return True
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Extraction Error", f"Extraction failed: {e}")
            return False
    else:
        messagebox.showerror("File Type Error", "The specified file is not a valid .tar.gz or .tar.xz file.")
        return False

#####################################################
def display_next_message(status_bar):
    global displaying_message
    if message_stack and not displaying_message:
        displaying_message = True
        message = message_stack.pop(0)  # Pop the next message from the stack
        status_bar.config(text=message)  # Display the message
        # Schedule to keep the message visible until a new one comes in
        status_bar.after(1500, lambda: message_still_displayed(status_bar))

#####################################################
def message_still_displayed(status_bar):
    global displaying_message
    displaying_message = False  # Allow the next message to be displayed

#####################################################
def update_progress(progress_var, status_bar, progress, message):
    if progress_var is not None:
        progress_var.set(progress)
    # Push the new message onto the stack
    message_stack.append(message)
    # Attempt to display the next message
    display_next_message(status_bar)

#####################################################
def get_the_files(progress_var, status_bar, root):  # check/get the files that are needed
    os.makedirs(os.path.join(script_dir, 'tmp'), exist_ok=True)
    if not os.path.isfile(os.path.join(script_dir, 'tmp', wine_file)):  #check for Wine install
        if download_file(wine_git, os.path.join(script_dir, 'tmp', wine_file), progress_var, status_bar, root):
            update_progress(progress_var, status_bar, 0, f"{wine_file} downloaded successfully.")
    if not os.path.isfile(os.path.join(script_dir, 'tmp', dcs_installer)): #check for DCS installer
        if download_file(f"{dcs_url}/{dcs_installer}", os.path.join(script_dir, 'tmp', dcs_installer), progress_var,                status_bar, root):
            update_progress(progress_var, status_bar, 0, f"{dcs_installer} downloaded successfully.")

#####################################################
def create_wine_prefix(progress_var, status_bar, root):
    global install_dir
    global wine_directory  # Use the global variables
    while True:  # Start a loop to keep asking for the directory
        install_dir = filedialog.askdirectory(title='Choose or add your DCS install location',
                                              initialdir=os.path.expanduser("~"))
        if not install_dir:
            messagebox.showwarning("Warning", "No installation directory selected.")
            return
        wine_prefix_path = install_dir  # Set the wine prefix path
        if os.path.exists(wine_prefix_path) and not messagebox.askyesno("Overwrite Existing Prefix",
                f"Wine prefix already exists at: {wine_prefix_path}.\nDo you want to overwrite it?"):
            # If the user chooses not to overwrite, continue the loop to ask for a new directory
            continue  # This will go back to the start of the while loop
        # If we reach here, either the prefix does not exist or the user chose to overwrite
        break  # Exit the loop
    os.makedirs(wine_prefix_path, exist_ok=True)
    runner_dir = os.path.join(install_dir, "runner")
    os.makedirs(runner_dir, exist_ok=True)
    wine_file_path = os.path.join(script_dir, "tmp", wine_file)
    try:
        update_progress(progress_var, status_bar, 10, "Extracting Wine files...")
        # Step 1: Extract Wine files
        success = extract_wine_files(wine_file_path, runner_dir, progress_var, status_bar)
        if not success:
            update_progress(progress_var, status_bar, 100, "Extraction failed.")
            return 1
        # Setup wine environment variables
        update_progress(progress_var, status_bar, 50, "Setting environment variables...")
        os.environ["WINEPREFIX"] = wine_prefix_path
        os.environ["wine_path"] = os.path.join(runner_dir, wine_directory, "bin")
        os.environ["WINEDLLOVERRIDES"] = "wbemprox=n;msdmo=n"
        # Install necessary components with winetricks
        update_progress(progress_var, status_bar, 75, "Installing necessary components...")
        # Verify that winetricks is installed
        if subprocess.call(["which", "winetricks"], stdout=subprocess.PIPE, stderr=subprocess.PIPE) != 0:
            messagebox.showerror("Error", "winetricks is not installed. Please install it before proceeding.")
            return 1
        # Now run wintricks
        subprocess.run(["winetricks", "-q", "corefonts", "oleaut32", "vcrun2017", "dxvk", "d3dcompiler_43",        "d3dcompiler_47", "d3dx9", "win10"])
        update_progress(progress_var, status_bar, 100, f"Wine prefix created successfully at {wine_prefix_path}")
    except subprocess.CalledProcessError as e:  #something failed
        messagebox.showerror("Error", f"Failed to set up Wine prefix: {e}")
        update_progress(progress_var, status_bar, 0, "Error occurred during Wine prefix setup.")
        return 1
    # Close the created prefix
    subprocess.run(["wineserver", "-k"], env={"WINEPREFIX": wine_prefix_path})

#####################################################
def run_dcs_installer(wine_path, install_dir, progress_var, status_bar, root):
    dcs_installer_path = os.path.join(script_dir, 'tmp', dcs_installer)
    if not os.path.isfile(dcs_installer_path):  #check if installer exists
        messagebox.showerror("Error", f"Installer file does not exist: {dcs_installer_path}")
        return
    try:
        update_progress(progress_var, status_bar, 0, f"Installing DCS World at {install_dir}.")
        # run DCS installer
        result = subprocess.run(
            [os.path.join(wine_path, 'wine'), dcs_installer_path],
            capture_output=True,
            check=True,
            env={**os.environ, "WINEDEUG": "+ALL"}) #<<<<< debugging on

        update_progress(progress_var, status_bar, 100, "DCS installation completed successfully.")
    except subprocess.CalledProcessError as e:
        # Log the error output to a file
        error_output = e.stderr.decode('utf-8', errors='replace')
        update_progress(progress_var, status_bar, 0, f"DCS installation failed. Writing wine_error_log.txt to {script_dir}.")
        with open(os.path.join(script_dir, 'wine_error_log.txt'), 'w') as log_file:
            log_file.write(error_output)
        # Show a truncated error message
        truncated_message = error_output[:500] + '...' if len(error_output) > 500 else error_output
        messagebox.showerror("Error", f"DCS installation failed:\n{truncated_message}")
    #routine checks for running wineserver and shuts it down
    try:
        subprocess.run([os.path.join(wine_path, 'wineserver'), '-q'], check=True)  # Check if wineserver is running
    except subprocess.CalledProcessError:
    # If wineserver is not running, return without shutting down
        return
    # If wineserver is running, attempt to shut it down
    try:
        subprocess.run([os.path.join(wine_path, 'wineserver'), '-k'], check=True)
    except subprocess.CalledProcessError as e:
        messagebox.showwarning("Warning", f"Failed to shut down the Wine server. Returned {e}")
    # Exit the function back to the GUI
    return

#####################################################
def create_gui():
    root = tk.Tk()
    root.title("DCS GNU/Linux Installer")
    root.geometry("400x300")  # Set a fixed size for the window
    title_frame = ttk.Frame(root)
    title_frame.pack(pady=10)
    tk.Label(title_frame, text="Welcome to GNU/Linux DCS Installer", font=("Arial", 16, "bold")).pack()
    progress_frame = ttk.Frame(root)
    progress_frame.pack(pady=10, fill=tk.X)
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(progress_frame, variable=progress_var, maximum=100)
    progress_bar.pack(fill=tk.X)
    button_frame = ttk.Frame(root)  # Ensure button_frame is defined here
    button_frame.pack(pady=10)
    busy_frame = ttk.Frame(root)
    busy_frame.pack(pady=10)
    busy_label = tk.Label(busy_frame, text="Please select:", font=("Arial", 11, "bold"), fg="green")
    busy_label.pack()
    tooltip = None  # Define tooltip variable here
    def show_tooltip(event, text):
        nonlocal tooltip
        if tooltip is None:
            tooltip = tk.Toplevel(root)
            tooltip.wm_overrideredirect(True)
            tooltip_label = tk.Label(tooltip, text=text, background="lightyellow", relief="solid", borderwidth=1)
            tooltip_label.pack()
        else:
            tooltip.children['!label'].config(text=text)
        tooltip.deiconify()
        x = event.x_root + 10
        y = event.y_root + 10
        tooltip.wm_geometry(f"+{x}+{y}")
    def hide_tooltip(event):
        nonlocal tooltip
        if tooltip is not None:
            tooltip.withdraw()
    def create_button_with_tooltip(text, command, tooltip_text):
        button = tk.Button(button_frame, text=text, command=command, width=30, font=("Arial", 10, "bold"))
        button.pack(pady=5)
        button.bind("<Enter>", lambda e, text=tooltip_text: show_tooltip(e, text))
        button.bind("<Leave>", hide_tooltip)
        return button
    def run_get_the_files():
        get_the_files(progress_var, status_bar, root)
        button2.config(state=tk.NORMAL)  # Enable button 2 after option 1 completes
        button1.config(state=tk.DISABLED)  # Disable button 1 after use
    def run_create_wine_prefix():
        create_wine_prefix(progress_var, status_bar, root)
        button3.config(state=tk.NORMAL)  # Enable button 3 after option 2 completes
        button2.config(state=tk.DISABLED)  # Disable button 2 after use
    def run_installer():
        run_dcs_installer(wine_path, install_dir, progress_var, status_bar, root)
        button3.config(state=tk.DISABLED)  # Disable button 3 after use

    button1 = create_button_with_tooltip("1. Download Necessary Files", lambda: run_task(run_get_the_files, button1), "Download required files for DCS.")
    button2 = create_button_with_tooltip("2. Create Wine Prefix", lambda: run_task(run_create_wine_prefix, button2), "Set up a Wine prefix for DCS.")
    button3 = create_button_with_tooltip("3. Install DCS", lambda: run_task(run_installer, button3), "Install the DCS game.")
    button_exit = create_button_with_tooltip("Exit", root.quit, "Close the application.")
    button2.config(state=tk.DISABLED)  # Disable button 2 initially
    button3.config(state=tk.DISABLED)  # Disable button 3 initially
    status_bar = tk.Label(root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.CENTER, font=("Arial", 11, "bold"))
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def run_task(task, button):
        global is_blinking
        button_exit.config(state=tk.DISABLED)   # Disable exit_button while routine runs
        button.config(state=tk.DISABLED)  # Disable the current button
        busy_label.config(text="--- Working ---")  # Show busy indicator
        busy_label['foreground'] = 'red'  # Set initial color to red
        is_blinking = True  # Set blinking flag to True
        blink_busy_indicator()  # Start blinking effect
        root.update()  # Update the GUI to reflect the change
        threading.Thread(target=task_wrapper, args=(task, button)).start()

    def task_wrapper(task, button):
        task()  # Run the task
        stop_blinking()  # Stop the blinking effect
        busy_label.config(text="Please Select", fg="green")  # Reset busy indicator
        button_exit.config(state=tk.NORMAL)   # Re-enable exit_button after routine runs

    def blink_busy_indicator():
        if is_blinking:  # Check if blinking should continue
            current_color = busy_label['foreground']
            busy_label['foreground'] = 'green' if current_color == 'red' else 'red'
            root.after(750, blink_busy_indicator)  # Change color every 500 milliseconds

    def stop_blinking():
        global is_blinking
        is_blinking = False  # Set blinking flag to False
        busy_label['foreground'] = 'green'  # Ensure the label is green when stopping
        # Status bar

    root.mainloop()

if __name__ == "__main__":
    create_gui()

