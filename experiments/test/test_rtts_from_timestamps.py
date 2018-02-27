from unittest import TestCase

import pandas as pd

from experiments.rtt.rtts_from_timestamps import rtts_from_flow
from experiments.test.utils import load_dataframe

STORE_PATH = 'resources/test_flow.hdf5'


class TestRTTsFromTimestamp(TestCase):
    def setUp(self):
        flow_df = load_dataframe(STORE_PATH, 'test_flow')
        flow_df.set_index('timestamp')
        self.rtt_df = rtts_from_flow(('test_flow', flow_df))

    def test_result_correctness(self):
        actual_rtt = self.rtt_df.iloc[0].rtt
        expected_rtt = pd.Timedelta('107528us')
        self.assertEqual(actual_rtt, expected_rtt,
                         'Expected RTT should be {expected_rtt}')

    def test_computed_rtt_count(self):
        actual_count = self.rtt_df.shape[0]
        expected_count = 7
        self.assertEqual(actual_count, expected_count,
                         'Expected count should be {expected_count}')
