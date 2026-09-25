import argparse
import ctypes
import os
import random
import sys
import time
from pathlib import Path
from typing import Optional, Tuple


def _get_symbols() -> Tuple[str, str, str]:
    """Return platform-safe symbols based on terminal encoding support."""
    try:
        encoding = sys.stdout.encoding or "utf-8"
        "👻✅❌".encode(encoding)
        return ("👻", "✅", "❌")
    except (UnicodeEncodeError, AttributeError):
        return ("[GHOST]", "[OK]", "[ERROR]")


ICON_GHOST, ICON_OK, ICON_ERR = _get_symbols()


def get_clipboard_text() -> str:
    """Read plain text from clipboard without external dependencies."""
    if os.name == "nt":
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        CF_UNICODETEXT = 13

        if not user32.OpenClipboard(None):
            return ""
        try:
            handle = user32.GetClipboardData(CF_UNICODETEXT)
            if not handle:
                return ""
            p_text = kernel32.GlobalLock(handle)
            if not p_text:
                return ""
            text = ctypes.wstring_at(p_text)
            kernel32.GlobalUnlock(handle)
            return text
        finally:
            user32.CloseClipboard()
    else:
        # Fallback for macOS / Linux using pbpaste or xclip
        import subprocess
        for cmd in (["pbpaste"], ["xclip", "-selection", "clipboard", "-o"]):
            try:
                res = subprocess.run(cmd, capture_output=True, text=True, check=True)
                return res.stdout
            except Exception:
                continue
        return ""


def _send_char_windows(char: str) -> None:
    """Send a single character via Windows SendInput API (supports Unicode & Umlauts)."""
    user32 = ctypes.windll.user32

    class KEYBDINPUT(ctypes.Structure):
        _fields_ = [
            ("wVk", ctypes.c_ushort),
            ("wScan", ctypes.c_ushort),
            ("dwFlags", ctypes.c_ulong),
            ("time", ctypes.c_ulong),
            ("dwExtraInfo", ctypes.c_void_p),
        ]

    class INPUT(ctypes.Structure):
        class _I(ctypes.Union):
            _fields_ = [("ki", KEYBDINPUT)]
        _anonymous_ = ("_i",)
        _fields_ = [("type", ctypes.c_ulong), ("_i", _I)]

    KEYEVENTF_KEYUP = 0x0002
    KEYEVENTF_UNICODE = 0x0004
    INPUT_KEYBOARD = 1
    VK_RETURN = 0x0D
    VK_BACK = 0x08

    if char == "\r":
        return  # Ignore carriage returns, handle \n
    elif char == "\n":
        inp_down = INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(wVk=VK_RETURN, dwFlags=0))
        inp_up = INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(wVk=VK_RETURN, dwFlags=KEYEVENTF_KEYUP))
    elif char == "\b":
        inp_down = INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(wVk=VK_BACK, dwFlags=0))
        inp_up = INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(wVk=VK_BACK, dwFlags=KEYEVENTF_KEYUP))
    else:
        scan = ord(char)
        inp_down = INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(wVk=0, wScan=scan, dwFlags=KEYEVENTF_UNICODE))
        inp_up = INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(wVk=0, wScan=scan, dwFlags=KEYEVENTF_UNICODE | KEYEVENTF_KEYUP))

    user32.SendInput(1, ctypes.byref(inp_down), ctypes.sizeof(INPUT))
    user32.SendInput(1, ctypes.byref(inp_up), ctypes.sizeof(INPUT))


def type_text(
    text: str,
    speed_wpm: int = 55,
    simulate_typos: bool = True,
    delay_start: int = 5,
) -> None:
    """
    Type out text with human rhythm, pauses, and optional realistic typos.
    
    Args:
        text: The text string to simulate typing.
        speed_wpm: Approximate words per minute (default 55).
        simulate_typos: Whether to simulate human typos and corrections.
        delay_start: Seconds to wait before starting typing (to switch windows).
    """
    if not text:
        print(f"{ICON_ERR} [Ghostwriter] No text provided to type.")
        return

    print(f"\n{ICON_GHOST} [Ghostwriter] Get ready! Switch to your target document now.")
    for i in range(delay_start, 0, -1):
        print(f"  Starting in {i}...", end="\r", flush=True)
        time.sleep(1)
    print("  Typing in progress... (Keep target window focused!)              \n")

    # Base delay per character from WPM (5 chars per word average)
    char_delay = 60.0 / (max(10, speed_wpm) * 5.0)

    try:
        for i, char in enumerate(text):
            # 1. Occasional realistic typo (approx 2% chance on alphabet letters)
            if simulate_typos and char.isalpha() and random.random() < 0.02:
                # Type an adjacent character
                fake_offset = random.choice([-1, 1])
                fake_char = chr(ord(char) + fake_offset)
                if fake_char.isalpha():
                    _send_char_windows(fake_char)
                    time.sleep(random.uniform(0.15, 0.35))  # Realize mistake
                    _send_char_windows("\b")                # Backspace
                    time.sleep(random.uniform(0.08, 0.20))

            # 2. Type real character
            _send_char_windows(char)

            # 3. Dynamic human pacing
            if char in ".!?":
                # Sentence end thinking pause
                time.sleep(random.uniform(0.5, 1.6))
            elif char in ",;":
                # Clause breath
                time.sleep(random.uniform(0.2, 0.5))
            elif char == "\n":
                # Paragraph break
                time.sleep(random.uniform(0.8, 2.2))
            elif char == " ":
                # Natural gap between words
                time.sleep(random.uniform(char_delay * 0.8, char_delay * 1.4))
            else:
                # Keystroke jitter
                jitter = random.gauss(char_delay, char_delay * 0.3)
                time.sleep(max(0.02, jitter))

        print(f"\n{ICON_OK} [Ghostwriter] Finished typing {len(text)} characters successfully!")
    except KeyboardInterrupt:
        print(f"\n{ICON_ERR} [Ghostwriter] Aborted by user.")


def main():
    parser = argparse.ArgumentParser(
        description="Ghostwriter: Simulates realistic human typing, thinking pauses, and typos."
    )
    parser.add_argument(
        "source",
        nargs="?",
        default=None,
        help="Text string or path to a text file to type",
    )
    parser.add_argument(
        "-c",
        "--clipboard",
        action="store_true",
        help="Use text currently copied to the system clipboard",
    )
    parser.add_argument(
        "--wpm",
        type=int,
        default=55,
        help="Target typing speed in Words Per Minute (default: 55)",
    )
    parser.add_argument(
        "--no-typos",
        action="store_true",
        help="Disable simulated human typos and corrections",
    )
    parser.add_argument(
        "--delay",
        type=int,
        default=5,
        help="Countdown delay in seconds before typing starts (default: 5)",
    )
    args = parser.parse_args()

    content = ""

    if args.clipboard:
        content = get_clipboard_text()
        if not content:
            print(f"{ICON_ERR} [Ghostwriter] Clipboard is empty or contains non-text data.")
            return
        print(f"{ICON_GHOST} [Ghostwriter] Loaded {len(content)} characters from clipboard.")
    elif args.source:
        source_path = Path(args.source)
        if source_path.is_file():
            try:
                content = source_path.read_text(encoding="utf-8")
                print(f"{ICON_GHOST} [Ghostwriter] Loaded {len(content)} characters from file: {source_path.name}")
            except Exception as e:
                print(f"{ICON_ERR} Failed to read file: {e}")
                return
        else:
            content = args.source
    else:
        # Prompt interactively
        print("=== Ghostwriter Human Typer ===")
        print("Tip: Use 'ghostwriter -c' to automatically type from clipboard!\n")
        print("Paste or type your text below, then press Enter:")
        content = input("> ").strip()
        if not content:
            print("No text provided. Exiting.")
            return

    type_text(
        text=content,
        speed_wpm=args.wpm,
        simulate_typos=not args.no_typos,
        delay_start=args.delay,
    )


if __name__ == "__main__":
    main()
