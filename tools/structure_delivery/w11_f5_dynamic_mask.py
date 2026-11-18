import gzip
import struct

import numpy as np


def write_dynamic_mask(path, layers, low):
    selected = layers[layers[:, 0] > 1]
    xyz = selected[:, 3:6]-low
    high = (xyz+np.c_[selected[:, 6]-1, np.zeros(len(selected), int), selected[:, 7]-1]).max(0)
    size = high//16+1
    rows = np.zeros((int(np.prod(size)), 64), np.uint64)
    count = int(np.sum(selected[:, 6].astype(np.int64)*selected[:, 7]))
    for record, point in zip(selected, xyz):
        x, y, z = map(int, point)
        for xx in range(x, x+int(record[6])):
            zz = np.arange(z, z+int(record[7]))
            owner = ((xx >> 4)*size[1]+(y >> 4))*size[2]+(zz >> 4)
            bit = (((y&15)*16+(zz&15))*16+(xx&15)).astype(np.uint64)
            np.bitwise_or.at(rows, (owner, (bit >> 6).astype(int)), np.left_shift(np.uint64(1), bit&63))
    occupied = np.flatnonzero(np.any(rows, axis=1))
    sx, sy, sz = occupied//(size[1]*size[2]), occupied//size[2]%size[1], occupied%size[2]
    keys = (sx << 38)|(sz << 12)|sy
    with gzip.GzipFile(filename='', fileobj=path.open('wb'), mode='wb', compresslevel=6, mtime=0) as stream:
        stream.write(struct.pack('>2i', 0x5731314d, len(occupied)))
        for i in np.argsort(keys):
            stream.write(struct.pack('>q', int(keys[i])))
            stream.write(rows[occupied[i]].astype('>u8').tobytes())
    return count, len(occupied)
