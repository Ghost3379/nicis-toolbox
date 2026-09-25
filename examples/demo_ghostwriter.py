"""
Demo: Realistic Human Typing Simulation with Ghostwriter.

Demonstrates typing rhythm, pauses, German umlaut support, and simulated typos.
"""

import sys
from pathlib import Path

# Add project root to sys.path so it works without pip install
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from nicis_toolbox import type_text
from nicis_toolbox.ghostwriter import get_clipboard_text


def demo_sample_text():
    print("=== Ghostwriter Demo ===")
    print("This demo will simulate typing a short sample paragraph.")
    print("It includes German umlauts (ä, ö, ü, ß), thinking pauses, and realistic typo correction.\n")

    sample = (
        "Hallo! Das ist ein Test für den Ghostwriter. "
        "Er tippt natürlich wie ein Mensch: mit Pausen, Umlauten (ä, ö, ü, ß) "
        "und kleinen Tippfehlern, die sofort korrigiert werden."
    )

    print("Sample text to type:")
    print(f'"{sample}"\n')

    input("Press [ENTER] to start the 5-second countdown (then switch to Notepad or Word)...")

    type_text(
        text=sample,
        speed_wpm=60,
        simulate_typos=True,
        delay_start=5,
    )


def demo_clipboard():
    print("\n--- Clipboard Check ---")
    clipboard_content = get_clipboard_text()
    if clipboard_content:
        preview = clipboard_content[:60] + ("..." if len(clipboard_content) > 60 else "")
        print(f"Current clipboard text: '{preview}'")
        print("Tip: Run 'ghostwriter -c' in terminal to automatically type whatever is copied!")
    else:
        print("Clipboard is currently empty or does not contain text.")


if __name__ == "__main__":
    demo_clipboard()
    print()
    demo_sample_text()
