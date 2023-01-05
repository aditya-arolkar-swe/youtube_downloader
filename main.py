#
# Basic python youtube downloader using pytube and ffmpeg for audio + video merging 0 - to achieve the best resolution
#
import os
import time
import ffmpeg
from pytube import YouTube, Search, Playlist
from utils import user_allows, enforce_options, print_dict


class YoutubeDownloader:
    def __init__(self, url: str = None, yt: YouTube = None, search_mode: bool = False):
        if yt:
            self.yt = yt
        elif url:
            self.yt = YouTube(url)
        elif search_mode:
            self.yt = self.search()
        else:
            self.yt = YouTube(input('Please enter the youtube URL: '))

    def get_title(self):
        return self.yt.title

    def search(self, search_query: str = None, search_list_length: int = 5):
        if not search_query:
            search_query = input('What would you like to search? \n')
        s = Search(search_query)
        video_to_downloader = {}
        for i, r in enumerate(s.results):
            if i >= search_list_length:
                break
            video_to_downloader[i] = r
            yd = YoutubeDownloader(yt=r)
            print(f'[{i}]  -  ({yd.get_best_video().resolution}, {yd.get_best_audio().abr}) {yd.get_title()}')

        print('Which video do you want to choose?')
        user_input = int(enforce_options([str(k) for k in video_to_downloader.keys()]))
        return video_to_downloader[user_input]

    def get_best_audio(self):
        # get best average bit rate audio stream
        return self.yt.streams.filter(only_audio=True).order_by('abr').desc().first()

    def get_best_video(self):
        # get best resolution DASH video stream
        return self.yt.streams.filter(adaptive=True).order_by('resolution').desc().first()

    def download_best_resolution(self, force_download: bool = False):
        # query audio and video stream, then merge them with ffmpeg
        best_audio = self.get_best_audio()
        best_video = self.get_best_video()

        if force_download or user_allows(f'Would you like to download this stream?\n '
                       f'Video resolution ({best_video.resolution}): {best_video} \n '
                       f'Audio resolution ({best_audio.abr}): {best_audio}'):
            start = time.time()
            best_audio.download(filename="temp/audio.mp3")
            best_video.download(filename="temp/video.mp4")
            audio = ffmpeg.input("temp/audio.mp3")
            video = ffmpeg.input("temp/video.mp4")
            output_dir = 'downloads'
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            output_fname = f"{output_dir}/{self.yt.title}.mp4"
            output_fname = ''.join(char for char in output_fname if ord(char) < 128)
            ffmpeg.output(audio, video, output_fname).run(overwrite_output=True)
            end = time.time()

            print(f'  -  DOWNLOAD COMPLETE  -  ')
            print(f'"{self.yt.title}"s video ({self.get_best_video().resolution}, {self.get_best_audio().abr}) has been '
                  f'saved to "{output_fname}".')
            print(f'Time taken: {round(end - start)} seconds')


class YoutubePlaylistDownloader:
    def __init__(self, url: str = None):
        if not url:
            url = input('Please enter the playlist URL: ')
        self.playlist = Playlist(url)
        print(f'Loaded playlist "{self.playlist.title}" which has {len(self.playlist)} videos!')

    def download(self):
        video_to_downloader = {}
        for i, video in enumerate(self.playlist):
            yd = YoutubeDownloader(video)
            video_to_downloader[i] = yd
            print(f'[{i}]  -  ({yd.get_best_video().resolution}, {yd.get_best_audio().abr}) {yd.get_title()}')
        user_input = input('Which videos do you want to download? '
                           'enter comma delimited list to specify or "all" for all videos: ')
        if 'all' in user_input:
            chosen_videos = range(len(self.playlist))
        else:
            chosen_videos = [int(i) for i in user_input.split(', ')]

        final_chosen = []
        for c in chosen_videos:
            if c not in range(len(self.playlist)):
                print(f'skipping {c} as not a valid video in this playlist')
            else:
                final_chosen.append(video_to_downloader[c])

        print(f'Downloading ({len(final_chosen)} videos): {[v.get_title() for v in final_chosen]}')
        for yd in final_chosen:
            yd.download_best_resolution(force_download=True)


def youtube_downloader_ui():
    print('=' * 20 + 'PYTHON HIGH RES. YOUTUBE DOWNLOADER ' + '=' * 20)
    print('OPTIONS:')
    options = {1: 'download a youtube video with a URL', 2: 'search for a video with a search query',
               3: 'download all or some videos in a playlist from a playlist URL'}
    print_dict(options)

    user_input = int(enforce_options([str(k) for k in options.keys()]))

    if user_input == 1:
        yd = YoutubeDownloader()
        yd.download_best_resolution()
    elif user_input == 2:
        yd = YoutubeDownloader(search_mode=True)
        yd.download_best_resolution()
    elif user_input == 3:
        ypd = YoutubePlaylistDownloader()
        ypd.download()


if __name__ == '__main__':
    youtube_downloader_ui()
