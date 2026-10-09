import asyncio
from helpers import fake_call, Timer

background_tasks : set[asyncio.Task] = set()

async def main():
    task = asyncio.create_task(fake_call("embed_query", 1.0))
    print("task started: doing other work...")
    await asyncio.sleep(0.9)
    print("other work done")
    print(await task)

   # Cancel a task
    slow = asyncio.create_task(fake_call("slow_llm",5))
    await asyncio.sleep(0.1)
    slow.cancel()
    try:
        await slow
    except asyncio.CancelledError:
        print("slow task cancelled")

    # 3) Fire-and-forget (e.g. log a trace): store the reference or it may be garbage-collected mid-run

    t = asyncio.create_task(fake_call("write_trace", 0.2))
    background_tasks.add(t)
    t.add_done_callback(background_tasks.discard)
    await asyncio.sleep(0.5)
    



if __name__ == '__main__':
    asyncio.run(main())