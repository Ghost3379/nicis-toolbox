import sys
import time
from functools import wraps
from typing import Callable, List, Optional, Tuple, Union


def _get_symbols() -> Tuple[str, str, str]:
    """Return platform-safe symbols based on terminal encoding support."""
    try:
        encoding = sys.stdout.encoding or "utf-8"
        "⏱️↳🏁".encode(encoding)
        return ("⏱️ ", "  ↳", "🏁")
    except (UnicodeEncodeError, AttributeError):
        return ("[START]", "  ->", "[DONE]")


START_SYM, LAP_SYM, DONE_SYM = _get_symbols()


class Pyklus:
    """
    Pyklus: A precision timer, stopwatch, context manager, and decorator.
    
    Supports:
    - Manual start/stop and lap timing
    - Context manager (`with Pyklus("My Task"): ...`)
    - Function decorator (`@Pyklus.timeit`)
    - Dynamic unit formatting (ns, us, ms, s, min:sec)
    """

    def __init__(self, name: str = "Task", verbose: bool = True):
        self.name = name
        self.verbose = verbose
        self._start_time: Optional[float] = None
        self._elapsed: Optional[float] = None
        self._laps: List[Tuple[str, float]] = []

    def start(self) -> "Pyklus":
        """Start the stopwatch timer."""
        self._start_time = time.perf_counter()
        self._elapsed = None
        self._laps.clear()
        if self.verbose:
            print(f"{START_SYM} [{self.name}] Timer started.")
        return self

    def lap(self, label: str = "Lap") -> float:
        """Record an intermediate lap/split time since start."""
        if self._start_time is None:
            raise RuntimeError(f"Cannot record lap '{label}': Pyklus has not been started.")
        
        now = time.perf_counter()
        lap_elapsed = now - self._start_time
        self._laps.append((label, lap_elapsed))
        
        if self.verbose:
            print(f"{LAP_SYM} [{self.name}] {label}: {self.format_time(lap_elapsed)}")
        return lap_elapsed

    def stop(self) -> float:
        """Stop the stopwatch and return the elapsed time in seconds."""
        if self._start_time is None:
            raise RuntimeError("Cannot stop: Pyklus has not been started.")
        
        now = time.perf_counter()
        self._elapsed = now - self._start_time
        self._start_time = None

        if self.verbose:
            print(f"{DONE_SYM} [{self.name}] Completed in {self.format_time(self._elapsed)}")
        return self._elapsed

    @property
    def elapsed(self) -> Optional[float]:
        """Returns the total elapsed seconds from the last run."""
        return self._elapsed

    @property
    def formatted_elapsed(self) -> str:
        """Returns the elapsed time formatted with appropriate time units."""
        if self._elapsed is None:
            return "0 s"
        return self.format_time(self._elapsed)

    @property
    def laps(self) -> List[Tuple[str, float]]:
        """Returns recorded lap times as list of (label, elapsed_seconds)."""
        return list(self._laps)

    def __enter__(self) -> "Pyklus":
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.stop()

    def __repr__(self) -> str:
        status = "running" if self._start_time else f"stopped ({self.formatted_elapsed})"
        return f"<Pyklus(name='{self.name}', status={status})>"

    @staticmethod
    def format_time(seconds: float) -> str:
        """Format seconds into human-readable unit (ns, us, ms, s, min:sec)."""
        if seconds < 1e-6:
            return f"{seconds * 1e9:.2f} ns"
        elif seconds < 1e-3:
            return f"{seconds * 1e6:.2f} us"
        elif seconds < 1.0:
            return f"{seconds * 1e3:.2f} ms"
        elif seconds < 60.0:
            return f"{seconds:.3f} s"
        else:
            mins, secs = divmod(seconds, 60)
            return f"{int(mins)}m {secs:.2f} s"

    @classmethod
    def timeit(cls, name_or_func: Optional[Union[str, Callable]] = None, verbose: bool = True):
        """
        Decorator to time a function's execution.
        
        Usage:
            @Pyklus.timeit
            def my_func(): ...
            
            @Pyklus.timeit("Custom Task Name")
            def my_func(): ...
        """
        def decorator(func: Callable) -> Callable:
            task_name = name_or_func if isinstance(name_or_func, str) else func.__name__

            @wraps(func)
            def wrapper(*args, **kwargs):
                timer = cls(name=task_name, verbose=verbose)
                with timer:
                    return func(*args, **kwargs)
            return wrapper

        if callable(name_or_func):
            # Called as @Pyklus.timeit without parentheses
            return decorator(name_or_func)
        return decorator


# Convenient alias in case someone prefers German lowercase naming
zyklus = Pyklus
