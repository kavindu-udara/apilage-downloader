import customtkinter
from tkinter import filedialog, messagebox
import YouTubeController
from YouTubeController import YouTubeController
import os
import threading
import re

class YouTubeFrame(customtkinter.CTkFrame):
    def __init__(self, master, title):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)

        self.title = customtkinter.CTkLabel(self, text=title, fg_color="gray30", corner_radius=6)
        self.title.grid(row=0, column=0, sticky="ew")

class URLFrame(customtkinter.CTkFrame):
    def __init__(self, master, title, fetch_video_info):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)

        self.title = customtkinter.CTkLabel(self, text=title, corner_radius=6)
        self.title.grid(row=0, column=0, padx=5, pady=(0, 5), sticky="ew")

        self.url_var = customtkinter.StringVar()
        self.url_entry = customtkinter.CTkEntry(self, textvariable=self.url_var)
        self.url_entry.grid(row=1, column=0, padx=5, sticky="ew")

        self.fetch_btn = customtkinter.CTkButton(self, text="Fetch Video Info", command=fetch_video_info)
        self.fetch_btn.grid(row=1, column=2, padx=5, sticky="ew")

    video_info = None

    def reset_fetch_button(self):
        self.fetch_btn.configure(state="normal")

    def fetch(self):
        url = self.url_entry.get()
        print(url)
        if url :
            if YouTubeController.isValidUrl(url=url):
                try:
                    video_info = YouTubeController.getVideoInfo(url=url)
                    self.update_video_info(video_info)
                except Exception as e:
                    messagebox.showerror("Error", f"Error fetching video info: {str(e)}")
            else:
                messagebox.showerror("Error", "Invalid YouTube URL")
    
    def getUrl(self):
        return self.url_entry.get()

class VideoInfoFrame(customtkinter.CTkFrame):
    def __init__(self, master, info_values):
        super().__init__(master)
        self.grid_columnconfigure((0, 1), weight=1)

        self.title = customtkinter.CTkLabel(self, text="Video Information")
        self.title.grid(row=0, column=0, padx=5, pady=(0, 5), sticky="ew")

        self.video_title = customtkinter.CTkLabel(self, text="Title")
        self.video_title.grid(row=1, column=0, padx=5, pady=(0, 5), sticky="ew")

        self.duration = customtkinter.CTkLabel(self, text="Duration")
        self.duration.grid(row=2, column=0, padx=5, pady=(0, 5), sticky="ew" )

        self.channel = customtkinter.CTkLabel(self, text="Channel")
        self.channel.grid(row=3, column=0, padx=5, pady=(0, 5), sticky="ew" )

        #  Value lables
        self.video_title_value = customtkinter.CTkLabel(self, text=info_values['title'])
        self.video_title_value.grid(row=1, column=1, padx=5, pady=(0, 5), sticky="ew")
        
        self.duration_value = customtkinter.CTkLabel(self, text=info_values['duration'])
        self.duration_value.grid(row=2, column=1, padx=5, pady=(0, 5), sticky="ew" )
        
        self.channel_value = customtkinter.CTkLabel(self, text=info_values['channel'])
        self.channel_value.grid(row=3, column=1, padx=5, pady=(0, 5), sticky="ew" )

    def update_info(self, info):
        self.video_title_value.configure(text=info['title'])
        self.duration_value.configure(text=info['duration'])
        self.channel_value.configure(text=info['channel'])

class DownloadOptionsFrame(customtkinter.CTkFrame):
    def __init__(self, master, download_callback):
        super().__init__(master)
        #  add top border to frame
        self.grid_rowconfigure(0, weight=1, minsize=2)
        self.grid_columnconfigure((0, 1), weight=1)

        self.title = customtkinter.CTkLabel(self, text="Download Options")
        self.title.grid(row=0, column=0, padx=5, pady=(0, 5), sticky="ew")

        self.quality_label = customtkinter.CTkLabel(self, text="Quality")
        self.quality_label.grid(row=1, column=0, padx=5, pady=(0, 5), sticky="ew")

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
        self.video_information = None
        self.output_path = None

        self.quality_combo = customtkinter.CTkComboBox(self, state="readonly")
        self.quality_combo.grid(row=1, column=1, padx=5, pady=(0, 5), sticky="ew")

        self.path_label = customtkinter.CTkLabel(self, text="Output Path")
        self.path_label.grid(row=2, column=0, padx=5, pady=(0, 5), sticky="ew")

        self.path_var = customtkinter.StringVar()
        self.path_entry = customtkinter.CTkEntry(self, textvariable=self.path_var)
        self.path_entry.grid(row=2, column=1, padx=5, pady=(0, 5), sticky="ew")

        self.browse_btn = customtkinter.CTkButton(self, text="Browse", command=self.browse)
        self.browse_btn.grid(row=3, column=1, padx=5, pady=(0, 5), sticky="ew")

        self.progress_var = customtkinter.DoubleVar()
        self.progress_bar = customtkinter.CTkProgressBar(self, variable=self.progress_var)
        self.progress_bar.grid(row=4, column=0, padx=5, pady=(0, 5), sticky="ew", columnspan=3)

        self.status_label = customtkinter.CTkLabel(self, text="Status")
        self.status_label.grid(row=5, column=0, padx=5, pady=(0, 5), sticky="ew")

        self.download_btn = customtkinter.CTkButton(self, text="Download", command=download_callback)
        self.download_btn.grid(row=6, column=0, padx=5, pady=(0, 5), columnspan=3, sticky="ew")

    def browse(self):
        path = filedialog.askdirectory()
        self.output_path = path
        self.path_var.set(path)

    def filter_and_sort_quality_options(self, video_info):
        self.video_information = video_info
        # Update quality options
        formats = video_info.get('formats', [])
        available_heights = set()
        for f in formats:
            if f.get('vcodec') != 'none' and f.get('height'):
                available_heights.add(f.get('height'))

        quality_options = []
        for quality, specs in self.QUALITY_PRESETS.items():
            if specs['height'] <= max(available_heights, default=0):
                    quality_options.append(f"{quality} - {specs['description']}")
        
        self.quality_combo.configure(values=quality_options)
        if quality_options:
            self.quality_combo.set(quality_options[0])
            self.download_btn["state"] = "normal"
        
    def start_download(self, url):
        if not self.video_information:
            return
        
        self.quality = self.quality_combo.get().split('-')[0].strip()
        
        if not os.path.exists(self.output_path):
            try:
                os.mkdir(self.output_path)
            except Exception as e:
                print(e)
                return
        
        self.download_btn["state"] = "disabled"
        self.browse_btn["state"] = "disabled"

        def download_progress_hook(d):
            if d['status'] == 'downloading':
                try:
                    # Remove escape sequences from the percentage string
                    percent = float(d['_percent_str'].replace('%', ''))
                    self.progress_var.set(percent)
                    self.status_label.configure(
                    text=f"Downloading: {d['_percent_str']} of {d.get('_total_bytes_str', 'Unknown size')}"
                    )
                except:
                    pass
            elif d['status'] == 'finished':
                self.status_label.configure(text="Download completed! Processing video...")

        self.download_thread = threading.Thread(target=YouTubeController.downloadVideo(self, url=url, download_progress_hook=download_progress_hook, output_path=self.output_path, target_height=self.QUALITY_PRESETS[self.quality]['height']), daemon=True)
        self.download_thread.start()