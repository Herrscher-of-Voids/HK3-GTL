package com.sirin.hk3gtl.client.dialogue;


/**
 * 【文件职责】
 * - 负责 DialogueRenderHelper 客户端渲染或 UI 逻辑。
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
/**
 * 对话渲染辅助工具 —— 逐字显示、颜色码处理、文本截断。
 */
public final class DialogueRenderHelper {

    private DialogueRenderHelper() {}

    /**
     * 计算文本中可见字符数（跳过 Minecraft 颜色码 §x）。
     */
    public static int countVisibleChars(String text) {
        int count = 0;
        for (int i = 0; i < text.length(); i++) {
            char c = text.charAt(i);
            if (c == '§' && i + 1 < text.length()) {
                i++;
            } else {
                count++;
            }
        }
        return count;
    }

    /**
     * 截断文本到指定可见字符数，保留颜色码完整性。
     */
    public static String truncateToVisibleChars(String text, int maxVisible) {
        StringBuilder sb = new StringBuilder();
        int visible = 0;
        for (int i = 0; i < text.length(); i++) {
            char c = text.charAt(i);
            if (c == '§' && i + 1 < text.length()) {
                sb.append(c).append(text.charAt(i + 1));
                i++;
            } else {
                if (visible >= maxVisible) break;
                sb.append(c);
                visible++;
            }
        }
        return sb.toString();
    }
}
