package com.sirin.hk3gtl.common.registration;

import com.sirin.hk3gtl.common.recipe.audit.RecipeReachability;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.AtomicMoveNotSupportedException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import java.util.TreeSet;

/**
 * 【变更记录 #1】2026-10-17 13:55:26（内测5修订160）
 * 删除：无。新增：工业依赖快照的中文HTML只读导出，生产配方、设备桥接和未知视图分别计数。
 * 修改：统一五类表格与原子覆盖；用途：展示逐项阻断，不授予物品、研究或事实，不冒充游戏现场验收。
 * 【变更记录 #2】2026-10-17 14:15:38（第2次备注 · 修订161）
 * 删除：过期160展示号。新增：当前构建追溯号；修改：报告头同步161；用途：避免命名迁移后沿用旧报告身份。
 */
public final class Hk3IndustrialAuditReport {
    private static final String FILE_NAME = "工业依赖核验_最新.html";
    private Hk3IndustrialAuditReport() {}

    public static Path write(Hk3IndustrialDependencyAudit.Snapshot snapshot, Path directory) throws IOException {
        Path folder = directory.toAbsolutePath().normalize();
        Files.createDirectories(folder);
        Path target = folder.resolve(FILE_NAME);
        Path temporary = Files.createTempFile(folder, "hk3gtl-industrial-audit-", ".tmp");
        try {
            Files.writeString(temporary, render(snapshot), StandardCharsets.UTF_8);
            try {
                Files.move(temporary, target, StandardCopyOption.REPLACE_EXISTING, StandardCopyOption.ATOMIC_MOVE);
            } catch (AtomicMoveNotSupportedException unsupported) {
                Files.move(temporary, target, StandardCopyOption.REPLACE_EXISTING);
            }
        } finally {
            Files.deleteIfExists(temporary);
        }
        return target;
    }

    private static String render(Hk3IndustrialDependencyAudit.Snapshot snapshot) {
        var result = snapshot.result();
        var production = new TreeSet<>(snapshot.productionRecipes());
        var allRules = new TreeSet<>(result.finishedRecipes());
        allRules.addAll(result.blockedRecipes().keySet());
        var bridges = allRules.stream().filter(id -> id.startsWith("device:")).toList();
        var auxiliary = allRules.stream().filter(id -> !id.startsWith("device:") && !production.contains(id)).toList();
        var bridgeTypes = new TreeSet<String>();
        var machines = new TreeMap<String, List<String>>();
        for (String bridge : bridges) {
            bridgeTypes.add(bridgeType(bridge));
            machines.computeIfAbsent(bridgeMachine(bridge), ignored -> new ArrayList<>()).add(bridge);
        }
        long reached = production.stream().filter(result.finishedRecipes()::contains).count();
        var html = new StringBuilder(65536);
        html.append(HEAD).append("<h1>工业依赖核验</h1><p class=muted>生成时间：")
                .append(escape(ZonedDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss XXX"))))
                .append(" · 修订163 · 只读拓扑快照</p>")
                .append("<div class=notice><strong>本报告不是生存验收通过证明。</strong>外部非HK3资源全部视为可用，这是乐观假设；")
                .append("未严格逐项核定它们是否属于MAX档或MAX阶段是否真的可得。魂钢等已被适配器识别为内部资源的对象仍按内部依赖计算。")
                .append("物品/流体的存在性、概率产物的拓扑可达，不等于数量够用、库存可扣、电压/供电满足、物理结构成型、")
                .append("实际配方执行、输出结算或单人/多人实测通过。本页不执行上述现场测试，也不授予任何研究、事实或物品。")
                .append("“阻断”仅表示在现有建模条件下不可达，不等于全局死锁；游戏行为凭据未获或尚未适配，须按来源另行核验。</div>")
                .append("<p>液态产线真实运行还要求玩家已有观测数据与团队归属。本图没有验证实际机器类的固定工艺职责、")
                .append("物理成型、能耗或上述玩家状态；控制器与配方类型同时可达也不代表运行通过。</p>");
        html.append("<div class=stats>");
        stat(html, "整包注册配方", snapshot.registeredRecipes());
        stat(html, "纳入生产配方", production.size());
        stat(html, "生产拓扑可达", reached);
        stat(html, "生产仍有阻断", production.size() - reached);
        stat(html, "设备桥接规则", bridges.size());
        stat(html, "桥接涉及设备定义", machines.size());
        stat(html, "研究所/许可等辅助规则", auxiliary.size());
        stat(html, "研究拓扑可达", result.state().research().size());
        stat(html, "研究仍有阻断", result.blockedResearch().size());
        stat(html, "未知配方视图", snapshot.unresolvedViews().size());
        html.append("</div><p>生产配方只统计<code>productionRecipes</code>；<code>device:</code>规则仅把可达控制器映射为配方类型的执行能力，")
                .append("不算新增制造配方，不计入每台至少15个可执行配方的验收。设备定义数量也不等于已批准的多方块结构台数。")
                .append("<code>laboratory:</code>实验和<code>facility:</code>许可就绪规则同样独立列示，不计为生产配方；")
                .append("外部账本凭据未作为种子授予。</p>");
        appendBlockerSummary(html, production, result, bridgeTypes);
        html.append("<div class=filters><label>搜索全部表格 <input id=search type=search placeholder=\"配方、设备、研究或物料ID\"></label>")
                .append("<label>状态 <select id=status><option value=all>全部</option><option value=blocked>仅阻断/未知</option>")
                .append("<option value=reachable>仅拓扑可达</option></select></label><span id=visible class=muted></span></div>");
        appendMachines(html, machines, result);
        appendProduction(html, production, result, bridgeTypes);
        appendAuxiliary(html, auxiliary, result);
        appendResearch(html, result);
        appendUnknown(html, snapshot.unresolvedViews());
        html.append("<h2>解释边界</h2><ul><li>每个物品/流体替代组任选一个，各组同时满足；非消耗催化剂仍须有起步种子。")
                .append("空组显示为“空标签/空候选”，不会当作免费输入。</li><li>研究需要全部前置、实验/证据、事实和可制备费用；")
                .append("按材料支付路径建图，只检查存在性，不模拟数量扣费、研究点替代支付、时间或研究所真实通电。")
                .append("材料路径阻断不等于研究点支付路径也失败。</li>")
                .append("<li>“缺执行器”可能是没有任何注册设备桥接规则，也可能是设备已注册但其控制器不可达；两者分别标注。")
                .append("桥接本身不检查结构成型、固定工艺身份或真实可运行状态。</li>")
                .append("<li>未知视图未被自动判为可达。空标签、未接执行器、实验来源、事实来源和材料来源仍需逐项修复或实测。</li></ul>")
                .append(SCRIPT).append("</main></body></html>");
        return html.toString();
    }

    private static void appendBlockerSummary(StringBuilder html, Set<String> production,
            RecipeReachability.Result result, Set<String> bridgeTypes) {
        long research = 0, device = 0, item = 0, fluid = 0, fact = 0, evidence = 0, empty = 0, absent = 0;
        var missingTypes = new TreeSet<String>();
        for (String id : production) {
            var b = result.blockedRecipes().get(id); if (b == null) continue;
            if (!b.research().isEmpty()) research++;
            if (!b.controllers().isEmpty()) device++;
            if (!b.itemAlternatives().isEmpty()) item++;
            if (!b.fluidAlternatives().isEmpty()) fluid++;
            if (!b.facts().isEmpty()) fact++;
            if (!b.evidence().isEmpty()) evidence++;
            if (hasEmpty(b)) empty++;
            if (b.controllers().stream().anyMatch(c -> !bridgeTypes.contains(executorType(c)))) {
                absent++;
                b.controllers().stream().map(Hk3IndustrialAuditReport::executorType)
                        .filter(t -> !bridgeTypes.contains(t)).forEach(missingTypes::add);
            }
        }
        html.append("<h2>生产配方阻断分类</h2><p>按受影响的生产配方行数统计；同一行可能同时属于多类，不能相加当作总配方数。</p><div class=stats>");
        stat(html, "缺全部研究条件中的至少一项", research);
        stat(html, "缺可达执行能力", device);
        stat(html, "其中无注册桥接规则", absent);
        stat(html, "缺物品替代组", item);
        stat(html, "缺流体替代组", fluid);
        stat(html, "缺运行事实", fact);
        stat(html, "缺实验/证据", evidence);
        stat(html, "含空标签/空候选", empty);
        html.append("</div><p>无已注册桥接规则的执行类型：</p><div class=ids>");
        names(html, missingTypes); html.append("</div>");
    }

    private static void appendMachines(StringBuilder html, Map<String, List<String>> machines,
            RecipeReachability.Result result) {
        html.append("<h2>逐台设备定义与桥接阻断</h2><p>包含整包注册设备定义；每台可提供多个配方类型。这里统计桥接能力，不能作为生产配方数。</p>")
                .append("<div class=scroll><table><thead><tr><th>设备定义</th><th>桥接规则数</th><th>拓扑可达</th><th>仍阻断</th><th>逐规则状态/原因</th></tr></thead><tbody>");
        for (var entry : machines.entrySet()) {
            long done = entry.getValue().stream().filter(result.finishedRecipes()::contains).count();
            html.append("<tr class=filter-row data-status=").append(done == entry.getValue().size() ? "reachable" : "blocked").append("><td><code>")
                    .append(escape(entry.getKey())).append("</code></td><td>").append(entry.getValue().size())
                    .append("</td><td>").append(done).append("</td><td>").append(entry.getValue().size() - done).append("</td><td>");
            for (String rule : entry.getValue()) {
                var blocker = result.blockedRecipes().get(rule);
                html.append("<div class=rule><code>").append(escape(bridgeType(rule))).append("</code> · ");
                if (blocker == null) html.append("拓扑可达");
                else { html.append("阻断："); compactBlockers(html, blocker); }
                html.append("</div>");
            }
            html.append("</td></tr>");
        }
        html.append("</tbody></table></div>");
    }

    private static void appendProduction(StringBuilder html, Set<String> production,
            RecipeReachability.Result result, Set<String> bridgeTypes) {
        html.append("<h2>逐生产配方依赖与阻断</h2><div class=scroll><table><thead><tr><th>生产配方ID</th><th>拓扑状态</th>")
                .append("<th>缺研究</th><th>缺执行器/能力</th><th>缺物品组</th><th>缺流体组</th><th>缺事实</th><th>缺实验/证据</th></tr></thead><tbody>");
        for (String id : production) {
            var b = result.blockedRecipes().get(id);
            boolean reached = result.finishedRecipes().contains(id);
            html.append("<tr class=filter-row data-status=").append(reached ? "reachable" : "blocked").append("><td><code>")
                    .append(escape(id)).append("</code></td><td>").append(reached ? "拓扑可达" : b == null ? "未纳入闭包，需核验" : "仍有阻断").append("</td>");
            if (b == null) html.append("<td colspan=6>—</td>");
            else {
                cell(html, b.research());
                html.append("<td>");
                if (b.controllers().isEmpty()) html.append("—");
                for (String controller : b.controllers()) {
                    html.append("<div><code>").append(escape(controller)).append("</code><br><span class=muted>")
                            .append(bridgeTypes.contains(executorType(controller)) ? "设备已注册；控制器/能力尚不可达" : "无已注册设备桥接规则")
                            .append("</span></div>");
                }
                html.append("</td><td>"); groups(html, b.itemAlternatives()); html.append("</td><td>");
                groups(html, b.fluidAlternatives()); html.append("</td>"); factCell(html, b.facts()); cell(html, b.evidence());
            }
            html.append("</tr>");
        }
        html.append("</tbody></table></div>");
    }

    private static void appendResearch(StringBuilder html, RecipeReachability.Result result) {
        html.append("<h2>逐研究阻断</h2><p><strong>本表按材料支付路径建图，不模拟研究点替代支付；材料路径阻断不等于点支付也失败。</strong></p>")
                .append("<p>拓扑可达研究："); names(html, result.state().research());
        html.append("</p><div class=scroll><table><thead><tr><th>研究ID</th><th>缺全部前置中的项目</th><th>缺实验/证据</th>")
                .append("<th>缺运行事实</th><th>缺费用/研究所物品组</th><th>缺流体费用组</th></tr></thead><tbody>");
        for (var entry : new TreeMap<>(result.blockedResearch()).entrySet()) {
            var b = entry.getValue();
            html.append("<tr class=filter-row data-status=blocked><td><code>").append(escape(entry.getKey())).append("</code></td>");
            cell(html, b.research()); cell(html, b.evidence()); factCell(html, b.facts());
            html.append("<td>"); groups(html, b.itemAlternatives()); html.append("</td><td>"); groups(html, b.fluidAlternatives());
            html.append("</td></tr>");
        }
        html.append("</tbody></table></div>");
    }

    private static void appendAuxiliary(StringBuilder html, List<String> auxiliary, RecipeReachability.Result result) {
        html.append("<h2>研究所实验、设施许可与其他辅助规则</h2><p>本表不计为生产配方。")
                .append("例如三类回收凭据、奇观二审许可等外部账本条件不会自动授予；按原始ID显示实际阻断。</p>")
                .append("<div class=scroll><table><thead><tr><th>辅助规则ID</th><th>拓扑状态</th><th>缺研究</th><th>缺执行器/能力</th>")
                .append("<th>缺物品/设施就绪组</th><th>缺流体组</th><th>缺账本/运行事实</th><th>缺实验/证据</th></tr></thead><tbody>");
        for (String id : auxiliary) {
            var b = result.blockedRecipes().get(id);
            html.append("<tr class=filter-row data-status=").append(b == null ? "reachable" : "blocked").append("><td><code>")
                    .append(escape(id)).append("</code></td><td>").append(b == null ? "拓扑可达" : "仍有阻断").append("</td>");
            if (b == null) html.append("<td colspan=6>—</td>");
            else {
                cell(html, b.research()); cell(html, b.controllers());
                html.append("<td>"); groups(html, b.itemAlternatives()); html.append("</td><td>");
                groups(html, b.fluidAlternatives()); html.append("</td>"); factCell(html, b.facts()); cell(html, b.evidence());
            }
            html.append("</tr>");
        }
        html.append("</tbody></table></div>");
    }

    private static void appendUnknown(StringBuilder html, List<String> unresolved) {
        html.append("<h2>未知/未完整解析视图</h2><p>以下内容单独列出，不计作已可达的生产配方，不自动推断其输入约束或生存可执行性。</p>")
                .append("<div class=scroll><table><thead><tr><th>配方或视图说明</th><th>核验状态</th></tr></thead><tbody>");
        for (String view : unresolved) html.append("<tr class=filter-row data-status=blocked><td><code>")
                .append(escape(view)).append("</code></td><td>未知，需专项核验</td></tr>");
        html.append("</tbody></table></div>");
    }

    private static void compactBlockers(StringBuilder html, RecipeReachability.Blockers b) {
        if (!b.research().isEmpty()) { html.append("研究 "); names(html, b.research()); html.append("；"); }
        if (!b.controllers().isEmpty()) { html.append("执行器 "); names(html, b.controllers()); html.append("；"); }
        if (!b.itemAlternatives().isEmpty()) { html.append("物品 "); groups(html, b.itemAlternatives()); }
        if (!b.fluidAlternatives().isEmpty()) { html.append("流体 "); groups(html, b.fluidAlternatives()); }
        if (!b.facts().isEmpty()) { html.append("事实/凭据 "); facts(html, b.facts()); html.append("；"); }
        if (!b.evidence().isEmpty()) { html.append("证据 "); names(html, b.evidence()); }
    }

    private static void groups(StringBuilder html, List<Set<String>> groups) {
        if (groups.isEmpty()) { html.append("—"); return; }
        for (Set<String> group : groups) {
            html.append("<div class=group>");
            if (group.isEmpty()) html.append("<strong class=bad>空标签/空候选：无法满足</strong>");
            else { html.append("任一："); names(html, group); }
            html.append("</div>");
        }
    }

    private static void names(StringBuilder html, Collection<String> values) {
        if (values.isEmpty()) { html.append("—"); return; }
        boolean first = true;
        for (String value : new TreeSet<>(values)) {
            if (!first) html.append("、");
            html.append("<code>").append(escape(value)).append("</code>"); first = false;
        }
    }

    private static void cell(StringBuilder html, Collection<String> values) { html.append("<td>"); names(html, values); html.append("</td>"); }
    private static void factCell(StringBuilder html, Set<String> values) { html.append("<td>"); facts(html, values); html.append("</td>"); }
    private static void facts(StringBuilder html, Set<String> values) {
        names(html, values);
        if (values.stream().anyMatch(Hk3IndustrialAuditReport::externalFact))
            html.append("<div class=muted>含未获/未适配的游戏行为或外部账本凭据；本图不会自行授予。</div>");
    }
    private static boolean externalFact(String fact) {
        return fact.startsWith("external_ledger:") || fact.startsWith("simulation_")
                || fact.equals("formal_communication") || fact.equals("cocoon_authorization");
    }
    private static boolean hasEmpty(RecipeReachability.Blockers b) {
        return b.itemAlternatives().stream().anyMatch(Set::isEmpty) || b.fluidAlternatives().stream().anyMatch(Set::isEmpty);
    }
    private static String bridgeMachine(String id) { return id.substring("device:".length(), id.lastIndexOf('/')); }
    private static String bridgeType(String id) { return id.substring(id.lastIndexOf('/') + 1); }
    private static String executorType(String id) { return id.startsWith("executor:") ? id.substring("executor:".length()) : id; }
    private static void stat(StringBuilder html, String title, long value) {
        html.append("<div><span>").append(escape(title)).append("</span><strong>").append(value).append("</strong></div>");
    }
    private static String escape(String value) {
        return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                .replace("\"", "&quot;").replace("'", "&#39;");
    }

    private static final String HEAD = """
            <!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
            <title>工业依赖核验 · 内测5</title><style>
            :root{color-scheme:dark;font-family:system-ui,"Microsoft YaHei",sans-serif;background:#10151e;color:#e3eaf5}
            body{margin:0}main{max-width:1700px;margin:auto;padding:30px 24px 70px}h1{font-size:32px;margin-bottom:8px}h2{margin-top:36px}
            p,li{line-height:1.75}.muted{color:#a9b7cb}.notice{padding:20px;border:1px solid #92784e;border-radius:12px;background:#2b251c;line-height:1.8}
            .notice strong{color:#ffcc83}.stats{display:flex;flex-wrap:wrap;gap:12px;margin:20px 0}.stats>div{background:#1a2433;border:1px solid #34475f;padding:14px 18px;border-radius:10px;min-width:150px}
            .stats span{display:block;font-size:13px;color:#b5c5dd}.stats strong{display:block;font-size:27px;color:#92c9ff;margin-top:7px}
            .filters{position:sticky;top:0;z-index:2;display:flex;flex-wrap:wrap;gap:18px;align-items:center;padding:16px;background:#142033f5;border:1px solid #3c5270;border-radius:10px}
            input,select{font:inherit;color:inherit;background:#0d1624;border:1px solid #58718e;border-radius:6px;padding:8px;margin-left:8px}input{width:min(450px,65vw)}
            .scroll{overflow:auto;border:1px solid #34475f;border-radius:8px}table{border-collapse:collapse;width:100%;font-size:13px}th,td{text-align:left;vertical-align:top;padding:11px;border-bottom:1px solid #304157;min-width:90px}
            th{background:#20324a;color:#cce1ff;white-space:nowrap}tbody tr:nth-child(even){background:#172230}code{font-family:ui-monospace,Consolas,monospace;overflow-wrap:anywhere;color:#bcdcff}
            .rule+.rule,.group+.group{border-top:1px dotted #3b4f68;margin-top:8px;padding-top:8px}.bad{color:#ffad9d}.ids{padding:12px;background:#192331;border-radius:8px;line-height:1.8}[hidden]{display:none!important}
            </style></head><body><main>
            """;
    private static final String SCRIPT = """
            <script>
            (()=>{const input=document.getElementById('search'),status=document.getElementById('status'),counter=document.getElementById('visible');
            const rows=[...document.querySelectorAll('.filter-row')].map(row=>({row,text:row.textContent.toLocaleLowerCase()}));let timer;
            function filter(){const query=input.value.trim().toLocaleLowerCase(),state=status.value;let visible=0;for(const entry of rows){
            const show=entry.text.includes(query)&&(state==='all'||entry.row.dataset.status===state);entry.row.hidden=!show;if(show)visible++;}
            counter.textContent='显示 '+visible+' / '+rows.length+' 行；上方统计保持完整快照口径';}
            input.addEventListener('input',()=>{clearTimeout(timer);timer=setTimeout(filter,100)});status.addEventListener('change',filter);filter();})();
            </script>
            """;
}

// 【变更记录 · 修订162】2026-10-17 14:43:20：报告标识更新至旧配方清理版本；统计仍来自最终运行时快照，历史报告不回写。
// 【变更记录 · 修订163】2026-10-17 15:10:00：报告标识同步研究权限接线；统计规则不变，以实际最终门槛重新建图。
