# main.py

import sys
import os
from youtube_search import search_youtube_music
from music_player import play_music, download_music_as_mp3 # Import new download function
from interactive_mode import get_user_choice

def main():
    """
    Main function for the YouTube Music CLI application.
    Orchestrates search, interactive selection, and playback/download.
    """
    print("Welcome to the YouTube Music CLI Player!")
    print("---------------------------------------")
    print("Note: This application requires 'yt-dlp' and 'mpv' (for playback) to be installed.")
    print("      Install yt-dlp: pip install yt-dlp")
    print("      Install mpv: (e.g., sudo apt install mpv on Debian/Ubuntu, brew install mpv on macOS)")
    print("      FFmpeg is required for MP3 conversion during download.")
    print("      Install FFmpeg: (e.g., sudo apt install ffmpeg on Debian/Ubuntu, brew install ffmpeg on macOS)")
    print("---------------------------------------")

    while True: # Main loop for search queries
        search_query = input("\nEnter your music search query (or 'q' to quit): ").strip()

        if search_query.lower() == 'q':
            print("Exiting YouTube Music CLI Player. Goodbye!")
            break

        print(f"Searching for '{search_query}'...")
        results = search_youtube_music(search_query, max_results=10) # Get up to 10 results

        if not results:
            print("No music found for your query. Please try a different search term.")
            continue

        # Nested loop to handle actions for the current search results
        while True:
            user_selection = get_user_choice(results)

            if user_selection is None:
                # User chose to quit from the selection menu, exit the entire app
                print("Exiting YouTube Music CLI Player. Goodbye!")
                sys.exit() # Exit the program immediately
            elif user_selection[0] == 'back':
                # User chose to go back to the main search prompt
                break # Break out of the inner loop, return to outer loop
            else:
                action, selected_song = user_selection
                if action == 'play':
                    print(f"\nPlaying: {selected_song['title']}")
                    play_music(selected_song['url'])
                    # After play_music finishes (or is interrupted),
                    # the inner loop continues, returning to the selection menu.
                elif action == 'download':
                    print(f"\nDownloading: {selected_song['title']}")
                    download_music_as_mp3(selected_song['url'])
                    # After download, the inner loop continues, returning to the selection menu.
                else:
                    print("Unknown action. Please try again.")

if __name__ == "__main__":
    main()
