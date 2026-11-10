package com.sirin.hk3gtl.client.phone;

import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.util.FormattedCharSequence;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/**
 * 【文件职责】文明总览内的团队机器目录与只读详情；仅显示服务端授权投影，不操作世界或机器。
 * 【变更记录 #1】2026-10-19 02:05:08（第1次备注 · 修订171）
 * - 删除：无。
 * - 新增：每页4台目录、来源/状态筛选、现场登记目录入口、原筛选返回、状态配色、完整详情分页与权限失效后的清空页面。
 * - 修改：复用手机既有缩放与按钮，不创建桌面图标；未加载状态明确保留最后可信存档刻。
 * - 用途：由Hk3PhoneExtraApps接入服务端机器索引，未知状态不冒充停机，不展示个人数据或写入控制。
 * 【变更记录 #2】2026-10-19 02:17:49（第2次备注 · 修订171）
 * - 删除：固定来源名单对筛选的限制；新增：服务端当前团队来源列表的动态循环。
 * - 修改：未知附属命名空间保留原名与返回路径；用途：既存附属均可按真实登记来源筛选，不猜测模组清单。
 */
final class Hk3MachineOverviewPane {
    private static final String[] SOURCES={"all","hk3gtl","gtceu","gtlcore","gtladditions","gtlsupb"};
    private static final String[] SOURCE_LABELS={"全部","HK3GTL","GTCEu","GTL Core","GTL附属","GTL SupB"};
    private static final String[] STATES={"all","running","stopped","need_energy","need_input","unloaded","unformed","unadapted","unknown"};
    private static final String[] STATE_LABELS={"全部","运行","停机","缺电","缺料","未加载","未成型","未适配","未知"};
    private static final int PAGE_SIZE=4,DETAIL_LINES=27;
    private final Hk3PhoneScreen host;
    private int detailPage;
    private String detailId="";
    private String unavailable="";
    private final List<FormattedCharSequence> detailLines=new ArrayList<>();

    Hk3MachineOverviewPane(Hk3PhoneScreen host){this.host=host;}

    void init(String mode,CompoundTag view,int x,int y){
        if(mode.equals("machines"))initDirectory(view,x,y);
        else if(mode.equals("machine_detail"))initDetail(view,x,y);
        else if(mode.equals("machine_unavailable"))host.button("重新查询团队目录",x,y+425,312,()->directory(0,"all"));
    }

    void unavailable(String reason){detailLines.clear();detailId="";detailPage=0;unavailable=reason.isBlank()?"这份机器记录当前不可查看。":reason;}

    private void initDirectory(CompoundTag view,int x,int y){
        String filter=filter(view.getString("Filter"));
        List<String> sources=new ArrayList<>();sources.add("all");
        for(Tag raw:view.getList("Sources",Tag.TAG_STRING)){
            String key=raw.getAsString();
            if(key.equals(filter(key))&&!sources.contains(key))sources.add(key);
        }
        int source=sources.indexOf(filter),state=indexOf(STATES,filter);
        host.button("来源："+(source<1?"全部":moduleLabel(sources.get(source)))+" ›",x,y+108,116,
            ()->directory(0,sources.get((Math.max(0,source)+1)%sources.size()))).active=sources.size()>1;
        host.button("状态："+STATE_LABELS[Math.max(0,state)]+" ›",x+122,y+108,110,
            ()->directory(0,STATES[(Math.max(0,state)+1)%STATES.length]));
        host.button("刷新",x+238,y+108,74,()->directory(view.getInt("Page"),filter));
        host.button("全部",x+238,y+140,74,()->directory(0,"all")).active=!filter.equals("all");
        var rows=view.getList("Rows",Tag.TAG_COMPOUND);
        for(int i=0;i<Math.min(PAGE_SIZE,rows.size());i++){
            var row=rows.getCompound(i);String id=validId(row.getString("Id"));
            String stateKey=row.getString("State");
            String stateLabel=row.getString("StateLabel").isBlank()?stateLabel(stateKey):row.getString("StateLabel");
            String location=row.getString("Dimension")+"\nX "+row.getInt("X")+"  Y "+row.getInt("Y")+"  Z "+row.getInt("Z");
            var card=host.widget(new Hk3PhoneAppCard(displayName(row.getString("Title")),location,
                stateLabel+" · "+moduleLabel(row.getString("Module"))+" · 查看详情",x,y+172+i*78,312,73,
                stateColor(stateKey),()->Hk3PhoneScreen.command("hk3phone apps machine "+id+" "+Math.max(0,view.getInt("Page"))+" "+filter)));
            card.active=!id.isEmpty();
        }
        int page=Math.max(0,view.getInt("Page")),last=Math.max(0,(view.getInt("Total")-1)/PAGE_SIZE);
        host.button("登记面前机器",x,y+493,122,()->Hk3PhoneScreen.command("hk3phone apps machines bind"));
        host.button("上一页",x+142,y+493,80,()->directory(page-1,filter)).active=page>0;
        host.button("下一页",x+232,y+493,80,()->directory(page+1,filter)).active=page<last;
    }

    private void initDetail(CompoundTag view,int x,int y){
        String id=validId(view.getString("Id"));
        if(!id.equals(detailId)){detailPage=0;detailId=id;}
        detailLines.clear();
        add(displayName(view.getString("Title")));
        add("状态："+(view.getString("StateLabel").isBlank()?stateLabel(view.getString("State")):view.getString("StateLabel")));
        if(!view.getString("Detail").isBlank())add("诊断："+view.getString("Detail"));
        add("注册 ID："+view.getString("Registry"));
        add("所属模组："+moduleLabel(view.getString("Module")));
        add("控制器类型："+view.getString("ControllerType"));
        add("维度："+view.getString("Dimension"));
        add("位置：X "+view.getInt("X")+"  Y "+view.getInt("Y")+"  Z "+view.getInt("Z"));
        add(view.getBoolean("Loaded")?"区块已加载。":"区块未加载；以下是最后可信记录。");
        add("最后可信记录：存档第 "+Math.max(0,view.getLong("LastObserved"))+" 刻");
        add("此页仅供查看，不改变机器设置。");
        detailPage=Math.max(0,Math.min(detailPage,detailPages()-1));
        host.button("刷新记录",x,y+493,122,()->Hk3PhoneScreen.command("hk3phone apps machine "+id+" "+Math.max(0,view.getInt("Page"))+" "+filter(view.getString("Filter")))).active=!id.isEmpty();
        host.button("上一页",x+142,y+493,80,()->{detailPage--;host.refresh();}).active=detailPage>0;
        host.button("下一页",x+232,y+493,80,()->{detailPage++;host.refresh();}).active=detailPage+1<detailPages();
    }

    void render(GuiGraphics graphics,String mode,CompoundTag view,int x,int y){
        var font=Minecraft.getInstance().font;
        if(mode.equals("machines")){
            String summary=Math.max(0,view.getInt("Total"))+" 台 · "+(Math.max(0,view.getInt("Page"))+1)+" / "+Math.max(1,(view.getInt("Total")+PAGE_SIZE-1)/PAGE_SIZE)+" 页";
            graphics.drawString(font,font.plainSubstrByWidth(summary,228),x,y+146,0xFFB6C8DA,false);
            if(view.getList("Rows",Tag.TAG_COMPOUND).isEmpty()){
                graphics.drawWordWrap(font,Component.literal("当前筛选下没有已登记的团队机器。可切换来源或状态查看其他记录。"),x+10,y+205,290,0xFFB6C8DA);
            }
        }else if(mode.equals("machine_detail")){
            for(int i=0;i<DETAIL_LINES&&detailPage*DETAIL_LINES+i<detailLines.size();i++)
                graphics.drawString(font,detailLines.get(detailPage*DETAIL_LINES+i),x+8,y+111+i*13,i==0&&detailPage==0?0xFFE8C673:0xFFBBC4D3,false);
            graphics.drawString(font,"详情 "+(detailPage+1)+" / "+detailPages(),x,y+476,0xFFB6C8DA,false);
        }else if(mode.equals("machine_unavailable")){
            graphics.drawWordWrap(font,Component.literal(unavailable),x+10,y+137,290,0xFFE7BE71);
        }
    }

    static void directory(int page,String filter){Hk3PhoneScreen.command("hk3phone apps machines "+Math.max(0,page)+" "+filter(filter));}
    static String filter(String raw){return raw!=null&&raw.matches("[a-z0-9_.-]{1,64}")?raw:"all";}
    private static String validId(String raw){try{return UUID.fromString(raw).toString();}catch(IllegalArgumentException ignored){return "";}}
    private static int indexOf(String[] values,String value){for(int i=0;i<values.length;i++)if(values[i].equals(value))return i;return -1;}
    private static String stateLabel(String key){int index=indexOf(STATES,key);return index>0?STATE_LABELS[index]:"未知";}
    private static String moduleLabel(String key){int index=indexOf(SOURCES,key);return index>0?SOURCE_LABELS[index]:key;}
    private static String displayName(String value){return Component.translatable(value).getString();}
    private int detailPages(){return Math.max(1,(detailLines.size()+DETAIL_LINES-1)/DETAIL_LINES);}
    private void add(String text){detailLines.addAll(Minecraft.getInstance().font.split(Component.literal(text),296));detailLines.add(FormattedCharSequence.EMPTY);}
    private static int stateColor(String key){return switch(key){
        case "running"->0xFF83D8A6;
        case "need_energy","need_input"->0xFFE7BE71;
        case "unformed"->0xFFE29598;
        case "unloaded","stopped"->0xFFA6BAD2;
        default->0xFFB7A7D8;
    };}
}
