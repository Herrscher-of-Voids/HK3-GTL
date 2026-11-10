package com.sirin.hk3gtl.common.gaze;

import com.sirin.hk3gtl.common.machine.Hk3WorkableMultiblockMachine;
import com.gregtechceu.gtceu.api.machine.IMachineBlockEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import java.util.UUID;
import java.util.Map;
import java.util.WeakHashMap;

/**
 * 【文件职责】查询已经注册的真实稳定锚；以机器所在维度、研究团队和已扣电工作刻为依据。
 * 【变更记录 #1】2026-09-30 15:50:54（内测5修订109）
 * 删除：无。新增：稳定锚生命周期入口及同维度覆盖查询，同类取最大值。
 * 修改：每次查询重验加载/成型/启用/供能，弱键不跨存档；用途：研究付款与推进共用s。
 * 边界：I36尚未接入正式机器，当前无提供者时返回0，不扫描方块名称冒充运行。
 */
/**
 * 【变更记录 #2】2026-11-04 21:04:10（内测5修订200）
 * 删除：仅按坐标登记导致替换机器继承旧稳定源资格的路径。
 * 新增：实例弱引用登记及查询时同一机器重验；修改：注销只撤销匹配实例。
 * 用途：拆除、替换与迟到卸载不转移或误删资格；I36仍无正式提供者，不新增免费抑制。
 */
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
