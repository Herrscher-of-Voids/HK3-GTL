package com.sirin.hk3gtl.common.research;



import java.util.List;
import java.util.concurrent.ThreadLocalRandom;

/**
 * 崩坏能研究院的聊天"文戏"配音池。
 *
 * <h3>职责</h3>
 * 研究完成时，{@link Hk3ResearchManager#completeResearch} 用它产生三行剧情化消息：
 * <ol>
 *   <li>研究员姓名（头衔 + 名字）— 从 {@link #RESEARCHERS} 随机</li>
 *   <li>进展台词 — 从 {@link #PROGRESS_LINES} 随机（句子里 {@code %s} 会被研究名替换）</li>
 *   <li>彩蛋/花絮台词 — 从 {@link #FLAVOR_LINES} 随机</li>
 * </ol>
 *
 * <h3>为什么独立成类</h3>
 * SRP：{@link Hk3ResearchManager} 只管研究状态机，"文戏"属于叙事层，拆开方便
 * 后期和世界文本叙事系统（需求 1）对接，也方便做本地化 / 不同阵营的配音分化。
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>加新研究员：往 {@link #RESEARCHERS} 追加（名字要符合崩坏三世界观，避免与官方角色硬撞）</li>
 *   <li>加新台词：往 {@link #PROGRESS_LINES} 追加；句子里必须有一处 {@code %s}</li>
 *   <li>彩蛋：纯装饰，不需要 {@code %s}</li>
 *   <li>线程安全：使用 {@link ThreadLocalRandom}，可在多线程下调用（虽然现在只在服务端主线程用）</li>
 * </ul>
 */
public final class ResearchAcademyChatter {

    private ResearchAcademyChatter() {}

    /**
     * 研究员人物池。每个条目形如 "首席研究员·薇塔"，通过 § 颜色码可各自带色。
     * 角色均为本模组虚构，不与官方崩坏三/星铁角色重名。
     */
    private static final List<String> RESEARCHERS = List.of(
            "§e首席研究员·薇兰德§r",
            "§e副院长·林渊§r",
            "§e材料组组长·卡莱§r",
            "§e电路组组长·安诺§r",
            "§e事件监察员·柯尔§r",
            "§e结构工程师·普瑞莎§r",
            "§e数据分析员·织歌§r",
            "§e虚数组主管·沉砚§r",
            "§e量子组主管·苏彻§r",
            "§e终焉观察员·晨钥§r",
            "§e理论物理学家·墨梧§r",
            "§e应用工程师·霜兰§r"
    );

    /** 头行话术 —— 研究员宣告成果进展（句子中 {@code %s} 必须存在，用于插研究名称）。 */
    private static final List<String> PROGRESS_LINES = List.of(
            "§f大人，不负所托 —— §e%s§f 项目已全面完成。",
            "§f报告大人，§e%s§f 的关键环节终于被我们打通了。",
            "§f我们连夜分析了整整 47 遍模型，§e%s§f 终于稳了。",
            "§f大人，§e%s§f 的核心公式刚刚在 0.3 秒前收敛。",
            "§f您一直期待的 §e%s§f，样本已经成形。",
            "§f经过全员三班倒，§e%s§f 的可行性已被验证。",
            "§f从崩坏能波纹里分离出的关键数据，§e%s§f 成了。",
            "§f我们把 §e%s§f 喂给了量子纠缠计算机，它吐出了可用结果。"
    );

    /** 尾行彩蛋 —— 纯装饰，不含参数替换，营造『研究院内部日常』的氛围。 */
    private static final List<String> FLAVOR_LINES = List.of(
            "§8[内部] §7薇兰德：我知道你们又熬夜了，别装。",
            "§8[内部] §7卡莱：材料仓又被你们薅空了！",
            "§8[内部] §7林渊：明天例会再提一次经费问题。",
            "§8[内部] §7安诺：这焊点……谁干的？是不是又是那台老焊枪？",
            "§8[内部] §7柯尔：事件监察系统又把这当成异常了，稍后我修一下。",
            "§8[内部] §7织歌：成功了！所以今天能吃顿好的了吗？",
            "§8[内部] §7普瑞莎：结构图纸请更新到最新版，别再用一周前的了。",
            "§8[内部] §7沉砚：虚数维度那边似乎有波动，不过没关系。",
            "§8[内部] §7苏彻：理论上，我们下一步就能摸到那个『更远』的东西了。",
            "§8[内部] §7晨钥：……大人一定在看着我们。",
            "§8[内部] §7墨梧：别问为什么能跑，问就是『它就这么 work 了』。",
            "§8[内部] §7霜兰：恭喜大人，下一步继续吧。"
    );

    /** 随机选一个研究员名牌。 */
    public static String randomResearcher() {
        return pick(RESEARCHERS);
    }

    /**
     * 随机选一句进展台词，把研究名替入 {@code %s}。
     * 若台词意外缺 {@code %s}，直接在末尾附加 "研究名" 作为容错。
     */
    public static String randomProgressLine(String researchDisplay) {
        String tmpl = pick(PROGRESS_LINES);
        if (tmpl.contains("%s")) {
            return String.format(tmpl, researchDisplay);
        }
        return tmpl + " " + researchDisplay;
    }

    /** 随机选一句彩蛋台词。 */
    public static String randomFlavorLine() {
        return pick(FLAVOR_LINES);
    }

    private static <T> T pick(List<T> list) {
        return list.get(ThreadLocalRandom.current().nextInt(list.size()));
    }
}
