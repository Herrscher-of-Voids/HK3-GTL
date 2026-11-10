package com.sirin.hk3gtl.common.phone;

import net.minecraftforge.common.ForgeConfigSpec;

/**
 * 【变更记录 #1】2026-09-30 16:19:31（内测5修订110）
 * 删除：被新版通知读取流程替代的旧分支，历史备注保留。
 * 新增／修改：客户端配置浮层位置、缩放、声音和非关键闲话，默认右侧；只影响显示，不删除消息。
 * 用途：通知与业务结果分离，服务端授权和个人持久化；不改结构、贴图和贸易。
 */
/**
 * 【变更记录 #2】2026-09-30 18:18:05（内测5修订112）
 * 删除：无；新增：归一化拖动坐标，未设置时读取旧边距。
 * 修改：位置不再依赖循环按钮；用途：预览与真实浮层共享同一坐标模型。
 */
/**
 * 【变更记录 #3】2026-09-30 18:44:46（内测5修订113）
 * 删除：无；新增：桌面应用排列持久配置；修改：无；用途：拖动重排重启后保留，未知项由白名单清理。
 */
/** 【变更记录 #4】2026-09-30 19:20:11（内测5修订115）：删除无；新增注视HUD归一化坐标与缩放配置；修改默认纵坐标40像素；用途：拖动预览与实际HUD一致。 */
public final class Hk3PhoneConfig {
    public static final ForgeConfigSpec SPEC;
    public static final ForgeConfigSpec.ConfigValue<java.util.List<? extends String>> APP_ORDER;
    public static final ForgeConfigSpec.BooleanValue RIGHT,SOUND,CHATTER;
    public static final ForgeConfigSpec.IntValue MARGIN,TOP;
    public static final ForgeConfigSpec.DoubleValue SCALE,POSITION_X,POSITION_Y,GAZE_X,GAZE_Y,GAZE_SCALE;
    static {
        var b=new ForgeConfigSpec.Builder();
        RIGHT=b.comment("浮层置于右侧；关闭后置于左侧，可避让小地图。").define("rightSide",true);
        MARGIN=b.comment("浮层离屏幕左右边缘的距离，按GUI像素。").defineInRange("horizontalMargin",12,0,500);
        TOP=b.comment("浮层距屏幕顶端，按GUI像素；可避让任务追踪。").defineInRange("top",24,0,600);
        SCALE=b.comment("通知浮层缩放，不改变游戏GUI缩放。").defineInRange("scale",1.0,.6,1.5);
        SOUND=b.comment("显示一组新通知时播放轻提示音。").define("sound",true);
        CHATTER=b.comment("非关键闲话是否显示浮层；关闭仍保留收件箱记录。").define("chatter",true);
        POSITION_X=b.comment("拖动后的横向位置比例；-1兼容旧边距。").defineInRange("positionX",-1.0,-1.0,1.0);
        POSITION_Y=b.comment("拖动后的纵向位置比例；-1兼容旧高度。").defineInRange("positionY",-1.0,-1.0,1.0);
        APP_ORDER=b.comment("手机桌面应用顺序；拖动图标交换位置。").defineListAllowEmpty("appOrder",java.util.List.of("inbox","letters","ae","updates","settings","quiet"),v->v instanceof String);
        GAZE_X=b.comment("注视HUD横向位置比例；-1默认左侧8像素。").defineInRange("gazeX",-1.0,-1.0,1.0);
        GAZE_Y=b.comment("注视HUD纵向位置比例；-1默认顶部40像素，避让帧率。").defineInRange("gazeY",-1.0,-1.0,1.0);
        GAZE_SCALE=b.comment("注视HUD显示缩放，手机设定中可预览和拖动。").defineInRange("gazeScale",1.0,.6,1.5);
        SPEC=b.build();
    }
    private Hk3PhoneConfig(){}
}
