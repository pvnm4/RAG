# import asyncio

# async def fetch_data(id, sleep_time):
#     print(f"Coroutine {id} starting to fetch data.")
#     await asyncio.sleep(sleep_time)
#     return {"id": id, "data": f"Sample data from coroutine {id}"}

# async def main():
#     tasks = []
#     async with asyncio.TaskGroup() as tg:
#         for i, sleep_time in enumerate([2,1,3], start=1):
#             task = tg.create_task(fetch_data(i,sleep_time))
#             tasks.append(task)

#     results = [task.result() for task in tasks]

#     for result in results:
#         print(f"Received result: {result}")

# asyncio.run(main())

# import asyncio

# async def embed_document(document_id, semaphore):
#     async with semaphore:
#         print(f"Embedding document {document_id}")
#         await asyncio.sleep(1)
#         return f"embedding_{document_id}"

# async def main():
#     semaphore = asyncio.Semaphore(5)

#     results = await asyncio.gather(*[
#         embed_document(i, semaphore)
#         for i in range(20)
#     ])

#     print(len(results))

# asyncio.run(main())

# import asyncio

# async def token_stream():
#     for token in ["Async", " programming", " is", " useful."]:
#         await asyncio.sleep(0.2)
#         yield token


# async def main():
#     async for token in token_stream():
#         print(token, end="", flush=True)

#     print()


# asyncio.run(main())

import asyncio
import httpx

async def fetch_all(urls: list[str]) -> list[int]:
    async with httpx.AsyncClient(timeout=10) as client:   # reuse ONE client
        responses = await asyncio.gather(*(client.get(u) for u in urls))
        return [r.status_code for r in responses]

print(asyncio.run(fetch_all(["https://pavanm.space"] * 5)))