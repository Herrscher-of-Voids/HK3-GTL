package com.sirin.hk3gtl.common.research;



import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;
import java.util.Set;

/**
 * 【变更记录 #1】2026-09-29 · 修订101。
 * 删除：无。新增：固定类别的真实结算回执校验。修改：研究核验读取服务端批次。
 * 用途：只保留每类首次有效批次，避免长期自动化产生无界历史；持有物不算工况。
 */
/**
 * 【变更记录 #2】2026-09-29 23:37:35（内测5修订101）
 * 删除：本轮被替代的单前置或旧提示分支；其余历史保留。
 * 新增／修改：检查有效回执及三种互异回收批次，拒绝空数据或重复批次充数。
 * 用途：补足研究接线并如实保留未接物理执行器及结构审批边界。
 * 追溯：logs/research-mainline-r101；R101_FINAL_RECORD。
 */
public final class Hk3ResearchBatchProofs {
    private Hk3ResearchBatchProofs() {}
    public static final Set<String> RECOVERY = Set.of("medium", "heat", "spent_rods");
    public static boolean valid(CompoundTag receipt) {
        return receipt.hasUUID("Batch") && !receipt.getString("Facility").isBlank()
                && !receipt.getString("Recipe").isBlank() && receipt.contains("Tick", Tag.TAG_LONG)
                && receipt.getLong("Tick") >= 0 && receipt.contains("Inputs", Tag.TAG_COMPOUND)
                && !receipt.getCompound("Inputs").isEmpty() && receipt.contains("Outputs", Tag.TAG_COMPOUND)
                && !receipt.getCompound("Outputs").isEmpty();
    }
    public static boolean recoveryReady(CompoundTag proofs) {
        var batches = new java.util.HashSet<java.util.UUID>();
        for (String category : RECOVERY) {
            CompoundTag receipt = proofs.getCompound(category);
            if (!valid(receipt) || !batches.add(receipt.getUUID("Batch"))) return false;
        }
        return true;
    }
}
