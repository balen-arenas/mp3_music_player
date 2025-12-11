"""
Minimal MP3 player using python-vlc

place mp3 files in folder named "music"
Commands while playing:
    P - Pause
    R - Resume
    S - Stop and return to track list
    Q - Quit the player

Requires python-vlc package:
    pip install python-vlc
    VLC (libVLC) native library installed on your system.
"""
from pathlib import Path
import vlc
#import os
import sys

MUSIC_FOLDER = Path("music")
VALID_EXTENSIONS = {'.mp3', '.wav', '.ogg'}

def list_tracks(music_folder: Path):
    if not music_folder.exists() or not music_folder.is_dir():
        print(f"Music folder '{music_folder}' does not exist.")
        return []
    
    # Use case-insensitive suffix matching and return a sorted list
    music_files = [f for f in music_folder.iterdir() if f.suffix.lower() in VALID_EXTENSIONS]
    return sorted(music_files)

""" def play_track(file_path: Path):
    instance = vlc.Instance()
    player = instance.media_player_new()
    media = instance.media_new(str(file_path))
    player.set_media(media)

    try:
        player.play()
    except Exception as e:
        print(f"Error playing track {file_path.name}: {e}")
        return
    print(f"\nNow playing: {file_path.name}")
    print("Commands: [P]ause, [R]esume, [S]top")

    try:
        while True:
            cmd = input("> ").strip().upper()
            if cmd == 'P':
                player.pause()
                print("Music paused.")
            elif cmd == 'R':
                player.play()
                print("Music resumed.")
            elif cmd == 'S':
                player.stop()
                print("Music stopped.")
                break
            elif cmd == 'Q':
                player.stop()
                print("Exiting player.")
                sys.exit(0)
            else:
                print("Invalid command. Please use [P], [R], [S], or [Q].")
    except (KeyboardInterrupt, EOFError):
        player.stop()
        print("\nInterrupted, stopping playback.")
    finally:
        try:
            player.release()
            instance.release()
        except Exception:
            pass """

""" def music_player():
    tracks = list_tracks(MUSIC_FOLDER)
    if not tracks:
        print(f"No music files found in '{MUSIC_FOLDER}'.")
        return
    
    while True:
        print("\n**** Music Player ****")
        print("\nAvailable tracks:")
        for idx, track in enumerate(tracks, start=1):
            print(f"{idx}. {track.name}")
        choice = input("\nSelect a track number to play (or 'Q' to quit): ").strip()
        if not choice:
            continue
        if choice.upper() == 'Q':
            print("Exiting music player.")
            break
        if not choice.isdigit() or not (1 <= int(choice) <= len(tracks)):
            print("Invalid selection. Please try again.")
            continue

        track_number = int(choice) - 1
        play_track(tracks[track_number]) """

class MusicPlayer:
    """Core music player logic encapsulating python-vlc usage.

    Methods return booleans for success where appropriate so a GUI
    can react to failures.
    """

    def __init__(self):
        self.instance = None
        self.player = None
        self.current_file = None
        self.is_playing = False
        self.is_paused = False

    def initialize(self) -> bool:
        """Initialize the VLC instance and player. Returns True on success."""
        try:
            self.instance = vlc.Instance()
            self.player = self.instance.media_player_new()
            return True
        except Exception as e:
            print(f"VLC initialization error: {e}")
            self.instance = None
            self.player = None
            return False

    def load_track(self, file_path: Path) -> bool:
        """Load a media file into the player without starting playback."""
        if not self.instance or not self.player:
            return False
        try:
            media = self.instance.media_new(str(file_path))
            self.player.set_media(media)
            self.current_file = file_path
            return True
        except Exception as e:
            print(f"Error loading track {file_path}: {e}")
            return False

    def play(self) -> bool:
        """Start playback of the loaded media."""
        if not self.player:
            return False
        try:
            self.player.play()
            self.is_playing = True
            self.is_paused = False
            return True
        except Exception as e:
            print(f"Play error: {e}")
            return False

    def pause(self) -> bool:
        """Pause playback. Mark paused state but keep is_playing True if desired."""
        if not self.player:
            return False
        try:
            self.player.pause()
            self.is_paused = True
            return True
        except Exception as e:
            print(f"Pause error: {e}")
            return False

    def resume(self) -> bool:
        """Resume playback from the paused state."""
        if not self.player:
            return False
        try:
            self.player.play()
            self.is_paused = False
            return True
        except Exception as e:
            print(f"Resume error: {e}")
            return False

    def stop(self) -> bool:
        """Stop playback and reset state."""
        if not self.player:
            return False
        try:
            self.player.stop()
            self.is_playing = False
            self.is_paused = False
            return True
        except Exception as e:
            print(f"Stop error: {e}")
            return False

    def get_duration(self) -> int:
        """Return media duration in milliseconds, or -1 if unknown."""
        try:
            media = self.player.get_media()
            if media:
                return media.get_duration()
        except Exception:
            pass
        return -1

    def get_current_time(self) -> int:
        """Return current playback time in milliseconds, or -1 on error."""
        try:
            return self.player.get_time()
        except Exception:
            return -1

    def set_position(self, position: float) -> bool:
        """Seek to position between 0.0 and 1.0."""
        if not self.player:
            return False
        try:
            self.player.set_position(max(0.0, min(1.0, float(position))))
            return True
        except Exception as e:
            print(f"Seek error: {e}")
            return False

    def cleanup(self) -> None:
        """Release VLC resources cleanly."""
        try:
            if self.player:
                self.player.stop()
                self.player.release()
            if self.instance:
                self.instance.release()
        except Exception:
            pass
