import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from models.video_info import VideoInfo
from models.state import State
from controllers.video_controller import VideoController
import os

class GUI:

    TITLE = "Apilage Downloader"
    QUALITY_PRESETS = {
            '4320p': {'resolution': '7680x4320', 'height': 4320, 'label': '8K', 'description': 'Ultra HD 8K'},
            '2160p': {'resolution': '3840x2160', 'height': 2160, 'label': '4K', 'description': 'Ultra HD 4K'},
            '1440p': {'resolution': '2560x1440', 'height': 1440, 'label': '2K', 'description': 'Quad HD'},
            '1080p': {'resolution': '1920x1080', 'height': 1080, 'label': 'HD', 'description': 'Full HD'},
            '720p':  {'resolution': '1280x720',  'height': 720,  'label': 'HD', 'description': 'HD Ready'},
            '480p':  {'resolution': '854x480',   'height': 480,  'label': 'SD', 'description': 'Standard Definition'},
            '360p':  {'resolution': '640x360',   'height': 360,  'label': 'SD', 'description': 'Low Definition'},
            '240p':  {'resolution': '426x240',   'height': 240,  'label': 'SD', 'description': 'Very Low Definition'}
        }

    def __init__(self):
        self.state = State()        
        self.video_info = VideoInfo()
        self.video_controller = VideoController(self.state, self.video_info, self)

        self.root = tk.Tk()
        self.setup()
        self.root.mainloop()

    def setup(self):
        """Setup GUI Elements"""
 
        #Title
        self.root.title(self.TITLE)

        # Icon
        icon = tk.PhotoImage(file="icon.png")
        self.root.iconphoto(True, icon)

        #Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        #URL Frame
        self.url_frame = ttk.LabelFrame(main_frame, text="Video URL", padding="5")
        self.url_frame.pack(fill=tk.X, pady=5)

        # URL Label
        ttk.Label(self.url_frame, text="Paste URL Here : ").pack(side=tk.LEFT)

        # URL Entry Block
        self.url_var = tk.StringVar()
        url_entry = ttk.Entry(self.url_frame, textvariable=self.url_var)
        url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # URL fetch button
        self.setup_submit_button(self.url_frame)

        # Video Infro Frame
        self.video_info_frame = ttk.LabelFrame(main_frame, text="Video Info", padding=5)
        self.video_info_frame.pack(fill=tk.X, pady=5)
        # Call the video info frame func
        self.setup_video_info_frame(self.video_info_frame)

        # Download opitons frame
        self.download_options_frame = ttk.LabelFrame(main_frame, text="Download Options", padding=5)
        self.download_options_frame.pack(fill=tk.X, expand=True)
        # Quality 
        self.setup_quality_options(self.download_options_frame)

        # Log frame
        self.log_frame = ttk.LabelFrame(main_frame, text="Logs", padding=5)
        self.log_frame.pack(fill=tk.X,  expand=True)

        # Log text widget
        self.log_text = tk.Text(self.log_frame, state=tk.DISABLED, height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Set min size
        self.root.minsize(400, 200)

    def setup_submit_button(self, parent_frame : ttk.LabelFrame):
        # Remove any existing buttons
        for child in parent_frame.winfo_children():
            if isinstance(child, ttk.Button):
                child.destroy()

        if self.state.state == "fetched":
            submit_button = ttk.Button(parent_frame, text="Download", command=self.download_video)
            submit_button.pack(side=tk.RIGHT, padx=5, pady=5)

            reset_button = ttk.Button(parent_frame, text="Reset", command=self.reset)
            reset_button.pack(side=tk.RIGHT, padx=5, pady=5)
        else:
           url_fetch_button = ttk.Button(parent_frame, text="Fetch video", command=self.fetch_video_info)
           url_fetch_button.pack(side=tk.RIGHT, padx=4)  

    def setup_quality_options(self, parent_frame : ttk.LabelFrame) : 
        self.destroy_children(parent_frame)
        if self.state.state == "fetched":

            # Quality frame row
            quality_frame_row = ttk.Frame(parent_frame)
            quality_frame_row.pack(fill=tk.X, pady=5)

            quality_label = ttk.Label(quality_frame_row, text="Select Quality : ")
            quality_label.pack(side=tk.LEFT, padx=5)
            self.quality_combo = ttk.Combobox(quality_frame_row, state="readonly")
            self.quality_combo.pack(side=tk.TOP, fill=tk.X, expand=True, padx=5, pady=5)

            # Update quality options based on available formats
            formats = self.video_info.fetched_info.get("formats", [])
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

            # Save to path frane row
            save_to_frame_row = ttk.Frame(parent_frame)
            save_to_frame_row.pack(fill=tk.X, pady=5)

            save_to_label = ttk.Label(save_to_frame_row, text="Save To : ")
            save_to_label.pack(side=tk.LEFT, padx=5)

            self.path_entry_var = tk.StringVar(value=os.path.expanduser("~/Downloads"))
            path_entry = ttk.Entry(save_to_frame_row, textvariable=self.path_entry_var)
            path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

            path_browse_button = ttk.Button(save_to_frame_row, text="Browse", command=self.browse_directory)
            path_browse_button.pack(side=tk.RIGHT, padx=5)


        elif self.state.state == "fetching":
            loading_label = ttk.Label(parent_frame, text="Loading...")
            loading_label.pack(side=tk.TOP, fill=tk.X, expand=True, padx=5)
        elif self.state.state == "error":
            error_label = ttk.Label(parent_frame, text="Fetch Failed")
            error_label.pack(side=tk.TOP, fill=tk.X, expand=True, padx=5)
        else :
            info_label = ttk.Label(parent_frame, text="Enter a valid URL and fetch video info to see quality options.")
            info_label.pack(side=tk.TOP, fill=tk.X, expand=True, padx=5)
            
    def setup_video_info_frame(self, parent_frame : ttk.LabelFrame):
        self.destroy_children(parent_frame)
        if self.state.state == "fetching" :
            loading_label = ttk.Label(parent_frame, text="Loading...")
            loading_label.pack(side=tk.TOP, fill=tk.X, expand=True, padx=5)
        elif self.state.state == "fetched":
            title_label = ttk.Label(parent_frame, text=f"Title : {self.video_info.fetched_info.get('title', 'N/A')}")
            title_label.pack(side=tk.TOP, fill=tk.X, expand=True, padx=5)

            uploader_label = ttk.Label(parent_frame, text=f"Uploader : {self.video_info.fetched_info.get('uploader', 'N/A')}")
            uploader_label.pack(side=tk.TOP, fill=tk.X, expand=True, padx=5)

            duration_label = ttk.Label(parent_frame, text=f"Duration : {self.video_info.fetched_info.get('duration', 'N/A')} seconds")
            duration_label.pack(side=tk.TOP, fill=tk.X, expand=True, padx=5)
        elif self.state.state == "error":
            error_label = ttk.Label(parent_frame, text="Fetch Failed")
            error_label.pack(side=tk.TOP, fill=tk.X, expand=True, padx=5)
        else:
            info_label = ttk.Label(parent_frame, text="Enter a valid URL and fetch video info to see details.")
            info_label.pack(side=tk.TOP, fill=tk.X, expand=True, padx=5)

    def destroy_children(self, parent : ttk.LabelFrame):
        for child in parent.winfo_children():
            if child.winfo_children():
                self.destroy_children(child)
            child.destroy()   

    def fetch_video_info(self):
        print("url found",  self.url_var.get())
        self.video_info.url = self.url_var.get()
        self.video_controller.fetch_video_info()

    def revalitade_ui(self):
        self.setup_submit_button(self.url_frame)
        self.setup_quality_options(self.download_options_frame)
        self.setup_video_info_frame(self.video_info_frame)

    def browse_directory(self):
        """Open a folder selection dialog and set the selected path to the provided variable."""
        directory = filedialog.askdirectory(initialdir=self.path_entry_var.get() or ".")
        if directory:
            self.path_entry_var.set(directory)

    def download_video(self):
        self.video_controller.start_download(self.quality_combo.get().split(' - ')[0], self.path_entry_var.get(), self.QUALITY_PRESETS)

    def download_complete(self):
        """Handle actions to be taken after download is complete."""
        messagebox.showinfo("Download Complete", "The video has been downloaded successfully!")
        self.state.state = "downloaded"
        self.revalitade_ui()

    def reset(self):
        """Reset the application state and clear all fields."""
        self.state.state = "init"
        self.video_info.url = None
        self.video_info.fetched_info = {}
        self.url_var.set("")
        self.revalitade_ui()

    def show_error(self, message):
        """Display an error message to the user."""
        messagebox.showerror("Error", message)
        self.state.state = "error"
        self.revalitade_ui()

    def log(self, message):
        """Append a message to the log text widget."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.config(state=tk.DISABLED)
        self.log_text.see(tk.END)  # Scroll to the end of the log

