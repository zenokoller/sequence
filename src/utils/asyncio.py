import asyncio


def cancel_pending_tasks():
    loop = asyncio.get_event_loop()
    pending = asyncio.Task.all_tasks()
    try:
        for task in pending:
            task.cancel()
        loop.run_until_complete(asyncio.gather(*pending))
    except:
        pass
