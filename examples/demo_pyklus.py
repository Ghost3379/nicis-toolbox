"""
Demo script showcasing all features of Pyklus.
"""
import sys
from pathlib import Path
import time

# Ensure nicis_toolbox is importable even without pip install -e .
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from nicis_toolbox import Pyklus


def demo_manual_stopwatch():
    print("=== 1. Manual Stopwatch with Laps ===")
    timer = Pyklus("Data Processing Pipeline").start()
    
    time.sleep(0.08)
    timer.lap("Downloaded data")
    
    time.sleep(0.12)
    timer.lap("Cleaned & parsed records")
    
    time.sleep(0.05)
    total = timer.stop()
    print(f"Total time recorded: {total:.4f} seconds ({timer.formatted_elapsed})\n")


def demo_context_manager():
    print("=== 2. Context Manager ===")
    with Pyklus("Fast Calculation"):
        result = sum(x * x for x in range(1_000_000))
    print(f"Calculation completed. (Result: {result})\n")


@Pyklus.timeit("Heavy Sorting Demo")
def demo_decorator():
    print("=== 3. Function Decorator ===")
    data = list(range(100_000, 0, -1))
    data.sort()
    return len(data)


if __name__ == "__main__":
    demo_manual_stopwatch()
    demo_context_manager()
    demo_decorator()
