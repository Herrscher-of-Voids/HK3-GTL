package com.sirin.hk3gtl.common.multiblock.pattern;

import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.api.machine.multiblock.PartAbility;
import com.gregtechceu.gtceu.api.pattern.BlockPattern;
import com.gregtechceu.gtceu.api.pattern.FactoryBlockPattern;
import com.gregtechceu.gtceu.api.pattern.MultiblockShapeInfo;
import com.gregtechceu.gtceu.api.pattern.Predicates;
import com.lowdragmc.lowdraglib.utils.BlockInfo;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.Property;
import java.util.HashMap;
import static com.gregtechceu.gtceu.api.pattern.util.RelativeDirection.RIGHT;
import static com.gregtechceu.gtceu.api.pattern.util.RelativeDirection.UP;
import static com.gregtechceu.gtceu.api.pattern.util.RelativeDirection.BACK;










































public final class Hk3LiquidLinePatterns {
    private Hk3LiquidLinePatterns() {}

    public static MultiblockShapeInfo shape(MultiblockMachineDefinition definition, Hk3LiquidLineLayout.Kind kind) {
        var layout=Hk3LiquidLineLayout.create(kind);
        var palette=new HashMap<Character,BlockInfo>();
        for(var entry:layout.materials().entrySet())
            palette.put(entry.getKey(),new BlockInfo(Hk3StructureBlocks.require(entry.getValue()).defaultBlockState()));
        var control=definition.getBlock().defaultBlockState();
        palette.put('S',new BlockInfo(north(control,control.getBlock().getStateDefinition().getProperty("facing"))));
        palette.put('#',BlockInfo.EMPTY);
        var blocks=new BlockInfo[kind.width][kind.height][kind.depth];
        for(int x=0;x<kind.width;x++)for(int y=0;y<kind.height;y++)for(int z=0;z<kind.depth;z++)
            blocks[x][y][z]=palette.get(layout.at(x,y,z));
        return new MultiblockShapeInfo(blocks);
    }

    private static <T extends Comparable<T>> BlockState north(BlockState state, Property<T> property) {
        return state.setValue(property,property.getValue("north").orElseThrow());
    }

    public static BlockPattern create(MultiblockMachineDefinition definition,Hk3LiquidLineLayout.Kind kind) {
        // 2026-09-25：I03使用已批准建筑；其余六台保留现有工艺与布局，旧分馏布局仅留作历史归档。
        if(kind==Hk3LiquidLineLayout.Kind.SEPARATION)return Hk3ApprovedArchitecturePatterns.create(definition,"i03");
        if(kind==Hk3LiquidLineLayout.Kind.STABILIZATION)return Hk3ApprovedArchitecturePatterns.create(definition,"i04");
        if(kind==Hk3LiquidLineLayout.Kind.REGENERATION)return Hk3ApprovedArchitecturePatterns.create(definition,"i05");
        var layout=Hk3LiquidLineLayout.create(kind);
        var builder=FactoryBlockPattern.start(RIGHT,UP,BACK);
        for(int z=0;z<kind.depth;z++)builder.aisle(layout.aisle(z));
        builder.where('S',Predicates.controller(Predicates.blocks(definition.getBlock())))
                .where('#',Hk3InterfacePredicates.clearance());
        boolean injection=kind==Hk3LiquidLineLayout.Kind.INJECTION;
        var itemOut=Hk3InterfacePredicates.abilities(PartAbility.EXPORT_ITEMS).setPreviewCount(injection?0:1);
        var fluidOut=Hk3InterfacePredicates.abilities(PartAbility.EXPORT_FLUIDS).setPreviewCount(injection?0:1);
        if (!injection) { itemOut.setMinGlobalLimited(1);fluidOut.setMinGlobalLimited(1); }
        var materialIO=Hk3InterfacePredicates.abilities(PartAbility.IMPORT_ITEMS).setMinGlobalLimited(1).setPreviewCount(1)
                .or(itemOut)
                .or(Hk3InterfacePredicates.abilities(PartAbility.IMPORT_FLUIDS).setMinGlobalLimited(1).setPreviewCount(1))
                .or(fluidOut);
        var universal=Hk3InterfacePredicates.interfaces(materialIO);
        for(var entry:layout.materials().entrySet())
            builder.where(entry.getKey(),Predicates.blocks(Hk3StructureBlocks.require(entry.getValue())).or(universal));
        return builder.build();
    }
}
