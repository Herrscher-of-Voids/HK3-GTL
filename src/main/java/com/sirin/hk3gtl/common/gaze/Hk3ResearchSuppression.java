package com.sirin.hk3gtl.common.gaze;

import com.sirin.hk3gtl.common.machine.Hk3WorkableMultiblockMachine;
import com.gregtechceu.gtceu.api.machine.IMachineBlockEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import java.util.UUID;
import java.util.Map;
import java.util.WeakHashMap;














public final class Hk3ResearchSuppression {
    /** 提供者须在实际完成本刻能源扣费后更新时间；强化还须真实RN-JOK与不消耗模块校验。 */
    public interface Source {
        long lastPaidTick();
        boolean enhancedSuppression();
    }
    private static final Map<ServerLevel, Hk3SuppressionSourceRegistry<BlockPos, Hk3WorkableMultiblockMachine>> SOURCES = new WeakHashMap<>();
    private Hk3ResearchSuppression() {}
    public static synchronized void register(Hk3WorkableMultiblockMachine machine) {
        if (machine instanceof Source && machine.getLevel() instanceof ServerLevel level)
            SOURCES.computeIfAbsent(level, key -> new Hk3SuppressionSourceRegistry<>())
                    .register(machine.getPos().immutable(), machine);
    }
    public static synchronized void unregister(Hk3WorkableMultiblockMachine machine) {
        if (machine.getLevel() instanceof ServerLevel level && SOURCES.containsKey(level))
            SOURCES.get(level).unregister(machine.getPos(), machine);
    }
    public static synchronized double at(ServerLevel level, BlockPos target, UUID team) {
        if (team == null) return 0;
        double highest = 0;
        var registry = SOURCES.get(level);
        if (registry == null) return 0;
        for (var registered : registry.snapshot().entrySet()) {
            var pos = registered.getKey();
            if (!level.hasChunkAt(pos)) continue;
            var be = level.getBlockEntity(pos);
            if (!(be instanceof IMachineBlockEntity holder)
                    || !(holder.getMetaMachine() instanceof Hk3WorkableMultiblockMachine machine)
                    || machine != registered.getValue()
                    || !(machine instanceof Source source)) continue;
            // 严格本刻扣电：不把上刻仍工作当作本刻有电；执行器应在研究推进前更新供能事实。
            boolean working = machine.isFormed() && machine.getRecipeLogic().isWorkingEnabled()
                    && source.lastPaidTick() == level.getGameTime();
            highest = Math.max(highest, Hk3GazeRules.suppression(team.equals(machine.getResearchTeamUUID()),
                    working, source.enhancedSuppression(), pos.distSqr(target)));
        }
        return highest;
    }
}
