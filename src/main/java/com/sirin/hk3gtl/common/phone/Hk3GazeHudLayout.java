package com.sirin.hk3gtl.common.phone;
/**
 * 【变更记录 #1】2026-09-30 19:18:43（修订115）
 * 删除：无；新增：注视HUD尺寸、缩放与位置纯计算；修改：无；用途：实际HUD和拖动预览共用边界，默认避开顶部帧率区。
 */
public final class Hk3GazeHudLayout {
    private Hk3GazeHudLayout(){}
    public record Box(int x,int y,int width,int height,double scale){}
    public static Box place(int sw,int sh,int naturalWidth,int naturalHeight,double requested,double px,double py){
        sw=Math.max(1,sw);sh=Math.max(1,sh);naturalWidth=Math.max(1,naturalWidth);naturalHeight=Math.max(1,naturalHeight);
        double scale=Math.min(Double.isFinite(requested)?Math.max(.6,Math.min(1.5,requested)):1,
            Math.min((double)sw/naturalWidth,(double)sh/naturalHeight));
        int w=Math.min(sw,Math.max(1,(int)Math.ceil(naturalWidth*scale))),h=Math.min(sh,Math.max(1,(int)Math.ceil(naturalHeight*scale)));
        int fx=Math.max(0,sw-w),fy=Math.max(0,sh-h);
        int x=px<0?Math.min(8,fx):(int)Math.round(Hk3PhoneLayout.unit(px)*fx);
        int y=py<0?Math.min(40,fy):(int)Math.round(Hk3PhoneLayout.unit(py)*fy);
        return new Box(x,y,w,h,scale);
    }
}
