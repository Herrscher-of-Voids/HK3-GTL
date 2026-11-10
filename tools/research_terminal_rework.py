"""#1 2026-09-23 02:26 Asia/Hong_Kong: replace archived text UI with server-owned display snapshots.
研究终端迁移工具：只替换已归档的界面区域，保留支付、运行及全部历史备注。
Replaces only the archived UI region; execution, payment and historical notes are retained.
"""
from pathlib import Path
from datetime import datetime

p = Path('src/main/java/com/sirin/hk3gtl/common/machine/research/Hk3ResearchInstituteMachine.java')
s = p.read_text(encoding='utf-8')
stamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
note = '''/**
 * 【变更记录 #6】STAMP（内测5修订51 · 新星工程参考界面重做）
 * 删除：原文本面板式UI从活动代码撤下，原文件完整保存在archive/research-terminal-2026-09-23_02-24-33。
 * 新增：Hk3ResearchTerminalWidget、只读NBT展示快照、整卡状态、材料图标与数量、真实运行状态。
 * 修改：研究所阶级参与锁定显示；费用/操作区固定，搜索和滚动由客户端处理，点击仍在服务端重新授权。
 * 用途：提供HK3GTL科幻研究终端，不改变研究规则、支付、物品注册或存档结构。
 * Remove archived text-only UI; add server snapshots for the sci-fi terminal. Preserve research execution and payment.
 * Client sends only an action or topic ID; prices, lab rank, ownership and evidence remain server-authoritative.
 */
'''.replace('STAMP', stamp)
s = s.replace('public final class Hk3ResearchInstituteMachine', note+'public final class Hk3ResearchInstituteMachine', 1)
start = s.index('    /** 原生GT/LDLib容器绑定当前操作者')
end = s.index('    /** 原生UI唯一付费入口', start)
s = s[:start] + '''    /** 界面仅请求选择或开题；费用快照从服务端生成，不使用客户端计算的资格。
     * Native LDLib transport carries display snapshots and action IDs, never client-supplied prices or permissions.
     */
    @Override public ModularUI createUI(Player player) {
        Session session = new Session(player);
        return new ModularUI(Hk3ResearchTerminalWidget.WIDTH, Hk3ResearchTerminalWidget.HEIGHT, this, player)
                .widget(new Hk3ResearchTerminalWidget(session::snapshot, session::action));
    }

    /** 每位操作者独立选择；展示不修改世界账本。图标按注册ID排序，保证标签代表物稳定。
     * Per-operator selection and read-only presentation; deterministic registry-ID ordering picks tag representatives.
     */
    private final class Session {
        private final Player player;
        private String selected = Hk3ResearchPlans.all().keySet().iterator().next();
        private String feedback = "";
        private Session(Player player) { this.player = player; }

        /** 快照单位：points为整数，eut为EU/t，remaining为基础秒，progress为[0,1]。
         * Server-thread snapshot with integer points, EU/t, remaining base seconds and normalized progress.
         * 缺失授权返回空快照；客户端无权替换其中任何字段。 / Missing authority yields no data; clients cannot replace fields.
         */
        private CompoundTag snapshot() {
            CompoundTag view = new CompoundTag();
            if (!(player instanceof ServerPlayer server) || !authorized(server)) return view;
            var data = Hk3ResearchData.get(server);
            var owner = server.getUUID();
            view.putBoolean("authorized", true);
            view.putBoolean("formed", isFormed());
            view.putBoolean("enabled", getRecipeLogic().isWorkingEnabled());
            view.putInt("lab", lab);
            view.putInt("slots", Hk3ResearchMath.slots(lab));
            view.putInt("active", data.activeResearch(owner, facility()).size());
            view.putString("points", data.points(owner).toString());
            view.putString("selected", selected);
            view.putString("feedback", feedback);
            ListTag topics = new ListTag();
            for (var plan : Hk3ResearchPlans.all().values()) {
                var definition = Hk3ResearchCatalog.bundled().get(plan.id());
                var job = data.researchJob(owner, plan.id());
                boolean done = data.completed(owner, plan.id());
                boolean ready = lab >= definition.lab() && data.hasExperiment(owner, plan.id())
                        && definition.prerequisites().stream().allMatch(id -> data.completed(owner, id));
                CompoundTag row = new CompoundTag();
                row.putString("id", plan.id());
                // 状态0锁定/1满足知识条件/2在研/3完成；成型与供电在独立状态栏呈现。
                // States: 0 locked, 1 knowledge-ready, 2 running, 3 complete. Formation and power are separate.
                row.putInt("state", done ? 3 : job != null ? 2 : ready ? 1 : 0);
                row.putInt("lab", definition.lab());
                row.put("icon", representative(plan.materials().get(0).tag()).save(new CompoundTag()));
                topics.add(row);
            }
            view.put("topics", topics);
            var plan = Hk3ResearchPlans.get(selected);
            var topic = Hk3ResearchCatalog.bundled().get(selected);
            var job = data.researchJob(owner, selected);
            view.putInt("requiredLab", topic.lab());
            view.putInt("tier", topic.tier());
            view.putString("evidence", plan.evidence());
            view.putString("result", plan.result());
            view.putBoolean("experiment", data.hasExperiment(owner, selected));
            view.putLong("cost", plan.points());
            view.putLong("seconds", plan.ticks() / 20);
            view.putLong("eut", job == null ? Hk3Values.VA_LONG[GTValues.MAX + topic.tier()] : job.quote().eut());
            view.putBoolean("running", job != null);
            view.putBoolean("localJob", job != null && facility().equals(job.quote().facility()));
            view.putBoolean("done", data.completed(owner, selected));
            view.putDouble("progress", job == null ? (data.completed(owner, selected) ? 1 : 0)
                    : Math.min(1, Math.max(0, job.progress() / job.quote().ticks())));
            view.putLong("remaining", job == null ? plan.ticks() / 20
                    : (long)Math.ceil(Math.max(0, job.quote().ticks() - job.progress()) / 20.0));
            view.putBoolean("powered", getEnergyContainer().getEnergyStored() >= view.getLong("eut"));
            ListTag prerequisites = new ListTag();
            for (String parent : topic.prerequisites()) {
                CompoundTag prerequisite = new CompoundTag();
                prerequisite.putString("id", parent); prerequisite.putBoolean("done", data.completed(owner, parent));
                prerequisites.add(prerequisite);
            }
            view.put("prerequisites", prerequisites);
            ListTag materials = new ListTag();
            for (var cost : scaled(plan, server)) {
                CompoundTag material = new CompoundTag();
                material.putString("tag", cost.tag()); material.putLong("count", cost.count());
                material.put("item", representative(cost.tag()).save(new CompoundTag()));
                var tag = TagKey.create(Registries.ITEM, new ResourceLocation(cost.tag()));
                long available = 0;
                // 与实际扣费一致，仅主背包36槽；数量是提示，重叠标签仍由原支付分配器复核。
                // Same 36 main slots as payment; counts are advisory, shared-tag allocation is checked at payment time.
                for (int i = 0; i < 36; i++) {
                    ItemStack stack = server.getInventory().getItem(i);
                    if (stack.is(tag)) available += stack.getCount();
                }
                material.putLong("available", available); materials.add(material);
            }
            view.put("materials", materials);
            view.putBoolean("canStart", isFormed() && job == null && !data.completed(owner, selected)
                    && lab >= topic.lab() && data.hasExperiment(owner, selected)
                    && topic.prerequisites().stream().allMatch(id -> data.completed(owner, id))
                    && data.activeResearch(owner, facility()).size() < Hk3ResearchMath.slots(lab));
            return view;
        }

        /** 只取标签中注册ID最小的物品作只读图标；缺失标签显示空图标，不赠送替代品。
         * Deterministic read-only icon; a missing tag remains empty and never creates a substitute reward.
         */
        private ItemStack representative(String id) {
            var tag = TagKey.create(Registries.ITEM, new ResourceLocation(id));
            return BuiltInRegistries.ITEM.getTag(tag).flatMap(set -> set.stream()
                    .map(holder -> holder.value()).min(java.util.Comparator.comparing(item -> BuiltInRegistries.ITEM.getKey(item).toString())))
                    .map(ItemStack::new).orElse(ItemStack.EMPTY);
        }

        /** 网络输入只接受已知动作/真实课题；每次点击先校验所有者、距离、控制器。
         * Accept only known actions/catalog IDs after validating ownership, distance and controller identity.
         */
        private void action(String action) {
            if (!(player instanceof ServerPlayer server) || !authorized(player)) return;
            if ("toggle".equals(action)) { getRecipeLogic().setWorkingEnabled(!getRecipeLogic().isWorkingEnabled()); return; }
            if (action.startsWith("select:")) {
                String id = action.substring(7);
                if (Hk3ResearchPlans.get(id) != null) { selected = id; feedback = ""; }
                return;
            }
            if (!("points".equals(action) || "materials".equals(action))) return;
            var result = requestResearch(server, selected, "points".equals(action));
            feedback = "hk3gtl.research.start." + result.name().toLowerCase(java.util.Locale.ROOT);
        }
    }

''' + s[end:]
p.write_text(s, encoding='utf-8')
print('Machine UI replaced; execution and payment retained:', stamp)

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
