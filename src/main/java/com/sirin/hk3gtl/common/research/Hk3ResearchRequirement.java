package com.sirin.hk3gtl.common.research;


/** 中文说明：该处说明已按当前代码行为整理。*/
import net.minecraft.core.Holder;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.tags.TagKey;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import org.jetbrains.annotations.Nullable;

import java.util.List;
import java.util.Objects;
import java.util.function.Supplier;

/** 中文说明：该处说明已按当前代码行为整理。*/
public record Hk3ResearchRequirement(List<Supplier<ItemStack>> stackSuppliers, String descriptionKey,
                                     @Nullable TagKey<Item> tag, int tagCount) {

    /**
     * 紧凑构造器：stackSuppliers/descriptionKey 均不可为 null。
     */
    public Hk3ResearchRequirement {
        Objects.requireNonNull(stackSuppliers, "stackSuppliers");
        Objects.requireNonNull(descriptionKey, "descriptionKey");
        stackSuppliers = List.copyOf(stackSuppliers);
        if (stackSuppliers.isEmpty()) {
            throw new IllegalArgumentException("stackSuppliers cannot be empty");
        }
    }

    /**
     * 获取主要展示用 ItemStack（已复制），调用方可安全修改。
     */
    public ItemStack createStack() {
        List<ItemStack> candidates = createCandidates();
        return candidates.isEmpty() ? ItemStack.EMPTY : candidates.get(0);
    }

    /**
     * 获取全部候选 ItemStack。研究校验/扣除时任一候选满足即可。
     */
    public List<ItemStack> createCandidates() {
        return stackSuppliers.stream()
                .map(Supplier::get)
                .map(ItemStack::copy)
                .toList();
    }

    public boolean hasAlternatives() {
        return tag != null || stackSuppliers.size() > 1;
    }

    /** 是否为 Tag 匹配模式 */
    public boolean isTagMode() {
        return tag != null;
    }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    public boolean matchesStack(ItemStack candidate, ItemStack stack) {
        if (stack.isEmpty()) return false;
        if (tag != null) return stack.is(tag);
        return ItemStack.isSameItemSameTags(stack, candidate);
    }

    /**
     * 工厂方法：与构造器等价，仅为链式调用时更可读。
     */
    public static Hk3ResearchRequirement of(Supplier<ItemStack> stackSupplier, String descriptionKey) {
        return new Hk3ResearchRequirement(List.of(stackSupplier), descriptionKey, null, 0);
    }

    @SafeVarargs
    public static Hk3ResearchRequirement oneOf(String descriptionKey, Supplier<ItemStack>... stackSuppliers) {
        return new Hk3ResearchRequirement(List.of(stackSuppliers), descriptionKey, null, 0);
    }

    /**
     * Tag 需求工厂：任意属于该 Tag 的物品均可满足（数量跨种类累计）。
     * <p>展示栈延迟解析为 Tag 的首个成员（数据包加载后才可用），Tag 为空时展示 EMPTY。</p>
     */
    public static Hk3ResearchRequirement ofTag(TagKey<Item> tag, int count, String descriptionKey) {
        Objects.requireNonNull(tag, "tag");
        if (count <= 0) throw new IllegalArgumentException("count must be positive");
        Supplier<ItemStack> display = () -> BuiltInRegistries.ITEM.getTag(tag)
                .flatMap(named -> named.stream().findFirst())
                .map(Holder::value)
                .map(item -> new ItemStack(item, count))
                .orElse(ItemStack.EMPTY);
        return new Hk3ResearchRequirement(List.of(display), descriptionKey, tag, count);
    }
}
