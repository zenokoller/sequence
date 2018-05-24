from functools import partial

from scripts.client_server_experiment import ClientServerExperiment, main
from scripts.loss_detector.evaluate import evaluate
from scripts.loss_detector.plot import plot

LossDetectorExperiment = partial(ClientServerExperiment,
                                 post_run_fn=evaluate,
                                 post_experiment_fn=plot)

if __name__ == '__main__':
    main(LossDetectorExperiment, config_file='loss_detector/config.yml')
