from unittest import TestCase

from utils.symbol_buffer import ByteBuffer, SymbolBuffer


class TestSymbolBuffer(TestCase):

    def test_overflow(self):
        buffer = SymbolBuffer(size=3)
        for i in [3, 1, 2, 0, 3, 2, 0, 1]:
            buffer.add_next(i)
        actual = buffer.as_list()
        expected = [0, 1, 2]
        self.assertEqual(expected, actual, 'Unexpected buffer values.')

    def test_is_full(self):
        buffer = SymbolBuffer(size=3)
        actual = []
        for i in [3, 1, 2, 0, 3, 2, 0, 1]:
            buffer.add_next(i)
            actual.append(buffer.is_full)
        expected = list(map(bool, [0, 0, 1, 0, 0, 1, 0, 0]))
        self.assertEqual(expected, actual, 'Incorrect reporting of buffer fullness.')

    def test_copy_byte_buffer(self):
        buffer = ByteBuffer(size=5)
        for i in [3, 1, 2, 0, 3, 2, 0, 1]:
            buffer.add_next(i)
        actual = buffer.as_list()
        expected = [0xd8, 0x63, 0x8e, 0x38, 0xe1]
        self.assertEqual(expected, actual, 'Buffer not filled as expected.')
