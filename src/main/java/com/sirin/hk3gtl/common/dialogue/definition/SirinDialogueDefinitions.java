package com.sirin.hk3gtl.common.dialogue.definition;


/**
 * 【文件职责】
 * - 维护 SirinDialogueDefinitions 的核心功能实现。
 * - 关键调用链：由上层系统入口调用 -> 本文件核心方法 -> 下游模块。
 *
 * 【变更记录 #1】2026-05-19（内测二首轮）
 *
 * 【变更记录 #2】2026-05-19 05:10:00（第 2 次备注 · 内测二第 5 次更新）
 * - 修改：
 *   1) 内测二 intro 首选键改为 {@code hk3gtl.dialogue.sirin.d01}～d24}，版本键 v0_2_0 作回退。
 *   2) 修改前后：仅改 d01～d52 或仅改 v0_2_0 时界面不更新 → 改 zh_cn 中 d01～d24 即生效。
 * - 用途：
 *   1) 与译者习惯的语言文件路径对齐。
 *
 * 【变更记录 #3】2026-05-31 22:30:00（第 3 次备注 · 内测三第 1 次更新）
 * - 删除：
 *   1) buildIfSegment 中对旧 {@code if.<i>.main}/非版本化 {@code if.<i>.<nn>} 的回退引用。
 *   2) 原因：内测三 IF 线为全新主题（不同模组包/模组类别），若回退到内测二文本会出现版本串台。
 *   3) 影响：运行版本(0.3.0)下仅读取版本化 IF 键；内测一/二 IF 文本保留在 lang 作历史，不再被读取（模组未发布，无版本兼容包袱）。
 * - 新增：
 *   1) IF 分支键改为版本化 {@code hk3gtl.dialogue.sirin.<ver>.if.<i>.<nn>}（ver 由模组版本推导，如 v0_3_0），回退置 null。
 *   2) intro 选项标签改为版本化 {@code hk3gtl.dialogue.sirin.<ver>.choice.<i>}，使每个内测版本拥有独立 5 条 IF 入口。
 *   3) 客户端过滤规则：无翻译的行(主键缺失且回退为 null)自动隐藏；故每分支可只填实际行数(其余 02~20 留空即可)。
 * - 修改：
 *   1) buildIfSegment / buildIntroSegment 均改用 SirinDialogueVersion.introKeySuffix() 推导版本段。
 * - 用途：
 *   1) 业务目标：让 5 条 IF 线随版本切换内容，内测三对应“不同 MC 模组包 / 不同模组类别”的隐喻叙事。
 *   2) 系统位置：终局对话 sirin_finale 的 intro 选项 + if_0~if_4 分支 segment。
 *   3) 风险点：选项标签不参与翻译过滤(缺键会显示原始键)，故 5 个版本化 choice 键必须在 lang 中齐全。
 *
 * 【变更记录 #4】2026-05-31 22:45:00（第 4 次备注 · 内测三第 2 次更新，订正 #3）
 * - 删除：
 *   1) 撤销 #3 的版本化方案：buildIfSegment/choice 不再使用 {@code <ver>.} 前缀。
 *   2) 原因：需求实为“在原 5 条基础上再加 5 条，共 10 条 IF 线”，而非替换；版本化反而隐藏了内测二原 5 条。
 * - 新增：
 *   1) 新增常量 IF_BRANCH_COUNT=10；register/intro 选项/段构建均按 10 条展开（if_0~if_9）。
 *   2) 0~4 沿用内测二主题(核电/内斗/女王/崩坏/魔法)，5~9 为内测三新增(模组包/模组类别隐喻 IF-06~IF-10)。
 * - 修改：
 *   1) buildIfSegment 恢复非版本化键 {@code if.<i>.<nn>}，首行回退 {@code if.<i>.main}（与内测二一致）。
 *   2) intro 选项恢复 {@code hk3gtl.dialogue.sirin.choice.<i>}，循环 5→10。
 *   3) 配套掩码扩展见 SirinIfProgressStore.ALL_MASK / DialogueSessionManager / Hk3DialogueScreen（5 位→10 位）。
 * - 用途：
 *   1) 业务目标：终局对话提供 10 条 IF 线，前 5 条文明走向 + 后 5 条模组包/模组类别隐喻。
 *   2) 风险点：10 个 choice 键必须齐全(选项不参与翻译过滤)；掩码须 10 位否则后 5 条无法选中。
 *
 * 【段内说明】
 * - 复杂方法补充“干什么 / 边界 / 线程侧”精简中文注释。
 */
/**
 * 【变更记录 #5】2026-09-29 17:51:46（内测5修订93）
 * - 删除：旧正文活动引用被审核原文替代；保留历史资源和存档。
 * - 新增／修改：移除未调用的旧段落构造器；正式入口换为F01及26条IF图，保留原结束处理器。
 * - 用途：接通审核正文；其他系统触发及归属不据此宣称完成。
 */
import com.sirin.hk3gtl.common.dialogue.*;
import com.sirin.hk3gtl.common.dialogue.handler.SirinDialogueEndHandler;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

/**
 * 西琳终局对话定义注册。
 * <p>
 * 对话ID: "sirin_finale"
 * 结构：审核 F01、26条 IF、暂缓及现实生活收束。
 */
public final class SirinDialogueDefinitions {

    public static final String DIALOGUE_ID = "sirin_finale";
    public static final String END_HANDLER_KEY = "sirin_finale_end";
    /** IF 分支总数：0~4 内测二主题，5~9 内测三模组包/模组类别隐喻，10~19 内测三第二批扩展。与各处掩码位数保持一致。 */
    public static final int IF_BRANCH_COUNT = 26;

    private SirinDialogueDefinitions() {}

    /**
     * 注册西琳终局对话到 DialogueRegistry。
     * 在模组初始化阶段调用。
     */
    public static void register() {
        // 注册结束处理器
        DialogueRegistry.registerEndHandler(END_HANDLER_KEY, new SirinDialogueEndHandler());

        Map<String, List<DialogueLine>> segments = Hk3ApprovedDialogues.finaleGraph();

        DialogueDefinition def = new DialogueDefinition(
                DIALOGUE_ID,
                segments,
                "F01",
                true,
                END_HANDLER_KEY
        );

        DialogueRegistry.registerDialogue(def);
    }

}
