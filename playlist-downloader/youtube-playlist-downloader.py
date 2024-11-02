import os
import yt_dlp
from typing import Dict, List

class YouTubeDownloader:
    QUALITY_OPTIONS: Dict[str, str] = {
        "144p": "144",
        "240p": "240",
        "360p": "360",
        "480p": "480",
        "720p": "720",
        "1080p": "1080",
        "1440p": "1440",
        "2160p": "2160",
        "4320p": "4320"
    }

    def __init__(self):
        self.ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
            'outtmpl': '%(title)s.%(ext)s',
            'quiet': False,
            'no_warnings': False,
            'ignoreerrors': True,
            'progress_hooks': [self.progress_hook],
        }

    @staticmethod
    def get_available_qualities() -> List[str]:
        """Display and return available video qualities."""
        print("\nAvailable Video Qualities:")
        for quality in YouTubeDownloader.QUALITY_OPTIONS.keys():
            print(f"- {quality}")
        return list(YouTubeDownloader.QUALITY_OPTIONS.keys())

    def select_quality(self) -> str:
        """Prompt user to select video quality."""
        while True:
            qualities = self.get_available_qualities()
            selected = input("\nEnter desired quality (e.g., 720p): ").strip()
            
            if selected in qualities:
                return selected
            print("Invalid quality. Please select from the list above.")

    def select_download_path(self) -> str:
        """Prompt user to select download path."""
        while True:
            path = input("\nEnter download path (press Enter for current directory): ").strip()
            
            if path == "":
                return os.getcwd()
            
            if os.path.isdir(path):
                return path
            
            try:
                os.makedirs(path)
                return path
            except Exception as e:
                print(f"Error creating directory: {e}")
                print("Please enter a valid path.")

    @staticmethod
    def progress_hook(d):
        """Progress hook for download status."""
        if d['status'] == 'downloading':
            percentage = d.get('_percent_str', 'N/A')
            speed = d.get('_speed_str', 'N/A')
            print(f"\rDownloading... {percentage} at {speed}", end='')
        elif d['status'] == 'finished':
            print("\nDownload completed!")

    def download_playlist(self, url: str, quality: str, download_path: str):
        """Download YouTube playlist with specified quality."""
        try:
            # Update options with selected quality and download path
            format_spec = f'bestvideo[height<={self.QUALITY_OPTIONS[quality]}][ext=mp4]+bestaudio[ext=m4a]/mp4'
            self.ydl_opts.update({
                'format': format_spec,
                'outtmpl': os.path.join(download_path, '%(playlist_index)s-%(title)s.%(ext)s'),
            })

            # Extract playlist info
            with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
                playlist_info = ydl.extract_info(url, download=False)
                video_count = len(playlist_info['entries']) if 'entries' in playlist_info else 0
                print(f"\nPlaylist: {playlist_info.get('title', 'Unknown')}")
                print(f"Number of videos: {video_count}")

            # Download videos
            print("\nStarting download...")
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                ydl.download([url])

            print("\n✓ Playlist download completed successfully!")

        except Exception as e:
            print(f"\nError downloading playlist: {e}")

def main():
    print("YouTube Playlist Downloader")
    print("=========================")
    
    # Initialize downloader
    downloader = YouTubeDownloader()
    
    # Get playlist URL
    url = input("Enter YouTube playlist URL: ").strip()
    
    # Get quality preference
    quality = downloader.select_quality()
    
    # Get download path
    download_path = downloader.select_download_path()
    
    # Start download
    print(f"\nDownloading playlist to: {download_path}")
    print(f"Selected quality: {quality}")
    downloader.download_playlist(url, quality, download_path)

if __name__ == "__main__":
    main()
