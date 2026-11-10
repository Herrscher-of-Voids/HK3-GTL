package com.sirin.hk3gtl.client.phone;

import com.sirin.hk3gtl.common.phone.Hk3PhoneConfig;
import com.sirin.hk3gtl.common.phone.Hk3PhoneLayout;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.AbstractSliderButton;
import net.minecraft.network.chat.Component;

/**
 * 【变更记录 #1】2026-09-30 18:18:05（内测5修订112）
 * 删除：无；新增：屏幕缩略预览、直接拖动通知卡与连续缩放滑条。
 * 修改：位置保存为可用空间比例；用途：预览和真实通知共用尺寸、缩放及边界。
 */
/** 【变更记录 #2】2026-09-30 18:44:46（修订113）：删除固定宽度；新增可用宽度参数；修改手机纵屏适配；用途：预览不越界。 */
/** 【变更记录 #3】2026-10-01 04:27:55（修订128）：删除：旧固定上限或被替代的分支；新增/修改：实际拖动松手保存后传归一化坐标，界面预览保持原样；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #4】2026-10-01 05:09:29（修订128）：删除：旧固定上限或被替代的分支；新增/修改：拖动松手须实际改变显示坐标才发旁注，原地按下松开不算移动；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
final class Hk3PhoneSettingsPane {
    private int x,y,w,h;private double ratio,grabX,grabY;private boolean dragging;private int originalX,originalY;
    private int sw,sh;
    void layout(int left,int top,int available){
        var win=Minecraft.getInstance().getWindow();sw=win.getGuiScaledWidth();sh=win.getGuiScaledHeight();
        ratio=Math.min((double)available/Math.max(1,sw),190.0/Math.max(1,sh));
        w=(int)(sw*ratio);h=(int)(sh*ratio);x=left+(available-w)/2;y=top+(190-h)/2;
    }
    private Hk3PhoneLayout.Toast placement(){
        return Hk3PhoneLayout.toast(sw,sh,sw<600||sh<240?1:2,Hk3PhoneConfig.SCALE.get(),
            Hk3PhoneConfig.POSITION_X.get(),Hk3PhoneConfig.POSITION_Y.get(),Hk3PhoneConfig.RIGHT.get(),
            Hk3PhoneConfig.MARGIN.get(),Hk3PhoneConfig.TOP.get());
    }
    void render(GuiGraphics g){
        var font=Minecraft.getInstance().font;
        g.fill(x-1,y-1,x+w+1,y+h+1,0xFF726287);g.fill(x,y,x+w,y+h,0xFF101923);
        for(int i=1;i<4;i++){g.fill(x+w*i/4,y,x+w*i/4+1,y+h,0xFF24303D);g.fill(x,y+h*i/4,x+w,y+h*i/4+1,0xFF24303D);}
        g.drawString(font,"游戏视野 · 拖动通知卡",x+7,y+7,0xFFAEB5C9,false);
        g.fill(x+w/2-34,y+h-10,x+w/2+34,y+h-4,0xFF485060);
        var p=placement();
        g.pose().pushPose();g.pose().translate(x+p.x()*ratio,y+p.y()*ratio,0);
        g.pose().scale((float)(ratio*p.scale()),(float)(ratio*p.scale()),1);
        Hk3PhoneStyle.card(g,"收到新的来信","这是通知的位置与大小预览。","拖住这张卡片移动");
        if(sw>=600&&sh>=240){g.pose().translate(0,72,0);Hk3PhoneStyle.card(g,"研究完成","第二条通知会排列在下方。","消息中心");}
        g.pose().popPose();
    }
    boolean click(double mx,double my,int button){
        var p=placement();double left=x+p.x()*ratio,top=y+p.y()*ratio;
        if(button!=0||mx<left||mx>left+p.width()*ratio||my<top||my>top+p.stackHeight()*ratio)return false;
        originalX=p.x();originalY=p.y();dragging=true;grabX=(mx-left)/ratio;grabY=(my-top)/ratio;return true;
    }
    boolean drag(double mx,double my){
        if(!dragging)return false;var p=placement();
        Hk3PhoneConfig.POSITION_X.set(Hk3PhoneLayout.unit(((mx-x)/ratio-grabX)/Math.max(1,sw-p.width())));
        Hk3PhoneConfig.POSITION_Y.set(Hk3PhoneLayout.unit(((my-y)/ratio-grabY)/Math.max(1,sh-p.stackHeight())));
        return true;
    }
    boolean release(){if(!dragging)return false;dragging=false;Hk3PhoneConfig.SPEC.save();var current=placement();if(current.x()!=originalX||current.y()!=originalY)Hk3EggUiClient.send("notification_position",Hk3PhoneConfig.POSITION_X.get()+","+Hk3PhoneConfig.POSITION_Y.get());return true;}
    static AbstractSliderButton scaleSlider(int x,int y,int width){
        return new AbstractSliderButton(x,y,width,22,Component.empty(),(Hk3PhoneConfig.SCALE.get()-.6)/.9){
            {updateMessage();}
            @Override protected void updateMessage(){setMessage(Component.literal("通知大小  "+Math.round((.6+value*.9)*100)+"%"));}
            @Override protected void applyValue(){Hk3PhoneConfig.SCALE.set(.6+value*.9);}
            @Override public void onRelease(double mx,double my){super.onRelease(mx,my);Hk3PhoneConfig.SPEC.save();}
        };
    }
}
