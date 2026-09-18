package com.sirin.hk3gtl.common.dialogue;



import javax.annotation.Nullable;
import java.util.List;
import java.util.Map;

/**
 * 完整对话定义。
 * <p>
 * 对话由多个 segment 组成，每个 segment 是有序的 {@link DialogueLine} 列表。
 * 播放时从 startSegmentId 开始，遇到带 choices 的行时暂停等待选择，
 * 选择后跳转到目标 segment。segment 播完且末行无 choices 则对话结束。
 *
 * @param dialogueId     唯一对话ID
 * @param segments       segmentId -> 有序行列表
 * @param startSegmentId 初始 segment
 * @param closableByEsc  是否允许 ESC 关闭
 * @param endHandlerKey  结束处理器注册键，null 则无回调
 */
public record DialogueDefinition(
        String dialogueId,
        Map<String, List<DialogueLine>> segments,
        String startSegmentId,
        boolean closableByEsc,
        @Nullable String endHandlerKey
) {}
