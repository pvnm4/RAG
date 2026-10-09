import asyncio
from helpers import fake_call, Timer

async def main():
    # 1) Basic: concurrent , results come back in INPUT order
    with Timer("gather"):
        results = await asyncio.gather(
            fake_call("dense", 0.8),
            fake_call("bm25", 0.6),
            fake_call("rerank", 0.2)
        )

    print(results) # total 0.8s

    # 2) Many items from a list: unpack with *
    with Timer("gather"):
        queries = ["q1","q2","q3","q4"]
        outs = await asyncio.gather( *(fake_call(q,0.3) for q in queries))
    print(outs) # total: 0.32s

    # 3) Failures: default = first exception propagates (others keep runnig!)
    try:
        await asyncio.gather(fake_call("ok"), fake_call("bad", fail=True))
    except RuntimeError as e:
        print("caught: ", e)

    # 4) return_exception= True: get partial results, inspect each
    # try:
    #     results = await asyncio.gather(fake_call("ok"), fake_call("bad", fail=True), return_exceptions=True)
    #     print(results)
    # except RuntimeError as e:
    #     print("caught: ", e)
    results = await asyncio.gather(
         fake_call("bad", fail=True), fake_call("ok"), return_exceptions=True
    )
    for r in results:
        print(f"ERR: {r}" if isinstance(r,Exception) else "ok")


if __name__ == '__main__':
    asyncio.run(main())