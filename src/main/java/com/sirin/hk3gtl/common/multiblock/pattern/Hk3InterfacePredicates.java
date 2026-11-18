package com.sirin.hk3gtl.common.multiblock.pattern;

import com.gregtechceu.gtceu.api.machine.multiblock.PartAbility;
import com.gregtechceu.gtceu.api.pattern.Predicates;
import com.gregtechceu.gtceu.api.pattern.TraceabilityPredicate;
import com.sirin.hk3gtl.common.machine.multiblock.part.Hk3PartAbility;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import java.util.LinkedHashSet;
import java.util.Set;

public final class Hk3InterfacePredicates {
    private static final ResourceLocation[] COMBINED_BUFFERS = {
            new ResourceLocation("gtladditions", "me_super_pattern_buffer"),
            new ResourceLocation("gtladditions", "me_super_pattern_buffer_proxy")
    };
    private static final PartAbility[] MATERIAL_IO = {PartAbility.IMPORT_ITEMS, PartAbility.EXPORT_ITEMS,
            PartAbility.IMPORT_FLUIDS, PartAbility.EXPORT_FLUIDS};
    private static final PartAbility[] AUXILIARY = {PartAbility.INPUT_ENERGY, PartAbility.OUTPUT_ENERGY,
            PartAbility.SUBSTATION_INPUT_ENERGY, PartAbility.SUBSTATION_OUTPUT_ENERGY,
            PartAbility.INPUT_LASER, PartAbility.OUTPUT_LASER, PartAbility.DATA_ACCESS,
            PartAbility.COMPUTATION_DATA_RECEPTION, PartAbility.COMPUTATION_DATA_TRANSMISSION,
            PartAbility.OPTICAL_DATA_RECEPTION, PartAbility.OPTICAL_DATA_TRANSMISSION,
            Hk3PartAbility.HONKAI_ENERGY_INPUT, Hk3PartAbility.HONKAI_ENERGY_OUTPUT,
            Hk3PartAbility.WIRELESS_HONKAI_INPUT, Hk3PartAbility.WIRELESS_HONKAI_OUTPUT};

    private static final class Interfaces {
        static final Set<Block> BLOCKS = interfaceBlocks();
    }

    private Hk3InterfacePredicates() {}

    public static TraceabilityPredicate abilities(PartAbility... abilities) {
        return Predicates.blocks(abilityBlocks(abilities).toArray(Block[]::new));
    }

    private static Set<Block> abilityBlocks(PartAbility... abilities) {
        var blocks = new LinkedHashSet<Block>();
        for (var ability : abilities) {
            blocks.addAll(ability.getAllBlocks());
            if (ability == PartAbility.IMPORT_ITEMS || ability == PartAbility.EXPORT_ITEMS
                    || ability == PartAbility.IMPORT_FLUIDS || ability == PartAbility.EXPORT_FLUIDS) {
                for (var id : COMBINED_BUFFERS)
                    if (BuiltInRegistries.BLOCK.containsKey(id)) blocks.add(BuiltInRegistries.BLOCK.get(id));
            }
        }
        return blocks;
    }

    public static TraceabilityPredicate interfaces() {
        return interfaces(abilities(MATERIAL_IO));
    }

    public static TraceabilityPredicate interfaces(TraceabilityPredicate materialIO) {
        return materialIO.or(abilities(AUXILIARY))
                .or(abilities(PartAbility.PARALLEL_HATCH).setMaxGlobalLimited(1).setPreviewCount(0))
                .or(abilities(PartAbility.MAINTENANCE).setMaxGlobalLimited(1).setPreviewCount(0))
                .or(Predicates.blocks(Hk3StructureBlocks.require("hk3gtl:industrial_port_casing")));
    }

    public static boolean isInterface(BlockState state) {
        return Interfaces.BLOCKS.contains(state.getBlock());
    }

    private static Set<Block> interfaceBlocks() {
        var blocks = abilityBlocks(MATERIAL_IO);
        blocks.addAll(abilityBlocks(AUXILIARY));
        blocks.addAll(abilityBlocks(PartAbility.PARALLEL_HATCH, PartAbility.MAINTENANCE));
        blocks.add(Hk3StructureBlocks.require("hk3gtl:industrial_port_casing"));
        return Set.copyOf(blocks);
    }

    public static TraceabilityPredicate clearance() {
        return Predicates.any();
    }
}
