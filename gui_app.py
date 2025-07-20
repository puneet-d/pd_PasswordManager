# gui_app.py

import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
import os
import sys
import subprocess # Added for dependency check

# Assume youtube_search.py and music_player.py are in the same directory
from youtube_search import search_youtube_music
from music_player import play_music, download_media

class MusicAppGUI:
    def __init__(self, master):
        self.master = master
        master.title("YouTube Music Player")
        master.geometry("800x600") # Set a default window size
        master.resizable(True, True) # Allow resizing

        self.current_results = []
        self.playing_thread = None
        self.downloading_thread = None
        self.download_progress_var = tk.StringVar() # To display download progress
        self.mpv_process = None # To store the MPV subprocess

        # --- Styling ---
        self.master.tk_setPalette(background='#e0f7fa', foreground='#004d40',
                                  activeBackground='#b2ebf2', activeForeground='#004d40')
        self.font_large = ("Inter", 12)
        self.font_medium = ("Inter", 10)
        self.button_bg = '#00796b'
        self.button_fg = 'white'
        self.entry_bg = '#ffffff'
        self.listbox_bg = '#ffffff'
        self.listbox_fg = '#212121'

        # --- Search Frame ---
        self.search_frame = tk.Frame(master, padx=10, pady=10, bg='#e0f7fa')
        self.search_frame.pack(fill=tk.X)

        self.search_label = tk.Label(self.search_frame, text="Search Music:", font=self.font_large, bg='#e0f7fa', fg='#004d40')
        self.search_label.pack(side=tk.LEFT, padx=(0, 10))

        self.search_entry = tk.Entry(self.search_frame, width=50, font=self.font_medium, bg=self.entry_bg, fg='#212121', relief=tk.FLAT)
        self.search_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.search_entry.bind("<Return>", self.perform_search_event) # Bind Enter key

        self.search_button = tk.Button(self.search_frame, text="Search", command=self.perform_search,
                                       font=self.font_medium, bg=self.button_bg, fg=self.button_fg,
                                       activebackground='#004d40', activeforeground='white', relief=tk.RAISED, bd=2)
        self.search_button.pack(side=tk.LEFT, padx=(10, 0))

        # --- Results Frame ---
        self.results_frame = tk.Frame(master, padx=10, pady=5, bg='#e0f7fa')
        self.results_frame.pack(fill=tk.BOTH, expand=True)

        self.results_label = tk.Label(self.results_frame, text="Search Results:", font=self.font_large, bg='#e0f7fa', fg='#004d40')
        self.results_label.pack(anchor=tk.NW, pady=(0, 5))

        self.listbox_frame = tk.Frame(self.results_frame)
        self.listbox_frame.pack(fill=tk.BOTH, expand=True)

        self.results_listbox = tk.Listbox(self.listbox_frame, font=self.font_medium, bg=self.listbox_bg, fg=self.listbox_fg,
                                          selectbackground='#b2ebf2', selectforeground='#004d40', relief=tk.FLAT, bd=2,
                                          exportselection=False) # Important for single selection
        self.results_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(self.listbox_frame, orient="vertical", command=self.results_listbox.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_listbox.config(yscrollcommand=self.scrollbar.set)

        # --- Control Buttons Frame ---
        self.control_frame = tk.Frame(master, padx=10, pady=10, bg='#e0f7fa')
        self.control_frame.pack(fill=tk.X)

        # Play Audio button
        self.play_button = tk.Button(self.control_frame, text="Play Audio", command=self.play_selected,
                                     font=self.font_medium, bg=self.button_bg, fg=self.button_fg,
                                     activebackground='#004d40', activeforeground='white', relief=tk.RAISED, bd=2)
        self.play_button.pack(side=tk.LEFT, expand=True, padx=5)

        # Stop Playback button (NEW)
        self.stop_button = tk.Button(self.control_frame, text="Stop Playback", command=self.stop_playback,
                                     font=self.font_medium, bg='#ff5722', fg='white', # Orange color for stop
                                     activebackground='#bf360c', activeforeground='white', relief=tk.RAISED, bd=2)
        self.stop_button.pack(side=tk.LEFT, expand=True, padx=5)
        self.stop_button.config(state=tk.DISABLED) # Initially disabled

        # Download MP3 button
        self.download_mp3_button = tk.Button(self.control_frame, text="Download MP3", command=lambda: self.download_selected_format('mp3'),
                                         font=self.font_medium, bg=self.button_bg, fg=self.button_fg,
                                         activebackground='#004d40', activeforeground='white', relief=tk.RAISED, bd=2)
        self.download_mp3_button.pack(side=tk.LEFT, expand=True, padx=5)

        # Download MP4 button
        self.download_mp4_button = tk.Button(self.control_frame, text="Download MP4", command=lambda: self.download_selected_format('mp4'),
                                         font=self.font_medium, bg=self.button_bg, fg=self.button_fg,
                                         activebackground='#004d40', activeforeground='white', relief=tk.RAISED, bd=2)
        self.download_mp4_button.pack(side=tk.LEFT, expand=True, padx=5)


        self.clear_button = tk.Button(self.control_frame, text="Clear Results", command=self.clear_results,
                                      font=self.font_medium, bg='#d32f2f', fg='white',
                                      activebackground='#b71c1c', activeforeground='white', relief=tk.RAISED, bd=2)
        self.clear_button.pack(side=tk.LEFT, expand=True, padx=5)

        # --- Status Bar ---
        self.status_label = tk.Label(master, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W, font=("Inter", 9), bg='#e0f7fa', fg='#004d40')
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

        # --- Download Progress Label (new) ---
        self.download_progress_label = tk.Label(master, textvariable=self.download_progress_var, bd=1, relief=tk.FLAT, anchor=tk.W, font=("Inter", 9), bg='#e0f7fa', fg='#004d40')
        self.download_progress_label.pack(side=tk.BOTTOM, fill=tk.X)
        self.download_progress_var.set("") # Initialize with empty text

        # Initial instructions
        self.update_status("Enter a search query and press Search or Enter.")

    def update_status(self, message):
        """Updates the status bar with a given message."""
        self.status_label.config(text=message)
        self.master.update_idletasks() # Ensure the message is displayed immediately

    def perform_search_event(self, event):
        """Event handler for Enter key press in search entry."""
        self.perform_search()

    def perform_search(self):
        """Performs a YouTube music search and displays results."""
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showwarning("Input Error", "Please enter a search query.")
            return

        self.update_status(f"Searching for '{query}'...")
        self._set_buttons_state(tk.DISABLED) # Disable all action buttons during search
        self.download_progress_var.set("") # Clear any previous download progress

        # Run search in a separate thread to keep GUI responsive
        threading.Thread(target=self._search_thread, args=(query,)).start()

    def _search_thread(self, query):
        """Threaded function to perform the search."""
        try:
            # Set max_results to 20 as requested
            results = search_youtube_music(query, max_results=20)
            self.master.after(0, self._display_results, results) # Update GUI on main thread
        except Exception as e:
            self.master.after(0, lambda: messagebox.showerror("Search Error", f"An error occurred during search: {e}"))
            self.master.after(0, lambda: self.update_status("Search failed."))
        finally:
            self.master.after(0, lambda: self._set_buttons_state(tk.NORMAL)) # Re-enable buttons


    def _display_results(self, results):
        """Displays search results in the listbox."""
        self.results_listbox.delete(0, tk.END) # Clear previous results
        self.current_results = results

        if not results:
            self.results_listbox.insert(tk.END, "No results found.")
            self.update_status("No results found.")
            return

        for i, result in enumerate(results):
            self.results_listbox.insert(tk.END, f"{i+1}. {result['title']}")
        self.update_status(f"Found {len(results)} results. Select a song to play or download.")

    def get_selected_song(self):
        """Helper to get the selected song's data."""
        selected_indices = self.results_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Selection Error", "Please select a song from the list.")
            return None
        selected_index = selected_indices[0]
        return self.current_results[selected_index]

    def _set_buttons_state(self, state):
        """Helper to set the state of control buttons."""
        self.search_button.config(state=state)
        self.play_button.config(state=state)
        self.download_mp3_button.config(state=state)
        self.download_mp4_button.config(state=state)
        self.clear_button.config(state=state)
        # Manage stop button state separately
        if state == tk.DISABLED:
            self.stop_button.config(state=tk.DISABLED)
        else:
            # Only enable stop button if a playing thread is active
            if self.playing_thread and self.playing_thread.is_alive():
                self.stop_button.config(state=tk.NORMAL)
            else:
                self.stop_button.config(state=tk.DISABLED)


    def play_selected(self):
        """Plays the selected song (audio only)."""
        selected_song = self.get_selected_song()
        if not selected_song:
            return

        if self.playing_thread and self.playing_thread.is_alive():
            messagebox.showinfo("Playback Info", "A song is already playing. Please wait or stop the current playback manually (e.g., by closing mpv window).")
            return

        self.update_status(f"Playing audio: {selected_song['title']}...")
        self._set_buttons_state(tk.DISABLED) # Disable all action buttons during playback
        self.download_progress_var.set("") # Clear any previous download progress
        self.stop_button.config(state=tk.NORMAL) # Enable stop button

        # Play in a separate thread
        self.playing_thread = threading.Thread(target=self._play_thread, args=(selected_song['url'],))
        self.playing_thread.start()

    def _play_thread(self, url):
        """Threaded function to play music."""
        try:
            self.mpv_process = play_music(url) # Store the MPV process
            if self.mpv_process:
                self.mpv_process.wait() # Wait for MPV to finish
        except Exception as e:
            self.master.after(0, lambda: messagebox.showerror("Playback Error", f"An error occurred during playback: {e}"))
        finally:
            self.mpv_process = None # Clear the process reference
            self.master.after(0, lambda: self._set_buttons_state(tk.NORMAL)) # Re-enable buttons
            self.master.after(0, lambda: self.update_status("Playback finished or stopped."))

    def stop_playback(self):
        """Stops the currently playing MPV process."""
        if self.mpv_process and self.mpv_process.poll() is None: # Check if process is running
            self.update_status("Stopping playback...")
            self.mpv_process.terminate() # Request termination
            self.mpv_process = None # Clear the process reference immediately
            # The _play_thread's finally block will handle re-enabling buttons and status update
        else:
            messagebox.showinfo("Playback Info", "No song is currently playing.")


    def download_selected_format(self, format_type):
        """Downloads the selected song in the specified format (MP3 or MP4)."""
        selected_song = self.get_selected_song()
        if not selected_song:
            return

        if self.downloading_thread and self.downloading_thread.is_alive():
            messagebox.showinfo("Download Info", "A download is already in progress. Please wait.")
            return

        self.update_status(f"Downloading {format_type}: {selected_song['title']}...")
        self.download_progress_var.set("Initializing download...")
        self._set_buttons_state(tk.DISABLED) # Disable all action buttons during download

        # Download in a separate thread, passing the progress callback
        self.downloading_thread = threading.Thread(target=self._download_thread, args=(selected_song['url'], format_type, self._download_progress_hook))
        self.downloading_thread.start()

    def _download_thread(self, url, format_type, progress_callback):
        """Threaded function to download media."""
        try:
            download_media(url, format_type, progress_callback=progress_callback)
            self.master.after(0, lambda: self.update_status(f"Download complete! Check 'downloads' folder for {format_type} file."))
        except Exception as e:
            self.master.after(0, lambda: messagebox.showerror("Download Error", f"An error occurred during download: {e}"))
            self.master.after(0, lambda: self.update_status("Download failed."))
        finally:
            self.master.after(0, lambda: self._set_buttons_state(tk.NORMAL)) # Re-enable buttons
            self.master.after(0, lambda: self.download_progress_var.set("")) # Clear progress text

    def _download_progress_hook(self, d):
        """
        Callback function for yt-dlp download progress.
        Updates the GUI's download progress label.
        """
        if d['status'] == 'downloading':
            p = d.get('_percent_str', 'N/A')
            s = d.get('_speed_str', 'N/A')
            e = d.get('_eta_str', 'N/A')
            message = f"Downloading: {p} at {s} (ETA: {e})"
            self.master.after(0, lambda: self.download_progress_var.set(message))
        elif d['status'] == 'finished':
            self.master.after(0, lambda: self.download_progress_var.set("Processing download..."))
        elif d['status'] == 'error':
            error_msg = d.get('message', 'Unknown download error')
            self.master.after(0, lambda: self.download_progress_var.set(f"Download error: {error_msg}"))


    def clear_results(self):
        """Clears the search results listbox."""
        self.results_listbox.delete(0, tk.END)
        self.current_results = []
        self.update_status("Results cleared. Ready for new search.")
        self.download_progress_var.set("") # Clear progress text

if __name__ == "__main__":
    # Check for mpv and ffmpeg installation (basic check)
    def check_dependency(command, name):
        try:
            subprocess.run([command, '--version'], check=True, capture_output=True, timeout=5) # Added timeout
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False

    # This check will only run if gui_app.py is executed directly
    # It's a basic check and might not catch all installation issues.
    # Full error handling for mpv/ffmpeg is in music_player.py
    if not check_dependency('mpv', 'MPV'):
        messagebox.showwarning("Dependency Warning", "MPV player not found. Playback functionality may not work.\n"
                               "Please install MPV (e.g., 'sudo apt install mpv' or 'brew install mpv').")
    if not check_dependency('ffmpeg', 'FFmpeg'):
        messagebox.showwarning("Dependency Warning", "FFmpeg not found. MP3/MP4 download conversion may not work.\n"
                               "Please install FFmpeg (e.g., 'sudo apt install ffmpeg' or 'brew install ffmpeg').")

    root = tk.Tk()
    app = MusicAppGUI(root)
    root.mainloop()
