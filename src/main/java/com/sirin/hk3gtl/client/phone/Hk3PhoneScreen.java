package com.sirin.hk3gtl.client.phone;









import com.sirin.hk3gtl.client.gui.Hk3FittedScreen;
import com.sirin.hk3gtl.common.phone.Hk3PhoneConfig;
import com.sirin.hk3gtl.common.phone.Hk3NotificationQueue;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.nbt.*;
import net.minecraft.network.chat.Component;
import net.minecraft.util.FormattedCharSequence;
import java.util.*;



public final class Hk3PhoneScreen extends Hk3FittedScreen {
    private static final Hk3NotificationQueue TOASTS=new Hk3NotificationQueue();
    private static List<Hk3NotificationQueue.Card> previous=List.of();
    private static boolean installed;
    private static CompoundTag runtime=new CompoundTag();
    private CompoundTag view;
    private final List<FormattedCharSequence> lines=new ArrayList<>();
    private final Hk3PhoneSettingsPane settings=new Hk3PhoneSettingsPane();
    private final Hk3GazeSettingsPane gazeSettings=new Hk3GazeSettingsPane();
    private final Hk3PhoneDesktop desktop=new Hk3PhoneDesktop();
    private final Hk3PhoneGalleryPane gallery=new Hk3PhoneGalleryPane();
    private final Hk3PhoneExtraApps extras=new Hk3PhoneExtraApps(this);
    private final Hk3SocialPane social=new Hk3SocialPane(this);
    private net.minecraft.client.gui.components.EditBox search;
    private String query="";
    private static final int BODY_WIDTH=348,BODY_HEIGHT=608,BEZEL=3,PER_PAGE=12;
    private static final float READING_SCALE=1.5F;
    private int page,x,y,cx,pollTicks;
    private final Hk3EggReadClient eggReading=new Hk3EggReadClient();
    private String lastFilter="all",lastArchiveFilter="all";private int lastInboxPage,lastArchivePage;
    private Hk3PhoneScreen(CompoundTag view){super(Component.literal("HK3GTL · 手机"),380,640);this.view=view.copy();desktop.accept(view);gallery.accept(view);}
    public static void reset(){Hk3SocialPane.reset();Hk3PhoneCipherPane.reset();TOASTS.clear();previous=List.of();installed=false;runtime=new CompoundTag();}
    public static void open(CompoundTag view){
        if(view.getString("Mode").equals("read_complete")){
            if(view.hasUUID("ReadToken")&&Minecraft.getInstance().screen instanceof Hk3PhoneScreen phone){phone.eggReading.confirm(view.getUUID("ReadToken"));phone.initFitted();}
            return;
        }
        if(view.contains("Runtime"))runtime=view.getCompound("Runtime").copy();
        if(view.getString("Mode").equals("status"))return;
        if(view.getString("Mode").equals("toast")){
            installed=view.getBoolean("Installed");
            if(!view.getString("Kind").equals("chatter")||Hk3PhoneConfig.CHATTER.get())
                TOASTS.offer(new Hk3NotificationQueue.Notice(view.getString("Id"),view.getString("Title"),view.getString("Body"),view.getString("Kind"),view.getInt("Priority")),now());
            return;
        }
        if(!view.getString("Mode").equals("letter"))installed=true;
        var mc=Minecraft.getInstance();
        if(mc.screen instanceof Hk3PhoneScreen phone){if(phone.extras.accept(view))return;phone.social.accept(view);phone.gallery.accept(view);phone.view=view.copy();phone.desktop.accept(view);phone.page=0;phone.initFitted();}
        else if(!view.getString("Mode").equals("app_error")&&!view.getString("Mode").equals("note_saved")){var phone=new Hk3PhoneScreen(view);phone.extras.accept(view);phone.social.accept(view);mc.setScreen(phone);}
        String id=view.getString("Id");
        if((view.getString("Mode").equals("detail")||view.getString("Mode").equals("diplomacy_read")||view.getString("Mode").equals("letter"))&&!id.isEmpty())command("hk3phone seen "+id);
    }
    public static void openLetter(int document,String state,CompoundTag context){
        if(document<0||document>5)return;
        String[] keys={"A01","A02","A03","A04","A05","A06"};
        var entry=com.sirin.hk3gtl.common.narrative.Hk3ApprovedProse.get("communication."+keys[document]);
        var body=new StringBuilder();
        for(int i=0;i<entry.lineCount();i++){if(i>0)body.append("\n\n");body.append(Component.translatable(entry.key()+".line."+i).getString());}
        var n=context.copy();n.putString("Mode","letter");n.putInt("Document",document);n.putString("State",state);
        n.putString("Title",Component.translatable(entry.key()+".title").getString());n.putString("Body",body.toString());
        n.putString("Id",context.getString("MessageId"));
        if(context.getInt("SupplementStep")>0)n.putString("Body","个人补谈第 "+context.getInt("SupplementStep")+" / "+context.getInt("SupplementTotal")+" 步：保留本队原决定，不重发奖励。阅读后亲自确认继续。\n\n"+n.getString("Body"));
        if(context.getBoolean("HistoryOnly"))n.putString("Body","原队往来历史 · 仅供回看，不算当前团队决定或个人补谈。\n\n"+n.getString("Body"));
        if(context.contains("ReadCanonical"))n.putString("Body",context.getString("ReadCanonical"));
        open(n);
    }
    private static long now(){return System.nanoTime()/1_000_000L;}
    static void command(String cmd){var c=Minecraft.getInstance().getConnection();if(c!=null)c.sendCommand(cmd);}
    boolean powered(){return !outOfPower();}
    private boolean outOfPower(){return !mode().equals("letter")&&installed&&(!runtime.getBoolean("Present")||runtime.getLong("Charge")<8);}
    Button button(String title,int bx,int by,int w,Runnable action){
        String label=font.width(title)>w-14?font.plainSubstrByWidth(title,Math.max(1,w-24))+"…":title;
        return addRenderableWidget(Hk3PhoneStyle.button(label,bx,by,w,26,action));
    }
    private void inbox(String filter,int index){lastFilter=filter;lastInboxPage=index;command(query.isBlank()?"hk3phone notifications "+filter+" "+index:"hk3phone search "+filter+" "+index+" "+query);}
    private boolean reading(){return mode().equals("detail")||mode().equals("letter")||mode().equals("archive_detail")||mode().equals("instruction_read")||mode().equals("diplomacy_read");}
    String mode(){return view.getString("Mode");}
    void clip(GuiGraphics g,int x1,int y1,int x2,int y2){fittedScissor(g,x1,y1,x2,y2);}
    void refresh(){initFitted();}
    void refreshSocial(){if(mode().startsWith("social")&&!mode().equals("social_ai"))initFitted();}
    <T extends net.minecraft.client.gui.components.AbstractWidget> T widget(T widget){return addRenderableWidget(widget);}
    void local(String mode){Hk3EggUiClient.send("open",mode);var n=new CompoundTag();n.putString("Mode",mode);view=n;page=0;initFitted();}
    private void app(String id){
        if(outOfPower()&&!id.equals("settings"))return;
        desktop.launch(id);
        switch(id){
            case "social"->command("hk3phone social");
            case "cipher"->command("hk3phone apps cipher");
            case "inbox"->inbox("all",0);case "letters"->command("hk3letter diplomacy");case "ae"->command("hk3phone ae");
            case "notes"->command("hk3phone apps notes");case "civilization"->command("hk3phone apps civilization");
            case "trade","tiles2048","snake"->local(id);
            case "updates"->command("hk3updates");case "settings"->local("settings");
            case "quiet"->{TOASTS.clear();previous=List.of();}
        }
    }
    @Override protected double fittedScale(int realWidth,int realHeight){
        return Hk3PhoneConfig.PHONE_SIZE.get()/100.0*Math.min((double)realWidth/(BODY_WIDTH+2*BEZEL),
                (double)realHeight/(BODY_HEIGHT+2*BEZEL));
    }
    @Override protected void initFitted(){
        if(mode().equals("archive")){lastArchiveFilter=view.getString("Filter");lastArchivePage=view.getInt("Page");}
        clearWidgets();search=null;x=(width-BODY_WIDTH)/2;y=(height-BODY_HEIGHT)/2;cx=x+18;String mode=view.getString("Mode");
        button("返回",cx,y+558,92,()->extras.navigate(()->{
            gallery.close();
            if(mode.equals("instruction_read"))eggReading.leaveInstruction(view);
            if(mode.equals("gallery"))command("hk3phone apps civilization");
            else if(mode.startsWith("social"))social.back();
            else if(mode.equals("machine_detail"))Hk3MachineOverviewPane.directory(view.getInt("Page"),view.getString("Filter"));
            else if(mode.equals("machines")||mode.equals("machine_unavailable"))command("hk3phone apps civilization");
            else if(mode.equals("archive_detail")&&view.getBoolean("CivilizationRead"))command("hk3phone apps civilization");
            else if(mode.equals("archive_detail")&&view.getBoolean("NoteRead"))command("hk3phone apps note "+view.getString("NoteId"));
            else if(mode.equals("instruction_read"))command(view.getBoolean("VoltagePage")?"hk3phone apps voltages":"hk3phone apps instructions");
            else if(mode.equals("archive_detail"))command("hk3phone apps archive "+lastArchivePage+" "+lastArchiveFilter);
            else if(mode.equals("archive")||mode.equals("civilization_milestones")||mode.equals("voltage_catalog")||mode.equals("instructions"))command("hk3phone apps civilization");
            else if(mode.equals("note")||mode.equals("todos"))command("hk3phone apps notes");
            else if(mode.equals("notification_settings")||mode.equals("gaze_settings")||mode.equals("about"))local("settings");
            else if(view.getBoolean("Story")&&mode.equals("diplomacy_read"))command("hk3phone apps story");
            else if(view.getBoolean("Story"))command("hk3phone apps civilization");
            else if(!view.getString("ProgressStage").isEmpty())command("hk3letter progress");
            else if(mode.startsWith("diplomacy"))command("hk3letter diplomacy");
            else if(reading())inbox(lastFilter,lastInboxPage);else command("hk3phone");
        }));
        button("桌面",cx+110,y+558,92,()->extras.navigate(()->{gallery.close();if(mode.equals("instruction_read"))eggReading.leaveInstruction(view);command("hk3phone");}));
        button("息屏",cx+220,y+558,92,this::onClose);
        if(mode.equals("home")){
            desktop.layout(cx,y+257);
            addRenderableWidget(Hk3PhoneStyle.button(Component.translatable("hk3gtl.phone.date.open").getString(),cx+190,y+109,122,26,()->command("hk3phone apps date")));
            button("上一页",cx+142,y+493,80,()->{desktop.turn(-1);initFitted();}).active=desktop.page()>0;
            button("下一页",cx+232,y+493,80,()->{desktop.turn(1);initFitted();}).active=desktop.page()+1<desktop.pages();
        }else if(mode.equals("settings")){
            widget(new Hk3PhoneAppCard("关于手机","电量、安装与充电","终端状态  ›",cx,y+115,312,69,0xFFB3C9DE,()->local("about")));
            widget(new Hk3PhoneAppCard("通知与显示","拖动位置 · 提示音 · 闲话提醒","个性化  ›",cx,y+193,312,69,0xFFBEA9EE,()->local("notification_settings")));
            widget(new Hk3PhoneAppCard("注视度 HUD","拖动位置 · 缩放 · 避让其他界面","位置预览  ›",cx,y+271,312,69,0xFF87D6E9,()->local("gaze_settings")));
            widget(new Hk3PhoneAppCard("AE 设备互联","携带已绑定且有电的无线终端","打开 AE 终端  ›",cx,y+349,312,69,0xFF8DDFC0,()->command("hk3phone ae")));
            widget(new Hk3PhoneAppCard("更新详情","查看本次内测更新","版本记录  ›",cx,y+427,312,69,0xFFE8C673,()->command("hk3updates")));
            int size=Hk3PhoneConfig.PHONE_SIZE.get();
            button(Component.translatable("hk3gtl.phone.bodySize",size).getString(),cx,y+505,312,()->{
                Hk3PhoneConfig.PHONE_SIZE.set(size<72?72:size<86?86:60);Hk3PhoneConfig.SPEC.save();init();
            });
        }else if(mode.equals("gaze_settings")){
            gazeSettings.layout(cx,y+157,312);widget(Hk3GazeSettingsPane.slider(cx,y+388));
            button("恢复默认位置与大小",cx,y+438,312,()->{Hk3PhoneConfig.GAZE_X.set(-1.0);Hk3PhoneConfig.GAZE_Y.set(-1.0);Hk3PhoneConfig.GAZE_SCALE.set(1.0);Hk3PhoneConfig.SPEC.save();initFitted();});
        }else if(mode.equals("notification_settings")){
            settings.layout(cx,y+152,312);
            addRenderableWidget(Hk3PhoneSettingsPane.scaleSlider(cx,y+359,312));
            button("声音："+(Hk3PhoneConfig.SOUND.get()?"开":"关"),cx,y+404,148,()->{
                Hk3PhoneConfig.SOUND.set(!Hk3PhoneConfig.SOUND.get());Hk3PhoneConfig.SPEC.save();initFitted();
            });
            button("闲话："+(Hk3PhoneConfig.CHATTER.get()?"提醒":"静默"),cx+164,y+404,148,()->{
                Hk3PhoneConfig.CHATTER.set(!Hk3PhoneConfig.CHATTER.get());Hk3PhoneConfig.SPEC.save();initFitted();
            });
            button("恢复默认通知位置",cx,y+450,312,()->{
                Hk3PhoneConfig.POSITION_X.set(-1.0);Hk3PhoneConfig.POSITION_Y.set(-1.0);
                Hk3PhoneConfig.RIGHT.set(true);Hk3PhoneConfig.MARGIN.set(12);Hk3PhoneConfig.TOP.set(24);Hk3PhoneConfig.SCALE.set(1.0);
                Hk3PhoneConfig.SPEC.save();initFitted();
            });
        }else if(reading()){
            lines.clear();
            for(String paragraph:view.getString("Body").split("\n",-1)){
                if(paragraph.isEmpty())lines.add(FormattedCharSequence.EMPTY);else lines.addAll(font.split(Component.literal(paragraph),(int)(292/READING_SCALE)));
            }
            page=com.sirin.hk3gtl.common.phone.Hk3PhoneLayout.page(page,lines.size(),PER_PAGE);
            button("上一页",cx+142,y+389,80,()->{page--;initFitted();}).active=page>0;
            button("下一页",cx+232,y+389,80,()->{page++;initFitted();}).active=page+1<pageCount();
            if(view.getBoolean("NoteRead")){
                if(view.getInt("NotePage")+1<view.getInt("NoteTotal"))button("手动翻至下一段",cx,y+439,312,()->command("hk3phone apps notenext "+view.getString("Token"))).active=page+1==pageCount()&&eggReading.complete(view);
            }else if(view.getBoolean("CollectionExplanation"))button("主动收藏这条说明",cx,y+439,312,()->command("hk3phone apps collect "+view.getString("Token"))).active=page+1==pageCount()&&eggReading.complete(view);
            if(mode.equals("letter"))letterActions();
            if(mode.equals("diplomacy_read")&&!view.getString("Topic").isEmpty())button("查看本主题与答复",cx,y+440,312,()->command("hk3letter diplomacy topic "+view.getString("Topic")));
            if(mode.equals("diplomacy_read")&&!view.getString("Token").isEmpty())button(view.getBoolean("PersonalSupplement")?"已阅读，确认本步补谈":"确认发送这份回信",cx,y+479,312,()->command("hk3letter diplomacy "+(view.getBoolean("PersonalSupplement")?"continue ":"confirm ")+view.getString("Token"))).active=!view.getBoolean("PersonalSupplement")||page+1==pageCount()&&eggReading.complete(view);
            if(mode.equals("diplomacy_read")&&!view.getString("Token").isEmpty()&&!view.getBoolean("PersonalSupplement"))button("稍后处理",cx,y+516,312,()->command("hk3letter diplomacy defer"));
            if(mode.equals("diplomacy_read")&&view.getBoolean("ReadOnly")&&(view.getString("ProgressStage").isEmpty()||view.getBoolean("ProgressPreview")))button("只读：由队长或授权成员确认",cx,y+479,312,()->{}).active=false;
            if(mode.equals("diplomacy_read")){
                int row=0;for(Tag raw:view.getList("Actions",Tag.TAG_COMPOUND)){var action=(CompoundTag)raw;button(action.getString("Title"),cx,y+440+row++*39,312,()->command(action.getString("Command")));}
                if(view.getBoolean("ProgressPreview")&&!view.getString("ProgressToken").isEmpty())button("确认发送这封回信",cx,y+479,312,()->command("hk3letter progress reply "+view.getString("ProgressStage")+" "+view.getInt("ProgressChoice")+" "+view.getString("ProgressToken")));
            }
        }else if(mode.equals("diplomacy")){
            int row=0;for(Tag raw:view.getList("Actions",Tag.TAG_COMPOUND)){var action=(CompoundTag)raw;button(action.getString("Title"),cx,y+202+row++*43,312,()->command(action.getString("Command")));}
        }else if(mode.equals("notifications")){
            lastFilter=view.getString("Filter");lastInboxPage=view.getInt("Page");query=view.getString("Query");int j=0;
            search=widget(new net.minecraft.client.gui.components.EditBox(font,cx+4,y+107,230,23,Component.literal("搜索讯息标题和正文")));
            search.setMaxLength(64);search.setHint(Component.literal("搜索讯息"));search.setValue(query);
            button("搜索",cx+244,y+105,68,()->{query=search.getValue().strip();inbox(lastFilter,0);});
            for(String filter:new String[]{"all","unread","pending"}){
                String name=filter.equals("all")?"全部":filter.equals("unread")?"未读":"待处理";
                button((lastFilter.equals(filter)?"• ":"")+name,cx+j++*106,y+140,100,()->inbox(filter,0));
            }
            int i=0;
            for(Tag raw:view.getList("Rows",Tag.TAG_COMPOUND)){
                var row=(CompoundTag)raw;
                String label=(row.getBoolean("Read")?"":"● ")+(row.getBoolean("Pending")?"[待处理] ":"")+row.getString("Title");
                widget(new Hk3PhoneAppCard(label,row.getString("Preview"),"",cx,y+177+i++*38,312,35,row.getBoolean("Read")?0xFF758398:0xFF94C5F8,()->command("hk3phone message "+row.getString("Id"))));
            }
            int last=Math.max(0,(view.getInt("Total")-1)/8);
            button("上一页",cx+142,y+493,80,()->inbox(lastFilter,lastInboxPage-1)).active=lastInboxPage>0;
            button("下一页",cx+232,y+493,80,()->inbox(lastFilter,lastInboxPage+1)).active=lastInboxPage<last;
        }
        if(mode.equals("gallery"))gallery.init(this,cx,y);
        extras.init(mode,view,cx,y);social.init(mode,view,cx,y);
    }
    private void letterActions(){
        int doc=view.getInt("Document");String state=view.getString("State");
        boolean canReply=state.equals("READ"),replied=state.equals("ACCEPTED")||state.equals("DECLINED");
        if(view.getBoolean("HistoryOnly"))return;
        if(view.getInt("SupplementStep")>0){
            button(view.getInt("SupplementStep")==view.getInt("SupplementTotal")?"确认完成本次个人交流":"已阅读，继续个人补谈",cx,y+479,312,()->command("hk3letter continue "+view.getString("Token"))).active=page+1==pageCount()&&eggReading.complete(view);return;
        }
        if(doc==0){
            if(replied)button(view.getBoolean("PersonalDone")?"个人交流已完成":"亲自补行本队首次交流",cx,y+516,312,()->command("hk3letter supplement")).active=!view.getBoolean("PersonalDone");
            button("观测资料附件",cx,y+440,312,()->command("hk3letter view 3"));
            if(canReply){
                button("预览接受回信",cx,y+479,148,()->command("hk3letter view 1"));
                button("预览拒绝回信",cx+164,y+479,148,()->command("hk3letter view 2"));
            }else if(replied){
                button("已发送回信",cx,y+479,148,()->command("hk3letter view "+(state.equals("ACCEPTED")?1:2)));
                button("奥托后续来信",cx+164,y+479,148,()->command("hk3letter view "+(state.equals("ACCEPTED")?4:5)));
            }
        }else{
            button("返回原信",cx,y+440,312,()->command("hk3letter"));
            if(canReply&&(doc==1||doc==2))button(view.getBoolean("CanDecide")?"确认发送这封回信":"只读：由队长或授权成员确认",cx,y+479,312,()->command((doc==1?"hk3letter accept ":"hk3letter decline ")+view.getString("Token"))).active=view.getBoolean("CanDecide")&&!view.getString("Token").isEmpty();
            if(replied){
                button("持续来信与研究往来",cx,y+479,312,()->command("hk3letter progress"));
                button("五方联络与成果公开",cx,y+516,312,()->command("hk3letter diplomacy"));
            }
        }
    }
    private int pageCount(){return com.sirin.hk3gtl.common.phone.Hk3PhoneLayout.pages(lines.size(),PER_PAGE);}
    private void round(GuiGraphics g,int left,int top,int w,int h,int color,int r){
        for(int row=0;row<h;row++){
            int edge=Math.min(row,h-1-row),inset=edge>=r?0:(int)Math.ceil(r-Math.sqrt(Math.max(0,r*r-(r-edge)*(r-edge))));
            g.fill(left+inset,top+row,left+w-inset,top+row+1,color);
        }
    }
    private String clock(){long minute=Math.floorMod(runtime.getLong("DayTime")+6000,24000)*1440/24000;return String.format(java.util.Locale.ROOT,"%02d:%02d",minute/60,minute%60);}
    private boolean inContent(double mx,double my){return mx>=x+10&&mx<x+338&&my>=y+58&&my<y+BODY_HEIGHT-58;}
    private void renderWidgets(GuiGraphics g,int mx,int my,float delta,boolean navigation){
        for(var child:children())if(child instanceof net.minecraft.client.gui.components.AbstractWidget widget&&(widget.getY()>=y+558)==navigation)widget.render(g,mx,my,delta);
    }
    private void navigation(GuiGraphics g,int mx,int my,float delta){
        renderWidgets(g,mx,my,delta,true);
        g.fill(x+141,y+597,x+207,y+600,0xFFC5C6D1);
    }
    private void header(GuiGraphics g){
        g.drawString(font,clock(),cx+4,y+24,0xFFF5F1FF,false);
        round(g,x+136,y+15,76,20,0xFF11121D,10);
        g.fill(x+166,y+22,x+178,y+25,0xFF45475B);
        g.drawString(font,runtime.getBoolean("AE")?"AE ●":"AE ×",cx+191,y+24,runtime.getBoolean("AE")?0xFF8AE0BD:0xFFAAA6B7,false);
        long charge=runtime.getLong("Charge"),capacity=Math.max(1,runtime.getLong("Capacity"));
        int percent=(int)Math.max(0,Math.min(100,charge*100/capacity));
        g.fill(cx+268,y+21,cx+304,y+34,0xFF252B3C);g.fill(cx+304,y+25,cx+307,y+30,0xFFDBE2EF);
        g.fill(cx+270,y+23,cx+270+percent*32/100,y+32,percent<20?0xFFE58B96:0xFF6CBCA8);
        g.drawCenteredString(font,percent+"",cx+285,y+23,0xFFFFFFFF);
    }
    private void home(GuiGraphics g){
        g.pose().pushPose();g.pose().translate(cx+9,y+81,0);g.pose().scale(3,3,1);g.drawString(font,clock(),0,0,0xFFFFFFFF,false);g.pose().popPose();
        g.drawString(font,"存档第 "+(Math.floorDiv(runtime.getLong("DayTime"),24000)+1)+" 天",cx+10,y+119,0xFFE9DFEC,false);
        g.drawString(font,runtime.getString("Weather")+"  "+runtime.getInt("Temperature")+"°C（群系估算）",cx+10,y+145,0xFFE9DFEC,false);
        String biome=runtime.getString("Biome"),dim=runtime.getString("Dimension");
        String[] parts=biome.split(":",2);
        String location=parts.length==2?Component.translatable("biome."+parts[0]+"."+parts[1]).getString():biome;
        g.drawString(font,font.plainSubstrByWidth(location+" · "+dim,292),cx+10,y+174,0xFFDAD5EB,false);
        g.drawString(font,"X "+runtime.getInt("X")+"  Z "+runtime.getInt("Z"),cx+10,y+191,0xFFDAD5EB,false);
        round(g,cx,y+217,312,25,0x70202439,10);
        g.drawCenteredString(font,"应用程序  ·  按住拖动调整位置",x+174,y+225,0xFFF4EEF9);
        desktop.render(g);
        g.drawString(font,Component.translatable("hk3gtl.phone.pages",desktop.page()+1,desktop.pages()),cx,y+502,0xFFD5DBEF,false);
        g.drawCenteredString(font,runtime.getBoolean("AE")?"无线终端在范围内 · AE可连接":"AE未连接 · 携带已绑定且有电的无线终端",x+174,y+534,0xFFD5DBEF);
    }
    @Override protected void renderFitted(GuiGraphics g,int mx,int my,float delta){
        g.fill(0,0,width,height,0x85040710);
        round(g,x-BEZEL,y-BEZEL,BODY_WIDTH+2*BEZEL,BODY_HEIGHT+2*BEZEL,0xFF9091A5,26);round(g,x,y,BODY_WIDTH,BODY_HEIGHT,0xFF151828,24);
        g.fillGradient(x+9,y+44,x+339,y+BODY_HEIGHT-58,0xFF76637E,0xFF1C476B);
        fittedScissor(g,x+10,y+44,x+338,y+BODY_HEIGHT-58);
        for(int row=0;row<240;row++){
            double t=row/240.0;int w=(int)(80+180*Math.sin(t*Math.PI));int left=x+18;
            g.fill(left,y+45+row,left+w,y+46+row,0x205DD7DC);
        }
        String mode=view.getString("Mode");boolean home=mode.equals("home");
        if(!home)g.fill(x+10,y+58,x+338,y+BODY_HEIGHT-58,0xF0191E30);
        g.disableScissor();
        header(g);
        fittedScissor(g,x+10,y+58,x+338,y+BODY_HEIGHT-58);
        if(outOfPower()){
            g.fill(x+10,y+55,x+338,y+546,0xFF121624);
            g.drawCenteredString(font,runtime.getBoolean("Present")?"电量不足":"未携带实体手机",x+174,y+190,Hk3PhoneStyle.GOLD);
            int row=0;for(var line:font.split(Component.literal("把手机放进 GT 兼容电力物品充电槽（LV 或以上）。充好后随身携带，再打开手机。安装不会消耗手机。"),272))
                g.drawString(font,line,cx+20,y+226+row++*15,Hk3PhoneStyle.INK,false);
            g.disableScissor();navigation(g,mx,my,delta);return;
        }
        if(home)home(g);
        else{
            g.drawString(font,view.getBoolean("Story")?"文明往来":mode.equals("date")?Component.translatable("hk3gtl.phone.date.title").getString():mode.equals("instructions")||mode.equals("instruction_read")?Component.translatable("hk3gtl.phone.instructions.title").getString():mode.equals("notifications")?"讯息":Hk3PhoneExtraApps.heading(mode),cx,y+77,Hk3PhoneStyle.GOLD,false);
            if(mode.equals("date"))Hk3PhoneDatePane.render(g,runtime,cx,y);
            if(reading()){
                int n=0;for(var part:font.split(Component.literal(view.getString("Title")),312)){if(n==3)break;g.drawString(font,part,cx,y+107+n++*13,Hk3PhoneStyle.GOLD,false);}
                g.pose().pushPose();g.pose().translate(cx+8,y+166,0);g.pose().scale(READING_SCALE,READING_SCALE,1);
                for(int i=0;i<PER_PAGE&&page*PER_PAGE+i<lines.size();i++)g.drawString(font,lines.get(page*PER_PAGE+i),0,i*12,Hk3PhoneStyle.INK,false);
                g.pose().popPose();
                g.drawString(font,Component.translatable("hk3gtl.phone.pages",page+1,pageCount()),cx,y+398,Hk3PhoneStyle.MUTED,false);
                if(view.getBoolean("NoteRead"))g.drawString(font,"已保存正文 · 第 "+(view.getInt("NotePage")+1)+" / "+view.getInt("NoteTotal")+" 段",cx,y+420,Hk3PhoneStyle.MUTED,false);
            }else if(mode.equals("diplomacy")){
                g.drawString(font,view.getString("Title"),cx,y+109,Hk3PhoneStyle.GOLD,false);
                g.drawWordWrap(font,Component.literal(view.getString("Body")),cx,y+135,306,Hk3PhoneStyle.INK);
            }else if(mode.equals("gaze_settings")){
                g.drawWordWrap(font,Component.literal("拖动预览中的注视度面板，避开帧率、小地图或任务列表。"),cx,y+110,302,Hk3PhoneStyle.INK);gazeSettings.render(g);
            }else if(mode.equals("notification_settings")){
                g.drawWordWrap(font,Component.literal("拖动预览通知卡调整位置，滑条调整大小。"),cx,y+110,302,Hk3PhoneStyle.INK);
                settings.render(g);
            }else if(mode.equals("notifications")){
                if(view.getInt("Total")==0)g.drawString(font,"目前没有符合条件的消息",cx+8,y+185,Hk3PhoneStyle.MUTED,false);
                g.drawString(font,Component.translatable("hk3gtl.phone.pages",lastInboxPage+1,Math.max(1,(view.getInt("Total")+7)/8)),cx,y+502,Hk3PhoneStyle.MUTED,false);
            }
        }
        if(mode.equals("gallery"))gallery.render(g,cx,y);
        extras.render(g,mode,view,cx,y);social.render(g,mode,cx,y);
        if(mode.equals("about")){
            g.drawWordWrap(font,Component.literal("HK3GTL 通讯终端\n\n安装后可用快捷键或右键打开，安装不会消耗手机。\n\n电池："+runtime.getLong("Charge")+" / "+runtime.getLong("Capacity")+" EU\n\n屏幕开启每秒消耗 8 EU；息屏不耗电。将实体手机放入 GT 兼容电力物品充电槽（LV 或以上）即可充电。\n\n时间与日期来自当前存档。"),cx+8,y+123,296,Hk3PhoneStyle.INK);
        }
        renderWidgets(g,mx,my,delta,false);
        g.disableScissor();navigation(g,mx,my,delta);
        if(home&&inContent(mx,my)){
            g.pose().pushPose();g.pose().translate(0,0,200);desktop.tooltip(g,mx,my);g.pose().popPose();
        }
    }
    @Override public void tick(){
        super.tick();boolean wasRead=eggReading.complete(view);
        if(reading()&&!outOfPower()){
            eggReading.tick(view,lines,page,PER_PAGE,0,Math.min(PER_PAGE,lines.size()-page*PER_PAGE));
        }else eggReading.close();
        if(wasRead!=eggReading.complete(view))initFitted();social.tick();extras.tick(!outOfPower(),mode());if(search!=null)search.tick();
        if(++pollTicks>=20){pollTicks=0;if(Minecraft.getInstance().getConnection()!=null)com.sirin.hk3gtl.common.network.Hk3Network.CHANNEL.sendToServer(new com.sirin.hk3gtl.common.phone.Hk3PhoneStatusRequestC2SPacket());}
    }
    @Override protected boolean clickFitted(double mx,double my,int button){
        if(my>=y+BODY_HEIGHT-52&&my<y+BODY_HEIGHT-20)return super.clickFitted(mx,my,button);
        if(!inContent(mx,my))return false;
        if(outOfPower())return true;
        if(mode().equals("gaze_settings")&&gazeSettings.click(mx,my,button))return true;
        if(view.getString("Mode").equals("home")&&desktop.press(mx,my,button))return true;
        if(view.getString("Mode").equals("notification_settings")&&settings.click(mx,my,button))return true;
        return super.clickFitted(mx,my,button);
    }
    @Override protected boolean dragFitted(double mx,double my,int button,double dx,double dy){
        if(mode().equals("gaze_settings")&&button==0&&gazeSettings.drag(mx,my))return true;
        if(view.getString("Mode").equals("home")&&button==0&&desktop.drag(mx,my))return true;
        if(view.getString("Mode").equals("notification_settings")&&button==0&&settings.drag(mx,my))return true;
        return super.dragFitted(mx,my,button,dx,dy);
    }
    @Override protected boolean releaseFitted(double mx,double my,int button){
        boolean visible=inContent(mx,my);
        if(mode().equals("gaze_settings")&&button==0&&gazeSettings.release())return true;
        if(view.getString("Mode").equals("home")&&button==0){String id=desktop.release(visible?mx:-1,visible?my:-1);if(!id.isEmpty())app(id);}
        if(view.getString("Mode").equals("notification_settings")&&button==0&&settings.release())return true;
        return super.releaseFitted(mx,my,button);
    }
    @Override public void onClose(){extras.navigate(()->{gallery.close();if(mode().equals("instruction_read"))eggReading.leaveInstruction(view);Hk3EggUiClient.send("close",mode());super.onClose();});}
    @Override public void removed(){gallery.cancel();desktop.removed();eggReading.close();gazeSettings.release();settings.release();Hk3PhoneConfig.SPEC.save();super.removed();}
    @Override public boolean keyPressed(int key,int scan,int modifiers){
        if(outOfPower()&&key!=256)return true;
        if(extras.pending())return true;
        if(extras.key(key))return true;
        if(mode().equals("notifications")&&key==257&&search!=null){query=search.getValue().strip();inbox(lastFilter,0);return true;}
        if(reading()&&(key==266||key==267||key==268||key==269)){
            page=switch(key){case 266->page-1;case 267->page+1;case 268->0;default->pageCount()-1;};initFitted();return true;
        }
        return super.keyPressed(key,scan,modifiers);
    }
    @Override public boolean charTyped(char c,int modifiers){return outOfPower()||extras.pending()||super.charTyped(c,modifiers);}
    public static void renderToast(GuiGraphics g){
        var mc=Minecraft.getInstance();if(mc.player==null||mc.screen!=null||mc.options.hideGui)return;
        int sw=mc.getWindow().getGuiScaledWidth(),sh=mc.getWindow().getGuiScaledHeight();
        var cards=TOASTS.visible(now(),sw<600||sh<240?1:2);
        if(Hk3PhoneConfig.SOUND.get()&&cards.stream().anyMatch(c->!previous.contains(c)))
            mc.getSoundManager().play(net.minecraft.client.resources.sounds.SimpleSoundInstance.forUI(net.minecraft.sounds.SoundEvents.UI_BUTTON_CLICK.value(),.7F,.25F));
        previous=cards;
        // 总是预留当前窗口可显示的最大卡数，避免第二条通知出现时整组改变锚点。
        var p=com.sirin.hk3gtl.common.phone.Hk3PhoneLayout.toast(sw,sh,sw<600||sh<240?1:2,Hk3PhoneConfig.SCALE.get(),
            Hk3PhoneConfig.POSITION_X.get(),Hk3PhoneConfig.POSITION_Y.get(),Hk3PhoneConfig.RIGHT.get(),Hk3PhoneConfig.MARGIN.get(),Hk3PhoneConfig.TOP.get());
        int index=0;
        for(var card:cards){
            String title=card.count()>1?(card.kind().equals("research")?"新增 "+card.count()+" 项研究成果":"另有 "+card.count()+" 条消息"):card.title();
            String body=card.count()>1?"各项记录已保存，请到消息中心逐项查看。":card.body();
            g.pose().pushPose();g.pose().translate(p.x(),p.y()+index++*72*p.scale(),0);g.pose().scale((float)p.scale(),(float)p.scale(),1);
            Hk3PhoneStyle.card(g,title,body,installed?Hk3PhoneKey.OPEN.getTranslatedKeyMessage().getString()+" · 消息中心":card.kind().equals("letter")?"/hk3letter · 阅读来信":"安装通讯终端后可打开消息中心");
            g.pose().popPose();
        }
    }
    @Override public boolean isPauseScreen(){return false;}
}
