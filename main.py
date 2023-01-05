#
# Basic python youtube downloader using pytube and ffmpeg for audio + video merging 0 - to achieve the best resolution
#
import time
import ffmpeg
from pytube import YouTube, Search
from utils import user_allows, enforce_options


class YoutubeDownloader:
    def __init__(self, url: str = None):
        if url:
            self.yt = YouTube(url)
        else:
            print('Would you like to input a URL for your video or search for one?')
            user_input = enforce_options(['url', 'search'])
            if user_input == 'url':
                self.yt = YouTube(input('Please enter the youtube URL: '))
            else:
                self.yt = self.search()

    def search(self, search_query: str = None, search_list_length: int = 5):
        if not search_query:
            search_query = input('What would you like to search? \n')
        s = Search(search_query)
        video_to_downloader = {}
        for i, r in enumerate(s.results):
            if i+1 > search_list_length:
                break
            video_to_downloader[i+1] = r
            temp_yd = YoutubeDownloader(r.watch_url)
            print(f'[{i+1}]  -  ({temp_yd.get_best_video().resolution}, {temp_yd.get_best_audio().abr}) {r.title}')

        print('Which video do you want to download?')
        user_input = int(enforce_options([str(k) for k in video_to_downloader.keys()]))
        return video_to_downloader[user_input]

    def get_best_audio(self):
        # get best average bit rate audio stream
        return self.yt.streams.filter(only_audio=True).order_by('abr').desc().first()

    def get_best_video(self):
        # get best resolution DASH video stream
        return self.yt.streams.filter(adaptive=True).order_by('resolution').desc().first()

    def download_best_resolution(self):
        # query audio and video stream, then merge them with ffmpeg
        best_audio = self.get_best_audio()
        best_video = self.get_best_video()

        if user_allows(f'Would you like to download this stream?\n '
                       f'Video resolution ({best_video.resolution}): {best_video} \n '
                       f'Audio resolution ({best_audio.abr}): {best_audio}'):
            start = time.time()
            best_audio.download(filename="temp/audio.mp3")
            best_video.download(filename="temp/video.mp4")
            audio = ffmpeg.input("temp/audio.mp3")
            video = ffmpeg.input("temp/video.mp4")
            ffmpeg.output(audio, video, f"downloads/{self.yt.title}.mp4").run(overwrite_output=True)
            end = time.time()

            print('  -  DOWNLOAD COMPLETE  -  ')
            print(f'    time taken: {round(end - start)} seconds')


if __name__ == '__main__':
    print('=' * 20 + 'PYTHON HIGH RES. YOUTUBE DOWNLOADER ' + '=' * 20)
    # select the video in initializing the downloader
    yd = YoutubeDownloader()
    # query a download operation
    yd.download_best_resolution()
