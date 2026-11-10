package com.sirin.hk3gtl.common.gui;



/**
 * 【文件职责／本轮边界】显示取消、领取和独立实验入口；按实际供电档位展示电流，新增区域沿用缩放逻辑。
 * 【变更记录 #2】2026-09-29 21:06:40（第 2 次编号备注 · 内测5修订100）
 * 删除：取消已被批准规则替代的研究个人独占、旧数值或在线限定分支；历史备注与其他系统保留。
 * 新增／修改：显示取消、领取和独立实验入口；按实际供电档位展示电流，新增区域沿用缩放逻辑。
 * 用途：接通实际证据→付款→研究完成与权限检查；不授予缺真实证据的课题。
 * 边界：编译和账本测试不代表游戏验收；S02至S05正式结构及未接线课题仍未完成。
 * 追溯：logs/research-mainline-r100；R100_FINAL_RECORD。
 */

import com.lowdragmc.lowdraglib.gui.widget.Widget;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.function.Consumer;
import java.util.function.Supplier;

/** 中文说明：该处说明已按当前代码行为整理。*/
/** 中文说明：该处备注已按当前代码行为整理，不使用问号占位。*/
/** 中文说明：该处说明已按当前代码行为整理。*/
/**
 * 【变更记录 #1】2026-09-26 21:56:00（第 1 次备注 · 内测5修订75）
 * 删除：功率行直接堆叠完整EU数值和无参数的研究所不足提示。
 * 新增：安培电压摘要、完整功率悬停提示及所需研究所阶级参数。
 * 修改：保留原交互坐标和支付方式，由语言文件显示“开始研究”。
 * 用途：让高电压研究信息可读，完整用电量在提示中保留；不改变服务器扣能。
 */
/**
 * 【变更记录 #3】2026-09-29 23:37:35（内测5修订101）
 * 删除：本轮被替代的单前置或旧提示分支；其余历史保留。
 * 新增／修改：展示经批准的证据来源与成功要求，区分未完成实验和未付款研究。
 * 用途：补足研究接线并如实保留未接物理执行器及结构审批边界。
 * 追溯：logs/research-mainline-r101；R101_FINAL_RECORD。
 */
/**
 * 【变更记录 #4】2026-09-30 03:24:34（内测5修订108）
 * 删除：无。新增：批准色卡接线及版本追溯。
 * 修改：研究终端功率说明使用Component精确电压色，保留宽度限制。
 * 用途：正确显示与核验，不修改研究逻辑。
 */
public final class Hk3ResearchTerminalWidget extends Widget {
    /** 修订100 · 2026-09-29：增加原付款人取消与待领取材料入口，原有布局保留。 */
    public static final int WIDTH = 520, HEIGHT = 350;
    private static final int CYAN=0xff70e4ea, WHITE=0xffe4e9f6, MUTED=0xff9faec8, GOLD=0xffffd679;
    private final Supplier<CompoundTag> source;
    private final Consumer<String> action;
    private CompoundTag state = new CompoundTag();
    private int ticks, listOffset, detailOffset;
    private String query = "";
    private boolean searchFocus;
    private int draggingBar, detailLineCount;

    /** 中文说明：该处说明已按当前代码行为整理。*/
    public Hk3ResearchTerminalWidget(Supplier<CompoundTag> source, Consumer<String> action) {
        super(0,0,WIDTH,HEIGHT); this.source=source; this.action=action;
    }
    @Override public void writeInitialData(FriendlyByteBuf buf) { super.writeInitialData(buf); state=source.get(); buf.writeNbt(state); }
    @Override public void readInitialData(FriendlyByteBuf buf) { super.readInitialData(buf); accept(buf.readNbt()); }
    @Override public void detectAndSendChanges() {
        super.detectAndSendChanges();
        if (++ticks % 10 != 0) return;
        CompoundTag next=source.get();
        if (!next.equals(state)) { state=next; writeUpdateInfo(51, b -> b.writeNbt(state)); }
    }
    @Override public void readUpdateInfo(int id, FriendlyByteBuf buf) {
        if (id==51) accept(buf.readNbt()); else super.readUpdateInfo(id,buf);
    }
    private void accept(CompoundTag next) {
        if (next==null) next=new CompoundTag();
        if (!next.getString("selected").equals(state.getString("selected"))) detailOffset=0;
        state=next;
    }
    /** 中文说明：该处说明已按当前代码行为整理。*/
    @Override public void handleClientAction(int id, FriendlyByteBuf buf) {
        if (id==51) { action.accept(buf.readUtf(96)); ticks=9; }
        else super.handleClientAction(id,buf);
    }
    /** 中文说明：该处说明已按当前代码行为整理。*/
    @OnlyIn(Dist.CLIENT) private Hk3GuiFit fit() {
        var window=Minecraft.getInstance().getWindow();
        return Hk3GuiFit.centered(Math.max(1,window.getGuiScaledWidth()),Math.max(1,window.getGuiScaledHeight()),WIDTH,HEIGHT,8);
    }
    /** 中文说明：该处说明已按当前代码行为整理。*/
    @Override @OnlyIn(Dist.CLIENT) public boolean isMouseOverElement(double x,double y) {
        return fit().contains(x,y,WIDTH,HEIGHT);
    }
    private void send(String value) { writeClientAction(51,b -> b.writeUtf(value,96)); }
    @OnlyIn(Dist.CLIENT) private String tr(String key,Object... args) { return Component.translatable(key,args).getString(); }
    @OnlyIn(Dist.CLIENT) private String ui(String key,Object... args) { return tr("hk3gtl.research.terminal."+key,args); }
    @OnlyIn(Dist.CLIENT) private String name(String id) { return tr("hk3gtl.research.topic."+id.toLowerCase(Locale.ROOT)); }
    @OnlyIn(Dist.CLIENT) private List<CompoundTag> filtered() {
        List<CompoundTag> rows=new ArrayList<>();
        for (var raw:state.getList("topics",10)) {
            var row=(CompoundTag)raw; String id=row.getString("id");
            if ((id+" "+name(id)).toLowerCase(Locale.ROOT).contains(query.toLowerCase(Locale.ROOT))) rows.add(row);
        }
        return rows;
    }
    @OnlyIn(Dist.CLIENT) private void text(GuiGraphics g,String s,int x,int y,int color,int width) {
        var f=Minecraft.getInstance().font;
        String shown=f.width(s)>width ? f.plainSubstrByWidth(s,Math.max(0,width-8))+"…" : s;
        g.drawString(f,shown,x,y,color,false);
    }
    @OnlyIn(Dist.CLIENT) private void text(GuiGraphics g,Component value,int x,int y,int color,int width) {
        var f=Minecraft.getInstance().font;
        var lines=f.split(value,Math.max(1,width-8));
        if(!lines.isEmpty()) g.drawString(f,lines.get(0),x,y,color,false);
        if(lines.size()>1) g.drawString(f,"…",x+width-8,y,color,false);
    }
    @OnlyIn(Dist.CLIENT) private void panel(GuiGraphics g,int x,int y,int w,int h,int edge,int fill) {
        g.fill(x,y,x+w,y+h,edge); g.fill(x+1,y+1,x+w-1,y+h-1,fill);
    }
    /** 中文说明：该处说明已按当前代码行为整理。*/
    @Override @OnlyIn(Dist.CLIENT) public void drawInBackground(GuiGraphics g,int mouseX,int mouseY,float partial) {
        g.pose().pushPose(); var fit=fit(); g.pose().translate(fit.left(),fit.top(),0);
        g.pose().scale((float)fit.scale(),(float)fit.scale(),1);
        panel(g,0,0,WIDTH,HEIGHT,0xff6374a0,0xff111725);
        panel(g,5,5,510,22,0xff574783,0xff201b36);
        g.fill(6,6,9,26,CYAN); text(g,ui("title"),15,12,WHITE,220);
        text(g,"HK3GTL / RESEARCH",365,12,0xffb49be8,143);
        panel(g,7,33,149,19,searchFocus?CYAN:0xff364b65,0xff090f1b);
        text(g,query.isEmpty()?ui("search"):query,13,39,query.isEmpty()?MUTED:WHITE,137);
        var rows=filtered(); listOffset=Math.max(0,Math.min(listOffset,Math.max(0,rows.size()-8)));
        for(int i=0;i<8 && i+listOffset<rows.size();i++) {
            var r=rows.get(i+listOffset); int y=56+i*28; int status=r.getInt("state");
            boolean selected=r.getString("id").equals(state.getString("selected"));
            int edge=selected?CYAN:status==0?0xffc55e79:status==1?0xffd5b367:status==2?0xffa390ef:0xff55bda0;
            int fill=selected?0xff254675:status==0?0xff452838:status==1?0xff594a2d:status==2?0xff342b53:0xff203f3d;
            panel(g,7,y,143,26,edge,fill); g.fill(8,y+1,10,y+25,edge);
            // 斜切电路线为原创几何装饰，颜色同时配合文字，不仅依赖色觉。
            // 中文备注：该处说明已按当前代码行为整理。
            for(int k=0;k<12;k++) g.fill(128+k,y+23-k,130+k,y+24-k,edge & 0x33ffffff | 0x33000000);
            ItemStack icon=ItemStack.of(r.getCompound("icon")); g.renderItem(icon,13,y+5);
            text(g,name(r.getString("id")),34,y+4,WHITE,110);
            text(g,ui("state."+status),34,y+15,edge,109);
        }
        if(rows.isEmpty()) text(g,ui("empty"),13,64,MUTED,137);
        scrollbar(g,152,56,222,rows.size(),8,listOffset);
        text(g,(rows.isEmpty()?0:listOffset+1)+"–"+Math.min(rows.size(),listOffset+8)+" / "+rows.size(),12,285,MUTED,142);
        panel(g,162,33,351,172,0xff40536e,0xff080e18);
        String selected=state.getString("selected");
        text(g,name(selected),170,40,WHITE,230);
        text(g,"S"+state.getInt("requiredLab")+" / T"+state.getInt("tier"),432,40,CYAN,72);
        g.fill(170,53,505,54,0xff4c456d);
        List<Component> lines=description(); var f=Minecraft.getInstance().font;
        List<net.minecraft.util.FormattedCharSequence> wrapped=new ArrayList<>();
        for(Component line:lines) wrapped.addAll(f.split(line,325));
        detailLineCount=wrapped.size();
        detailOffset=Math.max(0,Math.min(detailOffset,Math.max(0,wrapped.size()-9)));
        g.enableScissor((int)Math.floor(fit.screenX(168)),(int)Math.floor(fit.screenY(58)),
                (int)Math.ceil(fit.screenX(506)),(int)Math.ceil(fit.screenY(157)));
        for(int i=detailOffset;i<Math.min(wrapped.size(),detailOffset+9);i++) g.drawString(f,wrapped.get(i),170,59+(i-detailOffset)*11,WHITE,false);
        g.disableScissor(); scrollbar(g,507,57,99,wrapped.size(),9,detailOffset);
        g.fill(170,159,505,160,0xff4c456d);
        text(g,ui("cost",state.getLong("cost")),170,166,GOLD,327);
        text(g,Component.translatable("hk3gtl.research.terminal.time",state.getLong("seconds"),powerSummary()),170,179,CYAN,327);
        String notice=state.getString("feedback");
        if(notice.isEmpty()) notice=state.getString("blocker");
        text(g,notice.isEmpty()?ui("experiment",ui(state.getBoolean("experiment")?"yes":"no")):notice(notice).getString(),170,192,notice.isEmpty()?CYAN:0xfff087a0,327);
        panel(g,162,211,130,57,0xff40536e,0xff080e18);
        text(g,ui("lab",state.getInt("lab"),state.getInt("active"),state.getInt("slots")),168,217,CYAN,118);
        text(g,ui("points",state.getString("points")),168,230,GOLD,118);
        String status=!state.getBoolean("authorized")?"waiting":!state.getBoolean("formed")?"unformed":!state.getBoolean("enabled")?"paused":state.getBoolean("running")&&!state.getBoolean("localJob")?"remote":state.getBoolean("running")&&!state.getBoolean("powered")?"power":state.getBoolean("running")?"running":state.getBoolean("done")?"done":"idle";
        text(g,ui(status),168,243,MUTED,118);
        g.fill(168,258,286,262,0xff26334b);
        g.fill(168,258,168+(int)(118*state.getDouble("progress")),262,CYAN);
        panel(g,298,211,215,57,0xff40536e,0xff080e18);
        text(g,ui("materials"),304,216,MUTED,202);
        ListTag materials=state.getList("materials",10);
        for(int i=0;i<materials.size();i++) {
            int x=304+(i%6)*34,y=229+(i/6)*34; var m=materials.getCompound(i);
            panel(g,x,y,29,33,m.getLong("available")>=m.getLong("count")?0xff438f87:0xff75485d,0xff162134);
            g.renderItem(ItemStack.of(m.getCompound("item")),x+6,y+2);
            text(g,Long.toString(m.getLong("count")),x+2,y+22,WHITE,26);
        }
        button(g,162,273,110,"pointsButton",state.getBoolean("canStart"));
        button(g,276,273,119,"materialsButton",state.getBoolean("canStart"));
        button(g,399,273,114,state.getBoolean("enabled")?"pause":"resume",state.getBoolean("authorized"));
        button(g,162,299,169,"cancel",state.getBoolean("canCancel"));
        button(g,337,299,176,"claim",state.getInt("refunds")>0);
        button(g,162,325,169,"experimentButton",state.getBoolean("canExperiment"));
        text(g,ui(state.getBoolean("labExperiment")?"experimentRunning":"experimentHint"),338,331,MUTED,172);
        g.pose().popPose();
    }
    @OnlyIn(Dist.CLIENT) private List<Component> description() {
        List<Component> result=new ArrayList<>();
        String selected=state.getString("selected");
        if(selected.equals("RN-ALE") || selected.equals("RN-ERM") || selected.equals("RN-OPR"))
            result.add(Component.translatable("hk3gtl.research.terminal.experiment."+selected.substring(3).toLowerCase(Locale.ROOT)));
        result.add(Component.literal(ui("story")).withStyle(net.minecraft.ChatFormatting.LIGHT_PURPLE));
        result.add(Component.literal(state.getString("story")));
        result.add(Component.literal(""));
        result.add(Component.literal(ui("result")+state.getString("result")).withStyle(net.minecraft.ChatFormatting.AQUA));
        result.add(Component.literal(""));
        result.add(Component.literal(ui("evidence")+state.getString("evidence")));
        if(!state.getString("executionSource").isEmpty()){
            result.add(Component.translatable("hk3gtl.research.execution.source",state.getString("executionSource")));
            result.add(Component.translatable("hk3gtl.research.execution.success",state.getString("executionSuccess")));
        }
        result.add(Component.literal(""));
        ListTag prereqs=state.getList("prerequisites",10);
        if(prereqs.isEmpty()) result.add(Component.literal(ui("noPrerequisites")));
        for(var raw:prereqs) { var p=(CompoundTag)raw; result.add(Component.literal((p.getBoolean("done")?"✓ ":"× ")+name(p.getString("id"))).withStyle(p.getBoolean("done")?net.minecraft.ChatFormatting.GREEN:net.minecraft.ChatFormatting.RED)); }
        String feedback=state.getString("feedback"); if(!feedback.isEmpty()) result.add(notice(feedback).withStyle(net.minecraft.ChatFormatting.GOLD));
        result.add(Component.literal(ui("remaining",state.getLong("remaining"))));
        return result;
    }
    @OnlyIn(Dist.CLIENT) private net.minecraft.network.chat.MutableComponent notice(String key) {
        return "hk3gtl.research.terminal.block.lab".equals(key)
                ? Component.translatable(key, tr("hk3gtl.research.lab.grade."+state.getInt("requiredLab")))
                : Component.translatable(key);
    }
    @OnlyIn(Dist.CLIENT) private Component powerSummary() {
        int tier=Math.max(0,Math.min(30,state.getInt("powerTier")));
        long voltage=com.sirin.hk3gtl.common.constants.Hk3Values.VA_LONG[tier];
        String amps=java.math.BigDecimal.valueOf(state.getLong("eut"))
                .divide(java.math.BigDecimal.valueOf(voltage),4,java.math.RoundingMode.HALF_UP)
                .stripTrailingZeros().toPlainString();
        Component voltageText = tier >= 15
                ? Component.literal(com.sirin.hk3gtl.common.constants.Hk3Values.getVN(tier)).withStyle(style ->
                    style.withColor(com.sirin.hk3gtl.common.constants.Hk3VoltagePalette.text(tier)).withBold(true))
                : Component.literal(com.sirin.hk3gtl.common.constants.Hk3Values.getVNF(tier));
        return Component.literal(amps+"A (").append(voltageText).append(") / t");
    }
    @OnlyIn(Dist.CLIENT) private void button(GuiGraphics g,int x,int y,int w,String key,boolean enabled) {
        panel(g,x,y,w,20,enabled?0xff8771b4:0xff344159,enabled?0xff2a2343:0xff151c29);
        text(g,ui(key),x+5,y+6,enabled?WHITE:MUTED,w-10);
    }
    @OnlyIn(Dist.CLIENT) private void scrollbar(GuiGraphics g,int x,int y,int h,int count,int visible,int offset) {
        g.fill(x,y,x+3,y+h,0xff24314a);
        int thumb=count<=visible?h:Math.max(12,h*visible/count);
        int top=count<=visible?0:(h-thumb)*offset/(count-visible);
        g.fill(x,y+top,x+3,y+top+thumb,0xff8798c8);
    }
    @Override @OnlyIn(Dist.CLIENT) public void drawInForeground(GuiGraphics g,int mx,int my,float partial) {
        int x=(int)Math.floor(fit().x(mx)),y=(int)Math.floor(fit().y(my));
        if(x>=170 && x<505 && y>=175 && y<187) {
            g.renderComponentTooltip(Minecraft.getInstance().font,List.of(
                    Component.translatable("hk3gtl.research.terminal.powerExact",
                            String.format(Locale.ROOT,"%,d",state.getLong("eut")))),mx,my);
            return;
        }
        if(x>=162 && x<513 && y>=187 && y<205) {
            String notice=state.getString("feedback");
            if(notice.isEmpty()) notice=state.getString("blocker");
            if(!notice.isEmpty()) g.renderTooltip(Minecraft.getInstance().font,
                    Minecraft.getInstance().font.split(notice(notice),300),mx,my);
        }
        if(x>=7 && x<150 && y>=56 && y<280) {
            var rows=filtered(); int index=listOffset+(y-56)/28;
            if(index<rows.size()) { var row=rows.get(index);
                g.renderComponentTooltip(Minecraft.getInstance().font,List.of(Component.literal(name(row.getString("id"))),
                        Component.literal(row.getString("id")+" · S"+row.getInt("lab")),Component.literal(ui("state."+row.getInt("state")))),mx,my);
            }
        }
        if(x>=162 && y>=273 && y<293 && !state.getString("feedback").isEmpty())
            g.renderComponentTooltip(Minecraft.getInstance().font,List.of(notice(state.getString("feedback"))),mx,my);
        ListTag materials=state.getList("materials",10);
        for(int i=0;i<materials.size();i++) if(x>=304+i*34 && x<333+i*34 && y>=229 && y<262) {
            var m=materials.getCompound(i); ItemStack stack=ItemStack.of(m.getCompound("item"));
            g.renderComponentTooltip(Minecraft.getInstance().font,List.of(stack.isEmpty()?Component.translatable("hk3gtl.research.lab.unavailable_material"):stack.getHoverName(),Component.literal(ui("quantity",m.getLong("available"),m.getLong("count"))),Component.literal(m.getString("tag"))),mx,my);
        }
    }
    /** 中文说明：该处说明已按当前代码行为整理。*/
    @Override @OnlyIn(Dist.CLIENT) public boolean mouseClicked(double mx,double my,int button) {
        if(!isMouseOverElement(mx,my)) return false;
        int x=(int)Math.floor(fit().x(mx)),y=(int)Math.floor(fit().y(my));
        searchFocus=x>=7 && x<156 && y>=33 && y<52;
        if(button!=0) return true;
        draggingBar=x>=150 && x<157 && y>=56 && y<278 ? 1 : x>=505 && x<513 && y>=57 && y<156 ? 2 : 0;
        if(draggingBar!=0) { dragScroll(y); return true; }
        if(x>=7 && x<150 && y>=56 && y<280) {
            var rows=filtered(); int index=listOffset+(y-56)/28;
            if(index<rows.size()) send("select:"+rows.get(index).getString("id"));
        }
        if(y>=273 && y<293) {
            if(x>=162 && x<272 && state.getBoolean("authorized")) send("points");
            else if(x>=276 && x<395 && state.getBoolean("authorized")) send("materials");
            else if(x>=399 && x<513) send("toggle");
        }
        if(y>=299 && y<319) {
            if(x>=162 && x<331 && state.getBoolean("canCancel")) send("cancel");
            if(x>=337 && x<513 && state.getInt("refunds")>0) send("claim");
        }
        if(y>=325 && y<345 && x>=162 && x<331 && state.getBoolean("canExperiment"))send("experiment");
        return true;
    }
    /** 中文说明：该处说明已按当前代码行为整理。*/
    @OnlyIn(Dist.CLIENT) private void dragScroll(double y) {
        double ratio=Math.max(0,Math.min(1,(y-(draggingBar==1?56:57))/(draggingBar==1?222.0:99.0)));
        if(draggingBar==1) listOffset=(int)Math.round(ratio*Math.max(0,filtered().size()-8));
        else detailOffset=(int)Math.round(ratio*Math.max(0,detailLineCount-9));
    }
    @Override @OnlyIn(Dist.CLIENT) public boolean mouseDragged(double x,double y,int button,double dx,double dy) {
        if(draggingBar==0) return false; dragScroll(fit().y(y)); return true;
    }
    @Override @OnlyIn(Dist.CLIENT) public boolean mouseReleased(double x,double y,int button) {
        boolean wasDragging=draggingBar!=0; draggingBar=0; return wasDragging;
    }
    @Override @OnlyIn(Dist.CLIENT) public boolean mouseWheelMove(double mx,double my,double delta) {
        if(!isMouseOverElement(mx,my)) return false;
        int x=(int)Math.floor(fit().x(mx)),y=(int)Math.floor(fit().y(my)),step=delta>0?-1:1;
        if(x<157) listOffset=Math.max(0,Math.min(Math.max(0,filtered().size()-8),listOffset+step));
        else if(y<160) detailOffset=Math.max(0,detailOffset+step);
        return true;
    }
    @Override @OnlyIn(Dist.CLIENT) public boolean charTyped(char c,int modifiers) {
        if(!searchFocus) return false;
        if(!Character.isISOControl(c) && query.length()<64) { query+=c; listOffset=0; }
        return true;
    }
    @Override @OnlyIn(Dist.CLIENT) public boolean keyPressed(int key,int scan,int modifiers) {
        if(!searchFocus) return false;
        if(key==256 || key==257) searchFocus=false;
        else if(key==259 && !query.isEmpty()) { query=query.substring(0,query.offsetByCodePoints(query.length(),-1)); listOffset=0; }
        return true;
    }
}
