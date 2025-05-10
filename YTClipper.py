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
    yt_start_time_entry.config(state=state)
    yt_end_time_entry.config(state=state)

def validate_yt_output_dir():
    if not yt_output_dir_entry.get().strip():
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
    if not validate_yt_output_dir():
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
    if not validate_yt_output_dir():
        return

    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if not file_path:
        return

    output_dir = yt_output_dir_entry.get().strip()
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

def validate_ffmpeg_output_dir():
    if not ffmpeg_output_dir_entry.get().strip():
        messagebox.showerror("Error", "Please select an output directory for FFmpeg before proceeding.")
        return False
    return True

def cut_local_video():
    input_path = local_file_entry.get().strip()
    start_time = local_yt_start_time_entry.get().strip()
    end_time = local_yt_end_time_entry.get().strip()
    title = local_title_entry.get().strip()
    output_dir = ffmpeg_output_dir_entry.get().strip()

    if not input_path or not start_time or not end_time:
        messagebox.showerror("Error", "All fields except Title are required.")
        return

    base_name = title if title else os.path.splitext(os.path.basename(input_path))[0]
    output_filename = f"{base_name}.mp4" if title else f"{base_name}_{start_time.replace(':','-')}_to_{end_time.replace(':','-')}.mp4"
    output_path = os.path.join(output_dir, output_filename)
    output_path = get_unique_filename(output_path)

    if reencode_var.get():
        cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-ss", start_time, "-to", end_time,
            "-c:v", "libx264", "-c:a", "aac",
            output_path
        ]
    else:
        cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-ss", start_time, "-to", end_time,
            "-c", "copy",
            output_path
        ]

    try:
        subprocess.run(cmd, check=True)
        messagebox.showinfo("Success", f"Clip saved to:\n{output_path}")
    except subprocess.CalledProcessError:
        messagebox.showerror("Error", "Failed to cut video.")

# GUI setup
root = tk.Tk()
root.title("YouTube Downloader + FFmpeg Cutter")

notebook = ttk.Notebook(root)
notebook.pack(padx=10, pady=10, fill="both", expand=True)

# --- YouTube Downloader Tab ---
youtube_tab = tk.Frame(notebook)
notebook.add(youtube_tab, text="YouTube Downloader")

tk.Label(youtube_tab, text="Paste YouTube URL:").pack()
url_entry = tk.Entry(youtube_tab, width=40)
url_entry.pack()

tk.Label(youtube_tab, text="Filename (no extension):").pack()
filename_entry = tk.Entry(youtube_tab, width=40)
filename_entry.pack()

tk.Label(youtube_tab, text="Select Resolution:").pack()
resolution_var = tk.StringVar(value="1080")
ttk.Combobox(youtube_tab, textvariable=resolution_var,
             values=["720", "1080", "1440", "2160", "Best Available"],
             state="readonly", width=20).pack()

tk.Label(youtube_tab, text="Select Output Format:").pack()
output_format_var = tk.StringVar(value="mp4")
ttk.Combobox(youtube_tab, textvariable=output_format_var,
             values=["mp4", "mkv", "webm"],
             state="readonly", width=20).pack()

tk.Label(youtube_tab, text="Trim Video?").pack()
trim_var = tk.StringVar(value="yes")
tk.Radiobutton(youtube_tab, text="Yes", variable=trim_var, value="yes", command=toggle_time_entries).pack()
tk.Radiobutton(youtube_tab, text="No", variable=trim_var, value="no", command=toggle_time_entries).pack()

tk.Label(youtube_tab, text="Start Time (hh:mm:ss):").pack()
yt_start_time_entry = tk.Entry(youtube_tab, width=20)
yt_start_time_entry.pack()
yt_start_time_entry.bind("<KeyRelease>", lambda e: format_time_input(e, yt_start_time_entry))

tk.Label(youtube_tab, text="End Time (hh:mm:ss):").pack()
yt_end_time_entry = tk.Entry(youtube_tab, width=20)
yt_end_time_entry.pack()
yt_end_time_entry.bind("<KeyRelease>", lambda e: format_time_input(e, yt_end_time_entry))

tk.Label(youtube_tab, text="Select Output Directory:").pack()
output_dir_button = tk.Button(youtube_tab, text="Browse",
                              command=lambda: yt_output_dir_entry.insert(0, filedialog.askdirectory()))
output_dir_button.pack()
yt_output_dir_entry = tk.Entry(youtube_tab, width=40)
yt_output_dir_entry.pack()

progress_bar = ttk.Progressbar(youtube_tab, orient="horizontal", length=300, mode="determinate")
progress_bar.pack(pady=10)

tk.Button(youtube_tab, text="Download and Process",
          command=lambda: process_video(url_entry.get().strip(),
                                        filename_entry.get().strip(),
                                        yt_start_time_entry.get().strip(),
                                        yt_end_time_entry.get().strip(),
                                        resolution_var.get(),
                                        yt_output_dir_entry.get().strip(),
                                        output_format_var.get())).pack()

tk.Button(youtube_tab, text="Batch Process from CSV", command=process_bulk).pack(pady=5)

# --- FFmpeg Cutter Tab ---
ffmpeg_tab = tk.Frame(notebook)
notebook.add(ffmpeg_tab, text="FFmpeg Cutter")

tk.Label(ffmpeg_tab, text="Select Local Video File:").pack()
local_file_entry = tk.Entry(ffmpeg_tab, width=40)
local_file_entry.pack()
tk.Button(ffmpeg_tab, text="Browse", command=lambda: local_file_entry.insert(0, filedialog.askopenfilename())).pack()

tk.Label(ffmpeg_tab, text="Start Time (hh:mm:ss):").pack()
local_yt_start_time_entry = tk.Entry(ffmpeg_tab, width=20)
local_yt_start_time_entry.pack()
local_yt_start_time_entry.bind("<KeyRelease>", lambda e: format_time_input(e, local_yt_start_time_entry))

tk.Label(ffmpeg_tab, text="End Time (hh:mm:ss):").pack()
local_yt_end_time_entry = tk.Entry(ffmpeg_tab, width=20)
local_yt_end_time_entry.pack()
local_yt_end_time_entry.bind("<KeyRelease>", lambda e: format_time_input(e, local_yt_end_time_entry))

tk.Label(ffmpeg_tab, text="Optional Title (leave blank to auto-name):").pack()
local_title_entry = tk.Entry(ffmpeg_tab, width=40)
local_title_entry.pack()

tk.Label(ffmpeg_tab, text="Select Output Directory:").pack()
ffmpeg_output_dir_button = tk.Button(ffmpeg_tab, text="Browse",
                                     command=lambda: ffmpeg_output_dir_entry.insert(0, filedialog.askdirectory()))
ffmpeg_output_dir_button.pack()
ffmpeg_output_dir_entry = tk.Entry(ffmpeg_tab, width=40)
ffmpeg_output_dir_entry.pack()


reencode_var = tk.BooleanVar(value=False)
tk.Checkbutton(ffmpeg_tab, text="Force Re-encode (libx264 + AAC)", variable=reencode_var).pack()


tk.Button(ffmpeg_tab, text="Cut Video", command=cut_local_video).pack(pady=10)

root.mainloop()