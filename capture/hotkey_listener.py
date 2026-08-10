"""
Global hotkey listener module using pynput.
"""
from typing import Callable, Dict
from pynput import keyboard
import threading


class HotkeyManager:
    """Manages global hotkey registration and callbacks."""

    def __init__(self):
        self.hotkeys: Dict[str, Callable] = {}
        self.listener = None
        self._stop_event = threading.Event()

    def register(self, hotkey: str, callback: Callable) -> None:
        """
        Register a global hotkey with a callback function.

        Args:
            hotkey: Hotkey string (e.g., "<cmd>+<shift>+<f1>")
            callback: Function to call when hotkey is pressed
        """
        self.hotkeys[hotkey] = callback

    def start(self) -> None:
        """Start listening for registered hotkeys in background thread."""
        if self.listener is not None:
            return  # Already running

        # Create global hotkey listener
        self.listener = keyboard.GlobalHotKeys(self.hotkeys)
        self.listener.start()

    def stop(self) -> None:
        """Stop listening for hotkeys and cleanup."""
        if self.listener is not None:
            self.listener.stop()
            self.listener = None
            self._stop_event.set()

    def wait(self) -> None:
        """Block until stop() is called."""
        self._stop_event.wait()

    def is_running(self) -> bool:
        """Check if listener is currently active."""
        return self.listener is not None and self.listener.running
