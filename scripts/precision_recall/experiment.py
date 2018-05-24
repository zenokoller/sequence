from functools import partial

from scripts.client_server_experiment import ClientServerExperiment, main
from scripts.precision_recall.evaluate import evaluate
from scripts.precision_recall.plot import plot

PrecisionRecallExperiment = partial(ClientServerExperiment,
                                    post_run_fn=evaluate,
                                    post_experiment_fn=plot)

if __name__ == '__main__':
    main(PrecisionRecallExperiment, config_file='precision_recall/config.yml')
