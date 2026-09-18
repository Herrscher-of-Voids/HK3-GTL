package com.sirin.hk3gtl.common.dialogue;



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
