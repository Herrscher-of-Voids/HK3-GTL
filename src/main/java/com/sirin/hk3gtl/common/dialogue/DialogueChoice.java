package com.sirin.hk3gtl.common.dialogue;



import javax.annotation.Nullable;

/**
 * 对话选项定义。
 *
 * @param labelKey         按钮文本翻译键
 * @param targetSegmentId  选择后跳转的 segment ID
 */
public record DialogueChoice(
        String labelKey,
        String targetSegmentId
) {}
