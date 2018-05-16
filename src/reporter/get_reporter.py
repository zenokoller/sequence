from reporter.http_reporter import HttpReporter
from reporter.influx_reporter import InfluxReporter
from reporter.reporter import Reporter


reporters = {
    'http': HttpReporter,
    'influx': InfluxReporter
}


def get_reporter(name: str, *args, **kwargs) -> Reporter:
    reporter_cls = reporters[name]
    return reporter_cls(*args, **kwargs)
