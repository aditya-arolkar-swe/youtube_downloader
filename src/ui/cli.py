"""
Command-line interface for YouTube downloader
"""
import argparse
from pytube import innertube
from ..core.downloader import YoutubeDownloader
from ..core.playlist import YoutubePlaylistDownloader
from ..utils.helpers import user_allows, enforce_options, print_dict, clear_cache


def youtube_downloader_ui(url: str = None, audio_only: bool = False):
    """
    Simple UI to assist a user in downloading a YouTube video
    """
    innertube._default_clients['ANDROID'] = innertube._default_clients['WEB']  # can remove once pytube has updated
    print('=' * 20 + ' PYTHON HIGH RESOLUTION YOUTUBE DOWNLOADER ' + '=' * 20)

    if url is not None:
        yd = YoutubeDownloader(url=url)
        yd.download_best_resolution(sound_only=audio_only)

    else:
        print('OPTIONS:')
        options = {1: 'download a youtube video with a URL', 2: 'search for a video with a search query',
                   3: 'download all or some videos in a playlist from a playlist URL'}
        print_dict(options)

        user_input = int(enforce_options([str(k) for k in options.keys()]))

        sound_only = audio_only or user_allows(f'Would you like to download sound only?')

        if user_input == 3:
            ypd = YoutubePlaylistDownloader()
            ypd.download(sound_only=sound_only)

        else:
            yd = YoutubeDownloader(search_mode=user_input == 2)
            yd.download_best_resolution(sound_only=sound_only)

    clear_cache()


def parse_arguments():
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser(description='Download full video or audio of youtube videos!')
    parser.add_argument('--url', type=str, default=None)
    parser.add_argument('--audio', type=bool, default=False)
    return parser.parse_args()
