package com.sirin.hk3gtl.common.research;

















import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.StringTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.saveddata.SavedData;
import java.util.HashSet;
import java.util.Set;
import java.util.UUID;



































public final class Hk3ResearchData extends SavedData {
    private CompoundTag accounts = new CompoundTag();
    private Hk3ResearchWorkQueue jobs = new Hk3ResearchWorkQueue();
    private CompoundTag computers = new CompoundTag();
    /** 修订100 · 2026-09-29：团队知识、个人付款与待领退款在同一保存周期中结算。 */
    private CompoundTag memberships = new CompoundTag();
    private CompoundTag teams = new CompoundTag();
    private CompoundTag refunds = new CompoundTag();
    private CompoundTag legacyResearch = new CompoundTag();
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

    public static Hk3ResearchData get(ServerPlayer player) {
        return get(player.server);
    }

    public static Hk3ResearchData get(net.minecraft.server.MinecraftServer server) {
        CompoundTag recovered = Hk3ResearchPayment.recover(server);
        Hk3ResearchData data = com.sirin.hk3gtl.common.util.Hk3SavedDataGuard.get(server, NAME,
                Hk3ResearchData::load, Hk3ResearchData::new);
        if (recovered != null) {
            Hk3ResearchPayment.recovered(server, data, recovered);
        }
        return data;
    }

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
        data.legacyResearch = tag.getCompound("LegacyResearch").copy();
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
        legacyResearch = restored.legacyResearch;
        setDirty();
    }

    /** 输出独立副本，外部不能借save返回值修改内存状态。 / Serialize a copy, preventing external mutation through save output. */
    @Override public CompoundTag save(CompoundTag tag) {
        tag.put("Accounts", accounts.copy()); tag.put("Jobs", jobs.save());
        tag.put("Computers", computers.copy());
        tag.put("Memberships", memberships.copy()); tag.put("Teams", teams.copy());
        tag.put("Refunds", refunds.copy());
        tag.put("LegacyResearch", legacyResearch.copy()); return tag;
    }

    public void archiveLegacyResearch(UUID player, CompoundTag original) {
        var players = legacyResearch.getCompound("Players").copy();
        var record = players.getCompound(player.toString()).copy();
        var completed = record.getCompound("Completed").copy();
        for (var node : Hk3ResearchNodes.ordered())
            if (original.getBoolean("hk3gtl_res_" + node.id())) completed.putBoolean(node.id(), true);
        if (!completed.isEmpty()) record.put("Completed", completed);
        if (original.contains("hk3gtl_res_selected"))
            record.put("Selected", original.get("hk3gtl_res_selected").copy());
        if (record.isEmpty() || record.equals(players.getCompound(player.toString()))) return;
        players.put(player.toString(), record);
        legacyResearch.put("Players", players); setDirty();
    }

    public boolean legacyCompleted(UUID player, String research) {
        return legacyResearch.getCompound("Players").getCompound(player.toString())
                .getCompound("Completed").getBoolean(research);
    }

    public void archiveLegacyTask(String facility, CompoundTag original) {
        var tasks = legacyResearch.getCompound("Tasks").copy();
        var history = tasks.getList(facility, Tag.TAG_COMPOUND).copy();
        if (history.contains(original)) return;
        history.add(original.copy());
        tasks.put(facility, history);
        legacyResearch.put("Tasks", tasks); setDirty();
    }

    public CompoundTag legacyResearchArchive() { return legacyResearch.copy(); }

    public java.math.BigInteger points(UUID owner) {
        CompoundTag account = account(owner);
        if (!account.contains("Points")) return java.math.BigInteger.ZERO;
        if (!account.contains("Points", Tag.TAG_STRING)) throw new IllegalArgumentException("Invalid point balance type");
        java.math.BigInteger value = new java.math.BigInteger(account.getString("Points"));
        if (value.signum() < 0) throw new IllegalArgumentException("Negative research balance");
        return value;
    }

    private void putPoints(UUID owner, java.math.BigInteger value) {
        CompoundTag account = account(owner).copy(); account.putString("Points", value.toString());
        accounts.put(owner.toString(), account); setDirty();
    }

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

    public boolean startResearch(UUID owner, Hk3ResearchWorkQueue.Quote quote, boolean evidenceReady,
                                 java.util.function.BooleanSupplier debit) {
        rejectComputerReentry();
        var experiment=Hk3LabExperimentRules.get(quote.topic());
        if (experiment!=null && (hasExperiment(owner,experiment.research())
                || (quote.topic().equals("LAB-ERM-AID") && !hasLabBaseline(owner))
                || (experiment.baseline() && hasLabBaseline(owner)))) return false;
        if (quote.topic().equals("LAB-ERM-AID") && awaitingLabAid(owner)) {
            var baseline=jobs.snapshot(owner,"LAB-ERM-BASE");
            if(!baseline.quote().facility().equals(quote.facility())
                    || !baseline.id().equals(quote.paid().getUUID("BaselineJob")))return false;
        }
        if (quote.topic().equals("LAB-OPR") && (!recoveryAuditReady(owner)
                || !recoveryProofs(owner).equals(quote.paid().getCompound("RecoveryProofs")))) return false;
        boolean started = jobs.start(owner, quote, id -> completed(owner, id), evidenceReady, debit);
        if (started) setDirty();
        return started;
    }

    public Hk3ResearchWorkQueue.Outcome advanceResearch(UUID owner, String topic, String facility, long tick,
            boolean formed, boolean online, double speed, java.util.function.BooleanSupplier debitEnergy) {
        rejectComputerReentry();
        var snapshot = jobs.snapshot(owner, topic);
        if (snapshot == null) return Hk3ResearchWorkQueue.Outcome.MISSING;
        var experiment=Hk3LabExperimentRules.get(topic);
        if (experiment!=null && experiment.baseline() && hasLabBaseline(owner))
            return Hk3ResearchWorkQueue.Outcome.PAUSED;
        var definition = Hk3ResearchCatalog.bundled().get(experiment==null?topic:experiment.research());
        if (experiment!=null) { online=true; speed=1; }
        boolean valid = definition != null && snapshot.quote().lab() >= definition.lab()
                && definition.prerequisites().stream().allMatch(id -> completed(owner, id));
        Hk3ResearchWorkQueue.Outcome result = null;
        try {
            result = jobs.advance(owner, topic, facility, tick, formed && valid, online, speed, debitEnergy,
                    () -> experiment==null ? completed(owner, topic) || recordCompletion(owner, topic, snapshot.quote().lab())
                            : completeLabExperiment(owner,snapshot.quote(),experiment));
            if(experiment!=null && experiment.baseline() && hasLabBaseline(owner))
                result=Hk3ResearchWorkQueue.Outcome.STAGE_COMPLETED;
            if(result==Hk3ResearchWorkQueue.Outcome.COMPLETED && topic.equals("LAB-ERM-AID"))
                jobs.cancel(owner,"LAB-ERM-BASE");
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

    public java.util.List<Hk3ResearchWorkQueue.Snapshot> activeResearch(UUID owner, String facility) { return jobs.active(owner, facility); }
    public int usedResearchSlots(String facility) { return jobs.usedSlots(facility); }

    public boolean hasLabBaseline(UUID scope) { return values(scope,"LabSteps").contains("ERM_BASELINE_V1"); }
    public boolean awaitingLabAid(UUID scope) {
        return hasLabBaseline(scope) && jobs.snapshot(scope,"LAB-ERM-BASE")!=null
                && jobs.snapshot(scope,"LAB-ERM-AID")==null;
    }
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
    /** 工程凭据跟随最近一次真实生产机身；普通实验仍保留首份回执。 */
    public boolean recordEngineeringFact(UUID scope,String fact,CompoundTag receipt) {
        rejectComputerReentry();
        if (!(fact.matches("wonder_W(0[1-9]|1[0-5])") || fact.equals("hyperion_engineering") || fact.equals("wonder_application"))
                || !Hk3ResearchBatchProofs.valid(receipt)) return false;
        var account=account(scope).copy();var proofs=account.getCompound("ProcessFacts").copy();
        if(proofs.getCompound(fact).equals(receipt))return false;
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
        if(research.equals("RN-ERM")) {
            var aid=researchJob(scope,"LAB-ERM-AID");if(aid!=null)return aid;
        }
        return jobs.entries().stream().filter(e -> e.scope().equals(scope))
                .map(Hk3ResearchWorkQueue.Entry::snapshot).filter(s -> {
                    var spec=Hk3LabExperimentRules.get(s.quote().topic());
                    return spec!=null && spec.research().equals(research);
                }).findFirst().orElse(null);
    }
    private boolean completeLabExperiment(UUID scope,Hk3ResearchWorkQueue.Quote quote,Hk3LabExperimentRules.Spec spec) {
        if(spec.baseline()) {
            // 普通阶段保留原付费工单，辅助成功后才结算整项耗材。
            append(scope,"LabSteps","ERM_BASELINE_V1");
            return false;
        }
        var receipt=quote.paid(); var tools=checkedItems(receipt,"Tools");
        UUID payer=payer(scope,quote); var pending=refundItems(payer);
        for(Tag tool:tools)pending.add(tool.copy());
        String source=quote.facility()+"/"+spec.id();
        if(spec.id().equals("LAB-ERM-AID")) {
            var assisted=jobs.snapshot(scope,spec.id());
            var proof=new CompoundTag();proof.put("Assisted",labExperimentReceipt(assisted));
            var baseline=jobs.snapshot(scope,"LAB-ERM-BASE");
            if(baseline!=null) {
                proof.put("Baseline",labExperimentReceipt(baseline));
                source+="/baseline:"+baseline.id();
            }
            var account=account(scope).copy();account.put("ErmExperimentProof",proof);accounts.put(scope.toString(),account);
            source+="/assisted:"+assisted.id();
        }
        if(spec.id().equals("LAB-OPR")){
            var proofs=receipt.getCompound("RecoveryProofs");
            if(!Hk3ResearchBatchProofs.recoveryReady(proofs))return false;
            for(String category:Hk3ResearchBatchProofs.RECOVERY.stream().sorted().toList())
                source+="/"+category+":"+proofs.getCompound(category).getUUID("Batch");
        }
        recordExperiment(scope,spec.research(),source);
        if(!pending.isEmpty())refunds.put(payer.toString(),pending);
        setDirty(); return true;
    }
    private static CompoundTag labExperimentReceipt(Hk3ResearchWorkQueue.Snapshot job) {
        var quote=job.quote();var receipt=new CompoundTag();
        receipt.putUUID("Job",job.id());receipt.putString("Facility",quote.facility());
        receipt.putLong("Ticks",quote.ticks());receipt.putLong("EUt",quote.eut());
        receipt.put("Paid",quote.paid());return receipt;
    }

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
    public boolean hasCircuitTechnology(UUID id, String tier) {
        return values(id, "CircuitTechnology").contains(tier);
    }
    public boolean hasCircuitAnalysis(UUID id, String tier) {
        return values(id, "CircuitAnalysis").contains(tier);
    }
    public boolean recordCircuitAnalysis(UUID id, String tier) {
        return CIRCUIT_TIERS.contains(tier) && completed(id, CORE_RESEARCH)
                && hasCircuitTechnology(id, tier) && append(id, "CircuitAnalysis", tier);
    }
    /** 逐级授权，不把MAX知识自动展开为所有电路；物理核心仍由配方notConsumable检查。 / Per-tier entitlement; physical core is separately required by recipe input. */
    public boolean canReconstruct(UUID id, String tier) {
        return CIRCUIT_TIERS.contains(tier) && completed(id, CORE_RESEARCH)
                && hasCircuitTechnology(id, tier) && hasCircuitAnalysis(id, tier);
    }
    public boolean permits(UUID id, String key) {
        if (key.startsWith(CIRCUIT_PREFIX)) return canReconstruct(id, key.substring(CIRCUIT_PREFIX.length()));
        return completed(id, key);
    }
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
        if(topic.startsWith("LAB-ERM-")) {
            for(String stage:java.util.List.of("LAB-ERM-AID","LAB-ERM-BASE")) {
                var phase=jobs.snapshot(scope,stage);
                if(phase!=null)refundAndRemove(scope,phase.quote());
            }
            if(hasLabBaseline(scope))clearLabBaseline(scope);return true;
        }
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
        if(q.topic().equals("LAB-ERM-BASE"))clearLabBaseline(scope);
        if (nextBalance != null) putPoints(payer, nextBalance);
        if (!nextItems.isEmpty()) refunds.put(payer.toString(), nextItems);
        setDirty(); return true;
    }
    private void clearLabBaseline(UUID scope) {
        var steps=new ListTag();
        for(String step:values(scope,"LabSteps"))if(!step.equals("ERM_BASELINE_V1"))steps.add(net.minecraft.nbt.StringTag.valueOf(step));
        var account=account(scope).copy();account.put("LabSteps",steps);accounts.put(scope.toString(),account);setDirty();
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


