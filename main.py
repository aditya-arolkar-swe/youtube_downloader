#
# Basic python youtube downloader using pytube to import the youtube streams and using ffmpeg to merge the highest
# average bit rate audio streams with the highest resolution DASH video stream. Implements basic search function and can
# download a partial or an entire playlist at one go
#
import datetime
import os
import sys
import time
import traceback
import ffmpeg
from pytube import YouTube, Search, Playlist
from pytube.exceptions import VideoUnavailable
from utils import user_allows, enforce_options, print_dict


def search_youtube(search_query: str = None, search_list_length: int = 5) -> YouTube:
    """
    Searches youtube for the video you want, and returns the appropriate "YouTube" object for the video
    :param search_query: (optional) you can pre-select your search query - prompts the user otherwise
    :param search_list_length: (optional) can set the length of each page of the search list
    :return: "YouTube object" of the selected video
    """
    if not search_query:
        search_query = input('What would you like to search? \n')
    s = Search(search_query)
    video_to_downloader = {}
    user_input = None
    count = 0
    for i, r in enumerate(s.results):
        if i == len(s.results) - 1:
            s.get_next_results()
        count += 1
        video_to_downloader[i] = r
        yd = YoutubeDownloader(yt=r)
        yd.print_video_info(list_num=i)
        if count >= search_list_length:
            user_input = input(f'Select a video number to download OR enter "next" to see the next {search_list_length}'
                               f' videos in the search: ')
            if 'next' in user_input:
                count = 0
                continue
            else:
                user_input = int(user_input)
                if user_input not in video_to_downloader.keys():
                    user_input = int(enforce_options([str(k) for k in video_to_downloader.keys()]))
                break
    return video_to_downloader[user_input]


class YoutubeDownloader:
    """
    Stores all variables for a given youtube video and assists in the download process
    """
    def __init__(self, url: str = None, yt: YouTube = None, search_mode: bool = False):
        if yt:
            self.yt = yt
        elif search_mode:
            self.yt = search_youtube()
        else:
            if not url:
                url = input('Please enter the youtube URL: ')
            try:
                self.yt = YouTube(url)
            except VideoUnavailable:
                print(f' [ERROR] video {url} is unavailable! Please try another youtube URL...')
                sys.exit(1)

    def get_title(self):
        return self.yt.title

    def get_video_length(self):
        return str(datetime.timedelta(seconds=self.yt.length))

    def get_best_audio(self):
        # get best average bit rate audio stream
        return self.yt.streams.filter(only_audio=True).order_by('abr').desc().first()

    def get_best_video(self):
        # get best resolution DASH video stream
        return self.yt.streams.filter(adaptive=True).order_by('resolution').desc().first()

    def print_video_info(self, list_num: int = 0):
        print(f'[{list_num}]  -  {self.get_video_length()}     ({self.get_best_video().resolution}, '
              f'{self.get_best_audio().abr})     {self.get_title()}')

    def download_best_resolution(self, force_download: bool = False):
        # query audio and video stream, then merge them with ffmpeg
        best_audio = self.get_best_audio()
        best_video = self.get_best_video()

        if force_download or user_allows(f'Would you like to download this stream for "{self.get_title()}"?\n '
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

            print(f'  ===  DOWNLOAD COMPLETE  ===  ')
            self.print_video_info()
            print(f'Saved to "{output_fname}". Time taken: {round(end - start)} seconds')


class YoutubePlaylistDownloader:
    """
    Stores all variables for a given youtube playlist and assists in the download of some or all videos in the playlist
    """
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
            yd.print_video_info(list_num=i)
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
            try:
                yd.download_best_resolution(force_download=True)
            except Exception:
                print(f' [ERROR] failed to download "{yd.get_title()}" with traceback: ')
                print(traceback.format_exc())


def youtube_downloader_ui():
    """
    simple UI to assist a user in downloading a youtube video
    :return:
    """
    print('=' * 20 + ' PYTHON HIGH RESOLUTION YOUTUBE DOWNLOADER ' + '=' * 20)
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
