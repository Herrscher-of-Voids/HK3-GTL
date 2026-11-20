package com.sirin.hk3gtl.mixin.ae;

import appeng.api.stacks.AEKey;
import appeng.api.stacks.GenericStack;
import appeng.integration.modules.jeirei.EncodingHelper;
import appeng.menu.me.common.GridInventoryEntry;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;
import org.spongepowered.asm.mixin.gen.Invoker;

import java.util.Comparator;
import java.util.List;
import java.util.Map;

@Mixin(value = EncodingHelper.class, remap = false)
public interface Hk3EncodingHelperAccess {
    @Accessor("ENTRY_COMPARATOR")
    static Comparator<GridInventoryEntry> hk3gtl$entryComparator() { throw new AssertionError(); }

    @Invoker("findBestIngredient")
    static GenericStack hk3gtl$best(Map<AEKey, Integer> priorities, List<GenericStack> choices) { throw new AssertionError(); }

    @Invoker("addOrMerge")
    static void hk3gtl$merge(List<GenericStack> stacks, GenericStack addition) { throw new AssertionError(); }
}
