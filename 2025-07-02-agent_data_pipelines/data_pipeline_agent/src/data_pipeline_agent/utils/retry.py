import asyncio
import random


async def retry_llm_call(llm_call, max_retries=5, base_delay=2, jitter=1):
    """
    Retry an async LLM call with exponential backoff on 503 errors.
    llm_call: a coroutine function (e.g., lambda: await llm.ainvoke(...))
    """
    for attempt in range(max_retries):
        try:
            return await llm_call()
        except Exception as e:
            msg = str(e)
            if "503" in msg or "overloaded" in msg:
                delay = base_delay * (2**attempt) + random.uniform(0, jitter)
                print(
                    f"Model overloaded (attempt {attempt + 1}/{max_retries}), retrying in {delay:.1f}s..."
                )
                await asyncio.sleep(delay)
            else:
                raise
    raise RuntimeError("Max retries exceeded for LLM call due to repeated overloads.")
