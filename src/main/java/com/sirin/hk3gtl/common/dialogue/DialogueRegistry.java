package com.sirin.hk3gtl.common.dialogue;


/**
 * 【文件职责】
 * - 维护 DialogueRegistry 的核心功能实现。
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
import com.sirin.hk3gtl.common.constants.Hk3Constants;
import com.sirin.hk3gtl.common.dialogue.handler.IDialogueEndHandler;
import net.minecraft.resources.ResourceLocation;
import org.slf4j.Logger;
import com.mojang.logging.LogUtils;

import javax.annotation.Nullable;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 对话系统注册表 —— 管理所有对话定义和说话者主题。
 */
public final class DialogueRegistry {

    private static final Logger LOGGER = LogUtils.getLogger();

    private static final ConcurrentHashMap<String, DialogueDefinition> DIALOGUES = new ConcurrentHashMap<>();
    private static final ConcurrentHashMap<String, DialogueSpeakerTheme> SPEAKERS = new ConcurrentHashMap<>();
    private static final ConcurrentHashMap<String, IDialogueEndHandler> END_HANDLERS = new ConcurrentHashMap<>();

    private DialogueRegistry() {}

    // ═══════════════ 对话定义 ═══════════════

    public static void registerDialogue(DialogueDefinition definition) {
        DIALOGUES.put(definition.dialogueId(), definition);
        LOGGER.debug("[HK3GTL] 注册对话: {}", definition.dialogueId());
    }

    @Nullable
    public static DialogueDefinition getDialogue(String dialogueId) {
        return DIALOGUES.get(dialogueId);
    }

    // ═══════════════ 说话者主题 ═══════════════

    public static void registerSpeaker(DialogueSpeakerTheme theme) {
        SPEAKERS.put(theme.speakerId(), theme);
    }

    @Nullable
    public static DialogueSpeakerTheme getSpeaker(String speakerId) {
        return SPEAKERS.get(speakerId);
    }

    // ═══════════════ 结束处理器 ═══════════════

    public static void registerEndHandler(String key, IDialogueEndHandler handler) {
        END_HANDLERS.put(key, handler);
    }

    @Nullable
    public static IDialogueEndHandler getEndHandler(String key) {
        return END_HANDLERS.get(key);
    }

    // ═══════════════ 初始化 ═══════════════

    /**
     * 注册内置说话者主题。在模组初始化阶段调用。
     */
    public static void registerBuiltinSpeakers() {
        registerSpeaker(new DialogueSpeakerTheme(
                "sirin",
                "hk3gtl.dialogue.speaker.sirin",
                new ResourceLocation(Hk3Constants.MOD_ID, "textures/gui/dialogue/sirin.png"),
                0xFFDD55FF,
                0xFFDD55FF
        ));

        registerSpeaker(new DialogueSpeakerTheme(
                "unknown",
                "hk3gtl.dialogue.speaker.unknown",
                new ResourceLocation(Hk3Constants.MOD_ID, "textures/gui/dialogue/unknown.png"),
                0xFFFFAA00,
                0xFFFFAA00
        ));

        registerSpeaker(new DialogueSpeakerTheme(
                "system",
                "hk3gtl.dialogue.speaker.system",
                null,
                0xFF888888,
                0xFF888888
        ));
    }
}
