from functools import partial

from scripts.client_server_experiment import ClientServerExperiment, main
from scripts.packet_latency.evaluate import evaluate
from scripts.packet_latency.plot import plot

PacketLatencyExperiment = partial(ClientServerExperiment,
                                  post_run_fn=evaluate,
                                  post_experiment_fn=plot)

if __name__ == '__main__':
    main(PacketLatencyExperiment, config_file='packet_latency/config.yml')
