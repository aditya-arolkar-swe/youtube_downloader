"""
Utility functions for the YouTube downloader
"""
import os
from json import dumps
from pytube import YouTube
from pytube.exceptions import VideoUnavailable

def strip_non_ascii(string: str) -> str:
    """
    Strips out any characters that aren't ascii
    """
    return ''.join(char for char in string if ord(char) < 128)


def clear_cache(cache_dir: str = 'temp'):
    """
    Clear temporary cache of separate audio and video files
    """
    if not os.path.exists(cache_dir):
        return
    for f in os.listdir(cache_dir):
        os.remove(os.path.join(cache_dir, f))
    os.rmdir(cache_dir)


def download(url: str, use_oauth: bool = False):
    """
    Takes a YouTube URL and returns the highest resolution video stream available.
    
    Args:
        url (str): YouTube video URL
        use_oauth (bool): Whether to use OAuth for authentication (default: True)
    
    Returns:
        pytube.Stream: The highest resolution video stream available
        
    Raises:
        VideoUnavailable: If the video is unavailable or restricted
        Exception: For other errors that might occur during stream retrieval
    """
    try:
        # Create YouTube object
        yt = YouTube(url, use_oauth=use_oauth, allow_oauth_cache=use_oauth)
        
        # Get the highest resolution adaptive video stream
        best_video_stream = yt.streams.filter(adaptive=True).order_by('resolution').desc().first()
        
        if best_video_stream is None:
            # Fallback to progressive streams if no adaptive streams available
            best_video_stream = yt.streams.filter(progressive=True).order_by('resolution').desc().first()
        
        if best_video_stream is None:
            raise Exception("No video streams available for this video")
            
        return best_video_stream
        
    except VideoUnavailable as e:
        # Try with OAuth if it wasn't already enabled
        if not use_oauth:
            try:
                yt = YouTube(url, use_oauth=True, allow_oauth_cache=True)
                best_video_stream = yt.streams.filter(adaptive=True).order_by('resolution').desc().first()
                if best_video_stream is None:
                    best_video_stream = yt.streams.filter(progressive=True).order_by('resolution').desc().first()
                if best_video_stream is None:
                    raise Exception("No video streams available for this video")
                return best_video_stream
            except VideoUnavailable:
                raise VideoUnavailable(f"Video {url} is unavailable. It might be restricted or private.")
        else:
            raise VideoUnavailable(f"Video {url} is unavailable. It might be restricted or private.")


def print_dict(text):
    print(dumps(text, indent=4))


def enforce_options(options):
    user_input = input(f'Please enter one of {options}:\n')
    while user_input not in options:
        user_input = input(f'Please enter one of {options}:\n')
    return user_input


def user_allows(question: str = None):
    print(question)
    return 'y' == enforce_options(['y', 'n'])
