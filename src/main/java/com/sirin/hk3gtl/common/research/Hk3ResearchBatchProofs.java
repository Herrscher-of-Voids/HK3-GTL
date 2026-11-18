package com.sirin.hk3gtl.common.research;



import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;
import java.util.Set;

 




 






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
