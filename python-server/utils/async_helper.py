import asyncio
import logging
import nest_asyncio

logger = logging.getLogger(__name__)

def run_async_in_sync(coroutine):
    """
    Helper to run an async coroutine synchronously.
    Handles cases where an event loop is already running (e.g., in tests or some frameworks)
    by applying nest_asyncio, or creates a new loop if none exists.
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if loop.is_running():
        # Apply nest_asyncio to allow nested event loops
        nest_asyncio.apply(loop)
        return loop.run_until_complete(coroutine)
    else:
        return loop.run_until_complete(coroutine)
