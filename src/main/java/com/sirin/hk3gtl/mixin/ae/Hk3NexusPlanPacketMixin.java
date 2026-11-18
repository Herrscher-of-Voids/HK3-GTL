package com.sirin.hk3gtl.mixin.ae;

import appeng.core.sync.packets.CraftConfirmPlanPacket;
import appeng.menu.me.crafting.CraftingPlanSummary;
import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import com.sirin.hk3gtl.common.integration.ae.Hk3CraftingCycleFlag;
import com.sirin.hk3gtl.common.integration.ae.nexus.crafting.Hk3NexusPlanSummary;
import net.minecraft.network.FriendlyByteBuf;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;

@Mixin(value = CraftConfirmPlanPacket.class, remap = false)
public abstract class Hk3NexusPlanPacketMixin {
    @WrapOperation(method = "<init>(Lappeng/menu/me/crafting/CraftingPlanSummary;)V",
            at = @At(value = "INVOKE", target = "Lappeng/menu/me/crafting/CraftingPlanSummary;write(Lnet/minecraft/network/FriendlyByteBuf;)V"))
    private void hk3gtl$writeExact(CraftingPlanSummary plan, FriendlyByteBuf buffer, Operation<Void> original) {
        original.call(plan, buffer);
        buffer.writeBoolean(((Hk3CraftingCycleFlag) plan).hk3gtl$hasCycles());
        buffer.writeBoolean(plan instanceof Hk3NexusPlanSummary);
        if (plan instanceof Hk3NexusPlanSummary exact) exact.writeExact(buffer);
    }

    @WrapOperation(method = "<init>(Lnet/minecraft/network/FriendlyByteBuf;)V",
            at = @At(value = "INVOKE", target = "Lappeng/menu/me/crafting/CraftingPlanSummary;read(Lnet/minecraft/network/FriendlyByteBuf;)Lappeng/menu/me/crafting/CraftingPlanSummary;"))
    private CraftingPlanSummary hk3gtl$readExact(FriendlyByteBuf buffer, Operation<CraftingPlanSummary> original) {
        CraftingPlanSummary plan = original.call(buffer);
        boolean cycles = buffer.readBoolean();
        if (buffer.readBoolean()) plan = Hk3NexusPlanSummary.readExact(plan, buffer);
        ((Hk3CraftingCycleFlag) plan).hk3gtl$setHasCycles(cycles);
        return plan;
    }
}
