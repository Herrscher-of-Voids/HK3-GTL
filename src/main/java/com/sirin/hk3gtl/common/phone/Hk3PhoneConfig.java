package com.sirin.hk3gtl.common.phone;

import net.minecraftforge.common.ForgeConfigSpec;

public final class Hk3PhoneConfig {
    public static final ForgeConfigSpec SPEC;
    public static final ForgeConfigSpec.ConfigValue<java.util.List<? extends String>> APP_ORDER;
    public static final ForgeConfigSpec.BooleanValue RIGHT,SOUND,CHATTER;
    public static final ForgeConfigSpec.IntValue MARGIN,TOP,PHONE_SIZE;
    public static final ForgeConfigSpec.DoubleValue SCALE,POSITION_X,POSITION_Y,GAZE_X,GAZE_Y,GAZE_SCALE;
    static {
        var b=new ForgeConfigSpec.Builder();
        RIGHT=b.comment("浮层置于右侧；关闭后置于左侧，可避让小地图。").define("rightSide",true);
        MARGIN=b.comment("浮层离屏幕左右边缘的距离，按GUI像素。").defineInRange("horizontalMargin",12,0,500);
        TOP=b.comment("浮层距屏幕顶端，按GUI像素；可避让任务追踪。").defineInRange("top",24,0,600);
        SCALE=b.comment("通知浮层缩放，不改变游戏GUI缩放。").defineInRange("scale",1.0,.6,1.5);
        PHONE_SIZE=b.comment("手机机身占可用窗口的百分比，等比适配宽高。").defineInRange("phoneSize",72,60,86);
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
