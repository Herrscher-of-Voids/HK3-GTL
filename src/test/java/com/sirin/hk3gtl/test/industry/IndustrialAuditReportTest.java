package com.sirin.hk3gtl.test.industry;

import com.sirin.hk3gtl.common.recipe.audit.RecipeReachability;
import com.sirin.hk3gtl.common.registration.Hk3IndustrialAuditReport;
import com.sirin.hk3gtl.common.registration.Hk3IndustrialDependencyAudit;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.DirectoryNotEmptyException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.regex.Pattern;

/**
 * 【变更记录 #1】2026-10-17 13:59:04（内测5修订160）
 * 新增：真实快照接口的HTML导出回归，覆盖计数隔离、辅助规则、凭据边界、转义和重复替换。
 * 用途：验证审计交付不会隐去阻断或冒充生存通过；临时目录只清理本测试生成的固定报告。
 * 【变更记录 #2】2026-10-17 14:09:58（内测5修订160）
 * 修改：Windows目录延迟删除仅对目录非空错误作最多10次、25毫秒间隔重试；真残留仍失败。
 * 用途：清理失败以附加异常保留原始断言，不扩大删除范围、不吞掉其他文件系统错误。
 */
public final class IndustrialAuditReportTest {
    private static final String FILE_NAME = "工业依赖核验_最新.html";
    private static final String UNSAFE_ID = "hk3gtl:assembler/<recipe&\"'>";
    private static int checks;
    private IndustrialAuditReportTest() {}

    public static void main(String[] args) throws Exception {
        Path folder = Files.createTempDirectory("hk3gtl-industrial-report-test-");
        Path ownedReport = folder.resolve(FILE_NAME);
        Throwable failure = null;
        try {
            var first = snapshot("FIRST-UNKNOWN <script>alert('x')</script>");
            Path returned = Hk3IndustrialAuditReport.write(first, folder);
            String html = Files.readString(ownedReport, StandardCharsets.UTF_8);
            check(returned.equals(ownedReport.toAbsolutePath().normalize()), "返回固定绝对报告路径");
            check(html.contains("<html lang=\"zh-CN\">") && html.contains("工业依赖核验"), "中文HTML与UTF8正文可读取");
            check(html.contains("hk3gtl:assembler/&lt;recipe&amp;&quot;&#39;&gt;") && !html.contains(UNSAFE_ID), "配方ID的特殊字符完整转义");
            check(html.contains("&lt;script&gt;alert(&#39;x&#39;)&lt;/script&gt;")
                    && !html.contains("<script>alert('x')</script>"), "未知视图不能注入可执行HTML");
            check(stat(html, "纳入生产配方", 2) && stat(html, "生产拓扑可达", 1)
                    && stat(html, "生产仍有阻断", 1), "生产配方数独立计算");
            check(stat(html, "设备桥接规则", 2) && stat(html, "桥接涉及设备定义", 1), "一台设备的多个能力不冒充多台机器");
            check(stat(html, "研究所/许可等辅助规则", 3), "辅助实验和许可不计为生产配方或设备桥接");
            check(html.contains("laboratory:LAB-OPR") && html.contains("facility:S01") && html.contains("facility:S02"), "已达与未达的LAB和设施规则均保留");
            check(html.contains("external_ledger:three_recovery_proofs") && html.contains("formal_communication")
                    && html.contains("未获/未适配") && html.contains("不会自行授予"), "外部游戏行为凭据不被自动补齐");
            check(html.contains("在现有建模条件下不可达") && html.contains("不等于全局死锁"), "局部建模阻断不冒充全局死锁");
            check(html.contains("材料支付路径") && html.contains("研究点替代支付")
                    && html.contains("材料路径阻断不等于点支付也失败"), "材料支付与研究点替代路径明确区分");
            check(html.contains("外部非HK3资源全部视为可用") && html.contains("未严格逐项核定"), "外部资源乐观假设公开");
            check(html.contains("概率产物") && html.contains("团队归属") && html.contains("固定工艺职责")
                    && html.contains("不代表运行通过"), "概率可达和现场运行边界公开");
            check(html.contains("空标签/空候选：无法满足") && html.contains("无已注册设备桥接规则"), "空标签和缺执行器不隐藏");
            check(stat(html, "研究仍有阻断", 1) && stat(html, "未知配方视图", 1), "研究与未知视图另计");
            check(count(html, "<table>") == 5 && count(html, "<tr class=filter-row") == 8, "五类表格包含全部八行夹具");
            check(html.contains("addEventListener('input'") && html.contains("id=status")
                    && !Pattern.compile("<script\\s+[^>]*src\\s*=", Pattern.CASE_INSENSITIVE).matcher(html).find(), "筛选本地可用且无外链脚本");
            check(first.result().blockedRecipes().size() == 4 && first.productionRecipes().size() == 2, "导出不修改输入快照");
            Path second = Hk3IndustrialAuditReport.write(snapshot("SECOND-UNKNOWN"), folder);
            String replaced = Files.readString(second, StandardCharsets.UTF_8);
            check(second.equals(returned) && replaced.contains("SECOND-UNKNOWN") && !replaced.contains("FIRST-UNKNOWN"), "重复导出替换同一路径且不残留旧内容");
            try (var entries = Files.list(folder)) {
                check(entries.toList().equals(List.of(ownedReport)), "替换后只有报告，没有泄漏临时文件");
            }
        } catch (Exception | Error problem) {
            failure = problem;
            throw problem;
        } finally {
            try {
                Files.deleteIfExists(ownedReport);
                deleteOwnDirectory(folder);
            } catch (IOException | InterruptedException cleanup) {
                if (cleanup instanceof InterruptedException) Thread.currentThread().interrupt();
                if (failure != null) failure.addSuppressed(cleanup);
                else throw cleanup;
            }
        }
        check(!Files.exists(folder), "只删除本测试创建的报告与专用临时目录");
        System.out.println("IndustrialAuditReportTest: " + checks + " checks passed; report export only, no gameplay verification");
    }

    private static Hk3IndustrialDependencyAudit.Snapshot snapshot(String unknown) {
        var blocked = new RecipeReachability.Blockers(Set.of("RN-A"), Set.of("executor:gtceu:unregistered"),
                List.of(Set.of()), List.of(Set.of("hk3gtl:water")),
                Set.of("external_ledger:three_recovery_proofs", "formal_communication"), Set.of("RN-B"));
        var rows = new LinkedHashMap<String, RecipeReachability.Blockers>();
        rows.put(UNSAFE_ID, blocked);
        rows.put("device:fixture:machine/gtceu:missing", blocked);
        rows.put("laboratory:LAB-OPR", blocked);
        rows.put("facility:S02", blocked);
        var state = new RecipeReachability.State(Set.of(), Set.of(), Set.of(), Set.of(), Set.of());
        var result = new RecipeReachability.Result(state,
                Set.of("hk3gtl:assembler/reachable", "device:fixture:machine/gtceu:assembler", "facility:S01"),
                rows, Map.of("RN-A", blocked));
        return new Hk3IndustrialDependencyAudit.Snapshot(500,
                Set.of(UNSAFE_ID, "hk3gtl:assembler/reachable"), result, List.of(unknown));
    }

    private static boolean stat(String html, String title, int expected) {
        return html.contains("<span>" + title + "</span><strong>" + expected + "</strong>");
    }

    private static void deleteOwnDirectory(Path folder) throws IOException, InterruptedException {
        for (int attempt = 0; ; attempt++) {
            try {
                Files.deleteIfExists(folder);
                return;
            } catch (DirectoryNotEmptyException delayed) {
                if (attempt >= 9) throw delayed;
                Thread.sleep(25);
            }
        }
    }

    private static int count(String text, String fragment) {
        int count = 0;
        for (int index = text.indexOf(fragment); index >= 0; index = text.indexOf(fragment, index + fragment.length())) count++;
        return count;
    }

    private static void check(boolean valid, String message) {
        checks++; if (!valid) throw new AssertionError(message);
    }
}
