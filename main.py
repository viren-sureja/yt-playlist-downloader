import requests
from pytube import Playlist
from pytube import YouTube
from tqdm import tqdm
import math
import time

# Take input for the playlist URL
playlist_url = input("Enter the playlist URL: ")

# Create an instance of the playlist
playlist = Playlist(playlist_url)

# Retrieve the list of video URLs in the playlist
video_urls = playlist.video_urls

# Take input for the download location
download_location = input("Enter the download location: ")

# Initialize outer progress bar for overall progress
outer_pbar = tqdm(total=len(video_urls), desc="Overall Progress")

# Retry failed downloads up to a maximum number of attempts
max_retries = 3

# Download each video in the playlist with progress bars
for index, video_url in enumerate(video_urls, start=1):
    # Create a YouTube object for the current video
    video = YouTube(video_url)

    # Retrieve the video file size in bytes
    response = requests.head(video_url)


    retries = 0
    success = False

    while retries < max_retries and not success:
        try:
            # Download the video
            stream = video.streams.get_highest_resolution()
            file_size_bytes = int(stream.filesize)

            # Calculate the video file size in megabytes (MB)
            file_size_mb = file_size_bytes / (1024 * 1024)

            # Initialize inner progress bar for current video
            inner_pbar = tqdm(total=file_size_mb, desc=f"Downloading {video.title}", unit='MB',
                              unit_scale=True, leave=False)
            chunk_size = 1024 * 1024  # 1 MB
            response = requests.get(stream.url, stream=True)

            # Set the download location and file name
            video_title = f"{index}_{'_'.join(video.title.split(' '))}"
            file_path = f"{download_location}/{video_title}.{stream.subtype}"

            with open(file_path, "wb") as file:
                bytes_downloaded = 0
                start_time = time.time()

                for chunk in response.iter_content(chunk_size=chunk_size):
                    file.write(chunk)
                    chunk_size_in_MB = len(chunk) / (1024 * 1024)
                    bytes_downloaded += chunk_size_in_MB
                    inner_pbar.update(chunk_size_in_MB)
                    download_speed = bytes_downloaded / (time.time() - start_time)

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
