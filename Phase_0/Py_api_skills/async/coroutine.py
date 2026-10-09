import asyncio
from helpers import fake_call, Timer

async def main():
    coro = fake_call("dense") # Not executed: just a coroutine object
    print(type(coro)) # <class 'coroutine'>
    print(await coro) # now it runs -> "dense ok"


    # Sequential awaits add up
    with Timer("sequential"):
        await fake_call("a",0.5)
        await fake_call("b",0.5)  # total 1.0s

asyncio.run(main())  # the one entry point (once per program)
