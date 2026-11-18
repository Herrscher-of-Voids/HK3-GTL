package com.sirin.hk3gtl.common.machine.hyperion;

import java.io.DataInputStream;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.util.Arrays;
import java.util.zip.GZIPInputStream;

public final class Hk3HyperionInterior {
    private static final Hk3HyperionInterior INSTANCE = load();
    private final int[] starts;
    private final int[] ends;

    private Hk3HyperionInterior(int count) {
        starts = new int[count];
        ends = new int[count];
    }

    static boolean contains(int x, int y, int z) {
        int cell = (y * 549 + z) * 1145 + x;
        int run = Arrays.binarySearch(INSTANCE.starts, cell);
        if (run < 0) run = -run - 2;
        return run >= 0 && cell <= INSTANCE.ends[run];
    }

    public static java.util.BitSet movementVolume() {
        var volume = new java.util.BitSet(1145 * 549 * 240);
        for (int i = 0; i < INSTANCE.starts.length; i++) volume.set(INSTANCE.starts[i], INSTANCE.ends[i] + 1);
        return volume;
    }

    private static Hk3HyperionInterior load() {
        try (var input = new DataInputStream(new GZIPInputStream(Hk3HyperionInterior.class
                .getResourceAsStream("/data/hk3gtl/structures/hyperion_interior.bin.gz")))) {
            var interior = new Hk3HyperionInterior(input.readInt());
            for (int i = 0; i < interior.starts.length; i++) {
                interior.starts[i] = input.readInt();
                interior.ends[i] = input.readInt();
            }
            return interior;
        } catch (IOException failure) {
            throw new UncheckedIOException(failure);
        }
    }
}
