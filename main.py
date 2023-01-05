# This is a sample Python script.

# Press ⇧⏎ to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

import ffmpeg
from pytube import YouTube, Search
from utils import print_dict, user_allows


class YoutubeDownloader:
    def __init__(self, url: str = None):
        if not url:
            self.search()
            # url = str(input('What youtube URL would you like to download?'))
        self.yt = YouTube(url)

    def search(self, search_query: str = None):
        if not search_query:
            search_query = input('What would you like to search? \n')
        s = Search(search_query)

        print(len(s.results))
        for r in s.results:
            yd = YoutubeDownloader(url=r.watch_url)

            print(f'({yd.get_best_video().resolution}, {yd.get_best_audio().abr}) [{r.title}]')

    def get_best_audio(self):
        # get best audio bit rate
        return self.yt.streams.filter(adaptive=True).order_by('abr').desc().first()

    def get_best_video(self):
        # get best video resolution
        return self.yt.streams.filter(adaptive=True).order_by('resolution').desc().first()

    def download_best_resolution(self):
        best_audio = self.get_best_audio()
        best_video = self.get_best_video()

        if user_allows(f'Would you like to download this stream?\n '
                       f'Video resolution ({best_video.resolution}): {best_video} \n '
                       f'Audio resolution ({best_audio.abr}): {best_audio}'):
            best_audio.download(filename="temp/audio.mp3")
            best_video.download(filename="temp/video.mp4")
            audio = ffmpeg.input("temp/audio.mp3")
            video = ffmpeg.input("temp/video.mp4")
            ffmpeg.output(audio, video, f"~/Movies/YouTube Downloads/{self.yt.title}").run(overwrite_output=True)



if __name__ == '__main__':

    yd = YoutubeDownloader()
    yd.search(search_query='test')


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
