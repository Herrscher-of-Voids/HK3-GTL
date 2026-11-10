package com.sirin.hk3gtl.client.phone;


import com.sirin.hk3gtl.common.phone.*;
import com.sirin.hk3gtl.common.network.Hk3Network;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.EditBox;
import net.minecraft.nbt.*;
import net.minecraft.network.chat.Component;
import net.minecraft.util.FormattedCharSequence;
import java.util.*;

/** 【变更记录 #1】2026-09-30 19:56:03（修订116）：删除无；新增同屏联系人、分页聊天、朋友圈和API设置；修改无；用途：离线/AI发送明确分开，个人AI记录仅会话内存，断线清空，布局不侵入导航。 */
/** 【变更记录 #2】2026-09-30 20:41:09（修订118）：删除无；新增固定档案和拦截说明；修改聊天副标题及既有AI配置说明；用途：沿用同一手机布局，明确请求内容与无自动重试。 */
/**
 * 【变更记录 #3】2026-10-01 22:09:06（第3次备注 · 内测5修订154）
 * 删除：跨接口自动复用Key的行为。新增：配置边界核验或对应提示/回归。
 * 修改：Key输入框提示明确同接口可留空、更换地址须重填，不修改界面布局。
 * 用途：收尾微讯息通信生命周期，不涉及结构、贴图与任务。
 */
/** 【变更记录 #4】2026-10-01 22:50:14（第4次备注 · 内测5修订155）：删除玩家展示中的旧电压及开发说明；新增现行正文投影或对应回归；修改仅限呈现与检索，不改变进度、回执、触发条件或权限；用途：统一发布版玩家文案，历史备注保留。 */
/** 【变更记录 #5】2026-11-05 22:19:02（修订211）：删除无；新增联系人内置话题和欢迎消息按钮、显式停用AI意图；修改聊天文本避开新按钮；用途：提供真实可用入口，不上传API密钥。 */
final class Hk3SocialPane {
    private final Hk3PhoneScreen screen;
    private CompoundTag view=new CompoundTag();private int page;private String status="",draft="",lastContact="";
    private EditBox input,address,model,key;private final List<FormattedCharSequence> lines=new ArrayList<>();
    private static final Map<String,List<Hk3SocialTranscript.Entry>> AI=new HashMap<>();
    private static final int PAGE_LINES=18;
    Hk3SocialPane(Hk3PhoneScreen screen){this.screen=screen;}
    static void reset(){Hk3SocialAiClient.reset();AI.clear();}
    private net.minecraft.client.gui.Font font(){return Minecraft.getInstance().font;}
    private void send(String action,String contact,String text){Hk3Network.CHANNEL.sendToServer(new Hk3SocialPacket(action,contact,text,view.getBoolean("Preview")));}
    void accept(CompoundTag next){
        if(!next.getString("Mode").startsWith("social"))return;
        if(!next.getString("Contact").equals(lastContact)){draft="";page=0;}
        if(next.getString("Mode").equals("social_chat"))page=Integer.MAX_VALUE;
        if(next.contains("Accepted")&&draft.equals(next.getString("Accepted")))draft="";
        lastContact=next.getString("Contact");view=next.copy();status=next.getString("Status");
    }
    void back(){if(screen.mode().equals("social_topics")){send("chat",view.getString("Contact"),"");return;}if(screen.mode().equals("social_chat")||screen.mode().equals("social_feed")||screen.mode().equals("social_ai"))send("list","","");else Hk3PhoneScreen.command("hk3phone");}
    void init(String mode,CompoundTag data,int x,int y){
        input=null;address=null;model=null;key=null;
        if(!mode.startsWith("social"))return;
        if(!mode.equals("social_ai"))view=data.copy();
        if(mode.equals("social")){
            screen.button("联系人",x,y+108,96,()->send("list","",""));screen.button("朋友圈",x+108,y+108,96,()->send("feed","",""));screen.button("AI 设置",x+216,y+108,96,()->screen.local("social_ai"));
            var rows=view.getList("Rows",Tag.TAG_COMPOUND);page=Math.max(0,Math.min(page,Math.max(0,(rows.size()-1)/6)));
            for(int i=0;i<6&&page*6+i<rows.size();i++){
                var row=rows.getCompound(page*6+i);String id=row.getString("Id");
                screen.widget(new Hk3PhoneAppCard(row.getString("Name"),row.getBoolean("Active")?"点击打开对话":"暂不可联系 · 可回看记录","",x,y+149+i*53,312,48,0xFF8DDFC0,()->send("chat",id,"")));
            }
            pages(x,y+490,Math.max(1,(rows.size()+5)/6));
        }else if(mode.equals("social_chat")){
            screen.button("内置话题",x,y+145,148,()->send("topics",view.getString("Contact"),"")).active=view.getBoolean("Active");
            screen.button("欢迎消息",x+164,y+145,148,()->send("welcome",view.getString("Contact"),"")).active=view.getBoolean("Active");
            composeLines();pages(x,y+424,Math.max(1,(lines.size()+PAGE_LINES-1)/PAGE_LINES));
            input=edit(x,y+460,312,512,"输入话题：研究、休息、日常……",draft);input.setResponder(s->draft=s);
            screen.button("发送（离线）",x,y+493,148,()->{
                if(!Hk3SocialCatalog.validInput(draft)){status="请输入1至512字的普通文本。";return;}
                send("send",view.getString("Contact"),draft);
            }).active=view.getBoolean("Active");
            screen.button(Hk3SocialAiClient.busy()?"AI 请求中…":"AI 发送（自费）",x+164,y+493,148,this::aiSend).active=view.getBoolean("Active")&&!Hk3SocialAiClient.busy();
        }else if(mode.equals("social_topics")){
            var rows=view.getList("Rows",Tag.TAG_COMPOUND);
            for(int i=0;i<rows.size();i++){String text=rows.getCompound(i).getString("Text");screen.button(text,x,y+160+i*54,312,()->send("topic",view.getString("Contact"),text));}
        }else if(mode.equals("social_feed")){
            var rows=view.getList("Rows",Tag.TAG_COMPOUND);page=Math.max(0,Math.min(page,Math.max(0,(rows.size()-1)/2)));
            for(int i=0;i<2&&page*2+i<rows.size();i++){
                var row=rows.getCompound(rows.size()-1-page*2-i);String id=row.getString("Id");
                screen.button(row.getBoolean("Liked")?"已赞 · 取消":"赞",x+223,y+240+i*171,89,()->send("like",id,""));
            }pages(x,y+490,Math.max(1,(rows.size()+1)/2));
        }else if(mode.equals("social_ai")){
            address=edit(x,y+151,312,512,"https://服务地址/v1",Hk3SocialAiClient.endpoint());
            model=edit(x,y+211,312,128,"填写服务支持的模型名",Hk3SocialAiClient.model());
            key=edit(x,y+271,312,2048,Hk3SocialAiClient.configured()?"同一接口留空保留；换地址须重填":"填写自己的 API Key","");
            key.setFormatter((s,pos)->FormattedCharSequence.forward("•".repeat(s.length()),net.minecraft.network.chat.Style.EMPTY));
            screen.button("保存到本次连接",x,y+319,148,()->{
                status=Hk3SocialAiClient.configure(address.getValue(),model.getValue(),key.getValue());
                if(status.isEmpty()){send("enable_ai","","");status="已保存；普通发送仍走离线对话。";key.setValue("");}
            });
            screen.button("清除 Key / 停用",x+164,y+319,148,()->{boolean enabled=Hk3SocialAiClient.configured();Hk3SocialAiClient.reset();if(enabled)send("disable_ai","","");key.setValue("");status="已清除；进行中的结果将被忽略。";});
        }
    }
    private EditBox edit(int x,int y,int width,int max,String hint,String value){var e=screen.widget(new EditBox(font(),x,y,width,24,Component.literal(hint)));e.setMaxLength(max);e.setHint(Component.literal(hint));e.setValue(value);return e;}
    private void pages(int x,int y,int count){page=Math.max(0,Math.min(page,count-1));screen.button("上一页",x+142,y,80,()->{page--;screen.refresh();}).active=page>0;screen.button("下一页",x+232,y,80,()->{page++;screen.refresh();}).active=page<count-1;}
    private void add(String text){lines.addAll(font().split(Component.literal(text),292));lines.add(FormattedCharSequence.EMPTY);}
    private List<Hk3SocialTranscript.Entry> transcript(){
        var offline=new ArrayList<Hk3SocialTranscript.Entry>();
        for(Tag raw:view.getList("Rows",Tag.TAG_COMPOUND)){var n=(CompoundTag)raw;String who=n.getString("Who");offline.add(new Hk3SocialTranscript.Entry(who,n.getString("Body"),who.equals("我"),false,n.getLong("Time")));}
        return Hk3SocialTranscript.merge(offline,AI.getOrDefault(view.getString("Contact"),List.of()));
    }
    private void composeLines(){
        lines.clear();for(var m:transcript())add(m.speaker()+(m.ai()?(m.user()?" [AI会话]":" [AI生成]"):"")+"："+m.text());
        if(lines.isEmpty())add("对话已准备好。可以先说声你好，或聊聊研究、选择与休息。\n离线记录保存最近200条；AI会话仅保留本次连接。");
    }
    private void aiSend(){
        if(!screen.powered()||!view.getBoolean("Active"))return;
        if(!Hk3SocialAiClient.configured()){status="请先在联系人页打开 AI 设置。";return;}
        if(!Hk3SocialCatalog.validInput(draft)){status="请输入1至512字的普通文本。";return;}
        String id=view.getString("Contact"),message=draft;var c=Hk3SocialCatalog.get(id);if(c==null||Hk3SocialAiClient.busy())return;
        var history=Hk3SocialTranscript.context(transcript());int epoch=Hk3SocialAiClient.epoch();
        var future=Hk3SocialAiClient.send(c,message,history);
        var local=AI.computeIfAbsent(id,k->new ArrayList<>());local.add(new Hk3SocialTranscript.Entry("我",message,true,true,clock()));while(local.size()>40)local.remove(0);
        draft="";page=Integer.MAX_VALUE;status="已发送给你配置的服务；等待回复…";screen.refresh();
        future.thenAccept(result->Minecraft.getInstance().execute(()->{
            if(epoch!=Hk3SocialAiClient.epoch()||Minecraft.getInstance().player==null)return;
            if(result.ok()){
                var list=AI.computeIfAbsent(id,k->new ArrayList<>());list.add(new Hk3SocialTranscript.Entry(c.name(),result.text(),false,true,clock()));while(list.size()>40)list.remove(0);
                if(lastContact.equals(id)){page=Integer.MAX_VALUE;status="AI回复仅供闲聊；不影响游戏进度。";}
            }else if(lastContact.equals(id)){status=result.error();if(draft.isEmpty())draft=message;}
            if(Minecraft.getInstance().screen==screen)screen.refresh();
            else if(Minecraft.getInstance().screen instanceof Hk3PhoneScreen current)current.refreshSocial();
        }));
    }
    private long clock(){var level=Minecraft.getInstance().level;return level==null?0:level.getGameTime();}
    void tick(){if(input!=null)input.tick();if(address!=null)address.tick();if(model!=null)model.tick();if(key!=null)key.tick();}
    void render(GuiGraphics g,String mode,int x,int y){
        if(!mode.startsWith("social"))return;
        var font=font();
        if(mode.equals("social")){
            if(view.getList("Rows",Tag.TAG_COMPOUND).isEmpty())g.drawWordWrap(font,Component.literal("收到主线观察资料后，将建立第一批联系人。后续联系人按真实审查阶段开放。"),x+8,y+175,292,Hk3PhoneStyle.INK);
            g.drawString(font,"第 "+(page+1)+" 页",x,y+499,Hk3PhoneStyle.MUTED,false);
            g.drawString(font,view.getBoolean("Preview")?"管理员正文预览 · 不建档、不解锁":"离线对话可直接使用 · AI可选",x,y+530,Hk3PhoneStyle.MUTED,false);
        }else if(mode.equals("social_chat")){
            g.drawString(font,font.plainSubstrByWidth(view.getString("Name"),312),x,y+110,Hk3PhoneStyle.GOLD,false);
            g.drawString(font,view.getBoolean("Preview")?"只读预览":view.getBoolean("Active")?"固定角色档案 · 远程通信":"联系人暂不可用 · 历史只读",x,y+130,Hk3PhoneStyle.MUTED,false);
            screen.clip(g,x,y+180,x+312,y+414);
            for(int i=0;i<PAGE_LINES&&page*PAGE_LINES+i<lines.size();i++)g.drawString(font,lines.get(page*PAGE_LINES+i),x+8,y+181+i*13,Hk3PhoneStyle.INK,false);
            g.disableScissor();g.drawString(font,"第 "+(page+1)+" / "+Math.max(1,(lines.size()+PAGE_LINES-1)/PAGE_LINES)+" 页",x,y+433,Hk3PhoneStyle.MUTED,false);
         }else if(mode.equals("social_topics")){
            g.drawString(font,font.plainSubstrByWidth(view.getString("Name")+" · 内置话题",312),x,y+120,Hk3PhoneStyle.GOLD,false);
        }else if(mode.equals("social_feed")){
            var rows=view.getList("Rows",Tag.TAG_COMPOUND);if(rows.isEmpty())g.drawString(font,"暂时还没有动态",x+8,y+155,Hk3PhoneStyle.MUTED,false);
            for(int i=0;i<2&&page*2+i<rows.size();i++){
                var n=rows.getCompound(rows.size()-1-page*2-i);var c=Hk3SocialCatalog.get(n.getString("Contact"));if(c==null)continue;int top=y+113+i*171;
                g.fill(x,top,x+312,top+161,0xFF222B40);g.drawString(font,font.plainSubstrByWidth(c.name(),294),x+9,top+10,Hk3PhoneStyle.GOLD,false);
                g.drawString(font,"第 "+n.getLong("Day")+" 天",x+9,top+28,Hk3PhoneStyle.MUTED,false);
                screen.clip(g,x+9,top+47,x+302,top+115);g.drawWordWrap(font,Component.literal(n.getString("Body")),x+9,top+47,288,Hk3PhoneStyle.INK);g.disableScissor();
            }g.drawString(font,"第 "+(page+1)+" 页",x,y+499,Hk3PhoneStyle.MUTED,false);
            g.drawString(font,"每游戏日最多2条 · 最近120条",x,y+530,Hk3PhoneStyle.MUTED,false);
        }else if(mode.equals("social_ai")){
            g.drawString(font,"接口地址（兼容 Chat Completions）",x,y+131,Hk3PhoneStyle.INK,false);g.drawString(font,"模型",x,y+192,Hk3PhoneStyle.INK,false);g.drawString(font,"个人 API Key（仅本次连接内存）",x,y+252,Hk3PhoneStyle.INK,false);
            g.drawWordWrap(font,Component.literal("只有点击“AI发送”才调用，费用由你配置的服务收取。每次发送当前角色的固定档案、输入和最近8条消息。明显出戏回复会拦截，不自动重试。\n\nKey不发给游戏服务器，退出存档后清除；不自动重试。普通发送、朋友圈无需API。AI生成内容不授予奖励或推进剧情。\n\n支持HTTPS；本机服务可用HTTP。填写服务的/v1基础地址或完整/chat/completions地址。"),x+4,y+360,304,Hk3PhoneStyle.MUTED);
        }
        if(!status.isEmpty()){
            g.fill(x,y+520,x+312,y+550,0xFF192133);screen.clip(g,x,y+520,x+312,y+550);g.drawWordWrap(font,Component.literal(status),x+3,y+523,306,Hk3PhoneStyle.GOLD);g.disableScissor();
        }
    }
}
