package com.sirin.hk3gtl.common.machine.hyperion;

import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.api.pattern.*;
import com.gregtechceu.gtceu.api.pattern.error.PatternStringError;
import com.gregtechceu.gtceu.api.pattern.util.RelativeDirection;
import com.sirin.hk3gtl.common.multiblock.build.Hk3UniversalTerminalBuilder;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.entity.player.Player;
import com.sirin.hk3gtl.mixin.gtceu.Hk3MultiblockStateAccess;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3LargeStructurePattern;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3InterfacePredicates;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3StructureBlocks;
import com.gregtechceu.gtceu.api.machine.multiblock.PartAbility;

/** 搭建测试不以单格占位Pattern冒充147万格舰体成型，也不触发全体积扫描。 */
public final class Hk3HyperionConstructionPattern extends BlockPattern {
    private final TraceabilityPredicate control;
    private final TraceabilityPredicate port;
    public Hk3HyperionConstructionPattern(MultiblockMachineDefinition definition) {
        super(new TraceabilityPredicate[][][]{{{Predicates.controller(Predicates.blocks(definition.getBlock()))}}},
                new RelativeDirection[]{RelativeDirection.RIGHT, RelativeDirection.UP, RelativeDirection.BACK},
                new int[][]{{1, 1}}, new int[]{0, 0, 0, 0, 0});
        control=Predicates.controller(Predicates.blocks(definition.getBlock()));
        port=Predicates.blocks(Hk3StructureBlocks.require("hk3gtl:industrial_port_casing"))
                .or(Hk3InterfacePredicates.abilities(PartAbility.IMPORT_ITEMS,PartAbility.EXPORT_ITEMS,PartAbility.IMPORT_FLUIDS,PartAbility.EXPORT_FLUIDS,
                        PartAbility.INPUT_ENERGY,PartAbility.OUTPUT_ENERGY));
    }
    @Override public boolean checkPatternAt(MultiblockState state, BlockPos center, Direction front,
            Direction up, boolean flipped, boolean savePredicate) {
        if(!(state.getController() instanceof Hk3HyperionMachine ship)||!ship.hasVerifiedHull()
                ||Hk3UniversalTerminalBuilder.isBuilding(ship)||up!=Direction.NORTH||flipped) {
            state.setError(new PatternStringError("请使用控制器的检查舰体按钮；完整逐格检查通过后显示成型"));return false;
        }
        var access=(Hk3MultiblockStateAccess)(Object)state;access.hk3gtl$clean();
        if(!access.hk3gtl$update(center,control)||!control.test(state))return false;
        state.addPosCache(center);
        var rotation=Hk3UniversalTerminalBuilder.rotation(Direction.EAST,front);
        for(int z=-1;z<=1;z++) {
            for(var p:new BlockPos[]{new BlockPos(-2,-1,z),new BlockPos(1,1,z)}) {
                if(!access.hk3gtl$update(p.rotate(rotation).offset(center),port)||!port.test(state))return false;
            }
            if(z!=0 && (!access.hk3gtl$update(new BlockPos(0,0,z).rotate(rotation).offset(center),port)||!port.test(state)))return false;
        }
        state.getMatchContext().set(Hk3LargeStructurePattern.BOUNDS_KEY,ship.hullBounds());state.setError(null);state.setNeededFlip(false);return true;
    }
    @Override public void autoBuild(Player player, MultiblockState state) {
        Hk3UniversalTerminalBuilder.use(player, state, null);
    }
}
