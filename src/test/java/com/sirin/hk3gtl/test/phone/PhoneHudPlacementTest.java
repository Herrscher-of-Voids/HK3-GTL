package com.sirin.hk3gtl.test.phone;
import com.sirin.hk3gtl.common.phone.Hk3GazeHudLayout;
/** 【变更记录 #1】2026-09-30 19:20:11（修订115）：删除无；新增HUD多分辨率/缩放/越界拖动检查；修改无；用途：生产定位算法验证，不替代实机视觉验收。 */
public final class PhoneHudPlacementTest {
    static int checks;static void check(boolean v){if(!v)throw new AssertionError("HUD越界或默认位置错误");checks++;}
    public static void main(String[] args){
        for(int sw:new int[]{1,64,320,427,640,854,1280,1920,3840})
        for(int sh:new int[]{1,48,180,240,360,480,720,1080,2160})
        for(int width:new int[]{140,208,320,512})
        for(double scale:new double[]{.1,.6,1,1.5,9,Double.NaN})
        for(double pos:new double[]{-1,0,.25,.5,1,2,Double.NaN}){
            var p=Hk3GazeHudLayout.place(sw,sh,width,55,scale,pos,pos);
            check(p.x()>=0&&p.y()>=0&&p.width()>0&&p.height()>0);
            check(p.x()+p.width()<=sw&&p.y()+p.height()<=sh);
            check(Double.isFinite(p.scale())&&p.scale()>0);
        }
        var normal=Hk3GazeHudLayout.place(640,360,208,55,1,-1,-1);
        check(normal.x()==8&&normal.y()==40&&normal.scale()==1);
        var dragged=Hk3GazeHudLayout.place(640,360,208,55,1,1,1);
        check(dragged.x()==432&&dragged.y()==305);
        System.out.println("Phone gaze HUD: "+checks+" placement checks passed");
    }
}
