"""
YouTube playlist downloader functionality
"""
import traceback
import tqdm
from pytube import Playlist
from .downloader import YoutubeDownloader
from ..utils.helpers import enforce_options


class YoutubePlaylistDownloader:
    """
    Stores all variables for a given YouTube playlist and assists in the download of some or all videos in the playlist
    """
    def __init__(self, url: str = None):
        if not url:
            url = input('Please enter the playlist URL: ')
        self.playlist = Playlist(url)
        print(f'Loaded playlist "{self.playlist.title}" which has {len(self.playlist)} videos!')

    def download(self, sound_only: bool = False):
        video_to_downloader = {}
        for i, video in enumerate(self.playlist):
            yd = YoutubeDownloader(video)
            yd.print_video_info(list_num=i)
            video_to_downloader[i] = {'downloader': yd, 'resolution': yd.get_best_video().resolution}
        user_input = input('Which videos do you want to download? enter comma delimited list to specify OR "all" for '
                           'all videos OR "resolution" to filter for certain resolutions: ')
        if 'all' in user_input:
            chosen_videos = range(len(self.playlist))
        elif 'resolution' in user_input:
            resolutions = list(set([info['resolution'] for info in video_to_downloader.values()]))
            print('What resolution would you like to filter for?')
            user_input = enforce_options(resolutions)
            chosen_videos = [i for i, info in video_to_downloader.items() if info['resolution'] == user_input]
        else:
            chosen_videos = [int(i) for i in user_input.split(', ')]

        final_chosen = []
        for c in chosen_videos:
            if c not in range(len(self.playlist)):
                print(f'skipping {c} as not a valid video in this playlist')
            else:
                final_chosen.append(video_to_downloader[c])

        print(f"Downloading ({len(final_chosen)} videos): {[v['downloader'].get_title() for v in final_chosen]}")
        for video_info in tqdm.tqdm(final_chosen):
            yd = video_info['downloader']
            try:
                yd.download_best_resolution(force_download=True, output_dir=self.playlist.title, sound_only=sound_only)
            except Exception as e:
                print(f' [ERROR] {e}. failed to download "{yd.get_title()}" with traceback: ')
                print(traceback.format_exc())
