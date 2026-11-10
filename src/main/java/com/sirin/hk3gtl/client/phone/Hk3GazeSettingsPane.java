package com.sirin.hk3gtl.client.phone;
import com.sirin.hk3gtl.common.phone.*;
import com.sirin.hk3gtl.client.gaze.Hk3GazeHudOverlay;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.AbstractSliderButton;
import net.minecraft.network.chat.Component;
/**
 * 【变更记录 #1】2026-09-30 19:18:43（修订115）
 * 删除：无；新增：注视HUD拖动预览与缩放滑条；修改：无；用途：用户可避开其他模组HUD，位置随客户端保存。
 */
final class Hk3GazeSettingsPane {
    private int x,y,w,h,sw,sh;private double ratio,grabX,grabY;private boolean dragging;
    void layout(int left,int top,int available){
        var win=Minecraft.getInstance().getWindow();sw=win.getGuiScaledWidth();sh=win.getGuiScaledHeight();
        ratio=Math.min((double)available/Math.max(1,sw),200.0/Math.max(1,sh));
        w=(int)(sw*ratio);h=(int)(sh*ratio);x=left+(available-w)/2;y=top+(200-h)/2;
    }
    void render(GuiGraphics g){
        g.fill(x-1,y-1,x+w+1,y+h+1,0xFF726287);g.fill(x,y,x+w,y+h,0xFF101923);
        var font=Minecraft.getInstance().font;
        g.pose().pushPose();g.pose().translate(x,y,0);g.pose().scale((float)ratio,(float)ratio,1);
        g.drawString(font,"FPS · 顶部显示区",4,4,0xFFB6BFCE,false);
        var p=Hk3GazeHudOverlay.placement(sw,sh);
        g.pose().translate(p.x(),p.y(),0);g.pose().scale((float)p.scale(),(float)p.scale(),1);Hk3GazeHudOverlay.panel(g);g.pose().popPose();
    }
    boolean click(double mx,double my,int button){
        var p=Hk3GazeHudOverlay.placement(sw,sh);double left=x+p.x()*ratio,top=y+p.y()*ratio;
        if(button!=0||mx<left||mx>left+p.width()*ratio||my<top||my>top+p.height()*ratio)return false;
        dragging=true;grabX=(mx-left)/ratio;grabY=(my-top)/ratio;return true;
    }
    boolean drag(double mx,double my){
        if(!dragging)return false;var p=Hk3GazeHudOverlay.placement(sw,sh);
        Hk3PhoneConfig.GAZE_X.set(Hk3PhoneLayout.unit(((mx-x)/ratio-grabX)/Math.max(1,sw-p.width())));
        Hk3PhoneConfig.GAZE_Y.set(Hk3PhoneLayout.unit(((my-y)/ratio-grabY)/Math.max(1,sh-p.height())));return true;
    }
    boolean release(){if(!dragging)return false;dragging=false;Hk3PhoneConfig.SPEC.save();return true;}
    static AbstractSliderButton slider(int x,int y){
        return new AbstractSliderButton(x,y,312,24,Component.empty(),(Hk3PhoneConfig.GAZE_SCALE.get()-.6)/.9){
            {updateMessage();}
            @Override protected void updateMessage(){setMessage(Component.literal("注视 HUD 大小  "+Math.round((.6+value*.9)*100)+"%"));}
            @Override protected void applyValue(){Hk3PhoneConfig.GAZE_SCALE.set(.6+value*.9);}
            @Override public void onRelease(double mx,double my){Hk3PhoneConfig.SPEC.save();super.onRelease(mx,my);}
        };
    }
}
