"""休伯利安分段预检的边界测试。"""
import unittest

import numpy as np

from hyperion_litematic_preflight import segment_geometry, unpack_batches


def pack_indices(indices, bits):
    words = [0] * ((len(indices) * bits + 63) // 64)
    mask = (1 << 64) - 1
    for index, value in enumerate(indices):
        position = index * bits
        word = position >> 6
        shift = position & 63
        words[word] |= (value << shift) & mask
        if shift + bits > 64:
            words[word + 1] |= value >> (64 - shift)
    return np.asarray(words, dtype=np.uint64)


class HyperionPreflightTest(unittest.TestCase):
    def test_unpack_crosses_word_and_batch_boundaries(self):
        expected = [(index * 37 + 9) % 114 for index in range(53)]
        packed = pack_indices(expected, 7)
        actual = [
            int(value)
            for _, batch in unpack_batches(packed, len(expected), 7, 5)
            for value in batch
        ]
        self.assertEqual(expected, actual)

    def test_segment_grid_covers_partial_edges_once(self):
        grid, segments = segment_geometry(17, 2, 17, 16)
        self.assertEqual((2, 1, 2), grid)
        self.assertEqual(4, len(segments))
        self.assertEqual(17 * 2 * 17, sum(segment["cells"] for segment in segments))
        self.assertEqual([16, 16, 1, 1], [segment["size"][0] for segment in segments])
        self.assertEqual(16 * 16 * 2, segments[0]["cells"])
        self.assertEqual(1 * 2 * 1, segments[-1]["cells"])


if __name__ == "__main__":
    unittest.main()
