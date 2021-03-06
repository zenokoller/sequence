import asyncio

from reporter.accumulators.count import count_accumulator
from reporter.accumulators.pattern import pattern_accumulator
from reporter.accumulators.rate import rate_accumulator

from reporter.silent_reporter import SilentReporter
from reporter.http_reporter import HttpReporter
from reporter.influx_reporter import InfluxReporter
from reporter.reporter import Reporter

reporters = {
    'default': SilentReporter,
    'http': HttpReporter,
    'influx': InfluxReporter,
}

accumulators = {
    'count': count_accumulator,
    'rate': rate_accumulator,
    'pattern': pattern_accumulator,
}


def create_reporter(name: str, *args, **kwargs) -> Reporter:
    reporter_cls = reporters.get(name, SilentReporter)
    return reporter_cls(*args, **kwargs) if len(args) > 0 else reporter_cls(**kwargs)


def start_reporter(reporter: Reporter) -> asyncio.Queue:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(reporter.setup())
    reporter_queue = asyncio.Queue()
    _ = asyncio.ensure_future(reporter.run(reporter_queue))
    return reporter_queue
