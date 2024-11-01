import yt_dlp
import os
import re

# Define quality presets with their specifications
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

def get_format_height(format_dict):
    """
    Safely get the height from a format dictionary.
    
    Args:
        format_dict (dict): Format dictionary from yt-dlp
    
    Returns:
        int: Height value or 0 if not available
    """
    try:
        height = format_dict.get('height', 0)
        return int(height) if height is not None else 0
    except (ValueError, TypeError):
        return 0

def is_valid_youtube_url(url):
    """
    Validate if the given URL is a valid YouTube URL.
    """
    youtube_regex = (
        r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    )
    return bool(re.match(youtube_regex, url))

def get_valid_youtube_url():
    """
    Prompt user for a valid YouTube URL.
    """
    while True:
        url = input("\nEnter YouTube video URL: ").strip()
        if is_valid_youtube_url(url):
            return url
        print("Invalid YouTube URL. Please try again.")

def get_available_formats(formats):
    """
    Get list of available video formats with valid height information.
    
    Args:
        formats (list): List of format dictionaries from yt-dlp
    
    Returns:
        list: List of formats with valid height information
    """
    video_formats = []
    for f in formats:
        # Check if it's a video format
        if f.get('vcodec') != 'none':
            height = get_format_height(f)
            if height > 0:
                video_formats.append(f)
    return video_formats

def list_available_formats(url):
    """
    List available formats for a YouTube video.
    """
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("\nFetching video information...")
            info = ydl.extract_info(url, download=False)
            all_formats = info.get('formats', [])
            
            # Get valid video formats
            video_formats = get_available_formats(all_formats)
            
            print(f"\nVideo Title: {info.get('title', 'Unknown')}")
            print(f"Duration: {info.get('duration_string', 'Unknown')}")
            print(f"Channel: {info.get('channel', 'Unknown')}")
            
            # Find maximum available quality
            max_height = max((get_format_height(f) for f in video_formats), default=0)
            
            print("\nAvailable quality options:")
            print("Quality | Resolution  | Type | Description")
            print("-" * 65)
            
            # Show only available quality options
            for quality, specs in QUALITY_PRESETS.items():
                if specs['height'] <= max_height:
                    print(f"{quality:^7} | {specs['resolution']:^11} | {specs['label']:^4} | {specs['description']}")
            
            return video_formats
            
    except Exception as e:
        print(f"Error fetching video information: {str(e)}")
        return []

def download_youtube_video(url, output_path=None, quality='1080p'):
    """
    Download a YouTube video in specified quality.
    """
    try:
        if quality not in QUALITY_PRESETS:
            print(f"Invalid quality selection. Using 1080p as default.")
            quality = '1080p'
        
        if output_path is None:
            output_path = os.getcwd()
            
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        
        target_height = QUALITY_PRESETS[quality]['height']
        
        ydl_opts = {
            'format': f'bestvideo[height<={target_height}]+bestaudio/best[height<={target_height}]',
            'outtmpl': os.path.join(output_path, '%(title)s [%(resolution)s].%(ext)s'),
            'restrictfilenames': True,
            'noplaylist': True,
            'quiet': False,
            'merge_output_format': 'mp4',
            'progress_hooks': [lambda d: print(f"\rDownloading: {d['_percent_str']} of {d.get('_total_bytes_str', 'Unknown size')}", end='') if d['status'] == 'downloading' else None],
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"\nStarting download in {quality} ({QUALITY_PRESETS[quality]['description']})...")
            info = ydl.extract_info(url, download=True)
            file_path = os.path.join(output_path, f"{info['title']} [{info.get('resolution', quality)}].mp4")
            print(f"\nDownload completed! Saved to: {file_path}")
            return file_path
        
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        return None

def main():
    """
    Main function to run the interactive YouTube downloader.
    """
    print("=== YouTube Video Downloader ===")
    print("Supported qualities: 8K, 4K, 2K, 1080p, 720p, 480p, 360p, 240p")
    
    while True:
        url = get_valid_youtube_url()
        video_formats = list_available_formats(url)
        
        if not video_formats:
            print("Unable to fetch video information. Please try again.")
            continue
        
        # Get maximum available height
        max_available_height = max(get_format_height(f) for f in video_formats)
        
        # Filter quality presets based on available formats
        available_qualities = [
            (i, quality, specs) 
            for i, (quality, specs) in enumerate(QUALITY_PRESETS.items(), 1)
            if specs['height'] <= max_available_height
        ]
        
        print("\nSelect video quality:")
        for i, quality, specs in available_qualities:
            print(f"{i-1}. {quality} ({specs['resolution']}) - {specs['description']}")
        
        # Get user selection
        while True:
            try:
                default_choice = min(2, len(available_qualities))
                choice = int(input(f"\nEnter quality number [default: {default_choice} for {available_qualities[default_choice-1][1]}]: ").strip() or str(default_choice))
                if 1 <= choice <= len(available_qualities):
                    selected_quality = available_qualities[choice-1][1]
                    break
                else:
                    print("Invalid selection. Please try again.")
            except (ValueError, IndexError):
                print("Please enter a valid number.")
        
        output_dir = input("\nEnter output directory [default: downloads]: ").strip() or "downloads"
        result = download_youtube_video(url, output_dir, selected_quality)
        
        if input("\nDownload another video? (y/n): ").lower() != 'y':
            break
    
    print("\nThank you for using YouTube Video Downloader!")

if __name__ == "__main__":
    main()
