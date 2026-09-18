package com.sirin.hk3gtl.common.research;



import net.minecraft.core.Holder;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.tags.TagKey;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import org.jetbrains.annotations.Nullable;

import java.util.List;
import java.util.Objects;
import java.util.function.Supplier;

/**
 * 最小研究提交物定义 —— 研究节点所需的单个物品条目。
 *
 * <p>使用 {@link Supplier}&lt;ItemStack&gt; 而不是直接持有 ItemStack 的原因：
 * <ul>
 *   <li>GT 的材料物品在注册阶段尚未就绪，延迟获取可避开静态初始化顺序问题</li>
 *   <li>每次提交时生成新的 ItemStack 副本，避免多节点共享同一引用被修改</li>
 *   <li>Tag 需求同理：Tag 内容在数据包加载后才可解析，展示物品必须延迟获取</li>
 * </ul>
 *
 * <h3>三种匹配模式</h3>
 * <ul>
 *   <li>{@link #of}：单一物品，精确 Item+NBT 匹配</li>
 *   <li>{@link #oneOf}：多候选物品，任一满足即可</li>
 *   <li>{@link #ofTag}：物品 Tag，任意属于该 Tag 的物品均可（忽略 NBT）</li>
 * </ul>
 *
 * @param stackSuppliers 候选物品栈供应器：任一候选满足数量即可（Tag 模式下仅作 GUI 展示）
 * @param descriptionKey 本地化 key，用于 GUI 显示需求物的名称 / 说明
 * @param tag            非 null 时启用 Tag 匹配模式
 * @param tagCount       Tag 模式下的需求数量（跨物品种类累计）
 */
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

    /**
     * 判断背包中的某个物品栈是否可用于满足本需求。
     * <p>Tag 模式：{@code stack.is(tag)}（忽略 NBT）；否则精确 Item+NBT 对比候选栈。</p>
     *
     * @param candidate 当前正在结算的候选需求栈（来自 {@link #createCandidates}）
     * @param stack     背包物品栈
     */
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
