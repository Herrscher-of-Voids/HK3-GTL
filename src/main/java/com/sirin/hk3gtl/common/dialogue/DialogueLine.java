package com.sirin.hk3gtl.common.dialogue;


/**
 * 【文件职责】
 * - 维护 DialogueLine 的核心功能实现。
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
