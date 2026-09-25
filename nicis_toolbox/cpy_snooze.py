"""
cpy_snooze.py - CircuitPython Single-Button Deep Sleep & Power-Down Manager.

Solves the CircuitPython 'ValueError: Pin in use' dilemma by swapping the active
button pin to a dummy pin before arming PinAlarm on the real hardware pin.
Also handles batch deinitialization of power-draining peripherals (NeoPixels,
I2S, I2C, PWM) to achieve microamp sleep current.
"""

from typing import Any, List, Optional

try:
    import alarm
    import board
    from digitalio import DigitalInOut, Direction, Pull
    IS_CIRCUITPYTHON = True
except ImportError:
    # Graceful fallback on standard desktop Python
    IS_CIRCUITPYTHON = False


class CpySnooze:
    """
    Manages CircuitPython single-button deep sleep and peripheral deinitialization.

    Allows using the SAME physical button for runtime interaction AND deep sleep wakeup.
    """

    def __init__(self, button_pin: Any, dummy_pin: Optional[Any] = None):
        """
        Initialize the snooze manager.

        Args:
            button_pin: The hardware pin connected to your physical button (e.g. board.D2).
            dummy_pin: An unused GPIO pin to hold the button object during sleep (e.g. board.D6).
        """
        self.button_pin = button_pin
        self.dummy_pin = dummy_pin
        self.hardware_list: List[Any] = []
        self.button: Optional[Any] = None

        if IS_CIRCUITPYTHON:
            self.init_button()

    def init_button(self) -> Any:
        """Initialize or restore the button DigitalInOut on the real hardware pin."""
        if not IS_CIRCUITPYTHON:
            return None
        if self.button:
            try:
                self.button.deinit()
            except Exception:
                pass
        self.button = DigitalInOut(self.button_pin)
        self.button.direction = Direction.INPUT
        self.button.pull = Pull.UP
        return self.button

    def register(self, *peripherals: Any) -> None:
        """
        Register hardware instances (NeoPixels, PWM, I2S, I2C, sensors)
        that should be deinitialized before sleep to prevent power drain.
        """
        for item in peripherals:
            if item is not None and item not in self.hardware_list:
                self.hardware_list.append(item)

    def deep_sleep(self, wake_value: bool = False) -> None:
        """
        Perform pin swap, power down registered hardware, and enter deep sleep.

        Args:
            wake_value: Trigger alarm on False (pressed to GND / active low) or True (active high).
        """
        if not IS_CIRCUITPYTHON:
            print("[cpy-snooze] Not running in CircuitPython. Simulation mode.")
            return

        # 1. Release the physical button pin
        if self.button:
            self.button.deinit()
            if self.dummy_pin:
                # Redirect object to dummy pin so dangling references don't throw deinit error
                self.button = DigitalInOut(self.dummy_pin)
                self.button.direction = Direction.INPUT
                self.button.pull = Pull.UP

        # 2. Deinitialize all registered hardware to save power
        for item in self.hardware_list:
            if hasattr(item, "deinit"):
                try:
                    item.deinit()
                except Exception as e:
                    print(f"[cpy-snooze] Warning deiniting {item}: {e}")

        # 3. Arm the wake-up alarm on the freed physical button pin
        pin_alarm = alarm.pin.PinAlarm(pin=self.button_pin, value=wake_value, pull=True)

        print("[cpy-snooze] Board entering deep sleep. Press button to wake.")
        alarm.exit_and_deep_sleep_until_alarms(pin_alarm)

    def light_sleep(self, wake_value: bool = False) -> None:
        """Enter light sleep until button is pressed, then automatically restore pin."""
        if not IS_CIRCUITPYTHON:
            print("[cpy-snooze] Not running in CircuitPython. Simulation mode.")
            return

        # Free pin
        if self.button:
            self.button.deinit()

        pin_alarm = alarm.pin.PinAlarm(pin=self.button_pin, value=wake_value, pull=True)
        alarm.light_sleep_until_alarms(pin_alarm)

        # Restore button after wake
        self.init_button()

    @staticmethod
    def woke_from_sleep() -> bool:
        """Check if microcontroller just woke up from deep sleep."""
        if not IS_CIRCUITPYTHON:
            return False
        return bool(alarm.wake_alarm)


# Clean alias
SleepManager = CpySnooze
