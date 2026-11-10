package com.sirin.hk3gtl.client.phone;
import com.sirin.hk3gtl.common.phone.Hk3PhoneConfig;
import com.sirin.hk3gtl.common.phone.Hk3PhoneDesktopOrder;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import java.util.List;

/**
 * 【变更记录 #1】2026-09-30 18:44:46（内测5修订113）
 * 删除：无；新增：手机桌面网格图标、按住拖动与落点交换。
 * 修改：无；用途：点击打开与拖动排序分开，越界松手取消排序。
 */
/** 【变更记录 #2】2026-09-30 19:49:34（修订116）：删除无；新增微讯息接入；修改：第12个可拖动应用图标；用途：保留原手机布局与权限，AI不进入服务器业务。 */
/** 【变更记录 #3】2026-10-01 04:27:55（修订128）：删除：旧固定上限或被替代的分支；新增/修改：实际拖动保存后回报完整应用排列，不影响原排序；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
final class Hk3PhoneDesktop {
    private final Hk3PhoneAppHintClient hints=new Hk3PhoneAppHintClient();
    void accept(net.minecraft.nbt.CompoundTag view){hints.accept(view);}
    void launch(String app){hints.launch(app);}
    void removed(){hints.removed();}
    void tooltip(GuiGraphics g,int mx,int my){
        int i=cell(mx,my);String app="";
        if(i>=0&&!dragging&&pressed<0){int x=left+(i%3)*104+20,y=top+(i/3)*68;if(mx>=x&&mx<x+64&&my>=y&&my<y+66)app=order.get(i);}
        hints.tooltip(g,app,mx,my);
    }
    private List<String> order=Hk3PhoneDesktopOrder.normalize(Hk3PhoneConfig.APP_ORDER.get());
    private int left,top,pressed=-1;private double startX,startY,mx,my;private boolean dragging;
    void layout(int x,int y){left=x;top=y;}
    private int cell(double x,double y){
        int col=(int)((x-left)/104),row=(int)((y-top)/68);
        if(x<left||y<top||col<0||col>2||row<0||row>3)return -1;
        return row*3+col<order.size()?row*3+col:-1;
    }
    boolean press(double x,double y,int button){
        if(button!=0)return false;pressed=cell(x,y);startX=mx=x;startY=my=y;dragging=false;return pressed>=0;
    }
    boolean drag(double x,double y){
        if(pressed<0)return false;mx=x;my=y;if(Math.hypot(x-startX,y-startY)>6)dragging=true;return true;
    }
    String release(double x,double y){
        if(pressed<0)return "";int from=pressed;pressed=-1;
        if(dragging){
            int to=cell(x,y);dragging=false;
            if(to>=0){order=Hk3PhoneDesktopOrder.move(order,from,to);Hk3PhoneConfig.APP_ORDER.set(order);Hk3PhoneConfig.SPEC.save();Hk3EggUiClient.send("layout",String.join(",",order));}
            return "";
        }
        return cell(x,y)==from?order.get(from):"";
    }
    void render(GuiGraphics g){
        for(int i=0;i<order.size();i++){
            int x=left+(i%3)*104+24,y=top+(i/3)*68;
            if(dragging&&i==pressed){g.fill(x,y,x+56,y+56,0x505D628C);continue;}
            g.pose().pushPose();g.pose().translate(x+6,y,0);g.pose().scale(.78F,.78F,1);drawIcon(g,order.get(i),0,0);g.pose().popPose();
        }
        if(dragging&&pressed>=0)drawIcon(g,order.get(pressed),(int)mx-28,(int)my-28);
    }
    private static void round(GuiGraphics g,int x,int y,int w,int h,int color){
        for(int row=0;row<h;row++){int inset=row<3||row>=h-3?6:row<6||row>=h-6?3:0;g.fill(x+inset,y+row,x+w-inset,y+row+1,color);}
    }
    private static void drawIcon(GuiGraphics g,String id,int x,int y){
        int color=switch(id){case "social"->0xFF42AD80;case "notes"->0xFFC4A454;case "trade"->0xFFBD6B7D;case "tiles2048"->0xFFC98853;case "snake"->0xFF62A47D;case "civilization"->0xFF8474B0;case "inbox"->0xFF548CCE;case "letters"->0xFF9B6FC8;case "ae"->0xFF65AB98;case "updates"->0xFFC59851;case "settings"->0xFF687992;default->0xFF9C6682;};
        round(g,x,y,56,56,color);g.fill(x+9,y+5,x+47,y+7,0x60FFFFFF);
        int white=0xFFF9F5FF;
        switch(id){
            case "social"->{g.fill(x+11,y+15,x+39,y+32,white);g.fill(x+29,y+28,x+45,y+42,0xFFCFF2DE);g.fill(x+15,y+30,x+20,y+36,white);g.fill(x+22,y+20,x+25,y+23,color);g.fill(x+30,y+20,x+33,y+23,color);}
            case "inbox","letters"->{
                g.fill(x+12,y+18,x+44,y+38,white);g.fill(x+14,y+20,x+42,y+36,color);
                for(int i=0;i<14;i++){g.fill(x+14+i,y+20+i/2,x+15+i,y+21+i/2,white);g.fill(x+41-i,y+20+i/2,x+42-i,y+21+i/2,white);}
            }
            case "ae"->{for(int i=0;i<3;i++)for(int j=0;j<3;j++)g.fill(x+14+i*10,y+14+j*10,x+21+i*10,y+21+j*10,white);}
            case "settings"->{g.fill(x+25,y+12,x+31,y+44,white);g.fill(x+12,y+25,x+44,y+31,white);g.fill(x+18,y+18,x+38,y+38,white);g.fill(x+24,y+24,x+32,y+32,color);}
            case "notes","civilization","updates"->{g.fill(x+17,y+12,x+39,y+43,white);for(int i=0;i<4;i++)g.fill(x+21,y+18+i*6,x+35,y+20+i*6,color);}
            case "tiles2048"->{g.drawCenteredString(Minecraft.getInstance().font,"2048",x+28,y+25,white);}
            case "snake"->{g.fill(x+14,y+17,x+36,y+24,white);g.fill(x+29,y+21,x+36,y+39,white);g.fill(x+20,y+33,x+32,y+40,white);}
            case "trade"->{g.fill(x+14,y+22,x+42,y+41,white);g.fill(x+21,y+14,x+35,y+24,white);g.fill(x+24,y+17,x+32,y+25,color);}
            default->{g.fill(x+19,y+19,x+37,y+35,white);g.fill(x+16,y+35,x+40,y+38,white);g.fill(x+25,y+40,x+31,y+43,white);}
        }
        String label=switch(id){case "social"->"微讯息";case "notes"->"笔记本";case "trade"->"交易";case "tiles2048"->"2048";case "snake"->"贪吃蛇";case "civilization"->"文明总览";case "inbox"->"讯息";case "letters"->"信件";case "ae"->"AE终端";case "updates"->"更新";case "settings"->"设定";default->"收起提醒";};
        g.drawCenteredString(Minecraft.getInstance().font,label,x+28,y+65,white);
    }
}
