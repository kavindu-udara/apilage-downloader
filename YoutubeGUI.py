import customtkinter
import YouTubeFrame
from YouTubeFrame import YouTubeFrame, URLFrame, VideoInfoFrame, DownloadOptionsFrame
import YouTubeController
from YouTubeController import YouTubeController

class YoutubeGUI(customtkinter.CTk):

    def __init__(self):
        super().__init__()

        self.title("YouTube Video Downloader")
        self.geometry("400x420")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1), weight=1)

        self.ytFrame = YouTubeFrame(self, "Title")
        self.ytFrame.grid(row=0, column=0, sticky="nsew")

        self.url_frame = URLFrame(self, "Enter Youtube video URL : ", self.fetch_video_info)
        self.url_frame.grid(row=1, column=0, sticky="nsew")

        info_values = {'title': 'Title', 'duration': 'Duration', 'channel': 'Channel' }
        self.VideoInfoFrame = VideoInfoFrame(self, info_values)
        self.VideoInfoFrame.grid(row=2, column=0, sticky="nsew")

        self.DownloadOptionsFrame = DownloadOptionsFrame(self, self.download)
        self.DownloadOptionsFrame.grid(row=3, column=0, sticky="nsew")

    def fetch_video_info(self):
        url = self.url_frame.url_var.get()
        if YouTubeController.isValidUrl(url):
            info = YouTubeController.getVideoInfo(url)
            self.VideoInfoFrame.update_info(info)
            self.filter_quality_options(info)
        else:
            print("Invalid URL")

    def update_quality_options(formats):
        available_heights = set()
        for f in formats:
            if f.get('vcodec') != 'none' and f.get('height'):
                available_heights.add(f.get('height'))

    def filter_quality_options(self, video_info):    
        self.DownloadOptionsFrame.filter_and_sort_quality_options(video_info=video_info)
    
    def download(self):
        url = self.url_frame.url_var.get()
        self.DownloadOptionsFrame.start_download(url)

        

