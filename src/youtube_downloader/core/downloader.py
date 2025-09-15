"""
Core YouTube downloader functionality
"""
import datetime
import os
import sys
import time
import traceback

import ffmpeg
from pytube import YouTube, Search
from pytube.exceptions import VideoUnavailable
from ..utils.helpers import user_allows, strip_non_ascii, enforce_options


def search_youtube(search_query: str = None, search_list_length: int = 5, use_oauth: bool = True) -> YouTube:
    """
    Searches YouTube for the video you want, and returns the appropriate "YouTube" object for the video
    :param use_oauth:
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
    for i, yt in enumerate(s.results):
        if i == len(s.results) - 1:
            s.get_next_results()
        count += 1
        yd = YoutubeDownloader(yt=yt, sign_in=use_oauth)
        if yd.is_live_stream():
            print(f' [ALERT] skipping [{i}] "{yd.get_title()}" because it is a live stream... ')
            continue
        video_to_downloader[i] = yt
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
    Stores all variables for a given YouTube video and assists in the download process
    """
    def __init__(self, url: str = None, yt: YouTube = None, search_mode: bool = False, sign_in: bool = False):
        if yt:
            self.yt = yt
            self.yt.use_oauth = sign_in
            self.yt.allow_oauth_cache = sign_in
        elif search_mode:
            self.yt = search_youtube(use_oauth=sign_in)
        else:
            if not url:
                url = input('Please enter the youtube URL: ')
            try:
                self.yt = YouTube(url, use_oauth=sign_in, allow_oauth_cache=sign_in)
            except VideoUnavailable:
                print(f' [ERROR] video {url} is unavailable! Might be a restricted video...')
                self.attempt_sign_in(url=url)

    def attempt_sign_in(self, url: str = None):
        print(' [ALERT] Attempting to sign in to YouTube...')
        try:
            self.yt = YouTube(url if url else self.yt.watch_url, use_oauth=True, allow_oauth_cache=True)
            print(' [SUCCEEDED] Sign in succeeded!')
        except VideoUnavailable as e:
            print(f' [ERROR] {e} video {url} is unavailable! Exiting...')
            print('Traceback: ', traceback.format_exc())
            sys.exit(1)

    def is_live_stream(self):
        return self.get_vid_info()['videoDetails']['isLiveContent']

    def get_vid_info(self):
        return self.yt.vid_info

    def get_title(self):
        # removes any '/'s to not confuse the filename with a new directory in the os outputs
        return strip_non_ascii(self.yt.title.replace('/', ''))

    def get_video_length(self):
        return str(datetime.timedelta(seconds=self.yt.length))

    def get_best_audio(self):
        # get best average bit rate audio stream
        return self.yt.streams.filter(only_audio=True).order_by('abr').desc().first()

    def get_best_video(self):
        # get best resolution DASH video stream
        return self.yt.streams.filter(adaptive=True).order_by('resolution').desc().first()

    def print_video_info(self, list_num: int = 0, include_traceback: bool = False):
        succeeded = False
        while not succeeded:
            try:
                print(f'[{list_num}]  -  {self.get_video_length()}     ({self.get_best_video().resolution}, '
                      f'{self.get_best_audio().abr})     {self.get_title()}')
                succeeded = True
            except Exception as e:
                print(f' [ERROR] Failed to get video info with error {e} on "{self.get_title()}"!')
                print('Playability status: ', self.get_playability_status())
                self.attempt_sign_in()
                if include_traceback:
                    print('Traceback: ', traceback.format_exc())
                succeeded = False

    def download_best_resolution(self, force_download: bool = False, output_dir: str = None, sound_only: bool = False):
        # query audio and video stream, then merge them with ffmpeg
        self.print_video_info()
        best_audio = self.get_best_audio()
        best_video = self.get_best_video()

        prompt = f'Would you like to download this stream for "{self.get_title()}"?\n'
        if not sound_only:
            prompt += f' Video resolution ({best_video.resolution}): {best_video} \n'
        prompt += f' Audio resolution ({best_audio.abr}): {best_audio}'

        if force_download or user_allows(prompt):
            start = time.time()
            output_dir = os.path.join('downloads', output_dir) if output_dir else 'downloads'
            output_dir = os.path.join(os.getcwd(), output_dir)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            if sound_only:
                output_filename = os.path.join(output_dir, f"{self.get_title()}.mp3")
                best_audio.download(filename=output_filename)
            else:
                temp_path = os.path.join(os.getcwd(), "temp")
                if not os.path.exists(temp_path):
                    os.makedirs(temp_path)
                audio_filename = os.path.join(temp_path, f"{self.get_title()}_audio.mp3")
                video_filename = os.path.join(temp_path, f"{self.get_title()}_video.mp4")
                best_audio.download(filename=audio_filename)
                best_video.download(filename=video_filename)
                audio = ffmpeg.input(audio_filename)
                video = ffmpeg.input(video_filename)
                output_filename = os.path.join(output_dir, f"{self.get_title()}.mp4")
                ffmpeg.output(audio, video, output_filename).run(overwrite_output=True)
            end = time.time()

            print(f'  ===  DOWNLOAD COMPLETE  ===  ')
            self.print_video_info()
            print(f'Saved to "{os.path.join(os.getcwd(), output_filename)}". Time taken: {round(end - start)} seconds')

    def get_playability_status(self):
        p = self.get_vid_info()['playabilityStatus']
        return {'status': p['status'], 'reason': p['reason'], 'reasonTitle': p['reasonTitle']}
