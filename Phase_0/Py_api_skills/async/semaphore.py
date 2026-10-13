import asyncio

sem = asyncio.Semaphore(3)
in_flight = peak = 0

async def embed_batch(i: int):
    global in_flight, peak
    async with sem:
        in_flight += 1
        peak = max(peak, in_flight)
        await asyncio.sleep(0.2)
        in_flight -= 1
        return i

async def main():
    results = await asyncio.gather(*(embed_batch(i) for i in range(10)))
    print("done: ", results)
    print("peak concurrency: ", peak)

if __name__ == "__main__":
    asyncio.run(main(   ))