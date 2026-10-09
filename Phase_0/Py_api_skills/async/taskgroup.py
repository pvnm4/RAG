import asyncio
from helpers import fake_call, Timer

async def main():
    # 1) Happy path: leaving the `async with` block = all tasks are done
    async with asyncio.TaskGroup() as tg:
        t1 = tg.create_task(fake_call("dense", 0.8))
        t2 = tg.create_task(fake_call("bm25", 0.6))

    print(t1.result(), "|", t2.result())

    # 2) Failure: one failing task CANCELS its siblings, then raises ExceptionGroup

    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(fake_call("slow_but_ok", 2.0))
            tg.create_task(fake_call("bad",0.2, fail=True))
    except* RuntimeError as eg:
        print("caught: ", [str(e) for e in eg.exceptions])

if __name__ == '__main__':
    asyncio.run(main())