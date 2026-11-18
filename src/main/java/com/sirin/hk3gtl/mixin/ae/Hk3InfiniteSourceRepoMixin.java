package com.sirin.hk3gtl.mixin.ae;

import appeng.api.config.SortDir;
import appeng.api.config.SortOrder;
import appeng.client.gui.me.common.Repo;
import appeng.menu.me.common.GridInventoryEntry;
import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import com.sirin.hk3gtl.common.integration.ae.Hk3InfiniteSourceMenu;
import net.minecraft.client.Minecraft;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;

import java.util.Comparator;

@Mixin(value = Repo.class, priority = 900, remap = false)
public abstract class Hk3InfiniteSourceRepoMixin {
    @WrapOperation(method = "updateView", at = @At(value = "INVOKE",
            target = "Lappeng/client/gui/me/common/Repo;getComparator(Lappeng/api/config/SortOrder;Lappeng/api/config/SortDir;)Ljava/util/Comparator;"))
    private Comparator<? super GridInventoryEntry> hk3gtl$sortInfiniteSources(
            Repo repo, SortOrder order, SortDir direction,
            Operation<Comparator<? super GridInventoryEntry>> operation) {
        var original = operation.call(repo, order, direction);
        if (order == SortOrder.AMOUNT
                && Minecraft.getInstance().player.containerMenu instanceof Hk3InfiniteSourceMenu menu
                && !menu.hk3gtl$infiniteSources().isEmpty()) {
            var keys = menu.hk3gtl$infiniteSources();
            Comparator<GridInventoryEntry> infinite = Comparator.comparing(entry -> keys.contains(entry.getWhat()));
            if (direction == SortDir.DESCENDING) infinite = infinite.reversed();
            return infinite.thenComparing(original);
        }
        return original;
    }
}
