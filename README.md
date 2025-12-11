# Music Player (Minimal)

A small Python music player that uses `python-vlc` for audio playback and a simple Tkinter GUI.

This repository contains two main modules:

- `player.py` — core playback logic using python-vlc
- `player_gui.py` — a Tkinter-based graphical frontend that uses `player.py`

This README documents each class and method in both files and provides usage, troubleshooting, and extension notes.

---

## Requirements

- Python 3.8+ (tested with 3.10+)
- `python-vlc` Python package (listed in `requirements.txt`)
- VLC (libVLC) native library installed on the system. On Windows, install the VLC application from https://www.videolan.org/; on Linux install the `vlc` or `libvlc` package; on macOS install VLC.app or libVLC via Homebrew.
- `tkinter` (standard library GUI toolkit). Most Python installers include `tkinter` by default.

Install the Python dependency with:

```powershell
pip install -r requirements.txt
```

Make sure the VLC runtime (libvlc) is installed and that `python-vlc` can locate it. If playback fails, check that VLC is installed and available in PATH or known library locations.

---

## Running the GUI

From the project folder:

```powershell
python player_gui.py
```

The GUI presents a playlist (tracks are discovered from the `music` folder), buttons to Play / Pause / Resume / Stop, and a progress slider with time display (seekable).

---

## File: `player.py` — Overview

This file contains the core playback logic and a helper for discovering music files.
It is intentionally UI-agnostic so different interfaces (CLI, GUI, web) can reuse it.

Symbols exported / relevant to other modules:

- `MUSIC_FOLDER` — default `Path('music')` used as the default music folder.
- `VALID_EXTENSIONS` — set of file suffixes considered music files (lowercased in the discovery function).
- `list_tracks(music_folder: Path)` — returns a sorted list of `Path` objects for files in the folder whose suffix (case-insensitive) is in `VALID_EXTENSIONS`.

### Function: list_tracks(music_folder: Path)
- Purpose: Scan a `Path` directory and return a sorted list of files with audio extensions (`.mp3`, `.wav`, `.ogg`).
- Returns: `List[Path]` (empty list if the folder doesn't exist or no files matched).
- Notes: Uses `f.suffix.lower()` so uppercase extensions (e.g., `.MP3`) are recognized.

### Class: MusicPlayer

A thin wrapper around `python-vlc`'s libVLC to provide a clean, boolean-returning API useful for GUIs.

Attributes:
- `instance` — the `vlc.Instance()` object (or `None` if not initialized)
- `player` — the libVLC media player object (or `None`)
- `current_file` — the `Path` of the currently loaded file (or `None`)
- `is_playing` — boolean flag indicating playback state (set by `play()` and `stop()`)
- `is_paused` — boolean flag indicating paused state (set by `pause()` and `play()`)

Methods (concise behavior description):

- `initialize() -> bool`
  - Initializes libVLC and creates a media player instance.
  - Returns `True` when successful, otherwise prints an error and returns `False`.
  - Use this at application startup before attempting to load or play media.

- `load_track(file_path: Path) -> bool`
  - Loads the specified file into the media player but does not start playback.
  - Returns `True` on success, `False` if loading failed or if the player isn't initialized.
  - Sets `self.current_file` to the passed `Path` on success.

- `play() -> bool`
  - Starts playback of the currently loaded media.
  - Returns `True` if playback started, `False` on error (e.g., no media loaded).
  - Sets `is_playing = True` and `is_paused = False` on success.

- `pause() -> bool`
  - Pauses playback. Returns `True` on success, `False` on error.
  - Sets `is_paused = True` on success. (Note: libVLC toggles pause/unpause — the wrapper treats this as a pause action.)

- `resume() -> bool`
  - Resumes playback from the paused state, continuing from where it was paused.
  - Returns `True` on success, `False` on error.
  - Sets `is_paused = False` on success.

- `stop() -> bool`:
  - Stops playback and resets state flags.
  - Returns `True` on success.
  - Sets `is_playing = False` and `is_paused = False`.

- `get_duration() -> int`
  - Returns media duration in milliseconds, or `-1` if the duration is unknown or an error occurred.
  - Note: libVLC may return `-1` until the media is parsed. GUIs should handle `-1` by retrying or by showing `--:--`.

- `get_current_time() -> int`
  - Returns current playback time in milliseconds, or `-1` on error.

- `set_position(position: float) -> bool`
  - Seeks to a relative position in the track (a float from `0.0` to `1.0`).
  - Returns `True` on success, `False` on error.

- `cleanup() -> None`
  - Stops playback and releases libVLC resources. Call this before program exit to clean up native resources.

Design notes / behavior
- Methods return booleans so UI code can show messages or dialogs on failure.
- The wrapper is minimal; advanced behaviors (volume control, events, playlists) can be added later.

---

## File: `player_gui.py` — Overview

A small Tkinter GUI that uses `MusicPlayer` from `player.py`. It provides a playlist listbox, Play/Pause/Resume/Stop buttons, and a seekable progress slider with live time display.

### Class: MusicPlayerGUI

Constructor: `MusicPlayerGUI(root: tk.Tk)`
- Creates the GUI in the provided Tk root window.
- Calls `MusicPlayer().initialize()`; if initialization fails, the GUI shows an error and exits.
- Loads tracks using `list_tracks(Path('music'))` and populates the playlist listbox.

Widgets created and their responsibilities:
- `Listbox` (playlist)
  - Displays `track.name` for each track returned by `list_tracks()`.
  - User selects a track and presses Play to start playback.

- Buttons (Play / Pause / Resume / Stop)
  - `Play` → `on_play()`
    - Validates that a selection exists.
    - Calls `player.load_track(track)` then `player.play()`.
    - Updates the "Now Playing" label on success.
  - `Pause` → `on_pause()`
    - Calls `player.pause()` and updates label to "Paused" on success.
  - `Resume` → `on_resume()`
    - Calls `player.resume()` to continue playback from the paused position.
    - Updates label with the current track name on success.
  - `Stop` → `on_stop()`
    - Calls `player.stop()` and updates label to "Stopped" on success.

- `progress_scale` (seekable slider) and `time_label`
  - Shows elapsed/total time (MM:SS / MM:SS) updated from a background thread.
  - Slider movement seeks via `set_position` (0–100 → 0.0–1.0 position).

- `now_playing_label`
  - Displays the current state: e.g. "Now Playing: song.mp3", "Paused", or "Stopped".

Important callbacks / methods in `player_gui.py`:
- `on_play()`
  - Ensures a track is selected, loads the track via `MusicPlayer.load_track()`, and starts playback via `MusicPlayer.play()`.
  - Shows errors via `tkinter.messagebox` if loading or playback fails.

- `on_pause()`
  - Calls `MusicPlayer.pause()` and updates label to "Paused" on success.
  - Displays an error dialog if the call fails.

- `on_resume()`
  - Calls `MusicPlayer.resume()` to continue playback from the paused position.
  - Updates the label with the current track name on success.
  - Displays an error dialog if the call fails.

- `on_stop()`
  - Calls `MusicPlayer.stop()`; displays an error dialog if the call fails.

- `_on_slider_move()`
  - Seeks the track when the user drags the slider; maps 0–100 to 0.0–1.0 position.

- `_update_time_display()`
  - Background thread that polls `get_current_time()` / `get_duration()` and schedules UI updates (`_apply_progress`) via `root.after`.

- `_apply_progress()` / `_format_time()`
  - Update the slider and time label safely on the main thread and format times as `MM:SS`.

- `_on_closing()`
  - Stops the background thread, calls `player.stop()` and `player.cleanup()`, and closes the window.

Notes about this GUI
- The GUI is intentionally simple but now includes a seekable progress slider and live time display driven by a background thread (`_update_time_display` + `root.after`).
- The background thread is marked daemon and is stopped on close; cleanup calls `player.stop()` and `player.cleanup()`.
- The GUI assumes `player.initialize()` succeeds. If not, it shows an error and exits.

---

## What this project should do (overview)

The intended behavior of this project is:

1. Discover audio files placed in the `music` directory (supported formats: `.mp3`, `.wav`, `.ogg`).
2. Start a GUI window that lists discovered tracks.
3. Let the user select a track and control playback using Play, Pause, and Stop buttons.
4. Use `python-vlc` (libVLC) for reliable cross-platform playback, while keeping the UI code independent of playback details.

The architecture is deliberately modular: `player.py` contains only playback logic, while `player_gui.py` contains presentation and user interaction. This separation makes it straightforward to swap the GUI (e.g., to PyQt, web UI, or CLI) without changing the playback core.

---

## Troubleshooting

- "No tracks found": Ensure there is a `music` folder in the project root and it contains files with supported extensions. File extensions are matched case-insensitively.
- "Failed to initialize VLC": Make sure the VLC native runtime (libVLC) is installed and accessible. On Windows, the regular VLC installer is usually sufficient. If `python-vlc` can't find libVLC, you may need to set environment variables or install the correct package for your platform.
- "Duration shows -1" or progress not updating: libVLC may not have parsed the media information yet. You can call `media.parse()` or poll `get_duration()` until a valid duration (>0) is returned.

---

## Next steps / Recommended enhancements

- Add volume controls and mute.
- Add playlist controls (Next / Previous / Repeat / Shuffle).
- Add drag-and-drop support to add files/folders at runtime.
- Improve error reporting and logging (replace `print()` calls with Python `logging`).
- Add media parsing to ensure duration is known before showing progress (e.g., call `media.parse()` or wait for parsed events).

---

## License

No license is included. If you want to publish this project, consider adding a `LICENSE` file (e.g., MIT).
