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
