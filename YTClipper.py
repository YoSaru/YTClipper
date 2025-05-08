
import subprocess
import os
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import csv

def get_unique_filename(filepath):
    base, ext = os.path.splitext(filepath)
    counter = 1
    while os.path.exists(filepath):
        filepath = f"{base} ({counter}){ext}"
        counter += 1
    return filepath

def toggle_time_entries():
    state = "normal" if trim_var.get() == "yes" else "disabled"
    start_time_entry.config(state=state)
    end_time_entry.config(state=state)

def validate_output_dir():
    if not output_dir_entry.get().strip():
        messagebox.showerror("Error", "Please select an output directory before proceeding.")
        return False
    return True

def format_time_input(event, entry):
    text = entry.get().replace(":", "")[:6]
    formatted = "".join([text[i:i + 2] + ":" if i < 4 else text[i:i + 2] for i in range(0, len(text), 2)]).rstrip(":")
    entry.delete(0, tk.END)
    entry.insert(0, formatted)

def update_progress(progress):
    progress_bar["value"] = progress
    root.update_idletasks()

def process_video(url, filename, start, end, resolution, output_dir, output_format):
    if not validate_output_dir():
        return "Error: Output directory not selected."
    if not url or not filename:
        return "Error: Missing URL or filename."

    output_file = os.path.join(output_dir, f"{filename}.{output_format}")
    output_file = get_unique_filename(output_file)

    if resolution != "Best Available":
        resolution_option = f"bv*[height<={resolution}]+ba/b[height<={resolution}]"
    else:
        resolution_option = "bv+ba/b"

    yt_dlp_command = [
        "yt-dlp", "-f", resolution_option, "--merge-output-format", output_format, "-o", output_file, url
    ]

    if trim_var.get() == "yes" and start:
        if not end:
            end = "99:59:59"
        yt_dlp_command.extend(["--download-sections", f"*{start}-{end}"])

    try:
        update_progress(25)
        subprocess.run(yt_dlp_command, check=True)
        update_progress(100)
        return f"Success: Video saved as {output_file}"
    except subprocess.CalledProcessError:
        return "Error: Video download failed!"

def process_bulk():
    if not validate_output_dir():
        return

    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if not file_path:
        return

    output_dir = output_dir_entry.get().strip()
    resolution = resolution_var.get()
    output_format = output_format_var.get()

    with open(file_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) >= 2:
                url = row[0].strip()
                filename = row[1].strip()
                start = row[2].strip() if len(row) > 2 else ""
                end = row[3].strip() if len(row) > 3 else ""
                process_video(url, filename, start, end, resolution, output_dir, output_format)

    messagebox.showinfo("Batch Processing", "Batch processing completed.")

# GUI setup
root = tk.Tk()
root.title("YouTube Downloader + Trimmer")

tk.Label(root, text="Paste YouTube URL:").pack()
url_entry = tk.Entry(root, width=40)
url_entry.pack()

tk.Label(root, text="Filename (no extension):").pack()
filename_entry = tk.Entry(root, width=40)
filename_entry.pack()

tk.Label(root, text="Select Resolution:").pack()
resolution_var = tk.StringVar(value="1080")
ttk.Combobox(root, textvariable=resolution_var,
             values=["720", "1080", "1440", "2160", "Best Available"],
             state="readonly", width=20).pack()

tk.Label(root, text="Select Output Format:").pack()
output_format_var = tk.StringVar(value="mp4")
ttk.Combobox(root, textvariable=output_format_var,
             values=["mp4", "mkv", "webm"],
             state="readonly", width=20).pack()

tk.Label(root, text="Trim Video?").pack()
trim_var = tk.StringVar(value="yes")
tk.Radiobutton(root, text="Yes", variable=trim_var, value="yes", command=toggle_time_entries).pack()
tk.Radiobutton(root, text="No", variable=trim_var, value="no", command=toggle_time_entries).pack()

tk.Label(root, text="Start Time (hh:mm:ss):").pack()
start_time_entry = tk.Entry(root, width=20)
start_time_entry.pack()
start_time_entry.bind("<KeyRelease>", lambda e: format_time_input(e, start_time_entry))

tk.Label(root, text="End Time (hh:mm:ss):").pack()
end_time_entry = tk.Entry(root, width=20)
end_time_entry.pack()
end_time_entry.bind("<KeyRelease>", lambda e: format_time_input(e, end_time_entry))

tk.Label(root, text="Select Output Directory:").pack()
output_dir_button = tk.Button(root, text="Browse",
                              command=lambda: output_dir_entry.insert(0, filedialog.askdirectory()))
output_dir_button.pack()
output_dir_entry = tk.Entry(root, width=40)
output_dir_entry.pack()

progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
progress_bar.pack(pady=10)

tk.Button(root, text="Download and Process",
          command=lambda: process_video(url_entry.get().strip(),
                                        filename_entry.get().strip(),
                                        start_time_entry.get().strip(),
                                        end_time_entry.get().strip(),
                                        resolution_var.get(),
                                        output_dir_entry.get().strip(),
                                        output_format_var.get())).pack()

tk.Button(root, text="Batch Process from CSV", command=process_bulk).pack(pady=5)

root.mainloop()
