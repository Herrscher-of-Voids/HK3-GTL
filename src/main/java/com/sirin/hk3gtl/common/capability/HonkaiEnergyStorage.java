package com.sirin.hk3gtl.common.capability;



import net.minecraft.nbt.CompoundTag;

/**
 * 通用崩坏能存储实现 —— 可持久化 + 可配置 I/O 方向的 {@link IHonkaiEnergyContainer} 基础实现。
 *
 * <h3>典型用法</h3>
 * <pre>
 *   HonkaiEnergyStorage input = HonkaiEnergyStorage.input(capacity);
 *   HonkaiEnergyStorage output = HonkaiEnergyStorage.output(capacity);
 *   HonkaiEnergyStorage creative = HonkaiEnergyStorage.creative();
 * </pre>
 *
 * <h3>NBT 持久化</h3>
 * <ul>
 *   <li>{@link #saveNBT} / {@link #loadNBT} 给 BlockEntity / ItemStack 使用</li>
 *   <li>key 使用短名避免 NBT 臃肿：{@code h} = amount, {@code c} = capacity</li>
 *   <li>I/O 方向不序列化（由 BlockEntity 构造时根据自身类型固定）</li>
 * </ul>
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>改默认容量时同步检查 {@link com.sirin.hk3gtl.common.block.energy.HonkaiHatchType} 的设计值</li>
 *   <li>新增"转换损耗"字段：不要塞进本类，写一个装饰器 {@code LossyHonkaiEnergyStorage}</li>
 *   <li>多线程访问：本类非线程安全，服务端机器 tick 串行访问没问题；跨线程需外部同步</li>
 * </ul>
 */
public class HonkaiEnergyStorage implements IHonkaiEnergyContainer {

    private long amount;
    private long capacity;
    private final boolean canInsert;
    private final boolean canExtract;
    /** true 表示"创造仓"—— insert/extract 不改变 amount，始终满载 */
    private final boolean creative;

    public HonkaiEnergyStorage(long capacity, boolean canInsert, boolean canExtract, boolean creative) {
        this.capacity = capacity;
        this.canInsert = canInsert;
        this.canExtract = canExtract;
        this.creative = creative;
        this.amount = creative ? capacity : 0L;
    }

    /** 常用工厂：普通输入仓（只接受外部注入，机器可以抽取） */
    public static HonkaiEnergyStorage input(long capacity) {
        return new HonkaiEnergyStorage(capacity, true, true, false);
    }

    /** 常用工厂：普通输出仓（机器可以注入，外部可以抽取） */
    public static HonkaiEnergyStorage output(long capacity) {
        return new HonkaiEnergyStorage(capacity, true, true, false);
    }

    /** 常用工厂：创造仓（无限能量，insert 接受但不积累，extract 无限给） */
    public static HonkaiEnergyStorage creative() {
        return new HonkaiEnergyStorage(Long.MAX_VALUE, true, true, true);
    }

    @Override
    public long getAmount() { return creative ? capacity : amount; }

    @Override
    public long getCapacity() { return capacity; }

    @Override
    public boolean canInsert() { return canInsert; }

    @Override
    public boolean canExtract() { return canExtract; }

    @Override
    public long insert(long request, boolean simulate) {
        if (request <= 0 || !canInsert) return 0;
        if (creative) return request; // 接受但不积累
        long free = capacity - amount;
        long accepted = Math.min(free, request);
        if (!simulate) amount += accepted;
        return accepted;
    }

    @Override
    public long extract(long request, boolean simulate) {
        if (request <= 0 || !canExtract) return 0;
        if (creative) return request; // 无限输出
        long available = Math.min(amount, request);
        if (!simulate) amount -= available;
        return available;
    }

    /** 保存到 NBT（BlockEntity#saveAdditional 调用） */
    public CompoundTag saveNBT(CompoundTag tag) {
        if (!creative) {
            tag.putLong("h", amount);
            tag.putLong("c", capacity);
        }
        return tag;
    }

    /** 从 NBT 载入（BlockEntity#load 调用） */
    public void loadNBT(CompoundTag tag) {
        if (creative) return; // 创造仓忽略 NBT
        // 必须先恢复容量，再按新容量校验存量，避免合法能量被构造时的旧容量截断。
        if (tag.contains("c")) capacity = Math.max(1, tag.getLong("c"));
        if (tag.contains("h")) amount = Math.max(0, Math.min(tag.getLong("h"), capacity));
    }

    /** 给其他实现（如无线仓）共享基础读写的直接访问。 */
    public void setAmountUnchecked(long value) { this.amount = Math.max(0, Math.min(value, capacity)); }
}
