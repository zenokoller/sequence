from unittest import TestCase

import pandas as pd

from experiments.rtt.square_wave import signals_from_flow, rtts_from_signal
from experiments.test.utils import load_dataframe

STORE_PATH = 'resources/test_flow.hdf5'

EXPECTED_SIGNAL_BITS = tuple([bool(val) for val in signal] for signal in (
    [1, 0, 1, 0],
    [0, 1, 0, 1, 1, 0]
))

EXPECTED_RTT = pd.Timestamp('2008-03-28 23:22:20.670131') - pd.Timestamp(
    '2008-03-28 23:22:20.562603')


class TestRTTsFromSquareWave(TestCase):
    def setUp(self):
        self.flow_df = load_dataframe(STORE_PATH, 'test_flow')
        self.flow_df.set_index('timestamp')

    def test_signals_from_flow(self):
        signals = signals_from_flow(self.flow_df)
        actual_signal_bits = tuple([dp.spin_bit for dp in signal] for signal in signals)
        self.assertEqual(actual_signal_bits, EXPECTED_SIGNAL_BITS, 'Actual signal bits do not '
                                                                   'match expected signal bits!')

    def test_rtts_from_signal(self):
        _, down_signal = signals_from_flow(self.flow_df)
        rtt_df = rtts_from_signal('test_flow', down_signal)
        self.assertEqual(rtt_df.iloc[0].rtt, EXPECTED_RTT,
                         'Actual RTT does not match expected RTT!')
