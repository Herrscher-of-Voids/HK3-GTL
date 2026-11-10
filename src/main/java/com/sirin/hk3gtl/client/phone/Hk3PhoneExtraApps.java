package com.sirin.hk3gtl.client.phone;

/** 【变更记录 #4】2026-10-01 00:20:13（修订122）：删除无；新增/修改：五方通信页显示明确应用名称；用途：服务端主题状态与阅读权限一致。 */
import com.sirin.hk3gtl.common.phone.*;
import com.sirin.hk3gtl.common.network.Hk3Network;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.*;
import net.minecraft.nbt.*;
import net.minecraft.network.chat.Component;
/**
 * 【变更记录 #1】2026-09-30 19:03:21（内测5修订114）
 * 删除：无；新增：笔记编辑/保存确认、两款小游戏、文明档案与仅展示交易应用。
 * 修改：子应用复用手机外框；用途：草稿防丢、无经济接口、小游戏不发放物品或进度。
 */
/** 【变更记录 #2】2026-09-30 19:49:34（修订116）：删除无；新增微讯息接入；修改：统一应用标题；用途：保留原手机布局与权限，AI不进入服务器业务。 */
/** 【变更记录 #3】2026-09-30 23:43:42（修订120）：删除无；新增/修改：在既有手机内增加八页文明成果条件，不跳出外框，保留档案入口与原小游戏；用途：按真实团队事实展示文明进度，不给机器/配方增加等级锁。 */
/** 【变更记录 #5】2026-10-01 00:44:40（修订123）：删除无；新增/修改：文明总览增加真实个人经历入口，旧收藏单列不冒充终审进度；用途：个人交流、团队决定及收藏分开，保留真实记录。 */
/** 【变更记录 #7】2026-10-01 04:48:51（修订128）：删除：旧固定上限或被替代的分支；新增/修改：既有2048和贪吃蛇发送本局种子和实际方向步骤，服务端重放；不上传分数、不改变游戏棋盘或奖励；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #8】2026-10-01 22:50:14（第8次备注 · 内测5修订155）：删除玩家展示中的旧电压及开发说明；新增现行正文投影或对应回归；修改仅限呈现与检索，不改变进度、回执、触发条件或权限；用途：统一发布版玩家文案，历史备注保留。 */
/** 【变更记录 #9】2026-10-19 02:05:08（第9次备注 · 修订171）：删除无；新增文明总览内的团队机器目录与分页只读详情；修改文明首页留出第四个入口并委托独立面板；用途：显示服务端已授权的机器状态，不操作机器或公开个人账本。 */
/** 【变更记录 #10】2026-10-31 21:56:17（第10次备注 · 内测5修订191）：删除无；新增笔记冲突后的明确放弃重载与另存草稿按钮；修改仅失败回包更新冲突状态，原正文与版本保留，成功或新建时清除；用途：旧副本不覆盖新正文，删除冲突允许另存，恢复仍走服务端身份、供电、长度与配额检查。 */
/** 【变更记录 #11】2026-11-04（修订197）：删除文明称号的无历史限定展示；新增当前核验等级和工程待接入原因；修改里程碑行展示；用途：客户端如实呈现服务端资格，不授予进度。 */
/** 【变更记录 #12】2026-11-05 01:51:41（第12次备注 · 内测5修订204）：删除无；新增本人收藏搜索、第五百页说明入口与已保存笔记只读入口；修改目录行位置容纳搜索；用途：所有操作仍交服务端核验，未保存草稿不冒充已读笔记。 */
final class Hk3PhoneExtraApps {
    /** 【变更记录 #13】2026-11-05（修订205）：新增真实颜色标签、任务标志与本人待办页；勾选只发送笔记ID及版本，完成状态由服务端返回。 */
/** 【变更记录 #14】2026-11-05 22:32:30（修订211）：删除新话题页落入默认阅读标题的路径；新增话题模式标题映射；修改仅客户端页眉；用途：沿用微讯息导航名称，不改变按钮和服务端权限。 */
    private final Hk3PhoneScreen host;
    private final Hk3MachineOverviewPane machines;
    private long tilesSeed=System.nanoTime(),snakeSeed=System.nanoTime();
    private boolean tilesRegistered,snakeRegistered;
    private final Hk3PhoneGames.Tiles tiles=new Hk3PhoneGames.Tiles(tilesSeed);
    private Hk3PhoneGames.Snake snake=new Hk3PhoneGames.Snake(snakeSeed);
    private boolean paused=true,dirty,pending,confirmDelete,noteConflict,noteExists;private int snakeTicks,tradeTab;
    private String noteId="",title="",body="",error="";private int version,colors;private boolean task,taskDone;private int aePage;
    private Runnable leave;
    private EditBox titleBox;private MultiLineEditBox bodyBox;
    private final String[] factions={"天命","逆熵","世界蛇","圣芙蕾雅学园","往世乐土"};
    Hk3PhoneExtraApps(Hk3PhoneScreen host){this.host=host;this.machines=new Hk3MachineOverviewPane(host);}
    boolean accept(CompoundTag v){
        String mode=v.getString("Mode");
        if(mode.equals("app_error")){
            pending=false;error=v.getString("Error");noteConflict=v.getBoolean("NoteConflict");noteExists=v.getBoolean("NoteExists");
            if(host.mode().equals("machines")||host.mode().equals("machine_detail")||host.mode().equals("machine_unavailable")){
                machines.unavailable(error);host.local("machine_unavailable");
            }else host.refresh();
            return true;
        }
        if(mode.equals("note_saved")){pending=false;dirty=false;confirmDelete=false;noteConflict=false;error="";return true;}
        if(mode.equals("todos"))error="";
        if(mode.equals("note")){noteId=v.getString("Id");title=v.getString("Title");body=v.getString("Body");version=v.getInt("Version");colors=v.getInt("Colors");task=v.getBoolean("Task");taskDone=v.getBoolean("Done");dirty=false;pending=false;confirmDelete=false;noteConflict=false;error="";}
        return false;
    }
    boolean pending(){return pending;}
    void navigate(Runnable action){
        if(pending)return;
        if(dirty){leave=action;host.local("draft_exit");}else action.run();
    }
    void fresh(){noteId="";title="";body="";version=0;colors=0;task=false;taskDone=false;dirty=false;noteConflict=false;error="";confirmDelete=false;host.local("note");}
    private void save(boolean delete){
        if(pending)return;
        if(!delete&&title.isBlank()){error="请先填写标题。";host.refresh();return;}
        pending=true;error="正在保存…";host.refresh();
        Hk3Network.CHANNEL.sendToServer(new Hk3PhoneNotePacket(delete,noteId,version,title,body,colors,task));
    }
    private void pager(CompoundTag v,String command,int size,int x,int y){
        int p=v.getInt("Page"),last=Math.max(0,(v.getInt("Total")-1)/size);
        host.button("上一页",x+142,y+493,80,()->Hk3PhoneScreen.command(command+" "+(p-1))).active=p>0;
        host.button("下一页",x+232,y+493,80,()->Hk3PhoneScreen.command(command+" "+(p+1))).active=p<last;
    }
    void init(String mode,CompoundTag v,int x,int y){
        titleBox=null;bodyBox=null;
        switch(mode){
            case "ae_terminals"->{
                var rows=v.getList("Rows",Tag.TAG_COMPOUND);aePage=Math.max(0,Math.min(aePage,Math.max(0,(rows.size()-1)/6)));
                for(int i=aePage*6;i<Math.min(rows.size(),(aePage+1)*6);i++){
                    var row=rows.getCompound(i);int slot=row.getInt("Slot");
                    host.widget(new Hk3PhoneAppCard(row.getString("Title"),"背包槽 "+slot+(row.getBoolean("Available")?" · 可连接":" · 连接条件未满足"),"",x,y+140+(i%6)*54,312,48,0xFF8DDFC0,()->Hk3PhoneScreen.command("hk3phone ae "+slot)));
                }
                host.button("上一页",x+142,y+493,80,()->{aePage--;host.refresh();}).active=aePage>0;
                host.button("下一页",x+232,y+493,80,()->{aePage++;host.refresh();}).active=(aePage+1)*6<rows.size();
            }
            case "notes"->{
                host.button("+ 新建笔记",x,y+111,150,this::fresh);
                host.button("个人待办",x+164,y+111,148,()->Hk3PhoneScreen.command("hk3phone apps todos"));
                int i=0;for(Tag raw:v.getList("Rows",Tag.TAG_COMPOUND)){
                    var r=(CompoundTag)raw;int at=i++;
                    host.widget(new Hk3PhoneAppCard(r.getString("Title"),r.getString("Body"),"打开编辑",x+(at%2)*160,y+153+(at/2)*108,152,98,0xFFE8C673,()->Hk3PhoneScreen.command("hk3phone apps note "+r.getString("Id"))));
                }pager(v,"hk3phone apps notes",6,x,y);
            }
            case "todos"->{
                host.button("返回笔记列表",x,y+111,150,()->Hk3PhoneScreen.command("hk3phone apps notes"));
                int i=0;for(Tag raw:v.getList("Rows",Tag.TAG_COMPOUND)){
                    var r=(CompoundTag)raw;int yy=y+177+i++*46;
                    host.button(r.getString("Title"),x,yy,226,()->Hk3PhoneScreen.command("hk3phone apps note "+r.getString("Id")));
                    host.button(r.getBoolean("Done")?"✓ 已完成":"□ 待办",x+234,yy,78,()->Hk3PhoneScreen.command("hk3phone apps checknote "+r.getString("Id")+" "+r.getInt("Version")+" "+!r.getBoolean("Done")));
                }pager(v,"hk3phone apps todos",6,x,y);
            }
            case "note"->{
                titleBox=host.widget(new EditBox(Minecraft.getInstance().font,x+5,y+125,302,24,Component.literal("标题")));
                titleBox.setMaxLength(64);titleBox.setValue(title);titleBox.setResponder(s->{title=s;dirty=true;});
                bodyBox=host.widget(new MultiLineEditBox(Minecraft.getInstance().font,x+5,y+171,302,185,Component.literal("写下想记录的事…"),Component.literal("笔记正文")){
                    @Override /** 【变更记录 #6】2026-10-01 01:54:14（修订127）：删除：被替代的旧分支；新增/修改：既有手机外框增加收藏分类按钮与本人数量，保留翻页阅读；用途：个人收藏与正式资格分离，保留历史记录。 */
public void renderWidget(GuiGraphics g,int mx,int my,float delta){
                        if(!visible)return;renderBackground(g);host.clip(g,getX()+1,getY()+1,getX()+getWidth()-1,getY()+getHeight()-1);
                        g.pose().pushPose();g.pose().translate(0,-scrollAmount(),0);
                        renderContents(g,mx,my,delta);g.pose().popPose();g.disableScissor();renderDecorations(g);
                    }
                });
                bodyBox.setCharacterLimit(4096);bodyBox.setValue(body);bodyBox.setValueListener(s->{body=s;dirty=true;});
                titleBox.setEditable(!pending);bodyBox.active=!pending;
                for(int j=0;j<3;j++){
                    int bit=1<<j;String label=new String[]{"红色","绿色","蓝色"}[j];
                    host.button(((colors&bit)!=0?"✓ ":"□ ")+label,x+j*106,y+368,100,()->{colors^=bit;dirty=true;host.refresh();}).active=!pending;
                }
                host.button(task?"✓ 记为待办"+(taskDone?" · 已完成":" · 未完成"):"□ 记为待办",x,y+402,312,()->{task=!task;dirty=true;host.refresh();}).active=!pending;
                if(noteConflict){
                    host.button("放弃草稿并重载",x,y+439,148,()->Hk3PhoneScreen.command("hk3phone apps note "+noteId)).active=!pending&&noteExists;
                    host.button("另存草稿",x+164,y+439,148,()->{noteId="";version=0;noteConflict=false;confirmDelete=false;dirty=true;save(false);}).active=!pending;
                }
                else host.button("分页阅读已保存正文",x,y+439,312,()->Hk3PhoneScreen.command("hk3phone apps readnote "+noteId)).active=!pending&&!dirty&&!noteId.isEmpty();
                host.button(pending?"保存中…":"保存笔记",x,y+510,148,()->save(false)).active=!pending;
                host.button(confirmDelete?"确认删除":"删除笔记",x+164,y+510,148,()->{if(confirmDelete)save(true);else{confirmDelete=true;error="再次点击确认删除，此操作不可撤回。";host.refresh();}}).active=!pending&&!noteId.isEmpty();
            }
            case "draft_exit"->{
                host.button("保存草稿",x,y+236,312,()->save(false)).active=!pending;
                host.button("继续编辑",x,y+277,312,()->host.local("note")).active=!pending;
                host.button("放弃改动并离开",x,y+318,312,()->{dirty=false;error="";if(leave!=null)leave.run();}).active=!pending;
            }
            case "tiles2048","snake"->{
                if(mode.equals("tiles2048")&&!tilesRegistered){Hk3EggUiClient.send("tiles_start",Long.toString(tilesSeed));tilesRegistered=true;}
                if(mode.equals("snake")&&!snakeRegistered){Hk3EggUiClient.send("snake_start",Long.toString(snakeSeed));snakeRegistered=true;}
                for(int dir=0;dir<4;dir++){int d=dir;host.button(new String[]{"↑","→","↓","←"}[dir],x+dir*79,y+445,74,()->direction(d));}
                if(mode.equals("snake"))host.button(paused?"开始 / 继续":"暂停",x,y+485,148,()->{paused=!paused;host.refresh();}).active=!snake.over();
                host.button("重新开始",x+164,y+485,148,()->{if(mode.equals("snake")){snakeSeed=System.nanoTime();snake=new Hk3PhoneGames.Snake(snakeSeed);Hk3EggUiClient.send("snake_start",Long.toString(snakeSeed));paused=true;snakeTicks=0;}else{tilesSeed=System.nanoTime();var fresh=new Hk3PhoneGames.Tiles(tilesSeed);tiles.restore(fresh.cells(),0);Hk3EggUiClient.send("tiles_start",Long.toString(tilesSeed));}host.refresh();});
            }
            case "civilization"->{
                host.button("查看团队机器目录",x,y+337,312,()->Hk3MachineOverviewPane.directory(0,"all"));
                host.button("查看本人正式经历与待补项",x,y+375,312,()->Hk3PhoneScreen.command("hk3phone apps experience"));
                host.button("查看文明等级与成果条件",x,y+413,312,()->Hk3PhoneScreen.command("hk3phone apps milestones"));
                host.button("档案与收藏",x,y+451,312,()->Hk3PhoneScreen.command("hk3phone apps archive"));
                // 【变更记录 #207】2026-11-05：保留总览操作区，新增复用阅读界面的全文入口。
                host.button("阅读全文",x,y+489,148,()->Hk3PhoneScreen.command("hk3phone apps civilizationread"));
                host.button(Component.translatable("hk3gtl.phone.gallery.title").getString(),x+164,y+489,148,()->Hk3PhoneScreen.command("hk3phone apps gallery"));
            }
            case "civilization_milestones"->pager(v,"hk3phone apps milestones",1,x,y);
            case "archive"->{
                String[] ids={"all","optional","formal","milestone"};String[] labels={"全部","收藏","剧情","里程碑"};
                for(int j=0;j<ids.length;j++){String filter=ids[j];host.button((filter.equals(v.getString("Filter"))?"• ":"")+labels[j],x+j*79,y+108,75,()->Hk3PhoneScreen.command("hk3phone apps archive 0 "+filter));}
                var collectionSearch=host.widget(new EditBox(Minecraft.getInstance().font,x+4,y+146,230,23,Component.literal("搜索已拥有收藏")));
                collectionSearch.setMaxLength(64);collectionSearch.setValue(v.getString("Query"));collectionSearch.setHint(Component.literal("搜索已拥有收藏"));
                host.button("搜索",x+244,y+144,68,()->{String query=collectionSearch.getValue();if(!query.isBlank())Hk3PhoneScreen.command("hk3phone apps collectionsearch 0 "+query);});
                if(v.getBoolean("CollectionExplanation"))host.button("第五百页之后 · 阅读收藏说明",x,y+177,312,()->Hk3PhoneScreen.command("hk3phone apps collectionexplanation"));
                int i=0;for(Tag raw:v.getList("Rows",Tag.TAG_COMPOUND)){
                    var r=(CompoundTag)raw;host.button(r.getString("Title"),x,y+214+i++*30,312,()->Hk3PhoneScreen.command("hk3phone apps entry "+r.getString("Id")));
                }
                int p=v.getInt("Page"),last=Math.max(0,(v.getInt("Total")-1)/8);String f=v.getString("Filter");
                String query=v.getString("Query");
                host.button("上一页",x+142,y+493,80,()->Hk3PhoneScreen.command(query.isEmpty()?"hk3phone apps archive "+(p-1)+" "+f:"hk3phone apps collectionsearch "+(p-1)+" "+query)).active=p>0;
                host.button("下一页",x+232,y+493,80,()->Hk3PhoneScreen.command(query.isEmpty()?"hk3phone apps archive "+(p+1)+" "+f:"hk3phone apps collectionsearch "+(p+1)+" "+query)).active=p<last;
            }
            case "trade"->{
                for(int i=0;i<factions.length;i++){int index=i;host.button((tradeTab==i?"• ":"")+factions[i],x+(i%3)*105,y+111+(i/3)*34,101,()->{tradeTab=index;host.refresh();});}
            }
            default->{}
        }
        machines.init(mode,v,x,y);
    }
    void tick(boolean powered,String mode){
        if(titleBox!=null)titleBox.tick();if(bodyBox!=null)bodyBox.tick();
        if(!powered||!mode.equals("snake")){paused=true;snakeTicks=0;return;}
        if(!paused&&!snake.over()&&++snakeTicks>=4){snakeTicks=0;snake.step();Hk3EggUiClient.send("snake_step","");if(snake.over()){paused=true;host.refresh();}}
    }
    void direction(int dir){
        if(host.mode().equals("snake")){if(!paused){snake.turn(dir);Hk3EggUiClient.send("snake_turn",Integer.toString(dir));}}
        else if(host.mode().equals("tiles2048")){tiles.move(dir);Hk3EggUiClient.send("tiles_move",Integer.toString(dir));}
    }
    boolean key(int key){
        if(!host.mode().equals("snake")&&!host.mode().equals("tiles2048"))return false;
        int dir=switch(key){case 265,87->0;case 262,68->1;case 264,83->2;case 263,65->3;default->-1;};
        if(dir>=0){direction(dir);return true;}
        if(key==32&&host.mode().equals("snake")){if(!snake.over())paused=!paused;host.refresh();return true;}return false;
    }
    static String heading(String mode){return switch(mode){case "diplomacy","diplomacy_read"->"势力联络";case "social","social_chat","social_feed","social_topics"->"微讯息";case "social_ai"->"微讯息 · AI设置";case "notes","note","draft_exit"->"笔记本";case "todos"->"个人待办";case "tiles2048"->"2048";case "snake"->"贪吃蛇";case "trade"->"交易";case "gallery"->Component.translatable("hk3gtl.phone.gallery.title").getString();case "civilization"->"文明总览";case "machines"->"团队机器目录";case "machine_detail"->"机器详情";case "machine_unavailable"->"记录不可用";case "civilization_milestones"->"文明里程碑";case "archive","archive_detail"->"文明档案";case "settings"->"设定";case "notification_settings"->"通知设置";case "about"->"关于手机";case "ae_terminals"->"选择背包中的终端";case "gaze_settings"->"注视度 HUD";default->"阅读";};}
    private void text(GuiGraphics g,String text,int x,int y,int color){g.drawString(Minecraft.getInstance().font,text,x,y,color,false);}
    private void wrap(GuiGraphics g,String text,int x,int y,int w){g.drawWordWrap(Minecraft.getInstance().font,Component.literal(text),x,y,w,0xFFBBC4D3);}
    void render(GuiGraphics g,String mode,CompoundTag v,int x,int y){
        switch(mode){
            case "ae_terminals"->{wrap(g,"选择你要打开的那部终端，沿用它自身的功能与页面。",x,y+107,306);text(g,"第 "+(aePage+1)+" 页",x,y+502,0xFFBBC4D3);}
            case "notes","archive"->{
                if(mode.equals("archive"))text(g,"本人已收录 "+v.getInt("Total")+" / "+v.getInt("Available")+" 篇 · 回看不发奖",x,y+476,0xFFBBC4D3);
                if(v.getInt("Total")==0)wrap(g,mode.equals("notes")?"还没有笔记。记录你的配方、计划或旅途。":"暂无已解锁档案。亲自经历后，记录会出现在这里。",x+10,y+170,288);
                int size=mode.equals("notes")?6:8;
                text(g,"第 "+(v.getInt("Page")+1)+" / "+Math.max(1,(v.getInt("Total")+size-1)/size)+" 页",x,y+502,0xFFBBC4D3);
            }
            case "todos"->{text(g,"已完成 "+v.getInt("Done")+" / "+v.getInt("Total")+" · 点击右侧勾选",x,y+151,0xFFBBC4D3);wrap(g,error.isEmpty()&&v.getInt("Total")==0?"将笔记记为待办并保存后，会列在这里。":error,x,y+459,312);text(g,"第 "+(v.getInt("Page")+1)+" 页",x,y+502,0xFFBBC4D3);}
            case "note"->{text(g,"标题",x,y+107,0xFFBBC4D3);text(g,"正文 · "+body.length()+" / 4096",x,y+156,0xFFBBC4D3);wrap(g,error,x,y+472,312);}
            case "draft_exit"->{wrap(g,"还有未保存的笔记。保存后返回笔记列表，或继续编辑。",x+10,y+143,290);wrap(g,error,x+10,y+185,290);}
            case "tiles2048"->{
                text(g,"得分 "+tiles.score()+"  "+(tiles.over()?"无路可走":tiles.won()?"已达成 2048，可继续":"合并相同数字"),x,y+114,0xFFE8C673);
                int[] b=tiles.cells();
                for(int i=0;i<16;i++){int xx=x+14+i%4*72,yy=y+145+i/4*72;int power=b[i]==0?0:Integer.numberOfTrailingZeros(b[i]);int color=0xFF252E40;
                    if(b[i]>0)color=0xFF000000|Math.min(230,80+power*13)<<16|Math.max(75,180-power*7)<<8|Math.max(70,190-power*9);
                    g.fill(xx,yy,xx+67,yy+67,color);if(b[i]>0)g.drawCenteredString(Minecraft.getInstance().font,""+b[i],xx+33,yy+29,0xFFFFFFFF);
                }
            }
            case "snake"->{
                text(g,"得分 "+snake.score()+"  "+(snake.won()?"完成棋盘":snake.over()?"游戏结束":paused?"已暂停":"方向键 / WASD · 空格暂停"),x,y+114,0xFF8ADEB2);
                int xx=x+12,yy=y+145;g.fill(xx,yy,xx+288,yy+288,0xFF111C24);
                for(int i=0;i<=16;i++){g.fill(xx+i*18,yy,xx+i*18+1,yy+288,0xFF1B303A);g.fill(xx,yy+i*18,xx+288,yy+i*18+1,0xFF1B303A);}
                int index=0;for(int cell:snake.cells()){g.fill(xx+cell%16*18+2,yy+cell/16*18+2,xx+cell%16*18+16,yy+cell/16*18+16,index++==0?0xFFC2F5C4:0xFF5DC597);}
                int f=snake.food();if(f>=0)g.fill(xx+f%16*18+4,yy+f/16*18+4,xx+f%16*18+14,yy+f/16*18+14,0xFFECA376);
            }
            case "civilization"->{
                text(g,"历史最高："+v.getString("CivilizationTitle"),x+10,y+110,0xFFE8C673);
                text(g,"当前核验：C"+v.getInt("CivilizationVerified"),x+10,y+125,0xFFBBC4D3);
                summary(g,x,y+140,"团队研究",v.getInt("ResearchDone")+" / "+v.getInt("ResearchTotal")+" 项",0xFF9CC6F6);
                summary(g,x,y+229,"旧档案收藏（不代表资格）",v.getInt("Archives")+" / "+v.getInt("ArchiveTotal")+" 条",0xFFE8C673);
                wrap(g,"查看团队建设、文明进程与个人经历。",x+10,y+315,290);
            }
            case "civilization_milestones"->{
                text(g,v.getString("Title"),x+8,y+113,0xFFE8C673);
                text(g,"历史最高："+v.getString("Highest"),x+8,y+136,0xFFBBC4D3);
                text(g,"当前核验：C"+v.getInt("Current"),x+8,y+151,0xFFBBC4D3);
                var rows=v.getList("Rows",Tag.TAG_COMPOUND);int yy=y+177;
                for(Tag raw:rows){var r=(CompoundTag)raw;String pending=r.getString("Pending");wrap(g,(r.getBoolean("Done")?"已满足 · ":pending.isEmpty()?"未满足 · ":"待接入 · ")+r.getString("Title")+(pending.isEmpty()?"":"\n"+pending),x+8,yy,296);yy+=43;}
                if(rows.isEmpty())wrap(g,"起始状态；后续等级须逐级满足真实成果。",x+8,yy,296);
                wrap(g,v.getBoolean("LowerReady")?"各级条件累计，查看下方目标继续建设。":"前级成果尚未齐备；单独完成本页也不能跳级。",x+8,y+442,296);
                text(g,"第 "+(v.getInt("Page")+1)+" / 8 页",x,y+502,0xFFBBC4D3);
            }
            case "trade"->{
                g.fill(x,y+191,x+312,y+257,0xFF443A63);
                text(g,factions[tradeTab]+" · 联络商店",x+12,y+204,0xFFE8D7FF);
                text(g,"展示阶段 · 交易暂未开放",x+12,y+229,0xFFE8D7FF);
                String[] categories={"材料","元件","设备","补给"};
                for(int i=0;i<4;i++){int xx=x+i%2*160,yy=y+276+i/2*110;g.fill(xx,yy,xx+152,yy+100,0xFF252C3B);text(g,categories[i],xx+12,yy+13,0xFFEEE6F5);text(g,"暂无上架商品",xx+12,yy+48,0xFF9DA8BC);text(g,"等待报价开放",xx+12,yy+73,0xFF9DA8BC);}
                text(g,"目前不会接单、扣款或交付物品",x,y+513,0xFFBBC4D3);
            }
            default->{}
        }
        machines.render(g,mode,v,x,y);
    }
    private void summary(GuiGraphics g,int x,int y,String label,String value,int accent){
        g.fill(x,y,x+312,y+73,0xFF252C3B);text(g,label,x+14,y+13,accent);text(g,value,x+14,y+42,0xFFF1EFF6);
    }
}
