"""
YouTube Downloader Package

A modular YouTube downloader with support for:
- Single video downloads
- Playlist downloads  
- Search functionality
- Audio-only downloads
- High-resolution video downloads
"""

# Core functionality
from .core import YoutubeDownloader, YoutubePlaylistDownloader, search_youtube

# UI functionality
from .ui import youtube_downloader_ui, parse_arguments

# Utility functions
from .utils import (
    strip_non_ascii,
    clear_cache,
    user_allows,
    enforce_options,
    print_dict,
    download
)

__version__ = "1.0.0"
__author__ = "YouTube Downloader Team"

__all__ = [
    # Core classes and functions
    'YoutubeDownloader',
    'YoutubePlaylistDownloader',
    'search_youtube',
    
    # UI functions
    'youtube_downloader_ui',
    'parse_arguments',
    
    # Utility functions
    'strip_non_ascii',
    'clear_cache',
    'user_allows',
    'enforce_options',
    'print_dict',
    'download'
]
