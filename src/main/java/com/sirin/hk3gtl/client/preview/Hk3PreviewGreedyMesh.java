package com.sirin.hk3gtl.client.preview;

import com.lowdragmc.lowdraglib.client.model.custommodel.Connections;
import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.BufferBuilder;
import com.mojang.blaze3d.vertex.DefaultVertexFormat;
import com.mojang.blaze3d.vertex.VertexBuffer;
import com.mojang.blaze3d.vertex.VertexFormat;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3W01HallLayout;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3W01PreviewIndex;
import it.unimi.dsi.fastutil.ints.IntArrayList;
import it.unimi.dsi.fastutil.longs.LongArrayList;
import it.unimi.dsi.fastutil.longs.LongComparators;
import it.unimi.dsi.fastutil.longs.LongOpenHashSet;
import it.unimi.dsi.fastutil.longs.Long2ObjectLinkedOpenHashMap;
import net.minecraft.client.renderer.ShaderInstance;
import net.minecraft.client.renderer.texture.TextureAtlas;
import net.minecraft.core.Direction;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.BlockAndTintGetter;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RegisterShadersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.joml.Matrix4f;

import java.util.ArrayList;
import java.util.List;

/** 全景标准方块合面；只按实际暴露面分配空间，复杂模型仍用完整原世界。 */
public final class Hk3PreviewGreedyMesh implements AutoCloseable {
    public record Captured(Hk3W01HallLayout layout, Hk3W01PreviewIndex index, Hk3PreviewCubePalette palette, BlockAndTintGetter world,
            java.util.function.Predicate<BlockPos> hidden,boolean hasHiddenCells) {}
    public record Batch(Hk3PreviewCubePalette.Face face, int axis, int[] rectangles) {}
    public record Prepared(List<Batch> batches, int[] fallbackCells, long sourceFaces, int mergedFaces) {}
    private record Uploaded(Hk3PreviewCubePalette.Face face, VertexBuffer buffer) {}
    private static ShaderInstance shader;
    private static int resourceGeneration;
    private final int generation = resourceGeneration;
    private final Prepared prepared;
    private final List<Uploaded> buffers = new ArrayList<>();
    private static final BufferBuilder builder = new BufferBuilder(65536);
    private int batchAt, rectangleAt, uploadedFaces;
    private boolean closed;

    public static Captured capture(Hk3W01HallLayout layout, Hk3W01PreviewIndex index,
            BlockState[] states, BlockAndTintGetter world) {
        return new Captured(layout,index,new Hk3PreviewCubePalette(states,world),world,pos->false,false);
    }

    public static Captured capture(Hk3W01HallLayout layout,Hk3W01PreviewIndex index,BlockState[] states,
            BlockAndTintGetter world,java.util.function.Predicate<BlockPos> hidden){
        return new Captured(layout,index,new Hk3PreviewCubePalette(states,world),world,hidden,true);
    }

    public static Prepared prepare(Captured captured) {
        var layout = captured.layout();
        var palette = captured.palette();
        var faces = new Long2ObjectLinkedOpenHashMap<LongArrayList>();
        var fallback = new IntArrayList();
        var position = new BlockPos.MutableBlockPos();
        var adjacent = new BlockPos.MutableBlockPos();
        boolean all = captured.hasHiddenCells();
        for (int cellIndex = all ? 0 : captured.index().nextVisibleCell(0);
                cellIndex >= 0 && cellIndex < layout.count();
                cellIndex = all ? cellIndex + 1 : captured.index().nextVisibleCell(cellIndex + 1)) {
            if (Thread.currentThread().isInterrupted()) throw new java.util.concurrent.CancellationException();
            long cell = layout.cell(cellIndex);
            int state = Hk3W01HallLayout.state(cell);
            int x = Hk3W01HallLayout.x(cell), y = Hk3W01HallLayout.y(cell), z = Hk3W01HallLayout.z(cell);
            position.set(x, y, z);
            if(captured.hidden().test(position))continue;
            if (palette.faces[state] == null || x == layout.controllerX() && y == layout.controllerY() && z == layout.controllerZ()) {
                fallback.add(cellIndex); continue;
            }
            for (var direction : Direction.values()) {
                int neighbor = captured.index().stateAt(x + direction.getStepX(), y + direction.getStepY(), z + direction.getStepZ());
                if (neighbor >= 0 && palette.occluding[neighbor] && !captured.hidden().test(adjacent.set(
                        x+direction.getStepX(),y+direction.getStepY(),z+direction.getStepZ()))) continue;
                int axis = direction.getAxis().ordinal(), sign = direction.getAxisDirection().getStep();
                int plane = axis == 0 ? x : axis == 1 ? y : z;
                int u = axis == 0 ? y : axis == 1 ? z : x;
                int v = axis == 0 ? z : axis == 1 ? x : y;
                int pattern = 0;
                if (palette.ctmFaces[state][direction.ordinal()] != null) {
                    var connections = Connections.checkConnections(captured.world(), position, palette.states[state], direction);
                    int[] submaps = connections.getSubmapIndices();
                    for (int q = 0; q < 4; q++) pattern |= submaps[q] << (q * 5);
                    pattern++;
                }
                long id = (long) (state * 6 + direction.ordinal()) << 21 | pattern;
                faces.computeIfAbsent(id, ignored -> new LongArrayList()).add(key(plane + (sign > 0 ? 1 : 0), u, v));
            }
            if (Thread.currentThread().isInterrupted()) throw new java.util.concurrent.CancellationException();
        }
        var batches = new ArrayList<Batch>();
        long sourceFaces = 0;
        int mergedFaces = 0;
        for (var entry : faces.long2ObjectEntrySet()) {
            var ordered = entry.getValue();
            sourceFaces += ordered.size();
            ordered.sort(LongComparators.NATURAL_COMPARATOR);
            var rectangles = new IntArrayList();
            var remaining = new LongOpenHashSet();
            for (int start = 0; start < ordered.size();) {
                if (Thread.currentThread().isInterrupted()) throw new java.util.concurrent.CancellationException();
                int end = start;
                long plane = ordered.getLong(start) >>> 32;
                while (end < ordered.size() && ordered.getLong(end) >>> 32 == plane) {
                    remaining.add(ordered.getLong(end++));
                }
                mergePlane(ordered, start, end, remaining, rectangles);
                start = end;
            }
            int id = (int) (entry.getLongKey() >>> 21), pattern = (int) (entry.getLongKey() & 0x1fffff);
            var direction = Direction.values()[id % 6];
            var face = pattern == 0 ? palette.faces[id / 6][id % 6]
                    : palette.ctmFaces[id / 6][id % 6].connected(pattern - 1);
            mergedFaces += rectangles.size() / 5;
            batches.add(new Batch(face, direction.getAxis().ordinal(), rectangles.toIntArray()));
            entry.setValue(null);
            if (Thread.currentThread().isInterrupted()) throw new java.util.concurrent.CancellationException();
        }
        return new Prepared(List.copyOf(batches), fallback.toIntArray(), sourceFaces, mergedFaces);
    }

    private static void mergePlane(LongArrayList ordered, int start, int end, LongOpenHashSet remaining, IntArrayList rectangles) {
        for (int at = start; at < end; at++) {
            long first = ordered.getLong(at);
            if (!remaining.remove(first)) continue;
            int width = 1, height = 1;
            while (remaining.contains(first + ((long) width << 16))) width++;
            outer: while (true) {
                for (int du = 0; du < width; du++)
                    if (!remaining.contains(first + ((long) du << 16) + height)) break outer;
                height++;
            }
            for (int du = 0; du < width; du++) for (int dv = 0; dv < height; dv++)
                remaining.remove(first + ((long) du << 16) + dv);
            rectangles.add((int) (first >>> 32));
            rectangles.add((int) (first >>> 16) & 65535);
            rectangles.add((int) first & 65535);
            rectangles.add(width);
            rectangles.add(height);
        }
    }

    private static long key(int plane, int u, int v) { return (long) plane << 32 | (long) u << 16 | v; }

    public Hk3PreviewGreedyMesh(Prepared prepared) { this.prepared = prepared; }
    public boolean valid() { return !closed && generation == resourceGeneration; }
    public boolean ready() { return valid() && batchAt == prepared.batches().size(); }
    public int uploadedFaces() { return uploadedFaces; }
    public long vertexBytes() { return (long) prepared.mergedFaces() * 96; }

    /** 多个小材质批次共用本帧的四边形上传预算。 */
    public void step(int quadBudget) {
        while (quadBudget > 0 && valid() && !ready()) {
            var batch = prepared.batches().get(batchAt);
            int stop = Math.min(rectangleAt + quadBudget * 5, batch.rectangles().length);
            builder.begin(VertexFormat.Mode.QUADS, DefaultVertexFormat.POSITION_COLOR_TEX);
            for (int at = rectangleAt; at < stop; at += 5) emit(builder, batch, at);
            var buffer = new VertexBuffer(VertexBuffer.Usage.STATIC);
            buffer.bind(); buffer.upload(builder.end()); VertexBuffer.unbind();
            buffers.add(new Uploaded(batch.face(), buffer));
            int uploaded = (stop - rectangleAt) / 5;
            uploadedFaces += uploaded;
            quadBudget -= uploaded;
            rectangleAt = stop;
            if (rectangleAt == batch.rectangles().length) { batchAt++; rectangleAt = 0; }
        }
    }

    private static void emit(BufferBuilder builder, Batch batch, int at) {
        int[] rect = batch.rectangles();
        int axis = batch.axis(), u = (axis + 1) % 3, v = (axis + 2) % 3;
        float[] origin = new float[3], span = {1, 1, 1};
        origin[axis] = rect[at]; origin[u] = rect[at + 1]; origin[v] = rect[at + 2];
        span[axis] = 0; span[u] = rect[at + 3]; span[v] = rect[at + 4];
        var face = batch.face(); float[] vertices = face.vertices(); int color = face.color();
        for (int i = 0; i < 4; i++) builder
                .vertex(origin[0] + vertices[i * 5] * span[0], origin[1] + vertices[i * 5 + 1] * span[1], origin[2] + vertices[i * 5 + 2] * span[2])
                .color(color & 255, color >>> 8 & 255, color >>> 16 & 255, color >>> 24)
                .uv(vertices[i * 5 + 3] * span[face.uAxis()], vertices[i * 5 + 4] * span[face.vAxis()]).endVertex();
    }

    public void draw(Matrix4f modelView, Matrix4f projection) {
        RenderSystem.setShaderTexture(0, TextureAtlas.LOCATION_BLOCKS);
        RenderSystem.enableDepthTest(); RenderSystem.disableBlend(); RenderSystem.enableCull(); RenderSystem.depthMask(true);
        for (var batch : buffers) {
            float[] uv = batch.face().bounds();
            shader.safeGetUniform("SpriteBounds").set(uv[0], uv[1], uv[2], uv[3]);
            float[] tiles = batch.face().ctmTiles();
            shader.safeGetUniform("Connected").set(tiles == null ? 0 : 1);
            if (tiles != null) for (int q = 0; q < 4; q++) {
                int at = q * 6;
                shader.safeGetUniform("CtmU" + q).set(tiles[at], tiles[at + 2], tiles[at + 4]);
                shader.safeGetUniform("CtmV" + q).set(tiles[at + 1], tiles[at + 3], tiles[at + 5]);
            }
            batch.buffer().bind(); batch.buffer().drawWithShader(modelView, projection, shader);
        }
        VertexBuffer.unbind();
    }

    @Override public void close() { buffers.forEach(batch -> batch.buffer().close()); buffers.clear(); closed = true; }

    @Mod.EventBusSubscriber(modid = "hk3gtl", value = Dist.CLIENT, bus = Mod.EventBusSubscriber.Bus.MOD)
    public static final class Resources {
        @SubscribeEvent public static void shaders(RegisterShadersEvent event) throws java.io.IOException {
            resourceGeneration++;
            event.registerShader(new ShaderInstance(event.getResourceProvider(), new ResourceLocation("hk3gtl", "preview_greedy"),
                    DefaultVertexFormat.POSITION_COLOR_TEX), loaded -> shader = loaded);
        }
    }
}
