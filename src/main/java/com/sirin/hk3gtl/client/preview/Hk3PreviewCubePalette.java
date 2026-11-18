package com.sirin.hk3gtl.client.preview;

import com.lowdragmc.lowdraglib.client.model.custommodel.LDLMetadataSection;
import com.lowdragmc.lowdraglib.client.model.custommodel.CustomBakedModel;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.block.model.BakedQuad;
import net.minecraft.client.renderer.texture.TextureAtlasSprite;
import net.minecraft.client.resources.model.SimpleBakedModel;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.BlockAndTintGetter;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.client.model.data.ModelData;

import java.util.IdentityHashMap;
import java.util.HashSet;
import java.util.Set;

/** 仅捕获确定为标准实体立方体的真实烘焙面；其余模型交还原渲染器。 */
final class Hk3PreviewCubePalette {
    private static final Set<BlockState> REPORTED = new HashSet<>();
    record Face(float[] vertices, float[] bounds, int uAxis, int vAxis, int color, float[] ctmTiles) {}
    final Face[][] faces;
    final Hk3PreviewCtmFace[][] ctmFaces;
    final BlockState[] states;
    final boolean[] occluding;

    Hk3PreviewCubePalette(BlockState[] states, BlockAndTintGetter world) {
        this.states = states;
        faces = new Face[states.length][];
        ctmFaces = new Hk3PreviewCtmFace[states.length][];
        occluding = new boolean[states.length];
        var models = Minecraft.getInstance().getBlockRenderer().getBlockModelShaper();
        var opaqueSprites = new IdentityHashMap<TextureAtlasSprite, Boolean>();
        for (int i = 0; i < states.length; i++) {
            var state = states[i];
            occluding[i] = state.canOcclude() && !state.getBlock().hasDynamicShape()
                    && state.isSolidRender(world, BlockPos.ZERO);
            var renderedModel = models.getBlockModel(state);
            var model = renderedModel;
            boolean customModel = false;
            var chain = new StringBuilder(model.getClass().getName());
            while (model instanceof CustomBakedModel
                    || model.getClass().getName().equals("org.gtlcore.gtlcore.client.bloom.EmissiveAliases$Model")) {
                if (model instanceof CustomBakedModel custom) {
                    customModel = true;
                    model = Hk3PreviewCtmFace.parent(custom);
                } else model = Hk3PreviewCtmFace.delegate(model);
                chain.append(" -> ").append(model.getClass().getName());
            }
            if (!occluding[i] || state.hasBlockEntity() || !state.getFluidState().isEmpty()) {
                report(state, chain, "未查询", "非静态不透明实体"); continue;
            }
            if (!(model instanceof SimpleBakedModel)) {
                report(state, chain, "未查询", "非标准父模型"); continue;
            }
            var layers = renderedModel.getRenderTypes(state, RandomSource.create(42), ModelData.EMPTY).asList();
            if (layers.size() != 1) {
                report(state, chain, layers, "渲染层数量=" + layers.size()); continue;
            }
            var layer = layers.get(0);
            if (layer != RenderType.solid() && layer != RenderType.cutout() && layer != RenderType.cutoutMipped()) {
                report(state, chain, layer, "不支持的渲染层"); continue;
            }
            if (!renderedModel.getQuads(state, null, RandomSource.create(42), ModelData.EMPTY, layer).isEmpty()) {
                report(state, chain, layer, "存在不定向面"); continue;
            }
            Face[] candidate = new Face[6];
            var connectedFaces = new Hk3PreviewCtmFace[6];
            boolean cube = true;
            String result = "接受";
            for (var direction : Direction.values()) {
                var quads = renderedModel.getQuads(state, direction, RandomSource.create(42), ModelData.EMPTY, layer);
                if (quads.size() != 1) { cube = false; result = direction + "面数量=" + quads.size(); break; }
                var quad = quads.get(0);
                if (quad.getSprite() != model.getQuads(state, direction, RandomSource.create(42), ModelData.EMPTY, layer).get(0).getSprite()) {
                    cube = false; result = direction + "外包装已替换自发光贴图"; break;
                }
                var metadata = LDLMetadataSection.getMetadata(quad.getSprite());
                boolean connected = metadata.connection != null;
                if (metadata.emissive) { cube = false; result = direction + "自发光元数据"; break; }
                if (connected && !customModel) { cube = false; result = direction + "连接贴图缺少LDLib模型"; break; }
                if ((connected || layer != RenderType.solid())
                        && !opaqueSprites.computeIfAbsent(quad.getSprite(), Hk3PreviewCubePalette::opaque)) {
                    cube = false; result = direction + "源贴图含透明像素"; break;
                }
                if (connected && !opaqueSprites.computeIfAbsent(LDLMetadataSection.getConnection(quad.getSprite()), Hk3PreviewCubePalette::opaque)) {
                    cube = false; result = direction + "连接贴图含透明像素"; break;
                }
                var face = face(quad, direction, world);
                if (face == null) { cube = false; result = direction + "非完整无染色标准面"; break; }
                candidate[direction.ordinal()] = face;
                if (connected) connectedFaces[direction.ordinal()] = new Hk3PreviewCtmFace(face, quad);
            }
            if (cube) { faces[i] = candidate; ctmFaces[i] = connectedFaces; }
            report(state, chain, layer, result);
        }
    }

    private static void report(BlockState state, StringBuilder chain, Object layer, String result) {
        if (REPORTED.add(state)) com.mojang.logging.LogUtils.getLogger().info(
                "自家预览材质捕获：{}，模型链={}，层={}，结果={}", state, chain, layer, result);
    }

    private static boolean opaque(TextureAtlasSprite sprite) {
        var image = sprite.contents().getOriginalImage();
        for (int y = 0; y < image.getHeight(); y++)
            for (int x = 0; x < image.getWidth(); x++)
                if (image.getPixelRGBA(x, y) >>> 24 != 255) return false;
        return true;
    }

    private static Face face(BakedQuad quad, Direction direction, BlockAndTintGetter world) {
        if (quad.isTinted() || quad.getDirection() != direction) return null;
        int[] raw = quad.getVertices();
        int stride = raw.length / 4, axis = direction.getAxis().ordinal();
        float plane = direction.getAxisDirection() == Direction.AxisDirection.POSITIVE ? 1 : 0;
        float[] vertices = new float[20];
        float minU = Float.POSITIVE_INFINITY, minV = Float.POSITIVE_INFINITY;
        float maxU = Float.NEGATIVE_INFINITY, maxV = Float.NEGATIVE_INFINITY;
        int corners = 0;
        for (int i = 0; i < 4; i++) {
            int corner = 0;
            for (int a = 0; a < 3; a++) {
                float value = Float.intBitsToFloat(raw[i * stride + a]);
                if (a == axis ? value != plane : value != 0 && value != 1) return null;
                vertices[i * 5 + a] = value;
                if (value == 1) corner |= 1 << a;
            }
            corners |= 1 << corner;
            if (raw[i * stride + 3] != raw[3]) return null;
            float u = Float.intBitsToFloat(raw[i * stride + 4]);
            float v = Float.intBitsToFloat(raw[i * stride + 5]);
            vertices[i * 5 + 3] = u; vertices[i * 5 + 4] = v;
            minU = Math.min(minU, u); maxU = Math.max(maxU, u);
            minV = Math.min(minV, v); maxV = Math.max(maxV, v);
        }
        if (Integer.bitCount(corners) != 4 || minU == maxU || minV == maxV) return null;
        int uvCorners = 0;
        for (int i = 0; i < 4; i++) {
            float u = (vertices[i * 5 + 3] - minU) / (maxU - minU);
            float v = (vertices[i * 5 + 4] - minV) / (maxV - minV);
            if ((u != 0 && u != 1) || (v != 0 && v != 1)) return null;
            vertices[i * 5 + 3] = u; vertices[i * 5 + 4] = v;
            uvCorners |= 1 << ((int) u * 2 + (int) v);
        }
        if (uvCorners != 15) return null;
        int uAxis = uvAxis(vertices, 3), vAxis = uvAxis(vertices, 4);
        if (uAxis < 0 || vAxis < 0 || uAxis == vAxis) return null;
        float shade = world.getShade(direction, quad.isShade());
        int rgba = raw[3];
        int color = (int) ((rgba & 255) * shade) | (int) ((rgba >>> 8 & 255) * shade) << 8
                | (int) ((rgba >>> 16 & 255) * shade) << 16 | rgba & 0xff000000;
        return new Face(vertices, new float[]{minU, minV, maxU, maxV}, uAxis, vAxis, color, null);
    }

    private static int uvAxis(float[] vertices, int uv) {
        for (int i = 1; i < 4; i++) {
            if (vertices[i * 5 + uv] == vertices[uv] || vertices[i * 5 + 7 - uv] != vertices[7 - uv]) continue;
            int result = -1;
            for (int axis = 0; axis < 3; axis++) if (vertices[i * 5 + axis] != vertices[axis]) {
                if (result >= 0) return -1;
                result = axis;
            }
            return result;
        }
        return -1;
    }
}
