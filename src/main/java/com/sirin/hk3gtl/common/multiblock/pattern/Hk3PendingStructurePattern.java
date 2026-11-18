package com.sirin.hk3gtl.common.multiblock.pattern;

import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.api.pattern.*;
import com.gregtechceu.gtceu.api.pattern.error.PatternStringError;
import com.gregtechceu.gtceu.api.pattern.util.RelativeDirection;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.player.Player;

/** 缺少完整蓝图的身份可以注册配方，但绝不接受单主控作为结构。 */
public final class Hk3PendingStructurePattern extends BlockPattern {
    private final String reason;
    public Hk3PendingStructurePattern(MultiblockMachineDefinition definition, String reason) {
        super(new TraceabilityPredicate[][][]{{{Predicates.controller(Predicates.blocks(definition.getBlock()))}}},
                new RelativeDirection[]{RelativeDirection.RIGHT, RelativeDirection.UP, RelativeDirection.BACK},
                new int[][]{{1, 1}}, new int[]{0, 0, 0, 0, 0});
        this.reason = reason;
    }
    @Override public boolean checkPatternAt(MultiblockState state, BlockPos center, Direction front,
            Direction up, boolean flip, boolean save) {
        state.setError(new PatternStringError(reason));
        return false;
    }
    @Override public void autoBuild(Player player, MultiblockState state) {
        player.displayClientMessage(Component.literal(reason), false);
    }
}
