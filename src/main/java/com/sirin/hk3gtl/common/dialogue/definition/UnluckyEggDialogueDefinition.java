package com.sirin.hk3gtl.common.dialogue.definition;


/**
 * 【文件职责】
 * - 维护 UnluckyEggDialogueDefinition 的核心功能实现。
 * - 关键调用链：由上层系统入口调用 -> 本文件核心方法 -> 下游模块。
 *
 * 【变更记录】2026-05-19
 * - 删除：
 *   1) 初始归档备注：自 v0.3 基线梳理，无本次 diff。
 * - 新增：
 *   1) 新增统一变更备注块，便于后续维护与审计追踪。
 * - 修改：
 *   1) 未改动业务逻辑，仅补充文件级职责与维护注释模板。
 * - 用途：
 *   1) 帮助维护者快速理解文件职责、变更背景与风险点。
 *
 * 【段内说明】
 * - 复杂方法补充“干什么 / 边界 / 线程侧”精简中文注释。
 */
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
