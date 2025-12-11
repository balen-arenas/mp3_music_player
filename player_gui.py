"""
Player GUI for the music player application.

This module creates a simple Tkinter GUI and uses the player logic
from `player.py` (the `MusicPlayer` class and `list_tracks` function).
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import threading
import time
from player import MusicPlayer, list_tracks


class MusicPlayerGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Music Player")
        self.root.geometry("420x420")

        # Initialize player
        self.player = MusicPlayer()
        if not self.player.initialize():
            messagebox.showerror("Error", "Failed to initialize VLC player.")
            root.destroy()
            return

        # Load tracks from the local music folder
        self.tracks = list_tracks(Path("music"))

        # Threading control
        self.running = True
        self.is_slider_dragging = False

        # Create the UI
        self._create_widgets()

        # Start background update thread for time display
        self.update_thread = threading.Thread(target=self._update_time_display, daemon=True)
        self.update_thread.start()

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _create_widgets(self):
        """Create and layout GUI widgets."""
        frame = ttk.Frame(self.root, padding=8)
        frame.pack(fill=tk.BOTH, expand=True)

        lbl = ttk.Label(frame, text="Playlist", font=(None, 11, 'bold'))
        lbl.pack(anchor=tk.W)

        self.track_listbox = tk.Listbox(frame, height=12)
        self.track_listbox.pack(fill=tk.BOTH, expand=True, pady=6)
        for track in self.tracks:
            self.track_listbox.insert(tk.END, track.name)

        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=6)

        self.play_button = ttk.Button(btn_frame, text="Play", command=self.on_play)
        self.play_button.pack(side=tk.LEFT, padx=4)

        self.pause_button = ttk.Button(btn_frame, text="Pause", command=self.on_pause)
        self.pause_button.pack(side=tk.LEFT, padx=4)

        self.resume_button = ttk.Button(btn_frame, text="Resume", command=self.on_resume)
        self.resume_button.pack(side=tk.LEFT, padx=4)

        self.stop_button = ttk.Button(btn_frame, text="Stop", command=self.on_stop)
        self.stop_button.pack(side=tk.LEFT, padx=4)

        # Now playing label
        self.now_playing_label = ttk.Label(frame, text="Now Playing: None")
        self.now_playing_label.pack(anchor=tk.W, pady=(4, 0))

        # Time display
        self.time_label = ttk.Label(frame, text="00:00 / 00:00")
        self.time_label.pack(anchor=tk.W, pady=(2, 4))

        # Progress slider
        self.progress_var = tk.DoubleVar(value=0.0)
        self.progress_scale = ttk.Scale(
            frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.progress_var,
            command=self._on_slider_move,
            length=360,
        )
        self.progress_scale.pack(fill=tk.X, pady=(0, 8))

    def on_play(self):
        sel = self.track_listbox.curselection()
        if not sel:
            messagebox.showinfo("Info", "Please select a track to play.")
            return
        idx = sel[0]
        track = self.tracks[idx]
        ok = self.player.load_track(track)
        if not ok:
            messagebox.showerror("Error", f"Failed to load track: {track}")
            return
        if not self.player.play():
            messagebox.showerror("Error", "Failed to start playback.")
            return
        self.now_playing_label.config(text=f"Now Playing: {track.name}")
        self.progress_var.set(0)
        self.time_label.config(text="00:00 / 00:00")

    def on_pause(self):
        if not self.player.pause():
            messagebox.showerror("Error", "Failed to pause playback.")
            return
        self.now_playing_label.config(text="Paused")

    def on_resume(self):
        if not self.player.resume():
            messagebox.showerror("Error", "Failed to resume playback.")
            return
        self.now_playing_label.config(text=f"Now Playing: {self.player.current_file.name}")

    def on_stop(self):
        if not self.player.stop():
            messagebox.showerror("Error", "Failed to stop playback.")
            return
        self.now_playing_label.config(text="Stopped")
        self.progress_var.set(0)
        self.time_label.config(text="00:00 / 00:00")

    def _on_slider_move(self, value):
        """Seek in the track when the user moves the slider."""
        if self.is_slider_dragging:
            return
        self.is_slider_dragging = True
        try:
            position = float(value) / 100.0
            self.player.set_position(position)
        finally:
            self.is_slider_dragging = False

    def _apply_progress(self, current_ms: int, duration_ms: int):
        """Update UI elements from the main thread."""
        if duration_ms and duration_ms > 0:
            progress = max(0.0, min(100.0, (current_ms / duration_ms) * 100))
            self.progress_var.set(progress)
            self.time_label.config(
                text=f"{self._format_time(current_ms)} / {self._format_time(duration_ms)}"
            )
        else:
            # Unknown duration
            self.progress_var.set(0)
            self.time_label.config(text="--:-- / --:--")

    def _format_time(self, milliseconds: int) -> str:
        if milliseconds is None or milliseconds < 0:
            return "--:--"
        seconds = int(milliseconds // 1000)
        minutes, seconds = divmod(seconds, 60)
        return f"{minutes:02d}:{seconds:02d}"

    def _update_time_display(self):
        """Background thread: poll player time/duration and schedule UI updates."""
        while self.running:
            try:
                if self.player.is_playing and not self.is_slider_dragging:
                    duration = self.player.get_duration()
                    current = self.player.get_current_time()
                    # Schedule UI update on the main thread
                    self.root.after(0, self._apply_progress, current, duration)
            except Exception:
                pass
            time.sleep(0.1)

    def _on_closing(self):
        """Handle window close: stop thread, cleanup player, and close UI."""
        self.running = False
        try:
            self.player.stop()
            self.player.cleanup()
        except Exception:
            pass
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = MusicPlayerGUI(root)
    root.mainloop()