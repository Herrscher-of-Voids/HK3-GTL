package com.sirin.hk3gtl.client.dialogue;



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
