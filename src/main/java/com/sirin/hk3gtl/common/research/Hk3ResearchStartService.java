package com.sirin.hk3gtl.common.research;

/**
 * 【文件职责／本轮边界】从个人账户付费给固定团队任务，使用批准EU/t并保存实际支付，不重算存量收据。
 * 【变更记录 #1】2026-09-29 21:06:40（第 1 次编号备注 · 内测5修订100）
 * 删除：取消已被批准规则替代的研究个人独占、旧数值或在线限定分支；历史备注与其他系统保留。
 * 新增／修改：从个人账户付费给固定团队任务，使用批准EU/t并保存实际支付，不重算存量收据。
 * 用途：接通实际证据→付款→研究完成与权限检查；不授予缺真实证据的课题。
 * 边界：编译和账本测试不代表游戏验收；S02至S05正式结构及未接线课题仍未完成。
 * 追溯：logs/research-mainline-r100；R100_FINAL_RECORD。
 */

/** 修订100 · 2026-09-29：接通团队研究归属、个人付款及真实实验来源。 */

/** 【变更记录 · 内测5修订100】2026-09-29：落实已批准研究费用、三公式及离线账户规则。 */

import com.gregtechceu.gtceu.api.GTValues;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import java.util.List;

/** 中文说明：该处说明已按当前代码行为整理。*/
/**
 * 【变更记录 #2】2026-09-30 15:49:23（第2次编号备注 · 内测5修订109）
 * 删除：过期的计算或无运行依据的分支；保留历史备注。
 * 新增／修改：材料预览与实际支付共享稳定锚抑制参数；旧入口默认零，已付款收据不重算，点价不变。
 * 用途：统一注视与研究联动，服务端判定；不新增结构或贴图。
 */
/** 【变更记录 #3】2026-10-01 04:21:47（修订128）：删除：旧固定上限或被替代的分支；新增/修改：仅成功扣费并提交研究事务后投递可选旁注，余额不足和重复开题不触发；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/**
 * 【变更记录 #4】2026-11-04 01:23:43（第4次备注 · 内测5修订194）
 * - 删除：材料实扣后只等待世界自动保存的路径。
 * - 新增：点数和材料开题均进入Hk3ResearchPayment持久事务，失败不发成功回执。
 * - 修改：费用、前置与真实扣料保持原规则，成功工作与付款玩家文件同步持久化。
 * - 用途：阻止JVM硬崩后免费研究或丢失材料；不改变点价和研究设计。
 */
public final class Hk3ResearchStartService {
    private Hk3ResearchStartService() {}

    /** 玩家可读拒绝原因；枚举不包含客户端授权。 / User-facing rejection reasons, never client authorization. */
    public enum Result { STARTED, UNAVAILABLE, LOCKED, COMPLETED, RUNNING, INSUFFICIENT, CAPACITY }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    public static Result start(ServerPlayer player, String facility, int lab, boolean available,
                               String topicId, boolean points, double gaze) {
        return start(player, Hk3ResearchTeams.scope(player.server,player.getUUID()), facility, lab, available, topicId, points, gaze);
    }
    public static Result start(ServerPlayer player, java.util.UUID owner, String facility, int lab, boolean available,
                               String topicId, boolean points, double gaze) {
        return start(player, owner, facility, lab, available, topicId, points, gaze, 0);
    }
    public static Result start(ServerPlayer player, java.util.UUID owner, String facility, int lab, boolean available,
                               String topicId, boolean points, double gaze, double suppression) {
        if (!available || !Hk3ResearchData.get(player).isMember(player.getUUID(),owner)) return Result.UNAVAILABLE;
        var definition = Hk3ResearchCatalog.bundled().get(topicId);
        var plan = Hk3ResearchPlans.get(topicId);
        var data = Hk3ResearchData.get(player);

        if (definition == null || plan == null || lab < definition.lab() || !data.hasExperiment(owner, topicId)
                || !definition.prerequisites().stream().allMatch(id -> data.completed(owner, id))) return Result.LOCKED;
        if (data.completed(owner, topicId)) return Result.COMPLETED;
        if (data.researchJob(owner, topicId) != null) return Result.RUNNING;
        long eut = plan.eut();
        boolean accepted;
        if (points) {
            if (data.points(player.getUUID()).compareTo(java.math.BigInteger.valueOf(plan.points())) < 0) return Result.INSUFFICIENT;
            CompoundTag receipt = new CompoundTag(); receipt.putString("Points", Long.toString(plan.points()));
            accepted = Hk3ResearchPayment.commit(player, data, () -> data.startResearchWithPoints(owner, player.getUUID(),
                    new Hk3ResearchWorkQueue.Quote(topicId, facility, lab, plan.ticks(), eut, "points", receipt), true));
        } else {
            var payment = Hk3ResearchMaterialPayment.prepare(player.getInventory(), 36, materials(plan, lab, gaze, suppression));
            if (payment == null) return Result.INSUFFICIENT;
            accepted = Hk3ResearchPayment.commit(player, data, () -> data.startResearch(owner,
                    Hk3ResearchData.withPayer(new Hk3ResearchWorkQueue.Quote(topicId, facility, lab, plan.ticks(), eut, "materials", payment.receipt()), player.getUUID()),
                    true, payment::commit));
            if (accepted) player.inventoryMenu.broadcastChanges();
        }
        if(accepted)com.sirin.hk3gtl.common.easter.Hk3EggRuntime.observe(player,"research_paid",java.util.Map.of("topic",topicId,"committed","true"));
        return accepted ? Result.STARTED : Result.CAPACITY;
    }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    public static List<Hk3ResearchPlans.Material> materials(Hk3ResearchPlans.Plan plan, int lab, double gaze) {
        return materials(plan, lab, gaze, 0);
    }
    public static List<Hk3ResearchPlans.Material> materials(Hk3ResearchPlans.Plan plan, int lab, double gaze, double suppression) {
        return plan.materials().stream().map(m -> new Hk3ResearchPlans.Material(m.tag(),
                Hk3ResearchMath.materialCount(m.count(), lab, Math.max(0, gaze), suppression, m.sensitivity()), m.sensitivity())).toList();
    }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
