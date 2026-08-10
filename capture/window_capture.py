"""
Window capture module for macOS using Quartz and screencapture command.
"""
import subprocess
import time
from typing import Optional, Tuple
from Quartz import (
    CGWindowListCopyWindowInfo,
    kCGWindowListOptionOnScreenOnly,
    kCGNullWindowID
)


def get_browser_window_bounds(browser_name: str) -> Optional[Tuple[int, int, int, int]]:
    """
    Find browser window bounds without activating it.

    Args:
        browser_name: Name of the browser ("Safari", "Google Chrome", "Firefox", "Microsoft Edge")

    Returns:
        Tuple of (x, y, width, height) or None if window not found
    """
    # Get list of all visible windows
    window_list = CGWindowListCopyWindowInfo(
        kCGWindowListOptionOnScreenOnly,
        kCGNullWindowID
    )

    # Search for browser window
    for window in window_list:
        window_owner = window.get('kCGWindowOwnerName', '')

        if window_owner == browser_name:
            bounds = window.get('kCGWindowBounds', {})

            if bounds:
                x = int(bounds.get('X', 0))
                y = int(bounds.get('Y', 0))
                width = int(bounds.get('Width', 0))
                height = int(bounds.get('Height', 0))

                return (x, y, width, height)

    return None


def capture_window(bounds: Tuple[int, int, int, int], output_path: str, delay_ms: int = 0) -> bool:
    """
    Capture screenshot of specified window bounds using macOS screencapture command.

    Args:
        bounds: Tuple of (x, y, width, height)
        output_path: Path where screenshot should be saved
        delay_ms: Optional delay before capture in milliseconds

    Returns:
        True if capture successful, False otherwise
    """
    if delay_ms > 0:
        time.sleep(delay_ms / 1000.0)

    x, y, width, height = bounds

    # Build screencapture command
    # -R captures specific region: x,y,width,height
    # -x disables sound
    cmd = [
        'screencapture',
        '-x',  # No sound
        '-R', f'{x},{y},{width},{height}',
        output_path
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
        print(f"Capture failed: {e}")
        return False


def capture_browser(browser_name: str, output_path: str, delay_ms: int = 0) -> bool:
    """
    Convenience function to find and capture browser window in one call.

    Args:
        browser_name: Name of the browser to capture
        output_path: Path where screenshot should be saved
        delay_ms: Optional delay before capture in milliseconds

    Returns:
        True if capture successful, False otherwise
    """
    bounds = get_browser_window_bounds(browser_name)

    if bounds is None:
        print(f"Browser window '{browser_name}' not found")
        return False

    return capture_window(bounds, output_path, delay_ms)
