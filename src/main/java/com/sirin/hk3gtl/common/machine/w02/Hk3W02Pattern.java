package com.sirin.hk3gtl.common.machine.w02;

import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.api.machine.multiblock.PartAbility;
import com.gregtechceu.gtceu.api.pattern.*;
import com.gregtechceu.gtceu.api.pattern.error.PatternStringError;
import com.gregtechceu.gtceu.api.pattern.util.RelativeDirection;
import com.sirin.hk3gtl.common.multiblock.build.Hk3UniversalTerminalBuilder;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3InterfacePredicates;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3StructureBlocks;
import com.sirin.hk3gtl.mixin.gtceu.Hk3MultiblockStateAccess;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.entity.player.Player;

/** 先完整读取607万实体，再接入八个不限定仓型的通用接口。 */
public final class Hk3W02Pattern extends BlockPattern {
    public static final java.util.List<BlockPos> PORTS=java.util.List.of(
        new BlockPos(-1,-1,0),new BlockPos(0,-1,0),new BlockPos(1,-1,0),
        new BlockPos(-1,0,0),new BlockPos(1,0,0),
        new BlockPos(-1,1,0),new BlockPos(0,1,0),new BlockPos(1,1,0));
    private final TraceabilityPredicate control,port;
    public Hk3W02Pattern(MultiblockMachineDefinition definition){
        super(new TraceabilityPredicate[][][]{{{Predicates.controller(Predicates.blocks(definition.getBlock()))}}},
            new RelativeDirection[]{RelativeDirection.RIGHT,RelativeDirection.UP,RelativeDirection.BACK},new int[][]{{1,1}},new int[]{0,0,0,0,0});
        control=Predicates.controller(Predicates.blocks(definition.getBlock()));
        port=Predicates.blocks(Hk3StructureBlocks.require("hk3gtl:industrial_port_casing")).or(Hk3InterfacePredicates.abilities(
            PartAbility.IMPORT_ITEMS,PartAbility.EXPORT_ITEMS,PartAbility.IMPORT_FLUIDS,PartAbility.EXPORT_FLUIDS,PartAbility.INPUT_ENERGY,PartAbility.OUTPUT_ENERGY));
    }
    @Override public boolean checkPatternAt(MultiblockState state,BlockPos center,Direction front,Direction up,boolean flip,boolean save){
        if(!(state.getController() instanceof Hk3W02Machine m)||!m.verified()||Hk3UniversalTerminalBuilder.isBuilding(m)||up!=Direction.NORTH||flip){
            state.setError(new PatternStringError("请在主控内检查W02完整结构"));return false;
        }
        var access=(Hk3MultiblockStateAccess)(Object)state;access.hk3gtl$clean();
        if(!access.hk3gtl$update(center,control)||!control.test(state))return false;
        state.addPosCache(center);var rotation=Hk3UniversalTerminalBuilder.rotation(Direction.SOUTH,front);
        for(var local:PORTS){
            var pos=local.rotate(rotation).offset(center);
            if(!access.hk3gtl$update(pos,port)||!port.test(state))return false;
            state.addPosCache(pos);
        }
        state.setError(null);state.setNeededFlip(false);return true;
    }
    @Override public void autoBuild(Player player,MultiblockState state){Hk3UniversalTerminalBuilder.use(player,state,null);}
}
