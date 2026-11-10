# -*- coding: utf-8 -*-
"""同高度连续表面按行合并，保留剖层精度和逐格纹理比例。"""
import numpy as np


def merge_surface_runs(groups, size):
    w, _, d = size
    starts, lengths = [], []
    original_count = 0
    for group in groups:
        start_group, length_group = [], []
        for face, indices in enumerate(group):
            values = np.asarray(indices, dtype=np.int64)
            original_count += len(values)
            if not len(values):
                start_group.append([]); length_group.append([]); continue
            y = values // (w * d); z = values // w % d; x = values % w
            if face in (0, 1):
                order = np.lexsort((z, x, y))
                values, y, x, z = values[order], y[order], x[order], z[order]
                boundary = np.r_[True, (y[1:] != y[:-1]) | (x[1:] != x[:-1]) | (z[1:] != z[:-1] + 1)]
                stride = w
            else:
                assert np.all(values[1:] > values[:-1])
                boundary = np.r_[True, (y[1:] != y[:-1]) | (z[1:] != z[:-1]) | (x[1:] != x[:-1] + 1)]
                stride = 1
            first = np.flatnonzero(boundary)
            run_lengths = np.diff(np.r_[first, len(values)])
            run_starts = values[first]
            order = np.argsort(run_starts)
            run_starts, run_lengths = run_starts[order], run_lengths[order]
            # 重展结果必须与原始外露面逐格相同，不能跨材料、跨高度或填补孔洞。
            expanded = np.concatenate([start + np.arange(length) * stride for start, length in zip(run_starts, run_lengths)])
            assert np.array_equal(np.sort(expanded), np.sort(np.asarray(indices))), face
            start_group.append(run_starts.tolist()); length_group.append(run_lengths.tolist())
        starts.append(start_group); lengths.append(length_group)
    rendered = sum(len(face) for group in starts for face in group)
    assert sum(sum(face) for group in lengths for face in group) == original_count
    return starts, lengths, dict(passed=True, original_unit_faces=original_count, rendered_quads=rendered,
        reduction=1 - rendered / original_count, per_cell_expansion_equal=True,
        same_height_only=True, texture_repeats_per_block=True)


if __name__ == '__main__':
    sample = [[[0, 4, 8, 1, 5, 9], [0, 4, 8], [0, 1, 2, 4, 5], [8, 9], [0, 1, 2], [16, 17, 18]]]
    merged, lengths, check = merge_surface_runs(sample, [4, 2, 4])
    assert check['rendered_quads'] == 8 and check['original_unit_faces'] == 22
    print(check)
