package com.sirin.hk3gtl.common.machine.w03;

import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.api.machine.multiblock.PartAbility;
import com.gregtechceu.gtceu.api.pattern.*;
import com.gregtechceu.gtceu.api.pattern.error.PatternStringError;
import com.gregtechceu.gtceu.api.pattern.util.RelativeDirection;
import com.sirin.hk3gtl.common.multiblock.build.Hk3UniversalTerminalBuilder;
import com.sirin.hk3gtl.common.multiblock.pattern.*;
import com.sirin.hk3gtl.mixin.gtceu.Hk3MultiblockStateAccess;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.entity.player.Player;

/** 只有664万实体逐格实读通过的主机才可把八个通用接口接入GT。 */
public final class Hk3W03Pattern extends BlockPattern {
    private final TraceabilityPredicate control,port;
    public Hk3W03Pattern(MultiblockMachineDefinition definition){
        super(new TraceabilityPredicate[][][]{{{Predicates.controller(Predicates.blocks(definition.getBlock()))}}},
            new RelativeDirection[]{RelativeDirection.RIGHT,RelativeDirection.UP,RelativeDirection.BACK},new int[][]{{1,1}},new int[]{0,0,0,0,0});
        control=Predicates.controller(Predicates.blocks(definition.getBlock()));
        port=Predicates.blocks(Hk3StructureBlocks.require("hk3gtl:industrial_port_casing")).or(Hk3InterfacePredicates.abilities(
            PartAbility.IMPORT_ITEMS,PartAbility.EXPORT_ITEMS,PartAbility.IMPORT_FLUIDS,PartAbility.EXPORT_FLUIDS,PartAbility.INPUT_ENERGY,PartAbility.OUTPUT_ENERGY));
    }
    @Override public boolean checkPatternAt(MultiblockState state,BlockPos center,Direction front,Direction up,boolean flip,boolean save){
        if(!(state.getController() instanceof Hk3W03Machine m)||!m.verified()||Hk3UniversalTerminalBuilder.isBuilding(m)||up!=Direction.NORTH||flip){
            state.setError(new PatternStringError("请在控制器内检查C9完整结构"));return false;
        }
        var access=(Hk3MultiblockStateAccess)(Object)state;access.hk3gtl$clean();
        if(!access.hk3gtl$update(center,control)||!control.test(state))return false;
        state.addPosCache(center);var rotation=Hk3UniversalTerminalBuilder.rotation(Direction.NORTH,front);
        for(int x:new int[]{-18,-14,-10,-6,6,10,14,18}){
            var pos=new BlockPos(x,0,0).rotate(rotation).offset(center);
            if(!access.hk3gtl$update(pos,port)||!port.test(state))return false;
            state.addPosCache(pos);
        }
        // 完整实体由主机实读及精确写入回调维护；不能把整片空气也加入GT变更缓存。
        state.setError(null);state.setNeededFlip(false);return true;
    }
    @Override public void autoBuild(Player player,MultiblockState state){Hk3UniversalTerminalBuilder.use(player,state,null);}
}
