from functools import partial

from scripts.client_server_testbed import ClientServerTestbed, main
from scripts.loss_detector.evaluate import evaluate
from scripts.loss_detector.plot import plot

LossDetectorTestbed = partial(ClientServerTestbed,
                              post_run_fn=evaluate,
                              post_experiment_fn=plot)

if __name__ == '__main__':
    main(LossDetectorTestbed, config_file='loss_detector/config.yml')
