import asyncio
import time

async def fake_call(name: str, delay: float = 0.5, fail: bool = False) -> str:
    """simulates a network call (embedding api, vector DB, LLM...)"""
    print(f"{name}: started")
    await asyncio.sleep(delay)
    if fail:
        raise RuntimeError(f"{name} failed")
    print(f"{name}: completed")
    return f"{name} ok"

class Timer:

    def __init__(self, label: str = ""):
        self.label = label

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, *exc):
        print(f" {self.label} {time.perf_counter() - self.start:.2f}s")

        