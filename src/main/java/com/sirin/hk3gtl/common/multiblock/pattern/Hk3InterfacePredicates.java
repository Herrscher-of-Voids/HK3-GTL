package com.sirin.hk3gtl.common.multiblock.pattern;

import com.gregtechceu.gtceu.api.machine.multiblock.PartAbility;
import com.gregtechceu.gtceu.api.pattern.Predicates;
import com.gregtechceu.gtceu.api.pattern.TraceabilityPredicate;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import java.util.LinkedHashSet;

/** 修订216：总成和镜像共用四向物料能力；允许AE线缆经过原有空腔。 */
public final class Hk3InterfacePredicates {
    private static final ResourceLocation[] COMBINED_BUFFERS = {
            new ResourceLocation("gtladditions", "me_super_pattern_buffer"),
            new ResourceLocation("gtladditions", "me_super_pattern_buffer_proxy")
    };
    private static final ResourceLocation CABLE = new ResourceLocation("ae2", "cable_bus");
    private static final ResourceLocation SNOW = new ResourceLocation("minecraft", "snow");

    private Hk3InterfacePredicates() {}

    public static TraceabilityPredicate abilities(PartAbility... abilities) {
        var blocks = new LinkedHashSet<Block>();
        for (var ability : abilities) {
            blocks.addAll(ability.getAllBlocks());
            if (ability == PartAbility.IMPORT_ITEMS || ability == PartAbility.EXPORT_ITEMS
                    || ability == PartAbility.IMPORT_FLUIDS || ability == PartAbility.EXPORT_FLUIDS) {
                for (var id : COMBINED_BUFFERS)
                    if (BuiltInRegistries.BLOCK.containsKey(id)) blocks.add(BuiltInRegistries.BLOCK.get(id));
            }
        }
        return Predicates.blocks(blocks.toArray(Block[]::new));
    }

    public static TraceabilityPredicate clearance() {
        // 雪层会自然落在露天巨构上，不应使完整机器解体；雪块与细雪仍是障碍。
        var result = Predicates.air().or(Predicates.blocks(Blocks.SNOW));
        return BuiltInRegistries.BLOCK.containsKey(CABLE)
                ? result.or(Predicates.blocks(BuiltInRegistries.BLOCK.get(CABLE))) : result;
    }

    public static boolean isClearance(BlockState state) {
        return isClearance(state.isAir(), BuiltInRegistries.BLOCK.getKey(state.getBlock()));
    }

    static boolean isClearance(boolean air, ResourceLocation block) {
        return air || CABLE.equals(block) || SNOW.equals(block);
    }
}
