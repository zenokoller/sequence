from functools import partial

from scripts.client_server_experiment import ClientServerExperiment, main
from scripts.detector.reordering import evaluate
from scripts.detector import plot

ReorderingDetectorExperiment = partial(ClientServerExperiment,
                                       post_run_fn=evaluate,
                                       post_experiment_fn=plot)

if __name__ == '__main__':
    main(ReorderingDetectorExperiment, config_file='detector/reordering/config.yml')
