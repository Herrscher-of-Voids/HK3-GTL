package com.sirin.hk3gtl.common.multiblock.pattern;

import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.api.pattern.BlockPattern;
import com.gregtechceu.gtceu.api.pattern.MultiblockState;
import com.gregtechceu.gtceu.api.pattern.Predicates;
import com.gregtechceu.gtceu.api.pattern.TraceabilityPredicate;
import com.gregtechceu.gtceu.api.pattern.util.RelativeDirection;
import com.sirin.hk3gtl.common.multiblock.build.Hk3UniversalTerminalBuilder;
import net.minecraft.world.entity.player.Player;

/** 奇观蓝图分批供给GTL原生匹配器；建造仍由统一终端处理。 */
public class Hk3NativeWonderPattern extends BlockPattern {
    private final String role;

    public Hk3NativeWonderPattern(String role, MultiblockMachineDefinition definition) {
        super(new TraceabilityPredicate[][][]{{{Predicates.any()}}},
                new RelativeDirection[]{RelativeDirection.RIGHT, RelativeDirection.UP, RelativeDirection.BACK},
                new int[][]{{1, 1}}, new int[]{0, 0, 0, 0, 0});
        this.role = role;
    }

    public final String role() { return role; }

    @Override public void autoBuild(Player player, MultiblockState state) {
        Hk3UniversalTerminalBuilder.use(player, state, null);
    }
}
