import subprocess
import os
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog

# Function to get a unique filename
def get_unique_filename(filepath):
    base, ext = os.path.splitext(filepath)
    counter = 1
    while os.path.exists(filepath):
        filepath = f"{base} ({counter}){ext}"
        counter += 1
    return filepath

# Function to handle the download and trimming process
def process_video():
    # Get input from the GUI
    url = url_entry.get().strip()
    filename = filename_entry.get().strip()
    trim_choice = trim_var.get().lower()

    if not url or not filename:
        messagebox.showerror("Error", "Please provide both URL and filename.")
        return

    # Define output path
    output_dir = output_dir_entry.get()
    output_file = os.path.join(output_dir, f"{filename}.mp4")

    # Step 1: Rename the full video if it already exists
    output_file = get_unique_filename(output_file)

    # Step 2: Check if trimming is selected
    if trim_choice in ("yes", "y"):
        # Get start and end times from GUI
        start = start_time_entry.get().strip()
        end = end_time_entry.get().strip()

        # Ensure start and end times are provided
        if not start or not end:
            messagebox.showerror("Error", "Start and end times must be provided!")
            return

        # Step 2.1: Download only the selected section
        yt_dlp_command = [
            "yt-dlp", "-f", "bv*[height<=1080]+ba/b[height<=1080]", "--merge-output-format", "mp4",
            "--download-sections", f"*{start}-{end}",  # Download only the section from start to end
            "-o", output_file, url
        ]
        subprocess.run(yt_dlp_command, check=True)

        # Check if the video was downloaded
        if not os.path.exists(output_file):
            messagebox.showerror("Error", "Video download failed!")
            return

        messagebox.showinfo("Success", f"Trimmed video saved as {output_file}")

    else:
        # If no trim, download the full video
        yt_dlp_command = [
            "yt-dlp", "-f", "bv*[height<=1080]+ba/b[height<=1080]", "--merge-output-format", "mp4",
            "-o", output_file, url
        ]
        subprocess.run(yt_dlp_command, check=True)

        # Check if the video was downloaded
        if not os.path.exists(output_file):
            messagebox.showerror("Error", "Video download failed!")
            return

        messagebox.showinfo("Success", f"Full video saved as {output_file}")

# GUI setup
root = tk.Tk()
root.title("YouTube Video Downloader and Trimmer")

# URL entry
url_label = tk.Label(root, text="Paste YouTube URL:")
url_label.pack()
url_entry = tk.Entry(root, width=50)
url_entry.pack()

# Filename entry
filename_label = tk.Label(root, text="Enter a name for this video (without extension):")
filename_label.pack()
filename_entry = tk.Entry(root, width=50)
filename_entry.pack()

# Trim options
trim_var = tk.StringVar(value="no")
trim_label = tk.Label(root, text="Do you want to trim the video? (yes/y/no/n):")
trim_label.pack()
trim_yes_button = tk.Radiobutton(root, text="Yes", variable=trim_var, value="yes")
trim_yes_button.pack()
trim_no_button = tk.Radiobutton(root, text="No", variable=trim_var, value="no")
trim_no_button.pack()

# Start and end time for trimming
start_time_label = tk.Label(root, text="Enter start time (hh:mm:ss):")
start_time_label.pack()
start_time_entry = tk.Entry(root, width=50)
start_time_entry.pack()

end_time_label = tk.Label(root, text="Enter end time (hh:mm:ss):")
end_time_label.pack()
end_time_entry = tk.Entry(root, width=50)
end_time_entry.pack()

# Output directory selection
output_dir_label = tk.Label(root, text="Select Output Directory:")
output_dir_label.pack()
output_dir_button = tk.Button(root, text="Browse", command=lambda: output_dir_entry.insert(0, filedialog.askdirectory()))
output_dir_button.pack()

output_dir_entry = tk.Entry(root, width=50)
output_dir_entry.pack()

# Process Button
process_button = tk.Button(root, text="Download and Process", command=process_video)
process_button.pack()

# Run the GUI
root.mainloop()
