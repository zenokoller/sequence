import asyncio

from nodes.server import loop


def cancel_pending_tasks():
    pending = asyncio.Task.all_tasks()
    try:
        for task in pending:
            task.cancel()
        loop.run_until_complete(asyncio.gather(*pending))
    except:
        pass
