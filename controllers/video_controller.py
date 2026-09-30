from models.video_info import VideoInfo
from models.state import State
import yt_dlp
import threading
import os

class VideoController:
    def __init__(self, state : State, video_info : VideoInfo, gui):
          self.state = state
          self.video_info = video_info
          self.gui = gui

    def fetch_video_info(self, as_playlist: bool = False):
            """Fetch video information from YouTube"""
            url = self.video_info.url
            if not url:
                print("Please enter a valid URL")
                return

            url = url.strip()
            
            self.state.state = "fetching"
            self.gui.revalitade_ui()

            self.gui.log(f"Fetching video information for URL: {url}")

            def fetch():
                fetched_ok = False
                try:
                    ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'noplaylist': not as_playlist,
                    'extractor_args': {
                        'youtube': {'player_client': ['android']},
                    },
                    }

                    if as_playlist:
                        # Flat extraction keeps playlist fetch fast while still returning entry count/title.
                        ydl_opts['extract_flat'] = True
                
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        self.video_info.fetched_info = ydl.extract_info(url, download=False)
                        print(self.video_info)
                        fetched_ok = True
                    

                        # Update GUI in main thread
                        # self.root.after(0, self.update_video_info)
                    
                except Exception as e:
                    print(f"Error fetching video info: {str(e)}")
                    self.gui.log(f"Error fetching video info: {str(e)}")
                    self.gui.show_error(f"Error fetching video info: {str(e)}")
                finally:
                    if fetched_ok:
                        self.state.state = "fetched"
                        # Update GUI in main thread
                        self.gui.revalitade_ui()
        
            # Start fetching in a separate thread
            threading.Thread(target=fetch, daemon=True).start()

    def start_download(self, quality, output_path, quality_presets, download_playlist: bool = False):
        """Start video download process"""
        if not self.video_info or not self.video_info.url:
            return
        
        self.quality = quality
        self.output_path = output_path.strip()
        self.quality_presets = quality_presets
        
        if not os.path.exists(output_path):
            try:
                os.makedirs(output_path)
            except Exception as e:
                self.gui.log(f"Error creating directory: {str(e)}")
                self.gui.show_error(f"Error creating directory: {str(e)}")
                return
        
        self.state.state = "downloading"
        
        # self.progress_var.set(0)
        
        def download_progress_hook(d):
            if d['status'] == 'downloading':
                try:
                    # Log progress to the log widget
                    self.gui.log(f"Downloading: {d['_percent_str']} of {d.get('_total_bytes_str', 'Unknown size')}")
                    
                except:
                    pass
            elif d['status'] == 'finished':
                self.gui.log("Download completed! Processing video...")
        
        def download():
            try:
                target_height = self.quality_presets[quality]['height']
                is_audio_only = target_height is None
                output_template = '%(title)s [%(resolution)s].%(ext)s'
                if download_playlist:
                    output_template = '%(playlist_title)s/%(playlist_index)s - %(title)s [%(resolution)s].%(ext)s'

                format_selector = 'bestaudio/best' if is_audio_only else f'bestvideo[height<={target_height}]+bestaudio/best[height<={target_height}]'

                ydl_opts = {
                    'format': format_selector,
                    'outtmpl': os.path.join(output_path, output_template),
                    'restrictfilenames': True,
                    'noplaylist': not download_playlist,
                    'ignoreerrors': download_playlist,
                    'quiet': False,
                    'extractor_args': {
                        'youtube': {'player_client': ['android']},
                    },
                    'progress_hooks': [download_progress_hook],
                }

                if not is_audio_only:
                    ydl_opts['merge_output_format'] = 'mp4'
                else:
                    ydl_opts['postprocessors'] = [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }]
                    ydl_opts['keepvideo'] = False
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([self.video_info.url])
                
                self.gui.download_complete() 
                self.gui.log("Download complete!")

            except Exception as e:
                error_message = str(e)
                if 'ffmpeg' in error_message.lower():
                    error_message = f"{error_message}. Install FFmpeg to enable MP3 conversion."
                self.gui.log(f"Error during download: {error_message}")
                self.gui.show_error(f"Error during download: {error_message}")
        
        # Start download in a separate thread
        self.download_thread = threading.Thread(target=download, daemon=True)
        self.download_thread.start()
     