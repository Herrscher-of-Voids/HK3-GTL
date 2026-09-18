package com.sirin.hk3gtl.common.dialogue;



import javax.annotation.Nullable;
import java.util.List;

/**
 * 单行对话定义。
 *
 * @param speakerId       说话者ID，对应 DialogueRegistry 中注册的主题
 * @param textKey         首选文本翻译键（客户端优先显示）
 * @param fallbackTextKey 首选键无翻译时的回退键，可为 null
 * @param choices         选项列表，null 表示无选项（自动推进到下一行）
 */
public record DialogueLine(
        String speakerId,
        String textKey,
        @Nullable String fallbackTextKey,
        @Nullable List<DialogueChoice> choices
) {}
