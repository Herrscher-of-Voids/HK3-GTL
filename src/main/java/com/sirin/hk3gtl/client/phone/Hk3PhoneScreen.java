package com.sirin.hk3gtl.client.phone;

/** 【变更记录 #24】2026-10-31 01:06:22（第24次备注 · 修订187）：删除无；新增完整阅读确认包的当前页处理；修改收到确认后重绘按钮；用途：保留当前页与正文，不打开额外界面。 */

/** 【变更记录 #23】2026-10-31 00:46:39（第23次备注 · 修订187）：删除仅到末页即可确认的条件；新增完整阅读状态；修改完成时重绘按钮；用途：正常翻页后可确认，跳末页不能代替阅读。 */

/** 【变更记录 #14】2026-10-01 00:20:13（修订122）：删除无；新增/修改：正式来信在同屏返回所属主题；旧队历史不显示处理入口；用途：服务端主题状态与阅读权限一致。 */

/** 【变更记录 #13】2026-10-01 00:17:25（修订122）：删除无；新增/修改：正式往来阅读回执纳入本人已读机制；用途：五方首信与团队限定交流保持一致。 */

/** 【变更记录 #12】2026-10-01 00:14:30（修订122）：删除无；新增/修改：信件App内同屏五方联络、分页摘要与显式确认，不加入新贴图；用途：真实成果、团队授权与个人阅读分离，不开放贸易或免费完成研究。 */

/** 【变更记录 #11】2026-10-01 00:00:53（修订121）：删除无；新增/修改：跨队历史阅读无回信/补谈入口，避免旧消息错连新队；用途：个人与团队记录隔离，保留历史与权限。 */

/** 【变更记录 #10】2026-09-30 23:58:50（修订121）：删除旧个人答复自动代表新队的生产路径；新增/修改：回信预览只向授权者启用确认；三步补谈同屏分页且不把回看算经历；用途：团队外交、阅读与个人经历分账，不发研究或物品奖励。 */

/** 【变更记录 #1】2026-09-29 18:57:18（内测5修订95）：手机主页、分页通知和轻量右侧弹窗；阅读从服务端私人账本获取。 */
/** 【变更记录 #2】2026-09-29 19:50:20（内测5修订99）：删除：手机贸易App入口并重排剩余四个应用；新增：无；修改：按负责人决定撤下五方贸易；用途：保留其他系统独立运行。 */

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

/**
 * 【变更记录 #3】2026-09-30 16:19:31（内测5修订110）
 * 删除：被新版通知读取流程替代的旧分支，历史备注保留。
 * 新增／修改：用不抢焦点的排队浮层替代覆盖；新增全部/未读/待处理、单篇滚动与触控翻页、通知设置，正文打开后才确认已读，断线清空客户端。
 * 用途：通知与业务结果分离，服务端授权和个人持久化；不改结构、贴图和贸易。
 */

/**
 * 【变更记录 #4】2026-09-30 18:18:05（内测5修订112）
 * 删除：手机IF全览入口、滚动行号、切信即关闭屏幕与循环位置按钮。
 * 新增：固定终端布局、信件/通知同屏阅读、整页按钮与拖动预览。
 * 修改：原信件包转入本屏，已有屏幕原位更新，已读确认仍在正文打开后。
 * 用途：统一交互并保留安装、回信与服务器校验；独立IF指令不受影响。
 */

/**
 * 【变更记录 #5】2026-09-30 18:44:46（内测5修订113）
 * 删除：桌面侧栏布局；新增：纵向手机、游戏时间/日期/环境/电量/AE状态、可拖动App。
 * 修改：子应用仍在同一屏幕原位切换，电量从服务端采样；用途：真正手机桌面体验与统一翻页阅读。
 */
/**
 * 【变更记录 #6】2026-09-30 19:08:08（内测5修订114）
 * 删除：无；新增分组设定、搜索讯息卡、应用路由和草稿离开确认；修改同屏导航及缩放编辑框接入。
 * 用途：手机应用集成，保留既有电量和阅读权限；交易只展示不结算。
 */
/** 【变更记录 #7】2026-09-30 19:20:11（内测5修订115）：删除缺电时的半透明叠字覆盖；新增缺电独立渲染分支、HUD设置；修改缺电不绘制桌面正文；用途：解决文字穿透与位置调整。 */
/** 【变更记录 #8】2026-09-30 19:49:34（修订116）：删除无；新增微讯息接入；修改：增加社交面板与断线清理；用途：保留原手机布局与权限，AI不进入服务器业务。 */
/** 【变更记录 #9】2026-09-30 23:43:42（修订120）：删除无；新增/修改：文明里程碑路由纳入既有同屏应用白名单；用途：按真实团队事实展示文明进度，不给机器/配方增加等级锁。 */
/** 【变更记录 #15】2026-10-01 00:44:06（修订123）：删除无；新增/修改：个人补谈末页确认与团队发送分别路由，保持同屏分页阅读；用途：个人交流、团队决定及额外收藏分开，保留真实记录。 */
/** 【变更记录 #16】2026-10-01 00:59:10（修订124）：删除无；新增/修改：首信附件四步分页确认；已批准稍后处理可取消未提交预览，外交首页完整八入口；用途：按五方交流系统整链收口，真实权限和本人经历不混用。 */
/** 【变更记录 #17】2026-10-01 01:01:52（修订124）：删除无；新增按钮长标题按实际字体宽度省略；修改历史正文/离线成员长名称的边界；用途：避免完整交流入口文字越出按钮。 */
/** 【变更记录 #18】2026-10-01 01:54:14（修订127）：删除：被替代的旧分支；新增/修改：收藏阅读返回原筛选和页码，继续沿用同屏阅读；用途：个人收藏与正式资格分离，保留历史记录。 */
/** 【变更记录 #19】2026-10-01 04:19:02（修订128）：删除：旧固定上限或被替代的分支；新增/修改：显示一秒后提交实际页片段，界面布局与原页码不变，离开页面终止会话；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #20】2026-10-01 04:27:32（修订128）：删除：旧固定上限或被替代的分支；新增/修改：实际本地App打开和主动关闭回报，不将切换其他屏幕当主动退出；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #21】2026-10-01 16:30:04（修订134）：删除无；新增首页日期详情按钮与同框日期页；修改日期由服务端主世界时间实时同步；用途：完成即死年真实界面依赖，保留应用顺序及材质。 */
/** 【变更记录 #22】2026-10-19 02:05:08（第22次备注 · 修订171）：删除无；新增团队机器目录和详情返回路由；修改详情返回时保留服务端页码与筛选，目录返回文明总览；用途：在既有缩放手机内提供只读机器查询，不增设操作入口或桌面图标。 */
/** 【变更记录 #25】2026-11-01 00:36:24（第25次备注 · 内测5修订192）：删除每20tick发送hk3phone status聊天命令的后台路径；新增无载荷C2S状态请求；修改仍每20tick调用服务端原poll；用途：长篇阅读不因后台轮询累积聊天垃圾计数被踢，耗电及服务端限流保持原口径。 */
/** 【变更记录 #26】2026-11-05 01:51:41（第26次备注 · 内测5修订204）：删除无；新增保存笔记逐段阅读的主动翻页及说明读完后主动收藏按钮；修改返回路径识别笔记正文；用途：按钮依赖服务端完整阅读确认，沿用既有连续片段协议。 */
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
    private static final int PER_PAGE=16;
    private int page,x,y,cx,pollTicks;
    private final Hk3EggReadClient eggReading=new Hk3EggReadClient();
    private String lastFilter="all",lastArchiveFilter="all";private int lastInboxPage,lastArchivePage;
    private Hk3PhoneScreen(CompoundTag view){super(Component.literal("HK3GTL · 手机"),380,640);this.view=view.copy();desktop.accept(view);gallery.accept(view);}
    public static void reset(){Hk3SocialPane.reset();TOASTS.clear();previous=List.of();installed=false;runtime=new CompoundTag();}
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
    private boolean outOfPower(){return installed&&(!runtime.getBoolean("Present")||runtime.getLong("Charge")<8);}
    Button button(String title,int bx,int by,int w,Runnable action){
        String label=font.width(title)>w-14?font.plainSubstrByWidth(title,Math.max(1,w-24))+"…":title;
        return addRenderableWidget(Hk3PhoneStyle.button(label,bx,by,w,26,action));
    }
    private void inbox(String filter,int index){lastFilter=filter;lastInboxPage=index;command(query.isBlank()?"hk3phone notifications "+filter+" "+index:"hk3phone search "+filter+" "+index+" "+query);}
    private boolean reading(){return mode().equals("detail")||mode().equals("letter")||mode().equals("archive_detail")||mode().equals("diplomacy_read");}
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
            case "inbox"->inbox("all",0);case "letters"->command("hk3letter diplomacy");case "ae"->command("hk3phone ae");
            case "notes"->command("hk3phone apps notes");case "civilization"->command("hk3phone apps civilization");
            case "trade","tiles2048","snake"->local(id);
            case "updates"->command("hk3updates");case "settings"->local("settings");
            case "quiet"->{TOASTS.clear();previous=List.of();}
        }
    }
    @Override protected void initFitted(){
        if(mode().equals("archive")){lastArchiveFilter=view.getString("Filter");lastArchivePage=view.getInt("Page");}
        clearWidgets();search=null;x=(width-348)/2;y=(height-608)/2;cx=x+18;String mode=view.getString("Mode");
        button("返回",cx,y+558,92,()->extras.navigate(()->{
            gallery.close();
            if(mode.equals("gallery"))command("hk3phone apps civilization");
            else if(mode.startsWith("social"))social.back();
            else if(mode.equals("machine_detail"))Hk3MachineOverviewPane.directory(view.getInt("Page"),view.getString("Filter"));
            else if(mode.equals("machines")||mode.equals("machine_unavailable"))command("hk3phone apps civilization");
            // 【变更记录 #207】2026-11-05：文明总览全文返回原总览，不误入收藏目录。
            else if(mode.equals("archive_detail")&&view.getBoolean("CivilizationRead"))command("hk3phone apps civilization");
            else if(mode.equals("archive_detail")&&view.getBoolean("NoteRead"))command("hk3phone apps note "+view.getString("NoteId"));
            else if(mode.equals("archive_detail"))command("hk3phone apps archive "+lastArchivePage+" "+lastArchiveFilter);
            else if(mode.equals("archive")||mode.equals("civilization_milestones"))command("hk3phone apps civilization");
            else if(mode.equals("note")||mode.equals("todos"))command("hk3phone apps notes");
            else if(mode.equals("notification_settings")||mode.equals("gaze_settings")||mode.equals("about"))local("settings");
            else if(mode.startsWith("diplomacy"))command("hk3letter diplomacy");
            else if(reading())inbox(lastFilter,lastInboxPage);else command("hk3phone");
        }));
        button("桌面",cx+110,y+558,92,()->extras.navigate(()->{gallery.close();command("hk3phone");}));
        button("息屏",cx+220,y+558,92,this::onClose);
        if(mode.equals("home")){
            desktop.layout(cx,y+257);
            addRenderableWidget(Hk3PhoneStyle.button(Component.translatable("hk3gtl.phone.date.open").getString(),cx+190,y+109,122,26,()->command("hk3phone apps date")));
        }else if(mode.equals("settings")){
            widget(new Hk3PhoneAppCard("关于手机","电量、安装与充电","终端状态  ›",cx,y+115,312,69,0xFFB3C9DE,()->local("about")));
            widget(new Hk3PhoneAppCard("通知与显示","拖动位置 · 提示音 · 闲话提醒","个性化  ›",cx,y+193,312,69,0xFFBEA9EE,()->local("notification_settings")));
            widget(new Hk3PhoneAppCard("注视度 HUD","拖动位置 · 缩放 · 避让其他界面","位置预览  ›",cx,y+271,312,69,0xFF87D6E9,()->local("gaze_settings")));
            widget(new Hk3PhoneAppCard("AE 设备互联","携带已绑定且有电的无线终端","打开 AE 终端  ›",cx,y+349,312,69,0xFF8DDFC0,()->command("hk3phone ae")));
            widget(new Hk3PhoneAppCard("更新详情","查看本次内测更新","版本记录  ›",cx,y+427,312,69,0xFFE8C673,()->command("hk3updates")));
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
                if(paragraph.isEmpty())lines.add(FormattedCharSequence.EMPTY);else lines.addAll(font.split(Component.literal(paragraph),292));
            }
            page=com.sirin.hk3gtl.common.phone.Hk3PhoneLayout.page(page,lines.size(),PER_PAGE);
            button("上一页",cx+142,y+389,80,()->{page--;initFitted();}).active=page>0;
            button("下一页",cx+232,y+389,80,()->{page++;initFitted();}).active=page+1<pageCount();
            if(view.getBoolean("NoteRead")){
                if(view.getInt("NotePage")+1<view.getInt("NoteTotal"))button("手动翻至下一段",cx,y+439,312,()->command("hk3phone apps notenext "+view.getString("Token"))).active=page+1==pageCount()&&eggReading.complete(view);
            }else if(view.getBoolean("CollectionExplanation"))button("主动收藏这条说明",cx,y+439,312,()->command("hk3phone apps collect "+view.getString("Token"))).active=page+1==pageCount()&&eggReading.complete(view);
            if(mode.equals("letter"))letterActions();
            if(mode.equals("diplomacy_read")&&!view.getString("Topic").isEmpty())button("查看本主题与答复",cx,y+440,312,()->command("hk3letter diplomacy topic "+view.getString("Topic")));
            if(mode.equals("diplomacy_read")&&!view.getString("Token").isEmpty())button(view.getBoolean("PersonalSupplement")?"已阅读，确认本步补谈":"确认发送这份预览",cx,y+479,312,()->command("hk3letter diplomacy "+(view.getBoolean("PersonalSupplement")?"continue ":"confirm ")+view.getString("Token"))).active=page+1==pageCount()&&eggReading.complete(view);
            if(mode.equals("diplomacy_read")&&!view.getString("Token").isEmpty()&&!view.getBoolean("PersonalSupplement"))button("稍后处理",cx,y+516,312,()->command("hk3letter diplomacy defer"));
            if(mode.equals("diplomacy_read")&&view.getBoolean("ReadOnly"))button("只读：由队长或授权成员确认",cx,y+479,312,()->{}).active=false;
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
            if(canReply&&(doc==1||doc==2))button(view.getBoolean("CanDecide")?"确认发送这封回信":"只读：由队长或授权成员确认",cx,y+479,312,()->command((doc==1?"hk3letter accept ":"hk3letter decline ")+view.getString("Token"))).active=view.getBoolean("CanDecide")&&!view.getString("Token").isEmpty()&&page+1==pageCount()&&eggReading.complete(view);
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
        g.drawCenteredString(font,runtime.getBoolean("AE")?"无线终端在范围内 · AE可连接":"AE未连接 · 携带已绑定且有电的无线终端",x+174,y+534,0xFFD5DBEF);
    }
    @Override protected void renderFitted(GuiGraphics g,int mx,int my,float delta){
        g.fill(0,0,width,height,0x85040710);
        round(g,x-3,y-3,354,614,0xFF9091A5,26);round(g,x,y,348,608,0xFF151828,24);
        g.fillGradient(x+9,y+44,x+339,y+547,0xFF76637E,0xFF1C476B);
        // 自绘抽象壁纸，无外部图片依赖；所有应用共用同一手机外框。
        for(int row=0;row<240;row++){
            double t=row/240.0;int w=(int)(80+180*Math.sin(t*Math.PI));int left=x+18;
            g.fill(left,y+45+row,left+w,y+46+row,0x205DD7DC);
        }
        String mode=view.getString("Mode");boolean home=mode.equals("home");
        if(!home)g.fill(x+10,y+58,x+338,y+540,0xF0191E30);
        header(g);
        if(outOfPower()){
            g.fill(x+10,y+55,x+338,y+546,0xFF121624);
            g.drawCenteredString(font,runtime.getBoolean("Present")?"电量不足":"未携带实体手机",x+174,y+190,Hk3PhoneStyle.GOLD);
            int row=0;for(var line:font.split(Component.literal("把手机放进 GT 兼容电力物品充电槽（LV 或以上）。充好后随身携带，再打开手机。安装不会消耗手机。"),272))
                g.drawString(font,line,cx+20,y+226+row++*15,Hk3PhoneStyle.INK,false);
            for(var child:children())if(child instanceof net.minecraft.client.gui.components.AbstractWidget widget&&widget.getY()>=y+550)widget.render(g,mx,my,delta);
            g.fill(x+141,y+597,x+207,y+600,0xFFC5C6D1);return;
        }
        if(home)home(g);
        else{
            g.drawString(font,mode.equals("date")?Component.translatable("hk3gtl.phone.date.title").getString():mode.equals("notifications")?"讯息":Hk3PhoneExtraApps.heading(mode),cx,y+77,Hk3PhoneStyle.GOLD,false);
            if(mode.equals("date"))Hk3PhoneDatePane.render(g,runtime,cx,y);
            if(reading()){
                int n=0;for(var part:font.split(Component.literal(view.getString("Title")),312)){if(n==3)break;g.drawString(font,part,cx,y+107+n++*13,Hk3PhoneStyle.GOLD,false);}
                for(int i=0;i<PER_PAGE&&page*PER_PAGE+i<lines.size();i++)g.drawString(font,lines.get(page*PER_PAGE+i),cx+8,y+166+i*12,Hk3PhoneStyle.INK,false);
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
        super.renderFitted(g,mx,my,delta);
        if(home)desktop.tooltip(g,mx,my);
        g.fill(x+141,y+597,x+207,y+600,0xFFC5C6D1);
    }
    @Override public void tick(){super.tick();boolean wasRead=eggReading.complete(view);if(reading()&&!outOfPower())eggReading.tick(view,lines,page,PER_PAGE);else eggReading.close();if(wasRead!=eggReading.complete(view))initFitted();social.tick();extras.tick(!outOfPower(),mode());if(search!=null)search.tick();if(++pollTicks>=20){pollTicks=0;if(Minecraft.getInstance().getConnection()!=null)com.sirin.hk3gtl.common.network.Hk3Network.CHANNEL.sendToServer(new com.sirin.hk3gtl.common.phone.Hk3PhoneStatusRequestC2SPacket());}}
    @Override protected boolean scrollFitted(double x,double y,double d){return reading()||super.scrollFitted(x,y,d);}
    @Override protected boolean clickFitted(double mx,double my,int button){
        if(outOfPower()&&my<y+550)return true;
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
        if(mode().equals("gaze_settings")&&button==0&&gazeSettings.release())return true;
        if(view.getString("Mode").equals("home")&&button==0){String id=desktop.release(mx,my);if(!id.isEmpty())app(id);}
        if(view.getString("Mode").equals("notification_settings")&&button==0&&settings.release())return true;
        return super.releaseFitted(mx,my,button);
    }
    @Override public void onClose(){extras.navigate(()->{gallery.close();Hk3EggUiClient.send("close",mode());super.onClose();});}
    @Override public void removed(){gallery.cancel();desktop.removed();eggReading.close();gazeSettings.release();settings.release();Hk3PhoneConfig.SPEC.save();super.removed();}
    @Override public boolean keyPressed(int key,int scan,int modifiers){
        if(outOfPower()&&key!=256)return true;
        if(extras.pending())return true;
        if(extras.key(key))return true;
        if(mode().equals("notifications")&&key==257&&search!=null){query=search.getValue().strip();inbox(lastFilter,0);return true;}
        if(reading()&&(key==266||key==267||key==268||key==269)){
            page=switch(key){case 266->page-1;case 267->page+1;case 268->0;default->pageCount()-1;};initFitted();return true;
        }return super.keyPressed(key,scan,modifiers);
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
