package com.sirin.hk3gtl.common.research;

 









/** 修订100 · 2026-09-29：接通团队研究归属、个人付款及真实实验来源。 */

 

import com.gregtechceu.gtceu.api.GTValues;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import java.util.List;

 





 
 






public final class Hk3ResearchStartService {
    private Hk3ResearchStartService() {}

    public static boolean dedicatedToW13(String topic) {
        return topic.equals("RN-WCE") || topic.equals("RN-TAA");
    }

    /** 玩家可读拒绝原因；枚举不包含客户端授权。 / User-facing rejection reasons, never client authorization. */
    public enum Result { STARTED, UNAVAILABLE, LOCKED, COMPLETED, RUNNING, INSUFFICIENT, CAPACITY }

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
        return start(player, owner, facility, lab, available, topicId, points, gaze, suppression,
                String.format(java.util.Locale.ROOT, "S%02d", lab));
    }
    public static Result start(ServerPlayer player, java.util.UUID owner, String facility, int lab, boolean available,
                               String topicId, boolean points, double gaze, double suppression, String role) {
        if (!available || !Hk3ResearchData.get(player).isMember(player.getUUID(),owner)) return Result.UNAVAILABLE;
        if (dedicatedToW13(topicId) != role.equals("W13")) return Result.LOCKED;
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

    public static List<Hk3ResearchPlans.Material> materials(Hk3ResearchPlans.Plan plan, int lab, double gaze) {
        return materials(plan, lab, gaze, 0);
    }
    public static List<Hk3ResearchPlans.Material> materials(Hk3ResearchPlans.Plan plan, int lab, double gaze, double suppression) {
        return plan.materials().stream().map(m -> new Hk3ResearchPlans.Material(m.tag(),
                Hk3ResearchMath.materialCount(m.count(), lab, Math.max(0, gaze), suppression, m.sensitivity()), m.sensitivity())).toList();
    }
}

 
