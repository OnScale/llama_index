"""Async utils."""
import asyncio
from itertools import zip_longest
from typing import Any, Coroutine, Iterable, List


def run_async_tasks(
    tasks: List[Coroutine],
    show_progress: bool = False,
    progress_bar_desc: str = "Running async tasks",
) -> List[Any]:
    """Run a list of async tasks."""
    tasks_to_execute: List[Any] = tasks

    try:
        # Try importing and applying nest_asyncio
        import nest_asyncio
        nest_asyncio.apply()
    except ImportError:
        # If nest_asyncio can't be imported, we'll just continue
        # (this assumes that the environment does not have any event loop issues)
        pass

    # Get the existing event loop or create a new one
    loop = asyncio.get_event_loop()

    if show_progress:
        try:
            from tqdm.asyncio import tqdm

            async def _tqdm_gather() -> List[Any]:
                return await tqdm.gather(*tasks_to_execute, desc=progress_bar_desc)

            tqdm_outputs: List[Any] = loop.run_until_complete(_tqdm_gather())
            return tqdm_outputs
        # Run the operation without tqdm if there's an exception
        # This might occur in environments where tqdm.asyncio is not supported
        except Exception:
            pass

    async def _gather() -> List[Any]:
        return await asyncio.gather(*tasks_to_execute)

    outputs: List[Any] = loop.run_until_complete(_gather())
    return outputs


def chunks(iterable: Iterable, size: int) -> Iterable:
    args = [iter(iterable)] * size
    return zip_longest(*args, fillvalue=None)


async def batch_gather(
    tasks: List[Coroutine], batch_size: int = 10, verbose: bool = False
) -> List[Any]:
    output: List[Any] = []
    for task_chunk in chunks(tasks, batch_size):
        output_chunk = await asyncio.gather(*task_chunk)
        output.extend(output_chunk)
        if verbose:
            print(f"Completed {len(output)} out of {len(tasks)} tasks")
    return output
