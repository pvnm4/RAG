import asyncio
from helpers import fake_call

async def main():

    coros = [fake_call("a",0.2), fake_call("b",0.1), fake_call("c",0.3)]

    for finished in asyncio.as_completed(coros):
        print(await finished)

if __name__ == '__main__':
    asyncio.run(main())