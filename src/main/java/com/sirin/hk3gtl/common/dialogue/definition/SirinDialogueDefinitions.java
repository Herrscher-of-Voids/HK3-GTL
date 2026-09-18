package com.sirin.hk3gtl.common.dialogue.definition;



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
 * 结构: intro segment + 10个IF分支 segment（0~4 内测二主题，5~9 内测三模组包/模组类别隐喻）
 */
public final class SirinDialogueDefinitions {

    public static final String DIALOGUE_ID = "sirin_finale";
    public static final String END_HANDLER_KEY = "sirin_finale_end";
    /** IF 分支最大预留行数；客户端会自动过滤不存在的翻译键。 */
    private static final int MAX_IF_LINES = 20;
    /** IF 分支总数：0~4 内测二主题，5~9 内测三模组包/模组类别隐喻，10~19 内测三第二批扩展。与各处掩码位数保持一致。 */
    public static final int IF_BRANCH_COUNT = 20;

    private SirinDialogueDefinitions() {}

    /**
     * 注册西琳终局对话到 DialogueRegistry。
     * 在模组初始化阶段调用。
     */
    public static void register() {
        // 注册结束处理器
        DialogueRegistry.registerEndHandler(END_HANDLER_KEY, new SirinDialogueEndHandler());

        // 构建 segments
        Map<String, List<DialogueLine>> segments = new LinkedHashMap<>();
        segments.put("intro", buildIntroSegment());
        for (int i = 0; i < IF_BRANCH_COUNT; i++) {
            segments.put("if_" + i, buildIfSegment(i));
        }

        DialogueDefinition def = new DialogueDefinition(
                DIALOGUE_ID,
                segments,
                "intro",
                false,
                END_HANDLER_KEY
        );

        DialogueRegistry.registerDialogue(def);
    }

    /**
     * INTRO：内测二优先 {@code hk3gtl.dialogue.sirin.d01}～d24}（改 zh_cn 即生效），回退 {@code v0_2_0.dXX}；
     * 内测一优先版本键，回退 d01～d52。末行附 5 个 IF 选项。
     */
    private static List<DialogueLine> buildIntroSegment() {
        List<DialogueLine> lines = new ArrayList<>();
        String ver = SirinDialogueVersion.introKeySuffix();
        boolean beta2 = SirinDialogueVersion.isBeta2OrLater();
        int lineCount = SirinDialogueVersion.introLineCount();
        for (int ord = 1; ord <= lineCount; ord++) {
            String legacy = String.format(Locale.ROOT, "hk3gtl.dialogue.sirin.d%02d", ord);
            String versioned = String.format(Locale.ROOT, "hk3gtl.dialogue.sirin.%s.d%02d", ver, ord);
            String primary = versioned;
            String fallback = legacy;
            lines.add(new DialogueLine("sirin", primary, fallback, null));
        }

        List<DialogueChoice> choices = new ArrayList<>();
        for (int i = 0; i < IF_BRANCH_COUNT; i++) {
            choices.add(new DialogueChoice(
                    "hk3gtl.dialogue.sirin.choice." + i,
                    "if_" + i
            ));
        }
        lines.add(new DialogueLine("sirin", "hk3gtl.dialogue.sirin.choice_prompt", null, choices));

        return lines;
    }

    /** IF 线：多行键 if.&lt;index&gt;.01～，首行回退到旧 {@code .main} 占位；无翻译的行由客户端自动过滤。 */
    private static List<DialogueLine> buildIfSegment(int optionIndex) {
        List<DialogueLine> lines = new ArrayList<>();
        String base = "hk3gtl.dialogue.sirin.if." + optionIndex + ".";
        lines.add(new DialogueLine("sirin", base + "01", base + "main", null));
        for (int ln = 2; ln <= MAX_IF_LINES; ln++) {
            lines.add(new DialogueLine("sirin", base + String.format(Locale.ROOT, "%02d", ln), null, null));
        }
        return lines;
    }
}
