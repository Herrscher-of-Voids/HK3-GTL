package com.sirin.hk3gtl.mixin.ae;

import appeng.api.config.SortDir;
import appeng.api.config.SortOrder;
import appeng.client.gui.me.common.MEStorageScreen;
import appeng.client.gui.me.common.Repo;
import appeng.client.gui.widgets.ISortSource;
import appeng.menu.me.common.GridInventoryEntry;
import com.sirin.hk3gtl.common.integration.ae.Hk3InfiniteSourceMenu;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyArg;
import org.spongepowered.asm.mixin.injection.Slice;

import java.util.Comparator;

@Mixin(value = Repo.class, remap = false)
public abstract class Hk3InfiniteSourceRepoMixin {
    @Shadow @Final private ISortSource sortSrc;

    @ModifyArg(method = "updateView", index = 0,
            slice = @Slice(from = @At(value = "INVOKE",
                    target = "Lappeng/client/gui/widgets/ISortSource;getSortBy()Lappeng/api/config/SortOrder;")),
            at = @At(value = "INVOKE", target = "Ljava/util/ArrayList;sort(Ljava/util/Comparator;)V"))
    private Comparator<? super GridInventoryEntry> hk3gtl$sortInfiniteSources(Comparator<? super GridInventoryEntry> amount) {
        if (sortSrc.getSortBy() != SortOrder.AMOUNT || !(sortSrc instanceof MEStorageScreen<?> screen)) return amount;
        var keys = ((Hk3InfiniteSourceMenu) screen.getMenu()).hk3gtl$infiniteSources();
        if (keys.isEmpty()) return amount;

        Comparator<GridInventoryEntry> infinite = Comparator.comparing(entry -> keys.contains(entry.getWhat()));
        if (sortSrc.getSortDir() == SortDir.DESCENDING) infinite = infinite.reversed();
        return infinite.thenComparing(amount);
    }
}
