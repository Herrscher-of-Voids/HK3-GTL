package com.sirin.hk3gtl.common.worldbubble;



import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.saveddata.SavedData;

/**
 * 【变更记录 #1】2026-09-27 04:16:00（第 1 次备注 · 内测5修订90）
 * 删除：无。新增：主世界公共SavedData及账本修改自动标脏。
 * 修改：无旧账户/旧样本迁移；真实目标跨维度、跨机器共享，模拟批次独立。
 * 用途：后续机器从服务器取得同一账本，不依赖物品堆叠次数或机器移动；尚未接入工序和奖励交付。
 */
/**
 * 【变更记录 #2】2026-09-27 04:32:00（第 2 次备注 · 内测5修订90）
 * 删除：加载失败后创建空账本的隐式退路。新增：Hk3SavedDataGuard接入。
 * 修改：现有文件无法读取时明确拒绝服务且保留原文件；用途：防止次数及终止记录重置。
 */
/**
 * 【变更记录 #3】2026-09-29 23:37:35（内测5修订101）
 * 删除：本轮被替代的单前置或旧提示分支；其余历史保留。
 * 新增／修改：新增服务器线程的完成结算接口；尚无实际世界泡机器调用，不宣称物理任务已接通。
 * 用途：补足研究接线并如实保留未接物理执行器及结构审批边界。
 * 追溯：logs/research-mainline-r101；R101_FINAL_RECORD。
 */
/**
 * 【变更记录 #4】2026-09-29 23:51:00（内测5修订102）
 * 删除：资源结算不核对资源包来源的入口。新增：同一SavedData保存已冻结包与事务。
 * 修改：真实完成后准备资源，逐包核对后结算；用途：取消/重启不重抽，输出交付仍单独确认。
 */
public final class Hk3WorldBubbleData extends SavedData {
    private static final String NAME = "hk3gtl_world_bubbles_v5";
    private Hk3WorldBubbleLedger ledger = new Hk3WorldBubbleLedger();
    private Hk3WorldResourceBatches resources = new Hk3WorldResourceBatches();
    public Hk3WorldBubbleData() { ledger.onChange(this::setDirty); resources.onChange(this::setDirty); }

    public static Hk3WorldBubbleData get(MinecraftServer server) {
        return com.sirin.hk3gtl.common.util.Hk3SavedDataGuard.get(server, NAME,
                Hk3WorldBubbleData::load, Hk3WorldBubbleData::new);
    }
    /** 调用方须保持服务器线程，不把可写账本暴露给客户端消息直接结算。 */
    public Hk3WorldBubbleLedger ledger() { return ledger; }
    /** 工序实际成功后的原子结算；返回持久待交付收据，调用者仍须幂等输出并确认交付。 */
    public CompoundTag completeWithResources(MinecraftServer server,java.util.UUID operation,java.util.UUID actor,
            java.util.UUID scope,CompoundTag completed,Hk3WorldResourceCatalog catalog){
        if(!server.isSameThread())throw new IllegalStateException("World settlement requires server thread");
        var receipt=Hk3WorldResourceSettlement.prepare(ledger,resources,operation,actor,scope,completed,catalog,server.overworld().getSeed());
        settleCompleted(server,operation,actor,scope,receipt);return receipt.copy();
    }
    /** 修订101：已完成服务端工序的统一结算入口，证据只从持久账本投影。 */
    public void settleCompleted(MinecraftServer server,java.util.UUID operation,java.util.UUID actor,
            java.util.UUID scope,CompoundTag receipt) {
        if(!server.isSameThread())throw new IllegalStateException("World settlement requires server thread");
        var tx=ledger.transaction(operation);
        if(tx==null)throw new IllegalArgumentException("Unknown world operation");
        Hk3WorldResourceSettlement.validate(ledger,resources,operation,actor,scope,receipt);
        ledger.settle(operation,actor,receipt);
        Hk3WorldBubbleResearch.project(ledger,com.sirin.hk3gtl.common.research.Hk3ResearchData.get(server),scope);
    }
    public void createCompleted(MinecraftServer server,java.util.UUID batch,java.util.UUID actor,
            java.util.UUID scope,String origin,CompoundTag receipt) {
        if(!server.isSameThread()||!Hk3WorldBubbleResearch.valid(receipt,scope,batch,"I29"))
            throw new IllegalArgumentException("Invalid completed simulation");
        ledger.createSimulation(batch,actor,origin,receipt);
        Hk3WorldBubbleResearch.project(ledger,com.sirin.hk3gtl.common.research.Hk3ResearchData.get(server),scope);
    }
    public static Hk3WorldBubbleData load(CompoundTag tag) {
        if (!tag.contains("Ledger", Tag.TAG_COMPOUND)) throw new IllegalArgumentException("Missing world bubble ledger");
        if(tag.contains("ResourceVersion")&&(!tag.contains("ResourceVersion",Tag.TAG_INT)||tag.getInt("ResourceVersion")!=1
                ||!tag.contains("Resources",Tag.TAG_COMPOUND)))throw new IllegalArgumentException("Missing or unsupported resource ledger");
        if(tag.contains("Resources")&&!tag.contains("ResourceVersion",Tag.TAG_INT))throw new IllegalArgumentException("Missing resource schema");
        Hk3WorldBubbleData data = new Hk3WorldBubbleData();
        data.ledger = Hk3WorldBubbleLedger.load(tag.getCompound("Ledger"), data::setDirty);
        if(tag.contains("Resources")){
            if(!tag.contains("Resources",Tag.TAG_COMPOUND))throw new IllegalArgumentException("Invalid resource ledger");
            data.resources=Hk3WorldResourceBatches.load(tag.getCompound("Resources"),data.ledger);
            data.resources.onChange(data::setDirty);
        }
        return data;
    }
    @Override public CompoundTag save(CompoundTag tag) { tag.put("Ledger", ledger.save());tag.putInt("ResourceVersion",1);tag.put("Resources",resources.save()); return tag; }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
