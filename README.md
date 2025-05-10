
# YTClipper GUI – YouTube Video Downloader & Trimmer

A lightweight Python tool with GUI for downloading YouTube videos, trimming by timestamp, and exporting in `.mp4`, `.mkv`, or `.webm`.

## 🛠 Requirements
- Python 3.8+
- [`yt-dlp`](https://github.com/yt-dlp/yt-dlp): `pip install -U yt-dlp`
- [`ffmpeg`](https://ffmpeg.org/download.html) (must be in PATH)

## 🚀 Features
- Trim by start/end timestamp (optional)
- Choose output resolution (720p–4K)
- Select output format: mp4, mkv, or webm
- Batch processing via CSV
- GUI built with `tkinter`

## 📦 Usage
1. Run the script:
   ```bash
   python ytclipper_gui_updated.py
   ```
2. Paste a YouTube URL
3. Choose filename, resolution, and format
4. Optionally trim
5. Click **Download and Process** or use **Batch Process from CSV**

## 📁 CSV Format (for batch)
```
url,filename,start_time,end_time
https://youtube.com/... , myclip , 00:01:00 , 00:01:30
```

## 💬 License
MIT – Free to use, tweak, and share!### 🔵 FFmpeg Cutter Tab
- Trim **local video files** using FFmpeg
- Choose start and end times
- Optional custom title (skips timestamp auto-naming if set)
- Separate output directory
- ✅ New: **Force Re-encode** option for guaranteed compatibility
  - When unchecked: fast, stream copy (`-c copy`)
  - When checked: re-encodes using `libx264` + `aac` for full reliability


