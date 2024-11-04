import yt_dlp
import re
import os

class YouTubeController:
    def __init__(self):
        pass

    def isValidUrl(url):
        youtube_regex = (
            r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
            r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
        )
        return bool(re.match(youtube_regex, url))
    
    def getVideoInfo(url):
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            video_info = ydl.extract_info(url, download=False)
            return video_info
    
    def downloadVideo(self, url, download_progress_hook, output_path, target_height):
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
            ydl.download([url])
                