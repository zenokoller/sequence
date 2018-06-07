from functools import partial

from scripts.client_server_experiment import ClientServerExperiment, main
from scripts.trace_only.evaluate import evaluate
from scripts.trace_only.plot import plot

TraceOnlyExperiment = partial(ClientServerExperiment,
                              post_run_fn=evaluate,
                              post_experiment_fn=plot)

if __name__ == '__main__':
    main(TraceOnlyExperiment, config_file='trace_only/config.yml')
