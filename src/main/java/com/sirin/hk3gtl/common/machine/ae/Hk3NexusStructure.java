package com.sirin.hk3gtl.common.machine.ae;

import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.api.pattern.BlockPattern;
import com.gregtechceu.gtceu.api.pattern.FactoryBlockPattern;
import com.gregtechceu.gtceu.api.pattern.MultiblockShapeInfo;
import com.gregtechceu.gtceu.api.pattern.Predicates;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3InterfacePredicates;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.NbtIo;
import net.minecraft.nbt.NbtUtils;
import net.minecraft.nbt.Tag;

import java.io.IOException;
import java.util.Arrays;

import static com.gregtechceu.gtceu.api.pattern.util.RelativeDirection.*;

public final class Hk3NexusStructure {
    private static final CompoundTag TEMPLATE = read();
    private static final String[][] AISLES = aisles();

    private Hk3NexusStructure() {}

    public static CompoundTag template() { return TEMPLATE; }

    public static BlockPattern pattern(MultiblockMachineDefinition definition) {
        var builder = FactoryBlockPattern.start(RIGHT, UP, BACK);
        for (var aisle : AISLES) builder.aisle(aisle);
        builder.where('S', Predicates.controller(Predicates.blocks(definition.getBlock())))
                .where(' ', Hk3InterfacePredicates.clearance());
        var palette = TEMPLATE.getList("palette", Tag.TAG_COMPOUND);
        for (int i = 1; i < palette.size(); i++) {
            var state = NbtUtils.readBlockState(BuiltInRegistries.BLOCK.asLookup(), palette.getCompound(i));
            if (state.getBlock() != definition.getBlock())
                builder.where((char) (0xE000 + i), Predicates.states(state));
        }
        return builder.build();
    }

    public static MultiblockShapeInfo shape(MultiblockMachineDefinition definition) {
        var builder = MultiblockShapeInfo.builder();
        for (var aisle : AISLES) builder.aisle(aisle);
        builder.where('S', definition, Direction.NORTH).where(' ', net.minecraft.world.level.block.Blocks.AIR.defaultBlockState());
        var palette = TEMPLATE.getList("palette", Tag.TAG_COMPOUND);
        for (int i = 1; i < palette.size(); i++) {
            var state = NbtUtils.readBlockState(BuiltInRegistries.BLOCK.asLookup(), palette.getCompound(i));
            if (state.getBlock() != definition.getBlock()) builder.where((char) (0xE000 + i), state);
        }
        return builder.build();
    }

    private static String[][] aisles() {
        var size = TEMPLATE.getList("size", Tag.TAG_INT);
        var cells = new char[size.getInt(2)][size.getInt(1)][size.getInt(0)];
        for (var slice : cells) for (var row : slice) Arrays.fill(row, ' ');
        var palette = TEMPLATE.getList("palette", Tag.TAG_COMPOUND);
        for (var raw : TEMPLATE.getList("blocks", Tag.TAG_COMPOUND)) {
            var block = (CompoundTag) raw;
            var pos = block.getList("pos", Tag.TAG_INT);
            int material = block.getInt("state");
            cells[pos.getInt(2)][pos.getInt(1)][pos.getInt(0)] =
                    palette.getCompound(material).getString("Name").equals("hk3gtl:ae_nexus")
                            ? 'S' : (char) (0xE000 + material);
        }
        var result = new String[cells.length][size.getInt(1)];
        for (int z = 0; z < cells.length; z++)
            for (int y = 0; y < cells[z].length; y++) result[z][y] = new String(cells[z][y]);
        return result;
    }

    private static CompoundTag read() {
        try (var input = Hk3NexusStructure.class.getResourceAsStream("/data/hk3gtl/structures/ae_nexus_a1.nbt")) {
            return NbtIo.readCompressed(input);
        } catch (IOException failure) {
            throw new IllegalStateException("读取万象天枢A1蓝图失败", failure);
        }
    }
}
