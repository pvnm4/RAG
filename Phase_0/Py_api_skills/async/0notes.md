# Python asyncio Toolkit (Phase 0.1)

> **Requires Python 3.11+** for `asyncio.TaskGroup`, `asyncio.timeout()`, and `except*`.

## Table of Contents

1. [What is asyncio?](#what-is-asyncio)
2. [Why do we need it for RAG?](#why-do-we-need-it-for-rag)
3. [When should you use it?](#when-should-you-use-it)
4. [When should you not use it?](#when-should-you-not-use-it)
5. [Repository layout](#repository-layout)
6. [Shared helper utilities](#shared-helper-utilities)
7. [Coroutine basics](#01_coroutine_basicspy)
8. [Running concurrent work with gather](#02_gatherpy)
9. [Creating and cancelling tasks](#03_create_taskpy)
10. [Structured concurrency with TaskGroup](#04_taskgrouppy)
11. [Limiting concurrency with Semaphore](#05_semaphorepy)
12. [Timeouts](#06_timeoutspy)
13. [Processing results as they complete](#07_as_completedpy)
14. [Calling blocking code with to_thread](#08_to_threadpy)
15. [Producer-consumer pipelines with Queue](#09_queue_pipelinepy)
16. [Async generators and async context managers](#10_async_generatorspy)
17. [Retrying transient failures with backoff](#11_retry_backoffpy)
18. [Capstone: RAG retrieval](#12_capstone_retrievepy)
19. [Common mistakes](#common-mistakes)
20. [Topics to skip initially](#topics-to-skip-initially)
21. [Trade-offs](#trade-offs)
22. [Interview explanation](#interview-explanation)

---

## What is asyncio?

`asyncio` is Python's built-in library for **concurrent I/O on one thread**.

A useful mental model:

```text
async def  -> defines a coroutine function (a recipe for async work)
call it    -> creates a coroutine object; it does not run to completion
await      -> suspends the current coroutine while an awaitable completes
event loop -> schedules and coordinates asynchronous tasks
```

The event loop is usually started once in a standalone program with `asyncio.run(main())`.

### The tools to know first

| Job | Tool |
|---|---|
| Start a standalone async program | `asyncio.run()` |
| Run multiple awaitables and collect results | `asyncio.gather()` |
| Manage related tasks safely | `asyncio.TaskGroup` |
| Schedule work to run concurrently | `asyncio.create_task()` |
| Limit simultaneous operations | `asyncio.Semaphore` |
| Apply a timeout to one awaitable | `asyncio.wait_for()` |
| Apply a deadline to a block | `asyncio.timeout()` |
| Process results as tasks finish | `asyncio.as_completed()` |
| Run blocking synchronous code in a thread | `asyncio.to_thread()` |
| Build a producer-consumer pipeline | `asyncio.Queue` |
| Stream values | Async generators and `async for` |
| Manage asynchronous resources | `async with` |
| Retry transient errors | Exponential backoff with jitter (a pattern, not a built-in) |

## Why do we need it for RAG?

A Retrieval-Augmented Generation (RAG) request often involves network waits: an embedding API, a vector database, keyword/BM25 retrieval, a reranker, and an LLM.

Async can help you:

- Run dense retrieval and BM25 retrieval concurrently when both can operate independently.
- Embed many chunks with bounded concurrency to respect service limits.
- Serve multiple requests in an async web server such as FastAPI without dedicating one thread to every waiting request.
- Stream LLM output to a client.
- Apply timeouts and fallback policies to external operations.

For independent dense and sparse retrieval, latency can be close to the slower call's duration rather than the sum of both durations.

## When should you use it?

- Many independent network or database calls.
- FastAPI routes that call LLMs, embedding services, or vector databases.
- Streaming responses.
- Ingestion jobs that call rate-limited APIs.
- Workflows with multiple independent tools.

## When should you not use it?

- **CPU-bound work:** async does not automatically speed up local embedding inference, heavy PDF parsing, or large numerical computations. Consider native libraries, a process pool, batching, or a worker service. `to_thread()` is useful for blocking I/O and functions that release the GIL.
- **Dependent steps:** if you must rewrite a query before embedding it, those steps are sequential. Parallelize only independent work.
- **Tiny scripts:** for a few sequential calls, synchronous code may be simpler.
- **Blocking calls inside `async def`:** avoid `time.sleep()`, synchronous `requests.get()`, or synchronous database calls on the event-loop thread. A blocking call can stall other tasks on that loop.

---

## Repository layout

```text
RAG/
├── README.md
└── Phase_0/
    └── async_basics/
        ├── helpers.py
        ├── 01_coroutine_basics.py
        ├── 02_gather.py
        ├── 03_create_task.py
        ├── 04_taskgroup.py
        ├── 05_semaphore.py
        ├── 06_timeouts.py
        ├── 07_as_completed.py
        ├── 08_to_thread.py
        ├── 09_queue_pipeline.py
        ├── 10_async_generators.py
        ├── 11_retry_backoff.py
        └── 12_capstone_retrieve.py
```

Run these examples from the `async_basics` directory so that `from helpers import ...` works.

## Shared helper utilities

### `helpers.py`

```python
import asyncio
import time


async def fake_call(
    name: str,
    delay: float = 0.5,
    fail: bool = False,
) -> str:
    """Simulate a network call (embedding API, vector DB, LLM, etc.)."""
    await asyncio.sleep(delay)

    if fail:
        raise RuntimeError(f"{name} failed")

    return f"{name} ok"


class Timer:
    """Usage: with Timer('label'): ... (prints elapsed time)."""

    def __init__(self, label: str = ""):
        self.label = label

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, *exc):
        elapsed = time.perf_counter() - self.start
        print(f"  [{self.label}] {elapsed:.2f}s")
```

---

## `01_coroutine_basics.py`

**Topics:** coroutines, `await`, `asyncio.run()`.

```python
import asyncio
from helpers import fake_call, Timer


async def main():
    coro = fake_call("dense")  # Not executed to completion; this creates a coroutine object.
    print(type(coro))          # <class 'coroutine'>
    print(await coro)          # Await it to run it and get the result.

    # Sequential awaits add their waiting times.
    with Timer("sequential"):
        await fake_call("a", 0.5)
        await fake_call("b", 0.5)  # Total is about 1 second.


if __name__ == "__main__":
    asyncio.run(main())  # Typical entry point for a standalone script.
```

**Key points**

- Calling an `async def` function creates a coroutine object.
- `await` lets the coroutine run and obtain the result.
- Forgetting to await or schedule a coroutine can produce a “coroutine was never awaited” warning.
- In a Jupyter notebook that already has a running event loop, use `await main()` instead of `asyncio.run(main())`.

---

## `02_gather.py`

**Topic:** run awaitables concurrently and collect results in input order.

```python
import asyncio
from helpers import fake_call, Timer


async def main():
    # 1. Concurrent calls: results are returned in input order.
    with Timer("gather"):
        results = await asyncio.gather(
            fake_call("dense", 0.8),
            fake_call("bm25", 0.6),
            fake_call("rerank", 0.2),
        )

    print(results)  # ['dense ok', 'bm25 ok', 'rerank ok']; about 0.8s total.

    # 2. Build awaitables from a list and unpack them with *.
    queries = ["q1", "q2", "q3", "q4"]
    outs = await asyncio.gather(
        *(fake_call(query, 0.3) for query in queries)
    )
    print(outs)

    # 3. By default, an exception is propagated to the caller.
    # Other submitted awaitables are not automatically cancelled just
    # because one of them raises.
    try:
        await asyncio.gather(
            fake_call("ok"),
            fake_call("bad", fail=True),
        )
    except RuntimeError as exc:
        print("caught:", exc)

    # 4. return_exceptions=True returns exceptions as result entries.
    results = await asyncio.gather(
        fake_call("ok"),
        fake_call("bad", fail=True),
        return_exceptions=True,
    )

    for result in results:
        if isinstance(result, BaseException):
            print("ERR", result)
        else:
            print("OK", result)


if __name__ == "__main__":
    asyncio.run(main())
```

Use `gather()` when you want results in input order and its failure behavior suits the job—for example, batch embedding or multi-query retrieval.

**Important:** `gather()` is not a concurrency limit. If you submit thousands of awaitables, you may create thousands of tasks or operations. Use batching, a semaphore, or a bounded worker queue when necessary.

---

## `03_create_task.py`

**Topic:** schedule work now and await it later.

```python
import asyncio


async def fake_call(name: str, delay: float = 0.5) -> str:
    await asyncio.sleep(delay)
    return f"{name} ok"


background_tasks: set[asyncio.Task] = set()


async def main():
    # 1. Schedule work, then do something else before collecting its result.
    task = asyncio.create_task(fake_call("embed_query", 1.0))
    print("Task scheduled; doing other work...")
    await asyncio.sleep(0.3)  # For example, do independent work here.
    print("Other work done")
    print(await task)

    # 2. Cancel a task.
    slow = asyncio.create_task(fake_call("slow_llm", 5))
    await asyncio.sleep(0.1)
    slow.cancel()

    try:
        await slow
    except asyncio.CancelledError:
        print("Slow task cancelled")

    # 3. If a background task truly must outlive the current step,
    # keep a strong reference and define how its exception is observed.
    task = asyncio.create_task(fake_call("write_trace", 0.2))
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)

    await task  # This example awaits it so errors/results are observed.


if __name__ == "__main__":
    asyncio.run(main())
```

Use `create_task()` when work should start concurrently and finish later—for example, prefetching or independent operations.

**Production note:** Prefer `TaskGroup` for work that belongs to one request or operation. Do not treat important application work as untracked “fire-and-forget” tasks. Keep references, observe exceptions, and define shutdown behavior.

---

## `04_taskgroup.py`

**Topic:** structured concurrency with Python 3.11+.

```python
import asyncio
from helpers import fake_call


async def main():
    # 1. Happy path: exiting the TaskGroup waits for its child tasks.
    async with asyncio.TaskGroup() as tg:
        t1 = tg.create_task(fake_call("dense", 0.8))
        t2 = tg.create_task(fake_call("bm25", 0.6))

    print(t1.result(), "|", t2.result())

    # 2. If one child raises an ordinary exception, the group cancels
    # unfinished siblings and raises an ExceptionGroup.
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(fake_call("slow_but_ok", 2.0))
            tg.create_task(fake_call("bad", 0.2, fail=True))
    except* RuntimeError as group:
        print("Caught:", [str(exc) for exc in group.exceptions])


if __name__ == "__main__":
    asyncio.run(main())
```

### `gather()` versus `TaskGroup`

| Behavior | `asyncio.gather()` | `asyncio.TaskGroup` |
|---|---|---|
| Results | Returns results in input order | Retrieve results from task objects after the group exits |
| Child failure | By default, propagates an exception; other awaitables usually continue | Cancels unfinished siblings and raises an exception group |
| Partial failures | Can return exceptions as values with `return_exceptions=True` | Designed around a structured group of related tasks |
| Best fit | Batch jobs where partial results may be acceptable | Related request-scoped work where sibling cancellation is desirable |

Use `TaskGroup` when the tasks form one logical unit. Use `gather()` when its result-collection and error semantics fit your use case.

---

## `05_semaphore.py`

**Topic:** bounded concurrency.

```python
import asyncio

SEM_LIMIT = 3
sem = asyncio.Semaphore(SEM_LIMIT)

in_flight = 0
peak = 0


async def embed_batch(item_id: int) -> int:
    global in_flight, peak

    async with sem:
        in_flight += 1
        peak = max(peak, in_flight)

        try:
            await asyncio.sleep(0.2)  # Simulated API call.
            return item_id
        finally:
            in_flight -= 1


async def main():
    results = await asyncio.gather(
        *(embed_batch(i) for i in range(10))
    )

    print("Done:", results)
    print("Peak concurrency:", peak)  # Never more than 3.


if __name__ == "__main__":
    asyncio.run(main())
```

The semaphore permits at most three coroutines inside the protected section at the same time.

A common ingestion pattern is `gather()` plus a semaphore. Start with a modest concurrency limit, then tune it using provider quotas, latency, error rates, and measurements.

**Semaphore versus rate limiter:** a semaphore limits the number of simultaneous in-flight operations. It does not directly limit requests per second or tokens per minute.

---

## `06_timeouts.py`

**Topic:** place time limits around slow operations.

```python
import asyncio
from helpers import fake_call


async def main():
    # 1. wait_for(): timeout around one awaitable.
    try:
        await asyncio.wait_for(
            fake_call("llm", 5),
            timeout=1,
        )
    except TimeoutError:
        print("LLM timed out")

    # 2. asyncio.timeout(): deadline for an entire block (Python 3.11+).
    try:
        async with asyncio.timeout(1):
            await fake_call("step1", 0.4)
            await fake_call("step2", 0.4)
            await fake_call("step3", 0.4)
    except TimeoutError:
        print("Whole block timed out")

    # 3. Graceful degradation: skip reranking if it is too slow.
    candidates = ["c1", "c2", "c3"]

    try:
        reranked = await asyncio.wait_for(
            fake_call("rerank", 3),
            timeout=0.5,
        )
    except TimeoutError:
        print("Rerank skipped; use original order:", candidates)
    else:
        print("Reranker result:", reranked)


if __name__ == "__main__":
    asyncio.run(main())
```

- `wait_for()` applies a timeout to one awaitable.
- `asyncio.timeout()` applies a deadline to a block of async operations.
- A timeout cancels the relevant async operation; cancellation and cleanup can mean elapsed time exceeds the nominal timeout.

For production RAG, use an overall request deadline as well as sensible per-dependency timeouts. Choose timeout values based on measurements, service-level objectives, and provider behavior.

---

## `07_as_completed.py`

**Topic:** process results in completion order.

```python
import asyncio
from helpers import fake_call


async def main():
    coroutines = [
        fake_call("a", 0.3),
        fake_call("b", 0.1),
        fake_call("c", 0.2),
    ]

    for finished in asyncio.as_completed(coroutines):
        print(await finished)  # Usually b, c, a.


if __name__ == "__main__":
    asyncio.run(main())
```

Use `as_completed()` for progress updates, processing independent results as they arrive, or workflows where early results are useful.

Completion order is not input order. Use `gather()` if you need the original input order.

Python 3.13+ also supports asynchronous iteration over `as_completed()`; the ordinary iteration form above is broadly compatible.

---

## `08_to_thread.py`

**Topic:** call blocking synchronous code without blocking the event-loop thread.

```python
import asyncio
import time
from helpers import Timer


def blocking_parse(path: str) -> str:
    # Imagine a synchronous PDF parser or legacy synchronous SDK.
    time.sleep(1)
    return f"parsed {path}"


async def main():
    with Timer("to_thread x3"):
        results = await asyncio.gather(
            *(
                asyncio.to_thread(blocking_parse, f"doc{i}.pdf")
                for i in range(3)
            )
        )

    print(results)  # Roughly 1 second for these simulated waits.


if __name__ == "__main__":
    asyncio.run(main())
```

`asyncio.to_thread()` runs the blocking function in a worker thread. Here, the simulated one-second waits can overlap.

It is useful for blocking I/O and functions that release the GIL. For heavy pure-Python CPU work, consider `ProcessPoolExecutor`, native code that releases the GIL, or a separate worker service.

Cancelling the coroutine that awaits `to_thread()` does not forcibly terminate a synchronous function that is already running in the worker thread.

---

## `09_queue_pipeline.py`

**Topic:** producer-consumer pipeline with a bounded queue.

```python
import asyncio

NUM_WORKERS = 3


async def producer(queue: asyncio.Queue, n: int):
    for i in range(n):
        await queue.put(f"chunk_{i}")  # Waits if the bounded queue is full.

    # One stop signal per worker.
    for _ in range(NUM_WORKERS):
        await queue.put(None)


async def worker(name: str, queue: asyncio.Queue, results: list[str]):
    while True:
        item = await queue.get()

        try:
            if item is None:
                return

            await asyncio.sleep(0.1)  # Simulate embedding + database upsert.
            results.append(f"{name}:{item}")
        finally:
            queue.task_done()


async def main():
    queue: asyncio.Queue = asyncio.Queue(maxsize=5)
    results: list[str] = []

    async with asyncio.TaskGroup() as tg:
        tg.create_task(producer(queue, 12))
        for i in range(NUM_WORKERS):
            tg.create_task(worker(f"w{i}", queue, results))

    print(len(results), "chunks processed")


if __name__ == "__main__":
    asyncio.run(main())
```

A bounded queue creates **backpressure**: when the queue reaches its maximum size, the producer waits until a worker consumes an item.

Important methods:

- `put(item)`: add an item, waiting if the queue is full.
- `get()`: retrieve an item, waiting if the queue is empty.
- `task_done()`: mark a retrieved item as handled.
- `join()`: wait until all enqueued items have matching `task_done()` calls.

The worker calls `task_done()` for regular items and stop signals. The `TaskGroup` waits for the producer and all workers to finish.

This in-process pattern resembles a RAG ingestion pipeline: parse → chunk → embed → upsert. For distributed or durable workloads, consider a queue or task system such as Redis-backed workers, SQS, or Celery.

---

## `10_async_generators.py`

**Topics:** async generators, `async for`, async context managers, and `async with`.

```python
import asyncio
from contextlib import asynccontextmanager


# 1. An async generator can yield streaming output.
async def fake_llm_stream(prompt: str):
    tokens = ["RAG ", "is ", "retrieval ", "plus ", "generation."]

    for token in tokens:
        await asyncio.sleep(0.15)
        yield token


# 2. An async context manager can manage resource setup and cleanup.
@asynccontextmanager
async def fake_client():
    print("Client opened")
    try:
        yield "client"
    finally:
        print("Client closed")


async def main():
    async with fake_client() as client:
        print("Using", client)

        async for token in fake_llm_stream("What is RAG?"):
            print(token, end="", flush=True)

        print()


if __name__ == "__main__":
    asyncio.run(main())
```

- An async generator uses `async def` and `yield`.
- `async for` consumes values as they become available.
- `async with` enters and exits an asynchronous context manager, enabling async setup and cleanup.

In FastAPI, an async generator can supply chunks to a streaming response. Real HTTP clients and database pools should be managed according to their library's lifecycle recommendations and reused where appropriate.

---

## `11_retry_backoff.py`

**Topic:** retry transient failures with exponential backoff and jitter.

```python
import asyncio
import random
from collections.abc import Awaitable, Callable
from typing import TypeVar

T = TypeVar("T")


async def retry(
    fn: Callable[[], Awaitable[T]],
    *,
    attempts: int = 4,
    base: float = 0.2,
    retry_on: tuple[type[Exception], ...] = (RuntimeError,),
) -> T:
    """Retry a zero-argument async callable with backoff and jitter."""
    if attempts < 1:
        raise ValueError("attempts must be at least 1")

    for attempt in range(attempts):
        try:
            return await fn()
        except retry_on as exc:
            if attempt == attempts - 1:
                raise

            delay = base * (2 ** attempt) + random.uniform(0, base)
            print(
                f"Attempt {attempt + 1} failed ({exc}); "
                f"retrying in {delay:.2f}s"
            )
            await asyncio.sleep(delay)

    raise RuntimeError("Unreachable")


calls = 0


async def flaky_embedding_api() -> str:
    global calls
    calls += 1

    if calls < 3:
        raise RuntimeError("Simulated transient rate limit")

    return "embedding ok"


async def main():
    print(await retry(flaky_embedding_api))


if __name__ == "__main__":
    asyncio.run(main())
```

Exponential backoff increases the wait between retries. Jitter adds randomness so many clients are less likely to retry at exactly the same time.

Production rules:

- Retry only transient failures, such as selected rate-limit responses, temporary server errors, or appropriate network failures.
- Do not retry permanent errors such as invalid input or authentication failures.
- Respect `Retry-After` when provided by the service.
- Cap retries and total elapsed time.
- Be careful retrying operations that are not idempotent.
- Ensure the timeout and retry budget fit within the overall request deadline.

The example uses `RuntimeError` only to simulate a transient failure. Real applications should catch the specific exception types exposed by their SDK.

---

## `12_capstone_retrieve.py`

**Topic:** combine dependencies, concurrency, timeouts, and graceful degradation in a RAG-shaped retrieval pipeline.

```python
import asyncio
from helpers import fake_call, Timer

sem = asyncio.Semaphore(5)


async def embed_query(query: str) -> list[float]:
    async with sem:
        await asyncio.wait_for(
            fake_call("embed", 0.05),
            timeout=2,
        )

    return [0.1, 0.2, 0.3]


async def dense_search(vector: list[float]) -> list[str]:
    await asyncio.wait_for(
        fake_call("dense", 0.08),
        timeout=2,
    )
    return ["c12", "c7", "c30"]


async def bm25_search(query: str) -> list[str]:
    await asyncio.wait_for(
        fake_call("bm25", 0.05, fail=True),  # Simulate a failure.
        timeout=2,
    )
    return ["c7", "c99"]


async def retrieve(query: str) -> list[str]:
    # Dependency: embedding must finish before dense retrieval can start.
    vector = await embed_query(query)

    # These searches are independent and can run concurrently.
    dense, sparse = await asyncio.gather(
        dense_search(vector),
        bm25_search(query),
        return_exceptions=True,
    )

    # This demo allows partial results if either search fails.
    if isinstance(dense, BaseException):
        raise dense

    if isinstance(sparse, BaseException):
        print("BM25 failed; falling back to dense-only results")
        sparse = []

    # Deduplicate while preserving first-seen order.
    return list(dict.fromkeys(dense + sparse))


async def main():
    with Timer("retrieve"):
        print(await retrieve("refund policy"))


if __name__ == "__main__":
    asyncio.run(main())
```

### What this example demonstrates

1. The query embedding is awaited first because dense retrieval depends on it.
2. Dense and BM25 searches run concurrently because they are independent after the embedding is available.
3. The semaphore bounds access to the embedding stage across concurrent callers that share this semaphore and event loop.
4. Each external-operation simulation has a timeout.
5. `return_exceptions=True` allows the code to inspect individual retrieval failures and keep usable results when one search fails.
6. Results are deduplicated without changing their first-seen order.

The example intentionally makes BM25 fail. The expected behavior is to print a fallback message and return the dense results.

**Production note:** `return_exceptions=True` also captures cancellation-related exceptions as result values. For a real application, handle cancellation deliberately and do not accidentally suppress `asyncio.CancelledError`. Prefer a clear policy for which failures permit partial retrieval and which must fail the whole request. An overall request deadline is also advisable.

---

## Common mistakes

| Mistake | Symptom | Fix |
|---|---|---|
| Missing `await` | “Coroutine was never awaited” warning or missing work | Await the coroutine or schedule it as a task |
| `time.sleep()` or synchronous HTTP calls inside `async def` | Other work on the event loop stalls | Use `asyncio.sleep()`, an async client, or `to_thread()` when appropriate |
| `await a(); await b()` when both operations are independent | Waiting times add up | Use `gather()` or `TaskGroup` |
| Launching thousands of calls at once | Rate-limit errors, memory spikes | Use a semaphore, batches, or bounded worker queue |
| No timeout | Slow dependencies hold up requests | Use `wait_for()` or `asyncio.timeout()` |
| Creating a new HTTP client for every operation | Connection overhead and possible socket exhaustion | Reuse a client with a deliberate lifecycle |
| Creating tasks without keeping track of them | Lost results, unobserved exceptions, unclear shutdown | Own tasks in a `TaskGroup` or retain and supervise task references |
| Shared mutable state across tasks | Race conditions or inconsistent state | Prefer return values or queues; use `asyncio.Lock` when necessary |
| Assuming async speeds up CPU-heavy work | Little or no performance gain | Use batching, native code, processes, or a worker service |
| Retrying every exception | More failures, latency, and cost | Retry only suitable transient failures with a bounded policy |

---

## Topics to skip initially

You can usually defer these while learning to build RAG apps:

- Low-level event-loop APIs such as `loop.run_until_complete()` and `call_soon()`.
- Creating `Future` objects directly.
- Transports and protocols.
- `asyncio.subprocess`.
- `asyncio.Condition` and `asyncio.Barrier`.
- Custom event-loop policies and advanced loop tuning.

Learn them when you have a concrete use case.

## Trade-offs

- **Speed versus complexity:** Async can improve throughput and latency for I/O-heavy systems, but debugging and stack traces can be more complex.
- **`gather()` versus `TaskGroup`:** Choose based on failure semantics and whether partial results are acceptable.
- **Concurrency versus provider limits:** More concurrent calls may improve latency until rate limits or resource saturation occur.
- **Timeouts:** Too-short deadlines cause false failures; too-long deadlines tie up resources. Measure real latency and define service-specific budgets.
- **Retries versus cost and latency:** Every retry consumes time and may consume API quota. Bound retries and retry only transient failures.
- **Blocking code:** One blocking call can stall the event loop. Every dependency should have a suitable async interface or a deliberate offloading strategy.

## Interview explanation

> `asyncio` allows many I/O-bound operations to make progress concurrently on one thread. When a coroutine reaches an `await` that suspends, the event loop can run other ready tasks while the awaited operation is pending. In RAG, I can use `gather()` or `TaskGroup` to run dense and BM25 retrieval concurrently, a `Semaphore` to cap concurrent embedding requests, and `wait_for()` or `asyncio.timeout()` to enforce time limits. For ingestion, a bounded `Queue` with worker tasks provides backpressure, while async generators can stream LLM output through FastAPI. Async does not automatically speed up CPU-bound work, and blocking synchronous calls inside `async def` can freeze the event loop, so I use native async clients or `asyncio.to_thread()` where appropriate. I also handle cancellation, transient retries, and partial failures deliberately.

---

## Quick reference

```python
# Start a standalone async program
asyncio.run(main())

# Await a coroutine
result = await some_coroutine()

# Run independent operations concurrently
a, b = await asyncio.gather(task_a(), task_b())

# Manage related concurrent tasks
async with asyncio.TaskGroup() as tg:
    a = tg.create_task(task_a())
    b = tg.create_task(task_b())

# Limit concurrent work
sem = asyncio.Semaphore(5)
async with sem:
    await call_service()

# Timeout one operation
await asyncio.wait_for(call_service(), timeout=2)

# Timeout a whole block (Python 3.11+)
async with asyncio.timeout(5):
    await step_one()
    await step_two()

# Process completions as they arrive
for completed in asyncio.as_completed(tasks):
    result = await completed

# Run blocking synchronous code in a thread
result = await asyncio.to_thread(blocking_function, argument)

# Bounded producer-consumer queue
queue = asyncio.Queue(maxsize=100)

# Consume an async stream
async for chunk in async_generator():
    process(chunk)
```

**Phase 0.1 completion goal:** You should be able to explain coroutines and the event loop, choose between `gather()` and `TaskGroup`, bound concurrency, apply timeouts, process streaming output, and build a small concurrent retrieval pipeline with deliberate failure handling.
