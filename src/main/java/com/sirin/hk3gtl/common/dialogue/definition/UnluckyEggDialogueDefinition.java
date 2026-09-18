package com.sirin.hk3gtl.common.dialogue.definition;



import com.sirin.hk3gtl.common.dialogue.*;
import com.sirin.hk3gtl.common.dialogue.handler.UnluckyEggEndHandler;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * 非酋彩蛋对话定义注册。
 * <p>
 * 触发条件: 研究累计失败10次
 * 对话ID: "unlucky_egg"
 * 结构: 单 segment "main"，4行线性对话，无分支
 */
public final class UnluckyEggDialogueDefinition {

    public static final String DIALOGUE_ID = "unlucky_egg";
    public static final String END_HANDLER_KEY = "unlucky_egg_end";

    private UnluckyEggDialogueDefinition() {}

    public static void register() {
        DialogueRegistry.registerEndHandler(END_HANDLER_KEY, new UnluckyEggEndHandler());

        List<DialogueLine> mainLines = List.of(
                new DialogueLine("unknown", "hk3gtl.dialogue.unlucky.01", null, null),
                new DialogueLine("unknown", "hk3gtl.dialogue.unlucky.02", null, null),
                new DialogueLine("unknown", "hk3gtl.dialogue.unlucky.03", null, null),
                new DialogueLine("unknown", "hk3gtl.dialogue.unlucky.04", null, null),
                new DialogueLine("system", "hk3gtl.dialogue.unlucky.system", null, null)
        );

        Map<String, List<DialogueLine>> segments = new LinkedHashMap<>();
        segments.put("main", mainLines);

        DialogueDefinition def = new DialogueDefinition(
                DIALOGUE_ID,
                segments,
                "main",
                true,
                END_HANDLER_KEY
        );

        DialogueRegistry.registerDialogue(def);
    }
}
