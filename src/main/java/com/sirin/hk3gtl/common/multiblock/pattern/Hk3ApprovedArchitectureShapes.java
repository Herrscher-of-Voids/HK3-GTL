package com.sirin.hk3gtl.common.multiblock.pattern;

import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.api.pattern.MultiblockShapeInfo;
import com.lowdragmc.lowdraglib.utils.BlockInfo;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.NbtIo;
import net.minecraft.nbt.Tag;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.Property;

import java.io.IOException;
import java.lang.reflect.Array;
import java.util.Arrays;
import java.util.BitSet;
import java.util.IdentityHashMap;
import java.util.Map;
import java.util.Objects;
import java.util.function.BiFunction;

/**
 * 【变更记录 #1】2026-10-15 02:00:40（内测5修订157）
 * 删除：批准结构预览对逐空气格候选 BlockInfo 的依赖，正式 Pattern 的空气谓词不变。
 * 新增：从正式 NBT 烘焙显式 JEI 形状、普通状态共享和稀疏预览能力检测。
 * 修改：具备定制稀疏预览能力时省略空气；普通 GT 环境使用共享 EMPTY 保持兼容。
 * 用途：保留批准尺寸、逐块几何、真实仓室及北向主控，同时减少预览对象和空气映射。
 */
public final class Hk3ApprovedArchitectureShapes {
    private static final boolean SPARSE_AIR_SUPPORTED = supportsSparseAir();

    private Hk3ApprovedArchitectureShapes() {}

    /** 显式形状只影响预览；成型仍调用原有完整尺寸和严格空气 Pattern。 */
    public static MultiblockShapeInfo create(MultiblockMachineDefinition definition, String id) {
        return Hk3LargeArchitectureShapes.create(definition,id);
    }

    /**
     * NBT 的世界 X、Y、Z 直接对应预览数组；与 RIGHT、UP、BACK 的北向 Pattern 一致。
     * 泛型烘焙入口允许以纯状态字符串验收全部模板，不需要启动游戏或初始化方块注册表。
     */
    @SuppressWarnings("unchecked")
    public static <T> T[][][] bakeTemplate(CompoundTag template, Class<T> type, T air,
            BiFunction<CompoundTag, CompoundTag, T> blockFactory) {
        var size = requiredList(template, "size", Tag.TAG_INT);
        if (size.size() != 3) throw new IllegalStateException("批准模板尺寸必须有三个轴");
        int sx = size.getInt(0), sy = size.getInt(1), sz = size.getInt(2);
        if (sx <= 0 || sy <= 0 || sz <= 0) throw new IllegalStateException("批准模板尺寸必须为正数");
        int volume = Math.multiplyExact(Math.multiplyExact(sx, sy), sz);
        var palette = requiredList(template, "palette", Tag.TAG_COMPOUND);
        if (palette.isEmpty()) throw new IllegalStateException("批准模板缺少调色板");
        var blocks = requiredList(template, "blocks", Tag.TAG_COMPOUND);
        T[][][] shape = (T[][][]) Array.newInstance(type, sx, sy, sz);
        if (air != null) for (var plane : shape) for (var row : plane) Arrays.fill(row, air);
        BitSet occupied = new BitSet(volume);
        for (var raw : blocks) {
            var block = (CompoundTag) raw;
            var pos = requiredList(block, "pos", Tag.TAG_INT);
            if (pos.size() != 3 || !block.contains("state", Tag.TAG_INT))
                throw new IllegalStateException("批准模板方块缺少坐标或状态索引");
            int x = pos.getInt(0), y = pos.getInt(1), z = pos.getInt(2), state = block.getInt("state");
            if (x < 0 || x >= sx || y < 0 || y >= sy || z < 0 || z >= sz)
                throw new IllegalStateException("批准模板方块坐标越界");
            if (state < 0 || state >= palette.size()) throw new IllegalStateException("批准模板调色板索引越界");
            int packed = (x * sy + y) * sz + z;
            if (occupied.get(packed)) throw new IllegalStateException("批准模板出现重复方块坐标");
            occupied.set(packed);
            if (block.contains("nbt") && !block.contains("nbt", Tag.TAG_COMPOUND))
                throw new IllegalStateException("批准模板方块实体数据格式错误");
            CompoundTag entityTag = block.contains("nbt", Tag.TAG_COMPOUND) ? block.getCompound("nbt") : null;
            shape[x][y][z] = Objects.requireNonNull(blockFactory.apply(palette.getCompound(state), entityTag),
                    "批准模板实体不能返回空预览方块");
        }
        return shape;
    }

    private static ListTag requiredList(CompoundTag tag, String name, int elementType) {
        if (!(tag.get(name) instanceof ListTag list) || (!list.isEmpty() && list.getElementType() != elementType))
            throw new IllegalStateException("批准模板列表缺失或类型错误：" + name);
        return list;
    }

    private static CompoundTag readTemplate(String id) {
        try (var stream = Hk3ApprovedArchitectureShapes.class.getResourceAsStream(
                "/data/hk3gtl/structures/approved/" + id + ".nbt")) {
            if (stream == null) throw new IllegalStateException("缺少批准预览模板：" + id);
            return NbtIo.readCompressed(stream);
        } catch (IOException failure) {
            throw new IllegalStateException("读取批准预览模板失败：" + id, failure);
        }
    }

    private static BlockState state(CompoundTag palette) {
        var block = Hk3StructureBlocks.require(palette.getString("Name"));
        BlockState result = block.defaultBlockState();
        var properties = palette.getCompound("Properties");
        for (String name : properties.getAllKeys()) {
            Property<?> property = block.getStateDefinition().getProperty(name);
            if (property == null) throw new IllegalStateException("批准预览材料缺少属性：" + name);
            result = property(result, property, properties.getString(name));
        }
        return result;
    }

    private static <T extends Comparable<T>> BlockState property(BlockState state, Property<T> property, String value) {
        T parsed = property.getValue(value).orElseThrow(() -> new IllegalStateException("非法批准预览属性：" + value));
        return state.setValue(property, parsed);
    }

    /** 仅检查资源存在性，避免在专用服务器加载客户端类或硬绑定定制 GTLCore。 */
    private static boolean supportsSparseAir() {
        ClassLoader loader = Hk3ApprovedArchitectureShapes.class.getClassLoader();
        return loader.getResource("org/gtlcore/gtlcore/client/preview/SparsePreviewShape.class") != null
                && loader.getResource("org/gtlcore/gtlcore/api/gui/PatternPreviewWidget.class") != null
                && loader.getResource("org/gtlcore/gtlcore/mixin/gtm/gui/PatternPreviewWidgetMixin.class") != null;
    }
}
