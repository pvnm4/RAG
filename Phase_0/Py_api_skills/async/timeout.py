import asyncio
from helpers import fake_call

async def main():
    # wait_for: wrap one awaitable
    # try:
    #     await asyncio.wait_for(fake_call("llm", 3), timeout=2)
    #     print("hi")
    # except TimeoutError:
    #     print("LLM timed out")

    # asyncio.timeout: one deadline for a whole block
    # try:
    #     async with asyncio.timeout(1):
    #         await fake_call("step1",0.4)
    #         await fake_call("step2",0.4)
    #         await fake_call("stemp3",0.4)
    # except TimeoutError:
    #     print("whole block timed out")

    # 3) RAG pattern: graceful degradation (skip rerank if it's slow)
    canditates = ["c1","c2","c3"]
    try:
        await asyncio.wait_for(fake_call("rerank",3), timeout= 0.5)
        canditates = ["c2","c3","c1"]
        print(canditates)
    except TimeoutError:
        print("rerank skipped: Using original order:", canditates)


if __name__ == '__main__':
    asyncio.run(main())