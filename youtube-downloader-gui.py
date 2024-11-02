import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import yt_dlp
import os
import re
import threading
from datetime import timedelta

class YouTubeDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Video Downloader")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        
        # Quality presets
        self.QUALITY_PRESETS = {
            '4320p': {'resolution': '7680x4320', 'height': 4320, 'label': '8K', 'description': 'Ultra HD 8K'},
            '2160p': {'resolution': '3840x2160', 'height': 2160, 'label': '4K', 'description': 'Ultra HD 4K'},
            '1440p': {'resolution': '2560x1440', 'height': 1440, 'label': '2K', 'description': 'Quad HD'},
            '1080p': {'resolution': '1920x1080', 'height': 1080, 'label': 'HD', 'description': 'Full HD'},
            '720p':  {'resolution': '1280x720',  'height': 720,  'label': 'HD', 'description': 'HD Ready'},
            '480p':  {'resolution': '854x480',   'height': 480,  'label': 'SD', 'description': 'Standard Definition'},
            '360p':  {'resolution': '640x360',   'height': 360,  'label': 'SD', 'description': 'Low Definition'},
            '240p':  {'resolution': '426x240',   'height': 240,  'label': 'SD', 'description': 'Very Low Definition'}
        }
        
        self.setup_gui()
        self.video_info = None
        self.download_thread = None
        
    def setup_gui(self):
        """Set up the GUI elements"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # URL Frame
        url_frame = ttk.LabelFrame(main_frame, text="Video URL", padding="5")
        url_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        url_frame.columnconfigure(0, weight=1)
        
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(url_frame, textvariable=self.url_var)
        self.url_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5)
        
        self.fetch_btn = ttk.Button(url_frame, text="Fetch Video Info", command=self.fetch_video_info)
        self.fetch_btn.grid(row=0, column=1, padx=5)
        
        # Video Info Frame
        info_frame = ttk.LabelFrame(main_frame, text="Video Information", padding="5")
        info_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        info_frame.columnconfigure(1, weight=1)
        
        ttk.Label(info_frame, text="Title:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.title_label = ttk.Label(info_frame, text="")
        self.title_label.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        
        ttk.Label(info_frame, text="Duration:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.duration_label = ttk.Label(info_frame, text="")
        self.duration_label.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5)
        
        ttk.Label(info_frame, text="Channel:").grid(row=2, column=0, sticky=tk.W, padx=5)
        self.channel_label = ttk.Label(info_frame, text="")
        self.channel_label.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5)
        
        # Download Options Frame
        options_frame = ttk.LabelFrame(main_frame, text="Download Options", padding="5")
        options_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        options_frame.columnconfigure(1, weight=1)
        
        ttk.Label(options_frame, text="Quality:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.quality_combo = ttk.Combobox(options_frame, state="readonly")
        self.quality_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        
        ttk.Label(options_frame, text="Save to:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.path_var = tk.StringVar(value=os.path.join(os.getcwd(), "downloads"))
        path_entry = ttk.Entry(options_frame, textvariable=self.path_var)
        path_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5)
        
        browse_btn = ttk.Button(options_frame, text="Browse", command=self.browse_directory)
        browse_btn.grid(row=1, column=2, padx=5)
        
        # Download Button and Progress Frame
        download_frame = ttk.Frame(main_frame)
        download_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        download_frame.columnconfigure(0, weight=1)
        
        self.download_btn = ttk.Button(download_frame, text="Download Video", command=self.start_download)
        self.download_btn.grid(row=0, column=0, pady=5)
        self.download_btn["state"] = "disabled"
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(download_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.status_label = ttk.Label(download_frame, text="")
        self.status_label.grid(row=2, column=0, pady=5)
        
    def is_valid_youtube_url(self, url):
        """Validate YouTube URL"""
        youtube_regex = (
            r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
            '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
        )
        return bool(re.match(youtube_regex, url))
    
    def browse_directory(self):
        """Open directory browser dialog"""
        directory = filedialog.askdirectory(initialdir=self.path_var.get())
        if directory:
            self.path_var.set(directory)
    
    def fetch_video_info(self):
        """Fetch video information from YouTube"""
        url = self.url_var.get().strip()
        if not self.is_valid_youtube_url(url):
            messagebox.showerror("Error", "Invalid YouTube URL")
            return
        
        self.fetch_btn["state"] = "disabled"
        self.fetch_btn["text"] = "Fetching..."
        self.status_label["text"] = "Fetching video information..."
        
        def fetch():
            try:
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    self.video_info = ydl.extract_info(url, download=False)
                    
                    # Update GUI in main thread
                    self.root.after(0, self.update_video_info)
                    
            except Exception as e:
                self.root.after(0, lambda: self.show_error(f"Error fetching video info: {str(e)}"))
            finally:
                self.root.after(0, self.reset_fetch_button)
        
        # Start fetching in a separate thread
        threading.Thread(target=fetch, daemon=True).start()
    
    def update_video_info(self):
        """Update GUI with fetched video information"""
        if self.video_info:
            self.title_label["text"] = self.video_info.get('title', 'Unknown')
            duration = str(timedelta(seconds=self.video_info.get('duration', 0)))
            self.duration_label["text"] = duration
            self.channel_label["text"] = self.video_info.get('channel', 'Unknown')
            
            # Update quality options
            formats = self.video_info.get('formats', [])
            available_heights = set()
            for f in formats:
                if f.get('vcodec') != 'none' and f.get('height'):
                    available_heights.add(f.get('height'))
            
            # Filter and sort quality options
            quality_options = []
            for quality, specs in self.QUALITY_PRESETS.items():
                if specs['height'] <= max(available_heights, default=0):
                    quality_options.append(f"{quality} - {specs['description']}")
            
            self.quality_combo["values"] = quality_options
            if quality_options:
                self.quality_combo.set(quality_options[0])
                self.download_btn["state"] = "normal"
    
    def reset_fetch_button(self):
        """Reset fetch button state"""
        self.fetch_btn["state"] = "normal"
        self.fetch_btn["text"] = "Fetch Video Info"
        self.status_label["text"] = ""
    
    def show_error(self, message):
        """Show error message"""
        messagebox.showerror("Error", message)
        self.status_label["text"] = "Error occurred"
    
    def start_download(self):
        """Start video download process"""
        if not self.video_info:
            return
        
        quality = self.quality_combo.get().split(' - ')[0]
        output_path = self.path_var.get()
        
        if not os.path.exists(output_path):
            try:
                os.makedirs(output_path)
            except Exception as e:
                self.show_error(f"Error creating directory: {str(e)}")
                return
        
        self.download_btn["state"] = "disabled"
        self.fetch_btn["state"] = "disabled"
        self.progress_var.set(0)
        
        def download_progress_hook(d):
            if d['status'] == 'downloading':
                try:
                    percent = float(d['_percent_str'].replace('%', ''))
                    self.progress_var.set(percent)
                    self.status_label["text"] = f"Downloading: {d['_percent_str']} of {d.get('_total_bytes_str', 'Unknown size')}"
                except:
                    pass
            elif d['status'] == 'finished':
                self.status_label["text"] = "Download completed! Processing video..."
        
        def download():
            try:
                target_height = self.QUALITY_PRESETS[quality]['height']
                ydl_opts = {
                    'format': f'bestvideo[height<={target_height}]+bestaudio/best[height<={target_height}]',
                    'outtmpl': os.path.join(output_path, '%(title)s [%(resolution)s].%(ext)s'),
                    'restrictfilenames': True,
                    'noplaylist': True,
                    'quiet': False,
                    'merge_output_format': 'mp4',
                    'progress_hooks': [download_progress_hook],
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([self.url_var.get()])
                
                self.root.after(0, self.download_complete)
                
            except Exception as e:
                self.root.after(0, lambda: self.show_error(f"Download error: {str(e)}"))
                self.root.after(0, self.reset_download_button)
        
        # Start download in a separate thread
        self.download_thread = threading.Thread(target=download, daemon=True)
        self.download_thread.start()
    
    def download_complete(self):
        """Handle download completion"""
        self.status_label["text"] = "Download completed successfully!"
        self.reset_download_button()
        messagebox.showinfo("Success", "Video downloaded successfully!")
    
    def reset_download_button(self):
        """Reset download button state"""
        self.download_btn["state"] = "normal"
        self.fetch_btn["state"] = "normal"

def main():
    root = tk.Tk()
    app = YouTubeDownloaderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
