# youtube_search.py

import yt_dlp

def search_youtube_music(query, max_results=5):
    """
    Searches YouTube for music based on the given query and returns a list of results.

    Args:
        query (str): The search term for music.
        max_results (int): The maximum number of search results to return.

    Returns:
        list: A list of dictionaries, where each dictionary represents a video
              and contains 'title', 'id', and 'url'. Returns an empty list
              if no results are found or an error occurs.
    """
    ydl_opts = {
        'format': 'bestaudio/best',  # Prefer audio-only streams
        'quiet': True,               # Suppress console output
        'extract_flat': True,        # Only extract basic information without downloading
        'force_generic_extractor': True, # Force generic extractor for search
        'default_search': 'ytsearch', # Default to YouTube search
        'noplaylist': True,          # Do not extract playlist information
    }

    search_results = []
    try:
        # Use yt_dlp to search for videos. The query is prepended with 'ytsearch'
        # to ensure it performs a YouTube search.
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # The 'entries' key contains the list of search results.
            # We limit the search to max_results.
            info = ydl.extract_info(f"ytsearch{max_results}:{query}", download=False)
            if 'entries' in info:
                for entry in info['entries']:
                    if entry: # Ensure entry is not None
                        search_results.append({
                            'title': entry.get('title', 'Unknown Title'),
                            'id': entry.get('id', 'Unknown ID'),
                            'url': f"https://www.youtube.com/watch?v={entry.get('id')}"
                        })
    except Exception as e:
        print(f"Error during YouTube search: {e}")
    return search_results

if __name__ == "__main__":
    # Example usage when run directly
    search_term = input("Enter music to search: ")
    results = search_youtube_music(search_term, max_results=5)

    if results:
        print("\nSearch Results:")
        for i, result in enumerate(results):
            print(f"{i+1}. Title: {result['title']}")
            print(f"   URL: {result['url']}")
        print("\nNote: This module only performs searches. Use main.py to play music.")
    else:
        print("No results found or an error occurred.")
