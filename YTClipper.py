import subprocess
import os
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import csv


# Function to get a unique filename
def get_unique_filename(filepath):
    base, ext = os.path.splitext(filepath)
    counter = 1
    while os.path.exists(filepath):
        filepath = f"{base} ({counter}){ext}"
        counter += 1
    return filepath


# Function to enable/disable time entry fields
def toggle_time_entries():
    if trim_var.get() == "yes":
        start_time_entry.config(state="normal")
        end_time_entry.config(state="normal")
    else:
        start_time_entry.config(state="disabled")
        end_time_entry.config(state="disabled")


# Function to validate output directory selection
def validate_output_dir():
    if not output_dir_entry.get().strip():
        messagebox.showerror("Error", "Please select an output directory before proceeding.")
        return False
    return True


# Function to format time input
def format_time_input(event, entry):
    text = entry.get().replace(":", "")[:6]  # Remove colons and limit to 6 digits
    formatted = "".join([text[i:i + 2] + ":" if i < 4 else text[i:i + 2] for i in range(0, len(text), 2)]).rstrip(":")
    entry.delete(0, tk.END)
    entry.insert(0, formatted)


# Function to update progress bar
def update_progress(progress):
    progress_bar["value"] = progress
    root.update_idletasks()


# Function to process a single video
def process_video(url, filename, start, end, resolution, output_dir):
    if not validate_output_dir():
        return "Error: Output directory not selected."
    if not url or not filename:
        return "Error: Missing URL or filename."

    output_file = os.path.join(output_dir, f"{filename}.mp4")
    output_file = get_unique_filename(output_file)

    resolution_option = f"bv*[height<={resolution}]+ba/b[height<={resolution}]" if resolution != "Best Available" else "bv+ba/b"

    yt_dlp_command = [
        "yt-dlp", "-f", resolution_option, "--merge-output-format", "mp4", "-o", output_file, url
    ]

    if trim_var.get() == "yes" and start and end:
        yt_dlp_command.extend(["--download-sections", f"*{start}-{end}"])

    try:
        update_progress(25)
        subprocess.run(yt_dlp_command, check=True)
        update_progress(100)
        return f"Success: Video saved as {output_file}"
    except subprocess.CalledProcessError:
        return "Error: Video download failed!"


# Function to process batch CSV file
def process_bulk():
    if not validate_output_dir():
        return

    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if not file_path:
        return

    output_dir = output_dir_entry.get().strip()
    resolution = resolution_var.get()

    with open(file_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) >= 2:
                url = row[0].strip()
                filename = row[1].strip()
                start = row[2].strip() if len(row) > 2 else ""
                end = row[3].strip() if len(row) > 3 else ""
                process_video(url, filename, start, end, resolution, output_dir)

    messagebox.showinfo("Batch Processing", "Batch processing completed.")


# GUI setup
root = tk.Tk()
root.title("YouTube Video Downloader and Trimmer")

# URL entry
url_label = tk.Label(root, text="Paste YouTube URL:")
url_label.pack()
url_entry = tk.Entry(root, width=30)
url_entry.pack()

# Filename entry
filename_label = tk.Label(root, text="Enter a name for this video (without extension):")
filename_label.pack()
filename_entry = tk.Entry(root, width=30)
filename_entry.pack()

# Resolution selection
tk.Label(root, text="Select Resolution:").pack()
resolution_var = tk.StringVar(value="1080")
resolution_dropdown = ttk.Combobox(root, textvariable=resolution_var,
                                   values=["720", "1080", "1440", "2160", "Best Available"], state="readonly", width=15)
resolution_dropdown.pack()

# Trim option
tk.Label(root, text="Trim Video?").pack()
trim_var = tk.StringVar(value="yes")
trim_yes_button = tk.Radiobutton(root, text="Yes", variable=trim_var, value="yes", command=toggle_time_entries)
trim_yes_button.pack()
trim_no_button = tk.Radiobutton(root, text="No", variable=trim_var, value="no", command=toggle_time_entries)
trim_no_button.pack()

# Start and end time for trimming
start_time_label = tk.Label(root, text="Enter start time:")
start_time_label.pack()
start_time_entry = tk.Entry(root, width=15, state="normal")

start_time_entry.pack()
start_time_entry.bind("<KeyRelease>", lambda event: format_time_input(event, start_time_entry))

end_time_label = tk.Label(root, text="Enter end time:")
end_time_label.pack()
end_time_entry = tk.Entry(root, width=15, state="normal")

end_time_entry.pack()
end_time_entry.bind("<KeyRelease>", lambda event: format_time_input(event, end_time_entry))

# Output directory selection
output_dir_label = tk.Label(root, text="Select Output Directory:")
output_dir_label.pack()
output_dir_button = tk.Button(root, text="Browse",
                              command=lambda: output_dir_entry.insert(0, filedialog.askdirectory()))
output_dir_button.pack()
output_dir_entry = tk.Entry(root, width=30)
output_dir_entry.pack()

# Progress Bar
progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
progress_bar.pack()

# Process Buttons
process_button = tk.Button(root, text="Download and Process",
                           command=lambda: process_video(url_entry.get().strip(), filename_entry.get().strip(),
                                                         start_time_entry.get().strip(), end_time_entry.get().strip(),
                                                         resolution_var.get(), output_dir_entry.get().strip()))
process_button.pack()

bulk_process_button = tk.Button(root, text="Batch Process from CSV", command=process_bulk)
bulk_process_button.pack()

# Run the GUI
root.mainloop()
