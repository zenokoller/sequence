from functools import partial

from scripts.client_server_testbed import ClientServerTestbed, main
from scripts.packet_latency.evaluate import evaluate
from scripts.packet_latency.plot import plot

PacketLatencyTestbed = partial(ClientServerTestbed,
                               post_run_fn=evaluate,
                               post_experiment_fn=plot)

if __name__ == '__main__':
    main(PacketLatencyTestbed, config_file='packet_latency/config.yml')
