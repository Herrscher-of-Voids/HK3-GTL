package com.sirin.hk3gtl.common.multiblock.pattern;

import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.api.pattern.MultiblockShapeInfo;
import com.lowdragmc.lowdraglib.utils.BlockInfo;
import com.mojang.logging.LogUtils;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.NbtIo;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.Property;
import org.slf4j.Logger;

import java.io.ByteArrayInputStream;
import java.io.DataInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.BitSet;
import java.util.IdentityHashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;
import java.util.zip.GZIPInputStream;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 【文件职责】无损串流读取巨构预览，保留GT标准完整坐标数组及所有实体方块。
 * 【变更记录 #1】2026-10-26 21:57:03（修订178）
 * 删除：预览先展开百万NBT复合对象及逐空气BlockInfo的需求。
 * 新增：紧凑调色板、位置与必要方块实体数据的逐条解码，损坏或重复记录拒绝载入。
 * 修改：空气仅为null引用，普通BlockInfo按状态共享；本类不缓存或主动求值其他机器形状，JEI可逐台调用材料索引。
 * 用途：恢复I19至I28完整游戏内预览；标准数组仍随包围盒增长，不冒充无限内存方案。
 * 【变更记录 #2】2026-10-26 22:36:20（修订179）
 * 删除：仅有成功日志时无法区分未调用和解码失败的诊断缺口；新增：每台首次准备入口日志。
 * 修改：完整显式形状与Pattern回退共用此入口；用途：定位实际游戏预览路由及准备失败。
 */
public final class Hk3LargeArchitectureShapes {
    private static final Logger LOGGER = LogUtils.getLogger();
    private static final Set<String> STARTED = ConcurrentHashMap.newKeySet();
    private static final Set<String> LOGGED = ConcurrentHashMap.newKeySet();
    private static final boolean SPARSE_AIR=Hk3LargeArchitectureShapes.class.getClassLoader()
            .getResource("org/gtlcore/gtlcore/client/preview/SparsePreviewShape.class")!=null;
    public record Header(int width, int height, int depth, int controllerX, int controllerY, int controllerZ,
                         int count, List<String> palette) {
        public int volume() { return Math.multiplyExact(Math.multiplyExact(width, height), depth); }
        public int linear(int x, int y, int z) { return (x * height + y) * depth + z; }
    }
    @FunctionalInterface public interface CellVisitor {
        void accept(int linear, int paletteIndex, CompoundTag entity);
    }

    private Hk3LargeArchitectureShapes() {}

    public static MultiblockShapeInfo create(MultiblockMachineDefinition definition, String id) {
        long started = System.nanoTime();
        if (!Hk3ApprovedArchitecture.IDS.contains(id)) throw new IllegalArgumentException("非巨构预览：" + id);
        if (STARTED.add(id)) LOGGER.info("HK3GTL开始准备完整巨构预览：{}，定义={}", id, definition.getId());
        class Bake {
            Header header;
            BlockInfo[][][] blocks;
            BlockState[] states;
            final Map<BlockState, BlockInfo> plain = new IdentityHashMap<>();
        }
        Bake bake = new Bake();
        try (InputStream resource = Hk3StructureStream.open(id)) {
            if (resource == null) throw new IllegalStateException("缺少巨构预览：" + id);
            read(resource, header -> {
                bake.header = header;
                bake.blocks = new BlockInfo[header.width()][header.height()][header.depth()];
                if(!SPARSE_AIR)for(var plane:bake.blocks)for(var row:plane)java.util.Arrays.fill(row,BlockInfo.EMPTY);
                bake.states = header.palette().stream().map(Hk3LargeArchitectureShapes::state).toArray(BlockState[]::new);
            }, (linear, palette, entity) -> {
                Header header = bake.header;
                int z = linear % header.depth(), y = linear / header.depth() % header.height();
                int x = linear / header.depth() / header.height();
                BlockState state = bake.states[palette];
                if (state.isAir()) throw new IllegalStateException("巨构预览实体含空气：" + id);
                BlockInfo info;
                if (state.hasBlockEntity() || entity != null) {
                    info = BlockInfo.fromBlockState(state);
                    if (entity != null) info.setTag(entity);
                } else info = bake.plain.computeIfAbsent(state, BlockInfo::fromBlockState);
                bake.blocks[x][y][z] = info;
            });
        } catch (IOException failure) {
            throw new IllegalStateException("读取巨构预览失败：" + id, failure);
        }
        Header header = bake.header;
        BlockInfo controller = bake.blocks[header.controllerX()][header.controllerY()][header.controllerZ()];
        if (controller == null || controller.getBlockState().getBlock() != definition.getBlock())
            throw new IllegalStateException("巨构预览主控与定义不符：" + id);
        Property<?> facing = controller.getBlockState().getBlock().getStateDefinition().getProperty("facing");
        if (facing == null || !"north".equals(controller.getBlockState().getValue(facing).toString()))
            throw new IllegalStateException("巨构预览主控未朝北：" + id);
        if (LOGGED.add(id)) LOGGER.info("HK3GTL完整巨构预览就绪：{}，尺寸={}×{}×{}，实体={}，准备耗时={}ms",
                id, header.width(), header.height(), header.depth(), header.count(),
                (System.nanoTime() - started) / 1_000_000);
        return new MultiblockShapeInfo(bake.blocks);
    }

    /** 纯数据入口供逐格测试共用；不会读取完整NBT树或分配包围盒数组。 */
    public static Header read(InputStream compressed, Consumer<Header> begin, CellVisitor cells) throws IOException {
        try (var input=new Hk3StructureStream(compressed)) {
            var h=input.header();
            Header header=new Header(h.width(),h.height(),h.depth(),h.cx(),h.cy(),h.cz(),h.count(),h.palette());
            begin.accept(header);
            BitSet occupied=new BitSet(h.volume());
            for(int i=0;i<h.count();i++) {
                var cell=input.next();
                if(occupied.get(cell.linear()))throw new IOException("巨构预览坐标重复");
                occupied.set(cell.linear());
                cells.accept(cell.linear(),cell.state(),entity(cell.entity()));
            }
            if(!occupied.get(header.linear(h.cx(),h.cy(),h.cz())))throw new IOException("巨构预览主控缺格");
            input.finish();return header;
        }
    }
    public static CompoundTag entity(byte[] raw) throws IOException {
        if(raw==null)return null;
        try(DataInputStream input=new DataInputStream(new ByteArrayInputStream(raw))) {
            CompoundTag tag=NbtIo.read(input);
            if(tag==null||input.read()!=-1)throw new IOException("结构方块实体数据错误");
            return tag;
        }
    }

    public static BlockState state(String text) {
        int start = text.indexOf('[');
        var block = Hk3StructureBlocks.require(start < 0 ? text : text.substring(0, start));
        BlockState state = block.defaultBlockState();
        if (start >= 0) for (String entry : text.substring(start + 1, text.length() - 1).split(",")) {
            String[] pair = entry.split("=", 2);
            Property<?> property = pair.length == 2 ? block.getStateDefinition().getProperty(pair[0]) : null;
            if (property == null) throw new IllegalStateException("巨构预览属性错误：" + text);
            state = property(state, property, pair[1]);
        }
        return state;
    }
    private static <T extends Comparable<T>> BlockState property(BlockState state, Property<T> property, String value) {
        return state.setValue(property, property.getValue(value).orElseThrow(() -> new IllegalStateException("巨构预览属性值错误：" + value)));
    }
}
