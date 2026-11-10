package com.sirin.hk3gtl.common.dialogue;


/**
 * 【文件职责】
 * - 维护 DialogueDefinition 的核心功能实现。
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
