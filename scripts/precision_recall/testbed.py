from functools import partial

from scripts.client_server_testbed import ClientServerTestbed, main
from scripts.precision_recall.evaluate import evaluate
from scripts.precision_recall.plot import plot

PrecisionRecallTestbed = partial(ClientServerTestbed,
                                 post_run_fn=evaluate,
                                 post_experiment_fn=plot)

if __name__ == '__main__':
    main(PrecisionRecallTestbed, config_file='precision_recall/config.yml')
