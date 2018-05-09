from reporter.json_reporter import JsonReporter
from reporter.reporter import Reporter

reporters = {
    'json': JsonReporter
}


def get_reporter(name: str, *args, **kwargs) -> Reporter:
    reporter_cls = reporters[name]
    return reporter_cls(*args, **kwargs)
