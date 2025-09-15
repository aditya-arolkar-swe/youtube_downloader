"""
Utility functions for the YouTube downloader
"""
import os
from json import dumps

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
