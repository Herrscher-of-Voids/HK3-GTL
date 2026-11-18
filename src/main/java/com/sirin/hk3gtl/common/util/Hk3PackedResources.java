package com.sirin.hk3gtl.common.util;

import java.io.BufferedInputStream;
import java.io.DataInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.zip.GZIPInputStream;
import org.tukaani.xz.XZInputStream;

public final class Hk3PackedResources extends InputStream {
    private final DataInputStream input;
    private final int width;
    private final boolean delta;
    private final byte[] packed, decoded;
    private int cursor, limit;
    private boolean ended;

    private Hk3PackedResources(InputStream input) throws IOException {
        this.input = new DataInputStream(input);
        width = this.input.readUnsignedByte();
        delta = this.input.readBoolean();
        if (width < 1 || width > 18) throw new IOException("压缩资源记录宽度错误");
        packed = new byte[width * 65536];
        decoded = new byte[packed.length];
    }

    public static String xzPath(String gzipPath) {
        return gzipPath.substring(0, gzipPath.length() - 3) + ".xz";
    }

    public static InputStream resource(Class<?> owner, String gzipPath) {
        var gzip = owner.getResourceAsStream(gzipPath);
        return gzip != null ? gzip : owner.getResourceAsStream(xzPath(gzipPath));
    }

    public static BufferedInputStream decompress(InputStream compressed) throws IOException {
        var source = new BufferedInputStream(compressed, 65536);
        source.mark(1);
        boolean xz = source.read() == 0xfd;
        source.reset();
        return new BufferedInputStream(xz ? new XZInputStream(source) : new GZIPInputStream(source, 65536), 65536);
    }

    public static InputStream open(InputStream compressed) throws IOException {
        var input = decompress(compressed);
        input.mark(4);
        if (new DataInputStream(input).readInt() == 0x484B335A) return new Hk3PackedResources(input);
        input.reset();
        return input;
    }

    private boolean fill() throws IOException {
        if (ended) return false;
        limit = input.readInt();
        cursor = 0;
        if (limit == 0) {
            if (input.read() != -1) throw new IOException("压缩资源存在尾随数据");
            ended = true;
            return false;
        }
        if (limit < 0 || limit > decoded.length) throw new IOException("压缩资源分块长度错误");
        input.readFully(packed, 0, limit);
        int rows = limit / width, body = rows * width;
        for (int column = 0; column < width; column++) {
            int value = 0;
            for (int row = 0; row < rows; row++) {
                int next = packed[column * rows + row] & 255;
                value = delta ? (value + next) & 255 : next;
                decoded[row * width + column] = (byte) value;
            }
        }
        System.arraycopy(packed, body, decoded, body, limit - body);
        return true;
    }

    @Override public int read() throws IOException {
        if (cursor == limit && !fill()) return -1;
        return decoded[cursor++] & 255;
    }

    @Override public int read(byte[] bytes, int offset, int length) throws IOException {
        if (length == 0) return 0;
        if (cursor == limit && !fill()) return -1;
        int count = Math.min(length, limit - cursor);
        System.arraycopy(decoded, cursor, bytes, offset, count);
        cursor += count;
        return count;
    }

    @Override public void close() throws IOException { input.close(); }
}
