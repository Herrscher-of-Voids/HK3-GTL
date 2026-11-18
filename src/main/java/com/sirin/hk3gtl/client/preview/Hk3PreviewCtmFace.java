package com.sirin.hk3gtl.client.preview;

import com.lowdragmc.lowdraglib.client.bakedpipeline.Quad;
import com.lowdragmc.lowdraglib.client.bakedpipeline.Submap;
import com.lowdragmc.lowdraglib.client.model.custommodel.CustomBakedModel;
import com.lowdragmc.lowdraglib.client.model.custommodel.LDLMetadataSection;
import net.minecraft.client.renderer.block.model.BakedQuad;
import net.minecraft.client.resources.model.BakedModel;
import net.minecraftforge.client.model.BakedModelWrapper;

import java.lang.reflect.Field;

/** 在渲染线程捕获真实四分面UV，后台只选择已捕获的连接图样。 */
final class Hk3PreviewCtmFace {
    private final Hk3PreviewCubePalette.Face base;
    private final float[][][] tiles = new float[4][20][];
    private final int[] quarters = new int[4];

    Hk3PreviewCtmFace(Hk3PreviewCubePalette.Face base, BakedQuad source) {
        this.base = base;
        var connected = LDLMetadataSection.getConnection(source.getSprite());
        var vertices = base.vertices();
        int uAxis = base.uAxis(), vAxis = base.vAxis();
        float uSign = slope(vertices, uAxis, 3), vSign = slope(vertices, vAxis, 4);
        float uOrigin = vertices[3] - vertices[uAxis] * uSign;
        float vOrigin = vertices[4] - vertices[vAxis] * vSign;
        for (var part : Quad.from(source).derotate().subdivide(4)) {
            float midU = 0, midV = 0;
            for (int i = 0; i < 4; i++) {
                midU += uOrigin + part.getVert(i).get(uAxis) * uSign;
                midV += vOrigin + part.getVert(i).get(vAxis) * vSign;
            }
            int qx = (int) (midU / 2), qy = (int) (midV / 2), quadrant = qx + qy * 2;
            quarters[quadrant] = part.getUvs().normalize().getQuadrant();
            for (int submap = 0; submap < 20; submap++) {
                var sprite = submap > 15 ? source.getSprite() : connected;
                var quad = part.grow().transformUVs(sprite, Submap.uvs[submap]).rebake();
                int[] raw = quad.getVertices();
                int stride = raw.length / 4;
                int[] corners = new int[4];
                for (int i = 0; i < 4; i++) {
                    int u = Math.round((uOrigin + uv(raw, stride, i, uAxis) * uSign) * 2) - qx;
                    int v = Math.round((vOrigin + uv(raw, stride, i, vAxis) * vSign) * 2) - qy;
                    corners[u * 2 + v] = i;
                }
                float u0 = uv(raw, stride, corners[0], 4), v0 = uv(raw, stride, corners[0], 5);
                tiles[quadrant][submap] = new float[]{u0, v0,
                        uv(raw, stride, corners[2], 4) - u0, uv(raw, stride, corners[2], 5) - v0,
                        uv(raw, stride, corners[1], 4) - u0, uv(raw, stride, corners[1], 5) - v0};
            }
        }
    }

    Hk3PreviewCubePalette.Face connected(int pattern) {
        float[] selected = new float[24];
        for (int q = 0; q < 4; q++)
            System.arraycopy(tiles[q][pattern >>> (quarters[q] * 5) & 31], 0, selected, q * 6, 6);
        return new Hk3PreviewCubePalette.Face(base.vertices(), base.bounds(), base.uAxis(), base.vAxis(), base.color(), selected);
    }

    private static float slope(float[] vertices, int axis, int uv) {
        int adjacent = vertices[5 + axis] != vertices[axis] ? 5 : 15;
        return (vertices[adjacent + uv] - vertices[uv]) / (vertices[adjacent + axis] - vertices[axis]);
    }

    private static float uv(int[] raw, int stride, int vertex, int field) {
        return Float.intBitsToFloat(raw[vertex * stride + field]);
    }

    static BakedModel parent(CustomBakedModel model) {
        try { return (BakedModel) Parent.FIELD.get(model); }
        catch (IllegalAccessException failure) { throw new IllegalStateException(failure); }
    }

    static BakedModel delegate(BakedModel model) {
        try { return (BakedModel) Delegate.FIELD.get(model); }
        catch (IllegalAccessException failure) { throw new IllegalStateException(failure); }
    }

    private static final class Delegate {
        private static final Field FIELD;
        static {
            try {
                FIELD = BakedModelWrapper.class.getDeclaredField("originalModel");
                FIELD.setAccessible(true);
            } catch (NoSuchFieldException failure) { throw new ExceptionInInitializerError(failure); }
        }
    }

    private static final class Parent {
        private static final Field FIELD;
        static {
            try {
                FIELD = CustomBakedModel.class.getDeclaredField("parent");
                FIELD.setAccessible(true);
            } catch (NoSuchFieldException failure) { throw new ExceptionInInitializerError(failure); }
        }
    }
}
