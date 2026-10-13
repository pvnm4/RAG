import asyncio
import time
from helpers import Timer

def blocking_parse(path: str) -> str:
    time.sleep(1)
    return f"parsed {path}"

async def main():
    with Timer("to_thread x3 (concurrent)"):
        results = await asyncio.gather(
            *(asyncio.to_thread(blocking_parse, f"doc{i}.pdf") for i in range(3))
        )

    print(results)


if __name__ == '__main__':
    asyncio.run(main())