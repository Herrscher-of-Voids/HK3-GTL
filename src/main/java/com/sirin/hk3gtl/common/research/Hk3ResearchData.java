package com.sirin.hk3gtl.common.research;

/** 【变更记录 #8】2026-10-01 00:00:53（修订121）：删除无；新增/修改：正式交流来源严格核对首信、回复路径和本队归属；用途：个人与团队记录隔离，保留历史与权限。 */

/** 【变更记录 #7】2026-09-30 23:58:50（修订121）：删除旧个人答复自动代表新队的生产路径；新增/修改：历史迁队投影不作为新研究工况；真实答复原位替换并保留旧凭据；用途：团队外交、阅读与个人经历分账，不发研究或物品奖励。 */



/**
 * 【文件职责／本轮边界】同一SavedData保存团队知识、个人付款、任务及待领退款；完成成果迁移、在研不复制、解散退款。
 * 【变更记录 #3】2026-09-29 21:06:40（第 3 次编号备注 · 内测5修订100）
 * 删除：取消已被批准规则替代的研究个人独占、旧数值或在线限定分支；历史备注与其他系统保留。
 * 新增／修改：同一SavedData保存团队知识、个人付款、任务及待领退款；完成成果迁移、在研不复制、解散退款。
 * 用途：接通实际证据→付款→研究完成与权限检查；不授予缺真实证据的课题。
 * 边界：编译和账本测试不代表游戏验收；S02至S05正式结构及未接线课题仍未完成。
 * 追溯：logs/research-mainline-r100；R100_FINAL_RECORD。
 */

import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.StringTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.saveddata.SavedData;
import java.util.HashSet;
import java.util.Set;
import java.util.UUID;

/** 中文说明：该处说明已按当前代码行为整理。*/
/**
 * 【变更记录 #1】2026-09-27 04:15:46（第 1 次备注 · 内测5修订90）
 * 删除：无。新增：计算机扣电回调隔离；研究推进异常时标记存档待保存。
 * 修改：保留支付、实验和槽位规则，拒绝回调重入；异常后保留已发生的任务计时。
 * 用途：验证付费任务、点数生产及存档恢复的一致性，不改退款或团队归属。
 */
/**
 * 【变更记录 #2】2026-09-27 04:32:00（第 2 次备注 · 内测5修订90）
 * 删除：损坏存档加载失败后回落空研究账本的隐式路径。新增：共用保存读取保护。
 * 修改：保留旧Accounts存档兼容，但已有文件缺少Accounts时拒绝重置；用途：保留费用和完成记录。
 */
/**
 * 【变更记录 #4】2026-09-29 23:37:35（内测5修订101）
 * 删除：本轮被替代的单前置或旧提示分支；其余历史保留。
 * 新增／修改：保存三类回收回执与生产工况；OPR绑定开题时的真实批次快照，生产批次不随队员复制。
 * 用途：补足研究接线并如实保留未接物理执行器及结构审批边界。
 * 追溯：logs/research-mainline-r101；R101_FINAL_RECORD。
 */
/** 【变更记录 #5】2026-09-30 20:28:36（修订117）：删除无；新增：团队会面许可独立保存，茧授权不冒充机器配方结算；修改许可读取/结算守卫；用途：分开审查与研究，防预览或关闭误授予。 */
/** 【变更记录 #6】2026-09-30 23:43:42（修订120）：删除无；新增/修改：供文明等级核对真实来源的工况回执只读副本；用途：按真实团队事实展示文明进度，不给机器/配方增加等级锁。 */
/**
 * 【变更记录 #9】2026-11-04 01:23:43（第9次备注 · 内测5修订194）
 * - 删除：无，保留历史与原有内存事务入口。
 * - 新增：付款日志恢复和同对象后像恢复；加载先恢复文件，再恢复已缓存账本和在线库存。
 * - 修改：服务端取得账本时阻断未能恢复的日志，避免旧缓存覆盖已经支付的工作。
 * - 用途：配合Hk3ResearchPayment接通材料、实验和退款跨文件原子提交；计算机能源接口不变。
 */
/**
 * 【变更记录 #10】2026-11-04 02:53:59（第10次备注 · 内测5修订194）
 * - 删除：本类直接恢复缓存的分散调用；新增：无。
 * - 修改：缓存与玩家恢复委托Hk3ResearchPayment.recovered，成功后才结束日志，异常阻断运行。
 * - 用途：加载时的内存同步与文件提交共用完成边界，防旧缓存覆盖已付款工单。
 */
public final class Hk3ResearchData extends SavedData {
    private CompoundTag accounts = new CompoundTag();
    private Hk3ResearchWorkQueue jobs = new Hk3ResearchWorkQueue();
    private CompoundTag computers = new CompoundTag();
    /** 修订100 · 2026-09-29：团队知识、个人付款与待领退款在同一保存周期中结算。 */
    private CompoundTag memberships = new CompoundTag();
    private CompoundTag teams = new CompoundTag();
    private CompoundTag refunds = new CompoundTag();
    private boolean inRefundClaim;
    private boolean inComputerPayment;

    private void rejectComputerReentry() {
        if (inComputerPayment) throw new IllegalStateException("Computer payment callback reentry");
        if (inRefundClaim) throw new IllegalStateException("Refund callback reentry");
    }
    private static final String NAME = "hk3gtl_research_v5";
    public static final String CORE_RESEARCH = "RN-RCA";
    public static final String CIRCUIT_PREFIX = "RN-RCA/circuit/";
    public static final Set<String> CIRCUIT_TIERS = Set.of("ulv", "lv", "mv", "hv", "ev", "iv", "luv", "zpm", "uv", "uhv", "uev", "uiv", "uxv", "opv", "max");

    /** 中文说明：该处说明已按当前代码行为整理。*/
    public static Hk3ResearchData get(ServerPlayer player) {
        return get(player.server);
    }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    public static Hk3ResearchData get(net.minecraft.server.MinecraftServer server) {
        CompoundTag recovered = Hk3ResearchPayment.recover(server);
        Hk3ResearchData data = com.sirin.hk3gtl.common.util.Hk3SavedDataGuard.get(server, NAME,
                Hk3ResearchData::load, Hk3ResearchData::new);
        if (recovered != null) {
            Hk3ResearchPayment.recovered(server, data, recovered);
        }
        return data;
    }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    public static Hk3ResearchData load(CompoundTag tag) {
        if (!tag.contains("Accounts", Tag.TAG_COMPOUND)) throw new IllegalArgumentException("Invalid or missing research accounts");
        Hk3ResearchData data = new Hk3ResearchData();
        data.accounts = tag.getCompound("Accounts").copy();
        if (tag.contains("Jobs")) {
            if (!tag.contains("Jobs", Tag.TAG_COMPOUND)) throw new IllegalArgumentException("Invalid research jobs");
            data.jobs = Hk3ResearchWorkQueue.load(tag.getCompound("Jobs"));
        }
        if (tag.contains("Computers")) {
            if (!tag.contains("Computers", Tag.TAG_COMPOUND)) throw new IllegalArgumentException("Invalid computers");
            data.computers = tag.getCompound("Computers").copy();
        }
        for (String field : new String[]{"Memberships", "Teams", "Refunds"})
            if (tag.contains(field) && !tag.contains(field, Tag.TAG_COMPOUND))
                throw new IllegalArgumentException("Invalid research " + field);
        data.memberships = tag.getCompound("Memberships").copy();
        data.teams = tag.getCompound("Teams").copy();
        data.refunds = tag.getCompound("Refunds").copy();
        for (String member : data.memberships.getAllKeys()) {
            UUID.fromString(member);
            if (!data.memberships.hasUUID(member)) throw new IllegalArgumentException("Invalid membership");
        }
        for (String team : data.teams.getAllKeys()) UUID.fromString(team);
        for (String payer : data.refunds.getAllKeys()) data.refundItems(UUID.fromString(payer));
        return data;
    }
    /** 只替换持久状态，保留实例身份，避免DimensionDataStorage仍持有旧对象。 */
    void restore(CompoundTag snapshot) {
        Hk3ResearchData restored = load(snapshot);
        accounts = restored.accounts; jobs = restored.jobs; computers = restored.computers;
        memberships = restored.memberships; teams = restored.teams; refunds = restored.refunds;
        setDirty();
    }

    /** 输出独立副本，外部不能借save返回值修改内存状态。 / Serialize a copy, preventing external mutation through save output. */
    @Override public CompoundTag save(CompoundTag tag) {
        tag.put("Accounts", accounts.copy()); tag.put("Jobs", jobs.save());
        tag.put("Computers", computers.copy());
        tag.put("Memberships", memberships.copy()); tag.put("Teams", teams.copy());
        tag.put("Refunds", refunds.copy()); return tag;
    }

    /** 中文说明：该处备注已按当前代码行为整理，不使用问号占位。*/
    public java.math.BigInteger points(UUID owner) {
        CompoundTag account = account(owner);
        if (!account.contains("Points")) return java.math.BigInteger.ZERO;
        if (!account.contains("Points", Tag.TAG_STRING)) throw new IllegalArgumentException("Invalid point balance type");
        java.math.BigInteger value = new java.math.BigInteger(account.getString("Points"));
        if (value.signum() < 0) throw new IllegalArgumentException("Negative research balance");
        return value;
    }

    /** 中文说明：该处备注已按当前代码行为整理，不使用问号占位。*/
    private void putPoints(UUID owner, java.math.BigInteger value) {
        CompoundTag account = account(owner).copy(); account.putString("Points", value.toString());
        accounts.put(owner.toString(), account); setDirty();
    }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    public boolean tickComputer(UUID owner, String facility, long tick, int circuit, boolean online,
                                java.util.function.BooleanSupplier debitEnergy) {
        rejectComputerReentry();
        if (owner == null || facility == null || facility.isBlank() || tick < 0)
            throw new IllegalArgumentException("Invalid computer identity");
        if (!online || circuit < 0 || circuit > 16) return false;
        if (computers.contains(facility) && !computers.contains(facility, Tag.TAG_COMPOUND))
            throw new IllegalArgumentException("Invalid computer meter");
        CompoundTag stored = computers.getCompound(facility);
        int remainder = 0;
        if (!stored.isEmpty()) {
            if (!stored.hasUUID("Owner") || !stored.contains("Remainder", Tag.TAG_INT)
                    || !stored.contains("Tick", Tag.TAG_LONG)) throw new IllegalArgumentException("Invalid computer record");
            if (stored.getInt("Remainder") < 0 || stored.getInt("Remainder") >= 800 || stored.getLong("Tick") < 0)
                throw new IllegalArgumentException("Invalid computer progress");
            if (tick <= stored.getLong("Tick")) return false;
            if (owner.equals(stored.getUUID("Owner"))) remainder = stored.getInt("Remainder");
        }
        // 在扣电前解析余额，损坏账户不能先消耗能源后才报错。
        // 中文备注：该处说明已按当前代码行为整理。
        java.math.BigInteger balance = points(owner);
        inComputerPayment = true;
        try { if (!debitEnergy.getAsBoolean()) return false; }
        finally { inComputerPayment = false; }
        int work = remainder + 4 + circuit;
        if (work >= 800) putPoints(owner, balance.add(java.math.BigInteger.ONE));
        CompoundTag next = new CompoundTag(); next.putUUID("Owner", owner);
        next.putInt("Remainder", work % 800); next.putLong("Tick", tick);
        computers.put(facility, next); setDirty();
        return true;
    }

    /** 拆除清除未完成机器工作量，已结算点数保留。 / Removal discards fractional machine work, never credited points. */
    public void removeComputer(UUID owner, String facility) {
        rejectComputerReentry();
        CompoundTag meter = computers.getCompound(facility);
        if (meter.hasUUID("Owner") && meter.getUUID("Owner").equals(owner)) { computers.remove(facility); setDirty(); }
    }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    public boolean startResearchWithPoints(UUID owner, Hk3ResearchWorkQueue.Quote quote, boolean evidenceReady) {
        return startResearchWithPoints(owner, owner, quote, evidenceReady);
    }
    public boolean startResearchWithPoints(UUID scope, UUID payer, Hk3ResearchWorkQueue.Quote quote, boolean evidenceReady) {
        if (!"points".equals(quote.payment()) || !quote.paid().contains("Points", Tag.TAG_STRING)) return false;
        java.math.BigInteger price = new java.math.BigInteger(quote.paid().getString("Points"));
        if (price.signum() <= 0) return false;
        if (!scope(payer).equals(scope)) return false;
        return startResearch(scope, withPayer(quote, payer), evidenceReady, () -> {
            java.math.BigInteger balance = points(payer);
            if (balance.compareTo(price) < 0) return false;
            putPoints(payer, balance.subtract(price)); return true;
        });
    }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    public boolean startResearch(UUID owner, Hk3ResearchWorkQueue.Quote quote, boolean evidenceReady,
                                 java.util.function.BooleanSupplier debit) {
        rejectComputerReentry();
        var experiment=Hk3LabExperimentRules.get(quote.topic());
        if (experiment!=null && (hasExperiment(owner,experiment.research())
                || (quote.topic().equals("LAB-ERM-AID") && !hasLabBaseline(owner))
                || (experiment.baseline() && hasLabBaseline(owner)))) return false;
        if (quote.topic().equals("LAB-OPR") && (!recoveryAuditReady(owner)
                || !recoveryProofs(owner).equals(quote.paid().getCompound("RecoveryProofs")))) return false;
        boolean started = jobs.start(owner, quote, id -> completed(owner, id), evidenceReady, debit);
        if (started) setDirty();
        return started;
    }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    public Hk3ResearchWorkQueue.Outcome advanceResearch(UUID owner, String topic, String facility, long tick,
            boolean formed, boolean online, double speed, java.util.function.BooleanSupplier debitEnergy) {
        rejectComputerReentry();
        var snapshot = jobs.snapshot(owner, topic);
        if (snapshot == null) return Hk3ResearchWorkQueue.Outcome.MISSING;
        var experiment=Hk3LabExperimentRules.get(topic);
        var definition = Hk3ResearchCatalog.bundled().get(experiment==null?topic:experiment.research());
        if (experiment!=null) { online=true; speed=1; }
        boolean valid = definition != null && snapshot.quote().lab() >= definition.lab()
                && definition.prerequisites().stream().allMatch(id -> completed(owner, id));
        Hk3ResearchWorkQueue.Outcome result = null;
        try {
            result = jobs.advance(owner, topic, facility, tick, formed && valid, online, speed, debitEnergy,
                    () -> experiment==null ? completed(owner, topic) || recordCompletion(owner, topic, snapshot.quote().lab())
                            : completeLabExperiment(owner,snapshot.quote(),experiment));
            return result;
        } finally {
            // 只保存可能改变的计时；纯离线/未成型/重复调用不持续标脏。
            // 回调抛错也可能已记录本tick或满进度，必须进入同一SavedData保存周期。
            if (formed && valid && online && snapshot.quote().facility().equals(facility)
                    && result != Hk3ResearchWorkQueue.Outcome.DUPLICATE_TICK) setDirty();
        }
    }

    /** 用于后续界面同步的不可变任务快照；不存在返回null。 / Immutable job snapshot for future UI sync; absent jobs return null. */
    public Hk3ResearchWorkQueue.Snapshot researchJob(UUID owner, String topic) { return jobs.snapshot(owner, topic); }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    public boolean recordExperiment(UUID owner, String topic) {
        return recordExperiment(owner, topic, "legacy-real-event:" + owner);
    }
    public boolean recordExperiment(UUID scope, String topic, String source) {
        if (source == null || source.isBlank() || Hk3ResearchCatalog.bundled().get(topic) == null) return false;
        if (!append(scope, "Experiments", topic)) return false;
        append(scope, "EvidenceSources", topic + "|" + source); return true;
    }

    /** 购买样本/旧馈赠标记均不能替代实验记录。 / Bought samples and legacy gift flags do not substitute experimental evidence. */
    public boolean hasExperiment(UUID owner, String topic) {
        return Hk3ResearchCatalog.bundled().get(topic) != null && values(owner, "Experiments").contains(topic);
    }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    public java.util.List<Hk3ResearchWorkQueue.Snapshot> activeResearch(UUID owner, String facility) { return jobs.active(owner, facility); }

    public boolean hasLabBaseline(UUID scope) { return values(scope,"LabSteps").contains("ERM_BASELINE_V1"); }
    /** 修订101 · 2026-09-29：新增三类真实回收账；不继承原队生产批次，不重复扣生产投入。 */
    public boolean recordRecovery(UUID scope, String category, CompoundTag receipt) {
        rejectComputerReentry();
        if (!Hk3ResearchBatchProofs.RECOVERY.contains(category) || !Hk3ResearchBatchProofs.valid(receipt)) return false;
        var account = account(scope).copy(); var proofs = account.getCompound("RecoveryProofs").copy();
        if (proofs.contains(category)) return false;
        for (String key : proofs.getAllKeys()) if (proofs.getCompound(key).getUUID("Batch").equals(receipt.getUUID("Batch"))) return false;
        proofs.put(category, receipt.copy()); account.put("RecoveryProofs", proofs);
        accounts.put(scope.toString(), account); setDirty(); return true;
    }
    public CompoundTag recoveryProofs(UUID scope) { return account(scope).getCompound("RecoveryProofs").copy(); }
    public boolean recoveryAuditReady(UUID scope) { return Hk3ResearchBatchProofs.recoveryReady(recoveryProofs(scope)); }
    /** 修订101：生产工况不随成员复制；每个已定义工况只保留首份有效结算回执。 */
    public boolean recordProcessFact(UUID scope,String fact,CompoundTag receipt) {
        rejectComputerReentry();
        if(!Hk3ResearchExecutionContracts.factNames().contains(fact) || !Hk3ResearchBatchProofs.valid(receipt))return false;
        var account=account(scope).copy();var proofs=account.getCompound("ProcessFacts").copy();
        if(proofs.contains(fact))return false;
        proofs.put(fact,receipt.copy());account.put("ProcessFacts",proofs);accounts.put(scope.toString(),account);setDirty();return true;
    }
    /** 真实团队答复可替换旧迁队投影；旧凭据保留归档，不重新结算研究。 */
    public boolean recordFormalCommunication(UUID scope,CompoundTag receipt) {
        rejectComputerReentry();
        if(!Hk3ResearchBatchProofs.valid(receipt)||!receipt.hasUUID("Team")||!scope.equals(receipt.getUUID("Team"))
                ||!receipt.getString("Authority").equals("team_owner_or_explicit_delegate")||receipt.contains("TimeBasis")
                ||!receipt.getString("Recipe").equals("hk3gtl:first_contact_reply")
                ||!receipt.getCompound("Inputs").getString("Letter").equals("otto_first_contact")
                ||!Set.of("accepted","declined").contains(receipt.getCompound("Outputs").getString("Reply")))return false;
        var old=processFactReceipt(scope,"formal_communication");
        if(old.isEmpty())return recordProcessFact(scope,"formal_communication",receipt);
        if(!old.contains("TimeBasis"))return false;
        var a=account(scope).copy();a.put("ArchivedPersonalContactProjection",old.copy());var proofs=a.getCompound("ProcessFacts").copy();
        proofs.put("formal_communication",receipt.copy());a.put("ProcessFacts",proofs);accounts.put(scope.toString(),a);setDirty();return true;
    }
    /** 文明进度只读来源回执；返回副本，禁止把界面/物品标记当成工况。 */
    public CompoundTag processFactReceipt(UUID scope,String fact) {
        if(fact.startsWith("recovery_"))return recoveryProofs(scope).getCompound(fact.substring(9)).copy();
        return account(scope).getCompound("ProcessFacts").getCompound(fact).copy();
    }
    public boolean hasProcessFact(UUID scope,String fact) {
        if(fact.equals("formal_communication")&&processFactReceipt(scope,fact).contains("TimeBasis"))return false;
        if(fact.equals("cocoon_authorization"))return hasReviewPermission(scope,1);
        if(fact.startsWith("recovery_"))return Hk3ResearchBatchProofs.valid(recoveryProofs(scope).getCompound(fact.substring(9)));
        return Hk3ResearchBatchProofs.valid(account(scope).getCompound("ProcessFacts").getCompound(fact));
    }
    /** 团队会面许可与机器加工回执分开存；由真实审查结算桥写入，不随研究成果复制。 */
    public boolean recordReviewPermission(UUID scope,int stage,UUID meeting) {
        rejectComputerReentry();if(scope==null||meeting==null||stage<1||stage>2)return false;
        var current=account(scope).copy();var permits=current.getCompound("ReviewPermits").copy();String key="Stage"+stage;
        if(permits.hasUUID(key))return false;if(stage==2&&!permits.hasUUID("Stage1"))return false;
        permits.putUUID(key,meeting);current.put("ReviewPermits",permits);accounts.put(scope.toString(),current);setDirty();return true;
    }
    public boolean hasReviewPermission(UUID scope,int stage) {
        if(stage<1||stage>2)return false;var permits=account(scope).getCompound("ReviewPermits");
        return permits.hasUUID("Stage1")&&(stage==1||permits.hasUUID("Stage2"));
    }
    public Hk3ResearchWorkQueue.Snapshot displayJob(UUID scope,String research) {
        var formal=researchJob(scope,research); if(formal!=null)return formal;
        return jobs.entries().stream().filter(e -> e.scope().equals(scope))
                .map(Hk3ResearchWorkQueue.Entry::snapshot).filter(s -> {
                    var spec=Hk3LabExperimentRules.get(s.quote().topic());
                    return spec!=null && spec.research().equals(research);
                }).findFirst().orElse(null);
    }
    private boolean completeLabExperiment(UUID scope,Hk3ResearchWorkQueue.Quote quote,Hk3LabExperimentRules.Spec spec) {
        var receipt=quote.paid(); var tools=checkedItems(receipt,"Tools");
        UUID payer=payer(scope,quote); var pending=refundItems(payer);
        for(Tag tool:tools)pending.add(tool.copy());
        if(spec.baseline()) append(scope,"LabSteps","ERM_BASELINE_V1");
        else {
            String source=quote.facility()+"/"+spec.id();
            if(spec.id().equals("LAB-OPR")){
                var proofs=receipt.getCompound("RecoveryProofs");
                if(!Hk3ResearchBatchProofs.recoveryReady(proofs))return false;
                for(String category:Hk3ResearchBatchProofs.RECOVERY.stream().sorted().toList())
                    source+="/"+category+":"+proofs.getCompound(category).getUUID("Batch");
            }
            recordExperiment(scope,spec.research(),source);
        }
        if(!pending.isEmpty())refunds.put(payer.toString(),pending);
        setDirty(); return true;
    }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    private CompoundTag account(UUID id) {
        if (accounts.contains(id.toString()) && !accounts.contains(id.toString(), Tag.TAG_COMPOUND)) throw new IllegalArgumentException("Invalid research account " + id);
        return accounts.getCompound(id.toString());
    }
    private Set<String> values(UUID id, String field) {
        CompoundTag account = account(id);
        if (account.contains(field) && !account.contains(field, Tag.TAG_LIST)) throw new IllegalArgumentException("Invalid research field " + field);
        ListTag list = account.getList(field, Tag.TAG_STRING);
        if (account.contains(field) && ((ListTag)account.get(field)).size() != list.size()) throw new IllegalArgumentException("Invalid research list " + field);
        Set<String> result = new HashSet<>();
        for (int i=0;i<list.size();i++) result.add(list.getString(i));
        return result;
    }

    /** 单个完成标记不够：同时验证全部祖先，缺前置或未知课题不得放行。 / A completion flag must include all ancestors; unknown/orphaned nodes cannot unlock. */
    public boolean completed(UUID id, String research) {
        Set<String> complete = values(id, "Completed");
        return validCompleted(research, complete);
    }
    private boolean validCompleted(String research, Set<String> complete) {
        return validCompleted(research, complete, new HashSet<>());
    }
    /** 共享祖先每次查询只验证一次，避免菱形依赖导致重复遍历。 / Visit shared ancestors once per query, avoiding exponential diamond traversal. */
    private boolean validCompleted(String research, Set<String> complete, Set<String> verified) {
        if (verified.contains(research)) return true;
        var topic = Hk3ResearchCatalog.bundled().get(research);
        if (topic == null || !complete.contains(research)) return false;
        for (String parent : topic.prerequisites()) if (!validCompleted(parent, complete, verified)) return false;
        verified.add(research);
        return true;
    }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    public boolean recordCompletion(UUID id, String research, int lab) {
        Set<String> complete = values(id, "Completed");
        if (!Hk3ResearchCatalog.bundled().prerequisitesMet(research, complete, lab)) return false;
        for (String parent : Hk3ResearchCatalog.bundled().get(research).prerequisites()) {
            if (!validCompleted(parent, complete)) return false;
        }
        return append(id, "Completed", research);
    }

    /** 正常电路技术验证器完成后记账；不是拾取事件，绝不能将买来样本当作制造证据。 / Record verified normal-route technology, never mere inventory possession. */
    public boolean recordCircuitTechnology(UUID id, String tier) {
        return CIRCUIT_TIERS.contains(tier) && append(id, "CircuitTechnology", tier);
    }
    /** 中文说明：该处说明已按当前代码行为整理。*/
    public boolean recordCircuitAnalysis(UUID id, String tier) {
        return CIRCUIT_TIERS.contains(tier) && completed(id, CORE_RESEARCH)
                && values(id,"CircuitTechnology").contains(tier) && append(id, "CircuitAnalysis", tier);
    }
    /** 逐级授权，不把MAX知识自动展开为所有电路；物理核心仍由配方notConsumable检查。 / Per-tier entitlement; physical core is separately required by recipe input. */
    public boolean canReconstruct(UUID id, String tier) {
        return CIRCUIT_TIERS.contains(tier) && completed(id, CORE_RESEARCH)
                && values(id,"CircuitTechnology").contains(tier) && values(id,"CircuitAnalysis").contains(tier);
    }
    /** 中文说明：该处说明已按当前代码行为整理。*/
    public boolean permits(UUID id, String key) {
        if (key.startsWith(CIRCUIT_PREFIX)) return canReconstruct(id, key.substring(CIRCUIT_PREFIX.length()));
        return completed(id, key);
    }
    /** 中文说明：该处说明已按当前代码行为整理。*/
    private boolean append(UUID id, String field, String value) {
        rejectComputerReentry();
        Set<String> entries = values(id, field);
        if (!entries.add(value)) return false;
        ListTag list = new ListTag();
        entries.stream().sorted().forEach(v -> list.add(StringTag.valueOf(v)));
        CompoundTag account = account(id).copy(); account.put(field,list);
        accounts.put(id.toString(), account); setDirty(); return true;
    }

    public UUID scope(UUID player) {
        return memberships.hasUUID(player.toString()) ? memberships.getUUID(player.toString()) : player;
    }
    public boolean isMember(UUID player, UUID scope) { return scope != null && scope(player).equals(scope); }
    public Set<UUID> members(UUID scope) {
        Set<UUID> result = new HashSet<>();
        for (String key : memberships.getAllKeys()) if (memberships.getUUID(key).equals(scope)) result.add(UUID.fromString(key));
        if (result.isEmpty() && !teams.contains(scope.toString()) && scope(scope).equals(scope)) result.add(scope);
        return Set.copyOf(result);
    }

    /** 仅复制知识与已完成实验证据；点数、在研进度、投入与设施永不随成员迁移。 */
    private void inherit(UUID from, UUID to) {
        if (from.equals(to)) return;
        for (String field : new String[]{"Completed", "Experiments", "EvidenceSources", "CircuitTechnology", "CircuitAnalysis"})
            for (String value : values(from, field)) append(to, field, value);
    }
    public void reconcileTeams(java.util.Map<UUID, UUID> current, Set<UUID> liveTeams) {
        rejectComputerReentry();
        Set<UUID> players = new HashSet<>(current.keySet());
        for (String player : memberships.getAllKeys()) players.add(UUID.fromString(player));
        // 先提取旧队成果，再合并新队，避免同一次批量转队污染离队快照。
        for (UUID player : players) {
            UUID before = scope(player), after = current.getOrDefault(player, player);
            if (!before.equals(after)) inherit(before, player);
        }
        CompoundTag next = new CompoundTag();
        current.forEach((player, scope) -> next.putUUID(player.toString(), scope));
        if (!next.equals(memberships)) { memberships = next; setDirty(); }
        for (UUID player : players) inherit(player, scope(player));
        for (String oldTeam : teams.getAllKeys()) {
            UUID old = UUID.fromString(oldTeam);
            if (!liveTeams.contains(old)) {
                for (var entry : jobs.entries()) if (entry.scope().equals(old)) refundAndRemove(old, entry.snapshot().quote());
            }
        }
        CompoundTag nextTeams = new CompoundTag();
        liveTeams.forEach(id -> nextTeams.putBoolean(id.toString(), true));
        if (!nextTeams.equals(teams)) { teams = nextTeams; setDirty(); }
    }

    public static Hk3ResearchWorkQueue.Quote withPayer(Hk3ResearchWorkQueue.Quote q, UUID payer) {
        CompoundTag receipt = q.paid(); receipt.putUUID("Payer", payer);
        return new Hk3ResearchWorkQueue.Quote(q.topic(), q.facility(), q.lab(), q.ticks(), q.eut(), q.payment(), receipt);
    }
    public static UUID payer(UUID scope, Hk3ResearchWorkQueue.Quote q) {
        return q.paid().hasUUID("Payer") ? q.paid().getUUID("Payer") : scope;
    }
    public java.util.List<Hk3ResearchWorkQueue.Entry> paidResearch(UUID player) {
        return jobs.entries().stream().filter(e -> payer(e.scope(), e.snapshot().quote()).equals(player)).toList();
    }
    public boolean facilityOccupied(String facility) {
        return jobs.entries().stream().anyMatch(e -> e.snapshot().quote().facility().equals(facility));
    }
    public boolean cancelResearch(UUID scope, UUID player, String topic) {
        rejectComputerReentry();
        var job = jobs.snapshot(scope, topic);
        if (job == null || !payer(scope, job.quote()).equals(player)) return false;
        return refundAndRemove(scope, job.quote());
    }
    private boolean refundAndRemove(UUID scope, Hk3ResearchWorkQueue.Quote q) {
        UUID payer = payer(scope, q);
        CompoundTag paid = q.paid();
        java.math.BigInteger nextBalance = null;
        ListTag nextItems = refundItems(payer);
        if (q.payment().equals("points")) {
            if (!paid.contains("Points", Tag.TAG_STRING)) throw new IllegalArgumentException("Missing point receipt");
            var amount = new java.math.BigInteger(paid.getString("Points"));
            if (amount.signum() <= 0) throw new IllegalArgumentException("Invalid point receipt");
            nextBalance = points(payer).add(amount);
        } else {
            ListTag items = checkedItems(paid, "Items");
            for (Tag item : items) nextItems.add(item.copy());
        }
        if (!jobs.cancel(scope, q.topic())) return false;
        if (nextBalance != null) putPoints(payer, nextBalance);
        if (!nextItems.isEmpty()) refunds.put(payer.toString(), nextItems);
        setDirty(); return true;
    }
    private static ListTag checkedItems(CompoundTag parent, String key) {
        if (!parent.contains(key, Tag.TAG_LIST)) throw new IllegalArgumentException("Missing material receipt");
        ListTag items = parent.getList(key, Tag.TAG_COMPOUND);
        if (((ListTag)parent.get(key)).size() != items.size()) throw new IllegalArgumentException("Invalid material receipt");
        for (Tag raw : items) {
            CompoundTag item = (CompoundTag)raw;
            if (!item.contains("id", Tag.TAG_STRING) || !item.contains("Count", Tag.TAG_BYTE) || item.getByte("Count") <= 0)
                throw new IllegalArgumentException("Invalid refundable stack");
        }
        return items.copy();
    }
    public ListTag refundItems(UUID payer) {
        return refunds.contains(payer.toString()) ? checkedItems(refunds, payer.toString()) : new ListTag();
    }
    /** 按真实物品及NBT规划背包差量；容纳不下的留账，不丢地面。 */
    public int claimRefunds(UUID payer, net.minecraft.world.Container inventory) {
        rejectComputerReentry();
        ListTag pending = refundItems(payer), remain = new ListTag();
        var before = new java.util.ArrayList<net.minecraft.world.item.ItemStack>();
        var after = new java.util.ArrayList<net.minecraft.world.item.ItemStack>();
        int slots = Math.min(36, inventory.getContainerSize()), moved = 0;
        for (int i=0;i<slots;i++) { before.add(inventory.getItem(i).copy()); after.add(inventory.getItem(i).copy()); }
        for (Tag raw : pending) {
            var stack = net.minecraft.world.item.ItemStack.of((CompoundTag)raw);
            if (stack.isEmpty()) { remain.add(raw.copy()); continue; }
            int initial = stack.getCount();
            for (int pass=0;pass<2;pass++) for (int i=0;i<slots && !stack.isEmpty();i++) {
                var target = after.get(i);
                if (!inventory.canPlaceItem(i, stack) || (pass==0 ? target.isEmpty() : !target.isEmpty())) continue;
                if (!target.isEmpty() && !net.minecraft.world.item.ItemStack.isSameItemSameTags(target, stack)) continue;
                int n = Math.min(stack.getCount(), Math.min(inventory.getMaxStackSize(), stack.getMaxStackSize()) - target.getCount());
                if (n<=0) continue;
                if (target.isEmpty()) after.set(i, stack.copyWithCount(n)); else target.grow(n);
                stack.shrink(n);
            }
            moved += initial-stack.getCount();
            if (!stack.isEmpty()) remain.add(stack.save(new CompoundTag()));
        }
        if (moved == 0) return 0;
        inRefundClaim = true;
        try {
            var debit = new Hk3InventoryDebit<>(before, after, inventory::getItem, inventory::setItem,
                    net.minecraft.world.item.ItemStack::matches, net.minecraft.world.item.ItemStack::copy, inventory::setChanged);
            if (!debit.commit()) return 0;
            if (remain.isEmpty()) refunds.remove(payer.toString()); else refunds.put(payer.toString(), remain);
            setDirty(); return moved;
        } finally { inRefundClaim = false; }
    }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
