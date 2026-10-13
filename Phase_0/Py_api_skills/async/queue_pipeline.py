import asyncio
from helpers import Timer

NUM_WORKERS = 3

async def producer(q: asyncio.Queue, n: int):
    for i in range(n):
        await q.put(f"chunk_{i}")
    for _ in range(NUM_WORKERS):
        await q.put(None)

async def worker(name: str, q: asyncio.Queue, results: list):
    while True:
        item = await q.get()
        if item is None:
            break
        await asyncio.sleep(0.5)
        results.append(f"{name}: {item}")
        

async def main():
    with Timer("queue"):
            q: asyncio.Queue = asyncio.Queue(maxsize=5)
            results: list[str] = []
            await asyncio.gather(producer(q,12), *(worker(f"w{i}", q, results) for i in range(NUM_WORKERS)))
    print(len(results), "chunks processed")
    print(results)


if __name__ == '__main__':
    asyncio.run(main())