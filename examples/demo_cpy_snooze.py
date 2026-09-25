"""
CircuitPython Example: Single-Button Deep Sleep using cpy_snooze.

Copy this pattern to your CIRCUITPY drive (code.py) and drop cpy_snooze.py into /lib.
"""

# Example code.py for CircuitPython board (e.g. Feather RP2040, ESP32-S2/S3, SAMD51)
EXAMPLE_CIRCUITPYTHON_CODE = '''
import time
import board
import neopixel
from nicis_toolbox.cpy_snooze import CpySnooze

# 1. Setup Snooze Manager
# button_pin = physical button, dummy_pin = unused GPIO
snooze = CpySnooze(button_pin=board.D2, dummy_pin=board.D6)
button = snooze.button

# 2. Check if we just woke up from deep sleep
if CpySnooze.woke_from_sleep():
    print("Microcontroller woke up from button press!")
else:
    print("Normal fresh power-on boot.")

# 3. Setup peripherals
pixels = neopixel.NeoPixel(board.D5, 10, brightness=0.5)
pixels.fill((0, 255, 0))  # Green

# 4. Register peripherals to auto-deinitialize to save battery power during sleep
snooze.register(pixels)

# 5. Main loop
last_activity = time.monotonic()

while True:
    # Check button press during normal runtime
    if not button.value:
        print("Button pressed during normal operation!")
        pixels.fill((255, 0, 0))
        last_activity = time.monotonic()
        time.sleep(0.2)

    # Inactivity timeout -> Go to sleep
    if time.monotonic() - last_activity > 10:
        print("10 seconds inactive. Entering deep sleep...")
        # Automatically deinitializes pixels, frees D2, and arms wake alarm!
        snooze.deep_sleep()
'''

if __name__ == "__main__":
    from nicis_toolbox.cpy_snooze import CpySnooze
    print("=== cpy_snooze Demo & Documentation ===")
    print("CpySnooze class loaded successfully.")
    print("Running in desktop mode:", not CpySnooze.woke_from_sleep())
    print("\nTo use on your CircuitPython board (e.g. Feather, RP2040, ESP32):")
    print(EXAMPLE_CIRCUITPYTHON_CODE)
