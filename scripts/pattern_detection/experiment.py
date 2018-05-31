from functools import partial

from scripts.client_server_experiment import ClientServerExperiment, main
from scripts.pattern_detection.evaluate import evaluate
from scripts.pattern_detection.plot import plot

PatternDetectionExperiment = partial(ClientServerExperiment,
                                     post_run_fn=evaluate,
                                     post_experiment_fn=plot)

if __name__ == '__main__':
    main(PatternDetectionExperiment, config_file='pattern_detection/config.yml')
