# interactive_mode.py

import sys

def get_user_choice(results):
    """
    Presents search results to the user and prompts them to select a song
    to play or download, or to go back.

    Args:
        results (list): A list of dictionaries, where each dictionary represents
                        a video and contains 'title', 'id', and 'url'.

    Returns:
        tuple or None: A tuple (action, selected_video_dict) if a valid choice is made.
                       'action' can be 'play', 'download', or 'back'.
                       'selected_video_dict' is the chosen video dictionary or None.
                       Returns None if the user quits.
    """
    if not results:
        print("No search results to display.")
        return None

    print("\n--- Search Results ---")
    for i, result in enumerate(results):
        # Displaying only the title for cleaner output in interactive mode
        print(f"{i + 1}. {result['title']}")
    print("----------------------")

    while True:
        try:
            choice_input = input("Enter the number of the song to (p)lay or (d)ownload, 'b' to go back, or 'q' to quit: ").strip().lower()

            if choice_input == 'q':
                print("Exiting interactive mode.")
                return None # User wants to quit the entire application
            elif choice_input == 'b':
                print("Going back to main menu.")
                return ('back', None) # User wants to go back to the search prompt

            # Check if the input is a number followed by 'p' or 'd'
            if len(choice_input) > 1 and (choice_input.endswith('p') or choice_input.endswith('d')):
                action = choice_input[-1] # 'p' or 'd'
                num_str = choice_input[:-1] # The number part
            else:
                # Assume default action is play if only a number is entered
                action = 'p'
                num_str = choice_input

            choice = int(num_str)
            if 1 <= choice <= len(results):
                selected_song = results[choice - 1] # Get the selected result (0-indexed)
                if action == 'p':
                    return ('play', selected_song)
                elif action == 'd':
                    return ('download', selected_song)
                else:
                    print("Invalid action specified. Please use 'p' for play or 'd' for download.")
            else:
                print("Invalid choice. Please enter a number within the range, or 'b'/'q'.")
        except ValueError:
            print("Invalid input. Please enter a number followed by 'p' or 'd', 'b' to go back, or 'q' to quit.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None # Exit on unexpected error
