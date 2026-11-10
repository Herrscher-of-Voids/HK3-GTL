package com.sirin.hk3gtl.common.phone;

/**
 * 【变更记录 #1】2026-09-30 18:18:05（内测5修订112）
 * 删除：无；新增：整页索引与归一化通知布局计算。
 * 修改：无；用途：实际阅读/拖动预览/浮层共用边界，纯逻辑可回归。
 */
public final class Hk3PhoneLayout {
    private Hk3PhoneLayout(){}
    public static int pages(int lines,int perPage){return Math.max(1,(int)(((long)Math.max(0,lines)+Math.max(1,perPage)-1)/Math.max(1,perPage)));}
    public static int page(int requested,int lines,int perPage){return Math.max(0,Math.min(pages(lines,perPage)-1,requested));}
    public static double unit(double value){return Double.isFinite(value)?Math.max(0,Math.min(1,value)):0;}
    public record Toast(int x,int y,int width,int height,int stackHeight,double scale){}
    public static Toast toast(int sw,int sh,int count,double requested,double px,double py,boolean right,int margin,int top){
        sw=Math.max(1,sw);sh=Math.max(1,sh);count=Math.max(1,Math.min(2,count));
        double scale=Math.max(.001,Math.min(requested,Math.min(Math.max(1,sw-16)/218.0,Math.max(1,sh-16)/(count==2?136.0:64.0))));
        int w=Math.max(1,(int)(218*scale)),h=Math.max(1,(int)(64*scale));
        int stack=(int)((count==2?136:64)*scale);
        int freeX=Math.max(0,sw-w),freeY=Math.max(0,sh-stack);
        int x=px<0?Math.max(0,Math.min(freeX,right?freeX-margin:margin)):(int)Math.round(unit(px)*freeX);
        int y=py<0?Math.max(0,Math.min(freeY,top)):(int)Math.round(unit(py)*freeY);
        return new Toast(x,y,w,h,stack,scale);
    }
}
