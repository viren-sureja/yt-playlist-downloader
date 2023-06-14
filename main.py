import requests
from pytube import Playlist
from pytube import YouTube
from tqdm import tqdm
import math
import time

# Hardcoded playlist URL
playlist_url = "https://www.youtube.com/playlist?list=PLFr_jkwUp0hjcRpskdwHubPXLXeSKcZ5r"

# Create an instance of the playlist
playlist = Playlist(playlist_url)

# Retrieve the list of video URLs in the playlist
video_urls = playlist.video_urls

# Initialize outer progress bar for overall progress
outer_pbar = tqdm(total=len(video_urls), desc="Overall Progress")

# Retry failed downloads up to a maximum number of attempts
max_retries = 3

# Download each video in the playlist with progress bars
for video_url in video_urls:
    # Create a YouTube object for the current video
    video = YouTube(video_url)

    # Retrieve the video file size in bytes
    response = requests.head(video_url)
    file_size_bytes = int(response.headers.get('Content-Length', 0))

    # Calculate the video file size in megabytes (MB)
    file_size_mb = file_size_bytes / (1024 * 1024)

    # Initialize inner progress bar for current video
    inner_pbar = tqdm(total=file_size_mb, desc=f"Downloading {video.title}", unit='MB', unit_divisor=1024, leave=False)

    retries = 0
    success = False

    while retries < max_retries and not success:
        try:
            # Download the video
            stream = video.streams.get_highest_resolution()
            chunk_size = 1024 * 1024  # 1 MB
            response = requests.get(stream.url, stream=True)
            with open(f"{video.title}.{stream.subtype}", "wb") as file:
                bytes_downloaded = 0
                start_time = time.time()
                for chunk in response.iter_content(chunk_size=chunk_size):
                    file.write(chunk)
                    bytes_downloaded += len(chunk)
                    progress_fraction = min(bytes_downloaded / file_size_bytes, 1.0)
                    inner_pbar.update(progress_fraction * file_size_mb)
                    download_speed = bytes_downloaded / (time.time() - start_time)
                    inner_pbar.set_postfix(speed=f"{download_speed:.2f} MB/s")

            success = True
        except Exception as e:
            print(f"An error occurred while downloading {video.title}: {str(e)}")
            retries += 1

    # Check if the download was successful
    if success:
        # Update the progress bars
        inner_pbar.close()
        outer_pbar.update(1)
    else:
        print(f"Failed to download {video.title} after {retries} retries.")

# Close the outer progress bar
outer_pbar.close()
