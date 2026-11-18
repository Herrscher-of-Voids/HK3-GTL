package com.sirin.hk3gtl.mixin.ae;

import appeng.api.inventories.InternalInventory;
import appeng.api.networking.IGrid;
import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import com.sirin.hk3gtl.common.integration.ae.nexus.management.Hk3NexusPatternInventory;
import com.sirin.hk3gtl.common.integration.ae.nexus.network.Hk3NexusGrid;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Constant;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.ModifyConstant;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.util.List;

@Pseudo
@Mixin(targets = "com.extendedae_plus_gtladd.util.uploadPattern.GTMatrixUploadUtil", remap = false)
public abstract class Hk3NexusGtMatrixUploadMixin {
    @Unique private static final ThreadLocal<Boolean> hk3gtl$nexusUpload = ThreadLocal.withInitial(() -> false);

    @Inject(method = "findAllGTMatrixPatternInventories", at = @At("RETURN"))
    private static void hk3gtl$includeNexus(IGrid grid, CallbackInfoReturnable<List<InternalInventory>> cir) {
        cir.getReturnValue().addAll(0, Hk3NexusGrid.patternInventories(grid));
    }

    @WrapOperation(method = "uploadFromEncodingMenuToMatrix", at = @At(value = "INVOKE",
            target = "Lappeng/api/inventories/InternalInventory;addItems(Lnet/minecraft/world/item/ItemStack;)Lnet/minecraft/world/item/ItemStack;"))
    private static ItemStack hk3gtl$uploadDestination(InternalInventory inventory, ItemStack pattern,
            Operation<ItemStack> original) {
        ItemStack remaining = original.call(inventory, pattern);
        hk3gtl$nexusUpload.set(inventory instanceof Hk3NexusPatternInventory);
        return remaining;
    }

    @ModifyConstant(method = "completeUploadSuccess",
            constant = @Constant(stringValue = "extendedae_plus_gtladd.upload_to_GTMatrix.success"))
    private static String hk3gtl$uploadSuccess(String key) {
        return hk3gtl$nexusUpload.get() ? "hk3gtl.nexus.pattern_upload.success" : key;
    }
}
