# music_player.py

import yt_dlp
import subprocess
import sys
import os

def play_music(video_url):
    """
    Plays the audio from a given YouTube video URL using an external player (MPV).

    Args:
        video_url (str): The URL of the YouTube video to play.

    Returns:
        subprocess.Popen or None: The Popen object for the MPV process if started,
                                  otherwise None.
    """
    print(f"Attempting to play: {video_url}")

    # Options for yt_dlp to extract only audio stream information
    ydl_opts = {
        'format': 'bestaudio/best',  # Prioritize best audio quality
        'quiet': True,               # Suppress yt_dlp's console output
        'noplaylist': True,          # Do not extract playlist information
        'no_warnings': True,         # Suppress warnings
    }

    player_process = None # Initialize player_process

    try:
        # Extract information about the video, including the direct audio URL
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            audio_url = None

            # Find the direct audio URL. yt_dlp provides various formats.
            # We look for a direct URL that mpv can handle.
            if 'url' in info:
                audio_url = info['url']
            elif 'formats' in info:
                # Iterate through formats to find a suitable audio stream
                for f in info['formats']:
                    if 'url' in f and 'acodec' in f and f['acodec'] != 'none':
                        audio_url = f['url']
                        break

            if not audio_url:
                print("Could not find a suitable audio stream URL.")
                return None

            print(f"Playing audio stream: {audio_url}")

            # Determine the MPV command based on the operating system
            mpv_command = ['mpv', '--no-video', '--force-window=no', audio_url]

            # Start the MPV process and return it
            player_process = subprocess.Popen(mpv_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return player_process

    except yt_dlp.utils.DownloadError as e:
        print(f"Error fetching video information: {e}")
        print("This might be due to geo-restrictions, video not found, or other YouTube issues.")
        return None
    except FileNotFoundError:
        print("Error: MPV player not found.")
        print("Please ensure MPV is installed and accessible in your system's PATH.")
        print("You can usually install MPV via your system's package manager (e.g., 'sudo apt install mpv' on Debian/Ubuntu, 'brew install mpv' on macOS).")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def download_media(video_url, format_type, output_path="downloads", progress_callback=None):
    """
    Downloads media (audio as MP3 or video as MP4) from a given YouTube video URL.

    Args:
        video_url (str): The URL of the YouTube video to download.
        format_type (str): 'mp3' for audio-only, 'mp4' for video.
        output_path (str): The directory where the downloaded file will be saved.
        progress_callback (callable, optional): A function to call with download progress information.
                                                It receives a dictionary with 'status', 'total_bytes',
                                                'downloaded_bytes', 'elapsed', 'speed', 'eta', etc.
    """
    print(f"Attempting to download {format_type}: {video_url}")

    # Ensure the download directory exists
    if not os.path.exists(output_path):
        os.makedirs(output_path)
        print(f"Created download directory: {output_path}")

    ydl_opts = {
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'), # Output template
        'quiet': True,               # Suppress default yt_dlp progress output
        'noplaylist': True,          # Do not download playlists
        'no_warnings': True,         # Suppress warnings
    }

    if progress_callback:
        ydl_opts['progress_hooks'] = [progress_callback]

    if format_type == 'mp3':
        ydl_opts.update({
            'format': 'bestaudio/best',  # Select the best audio format
            'postprocessors': [{
                'key': 'FFmpegExtractAudio', # Extract audio
                'preferredcodec': 'mp3',     # Convert to MP3
                'preferredquality': '192',   # Set quality (e.g., 192kbps)
            }],
        })
    elif format_type == 'mp4':
        ydl_opts.update({
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', # Select best video and audio, then merge to mp4
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor', # Convert video (if necessary)
                'preferedformat': 'mp4',       # Preferred output format
            }],
        })
    else:
        print(f"Error: Unsupported format type '{format_type}'. Please choose 'mp3' or 'mp4'.")
        if progress_callback:
            progress_callback({'status': 'error', 'message': f"Unsupported format: {format_type}"})
        return

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        print(f"Download complete! Check '{output_path}' directory.")
        if progress_callback:
            progress_callback({'status': 'finished', 'message': 'Download complete!'})
    except yt_dlp.utils.DownloadError as e:
        print(f"Error during download: {e}")
        if progress_callback:
            progress_callback({'status': 'error', 'message': f"Download error: {e}"})
    except Exception as e:
        print(f"An unexpected error occurred during download: {e}")
        if progress_callback:
            progress_callback({'status': 'error', 'message': f"Unexpected error: {e}"})

if __name__ == "__main__":
    # Example usage when run directly
    print("This module plays and downloads music. To test, provide a YouTube video URL.")
    test_url = input("Enter a YouTube video URL to play/download: ")
    if test_url:
        action = input("Do you want to (p)lay, (d_mp3)ownload as MP3, or (d_mp4)ownload as MP4? ").strip().lower()

        def test_progress_hook(d):
            if d['status'] == 'downloading':
                p = d.get('_percent_str', 'N/A')
                s = d.get('_speed_str', 'N/A')
                e = d.get('_eta_str', 'N/A')
                print(f"Progress: {p}, Speed: {s}, ETA: {e}")
            elif d['status'] == 'finished':
                print("Done downloading, now converting ...")
            elif d['status'] == 'error':
                print(f"Error during download: {d.get('message', 'Unknown error')}")

        if action == 'p':
            player_proc = play_music(test_url)
            if player_proc:
                try:
                    player_proc.wait() # Wait for it to finish
                except KeyboardInterrupt:
                    print("\nStopping playback...")
                    player_proc.terminate()
        elif action == 'd_mp3':
            download_media(test_url, 'mp3', progress_callback=test_progress_hook)
        elif action == 'd_mp4':
            download_media(test_url, 'mp4', progress_callback=test_progress_hook)
        else:
            print("Invalid action. Exiting.")
    else:
        print("No URL provided. Exiting.")
