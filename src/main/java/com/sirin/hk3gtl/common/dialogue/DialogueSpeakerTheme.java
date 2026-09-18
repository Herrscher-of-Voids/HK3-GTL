package com.sirin.hk3gtl.common.dialogue;



import net.minecraft.resources.ResourceLocation;

import javax.annotation.Nullable;

/**
 * 说话者主题配置 —— 控制对话界面中角色名牌颜色、头像、强调色。
 *
 * @param speakerId   说话者唯一ID
 * @param nameKey     角色名翻译键
 * @param portrait    头像纹理路径(128x128)，null 表示无头像
 * @param nameColor   名牌文字颜色 (ARGB)
 * @param accentColor 强调色（面板边框、选项悬停等）
 */
public record DialogueSpeakerTheme(
        String speakerId,
        String nameKey,
        @Nullable ResourceLocation portrait,
        int nameColor,
        int accentColor
) {}
