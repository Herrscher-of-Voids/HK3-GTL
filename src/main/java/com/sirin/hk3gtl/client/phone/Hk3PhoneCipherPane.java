package com.sirin.hk3gtl.client.phone;

import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.EditBox;
import net.minecraft.client.gui.components.MultiLineEditBox;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.util.FormattedCharSequence;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.function.UnaryOperator;

final class Hk3PhoneCipherPane {
    private static final int LINES=12;
    private static final Map<Integer,String> DRAFTS=new HashMap<>();
    private static final Deque<String> HISTORY=new ArrayDeque<>();
    private static String work="";
    private static boolean workbench;
    private final Hk3PhoneScreen host;
    private final List<FormattedCharSequence> lines=new ArrayList<>();
    private final List<CompoundTag> inventory=new ArrayList<>();
    private int page=-1,stage,total,textPage;
    private int relicPage,relicMask,selectedSlot=-1;
    private String hint="";
    private boolean completed,jumpToHint,seaVisited,giftFound,inSeedSea,revelation;
    private EditBox answerBox;
    private MultiLineEditBox workBox;
    private Button submit;

    Hk3PhoneCipherPane(Hk3PhoneScreen host){this.host=host;}

    static void reset(){DRAFTS.clear();HISTORY.clear();work="";workbench=false;}

    void accept(CompoundTag view){
        int next=view.getInt("Page");
        jumpToHint=page==next&&relicPage==view.getInt("RelicPage")&&!hint.equals(view.getString("Hint"));
        if(page!=next||relicPage!=view.getInt("RelicPage"))textPage=0;
        page=next;stage=view.getInt("Stage");total=view.getInt("Total");
        hint=view.getString("Hint");completed=view.getBoolean("Completed");
        seaVisited=view.getBoolean("SeaVisited");giftFound=view.getBoolean("GiftFound");
        inSeedSea=view.getBoolean("InSeedSea");
        revelation=view.getBoolean("Revelation");relicPage=view.getInt("RelicPage");relicMask=view.getInt("RelicMask");
        inventory.clear();
        for(Tag row:view.getList("Inventory",Tag.TAG_COMPOUND))inventory.add((CompoundTag)row);
        if(inventory.stream().noneMatch(row->row.getInt("Slot")==selectedSlot))selectedSlot=-1;
        if(page==total)workbench=false;
    }

    void init(CompoundTag view,int x,int y){
        if(workbench){initWorkbench(x,y);return;}
        lines.clear();
        add(view.getString("Title")+"\n\n"+view.getString("Body"));
        if(!hint.isEmpty())add("\n"+tr("section.hint")+"\n"+hint);
        if(!view.getString("Keys").isEmpty())add("\n"+tr("section.keys")+"\n"+view.getString("Keys"));
        if(!view.getString("Feedback").isEmpty())add("\n"+tr("section.feedback")+"\n"+view.getString("Feedback"));
        textPage=jumpToHint?pages()-1:Math.min(textPage,pages()-1);jumpToHint=false;
        if(revelation){
            host.button("外封",x,y+138,64,()->openPage(total-1));
            for(int i=0;i<4;i++){
                int target=i;
                host.button(((relicMask&1<<i)!=0?"✓":"")+"残页"+(i+1),x+70+i*62,y+138,56,
                    ()->Hk3PhoneScreen.command("hk3phone apps cipher relic page "+target)).active=i!=relicPage;
            }
        }else{
            host.button(tr("pagePrevious"),x,y+138,100,()->openPage(page-1)).active=page>0;
            host.button(tr(completed?"voyage.current":"pageCurrent"),x+106,y+138,100,()->Hk3PhoneScreen.command("hk3phone apps cipher")).active=page!=stage;
            host.button(tr("pageNext"),x+212,y+138,100,()->openPage(page+1)).active=page<stage&&page<total;
        }
        host.button(tr("textPrevious"),x+142,y+322,80,()->{textPage--;host.refresh();}).active=textPage>0;
        host.button(tr("textNext"),x+232,y+322,80,()->{textPage++;host.refresh();}).active=textPage+1<pages();
        if(page==total){
            if(revelation){initRevelation(x,y);return;}
            if(giftFound)host.button(tr("voyage.letter"),x,y+434,312,()->Hk3PhoneScreen.command("hk3phone apps cipher"));
            if(inSeedSea)host.button(tr("voyage.return"),x,y+477,312,()->Hk3PhoneScreen.command("hk3phone apps cipher return"));
            return;
        }
        answerBox=host.widget(new EditBox(Minecraft.getInstance().font,x+4,y+399,304,24,Component.literal(tr("placeholder"))));
        answerBox.setMaxLength(160);answerBox.setValue(DRAFTS.getOrDefault(page,""));answerBox.setEditable(current());
        submit=host.button(tr("submit"),x,y+434,148,this::submit);
        submit.active=current()&&!answerBox.getValue().isBlank();
        answerBox.setResponder(value->{DRAFTS.put(page,value);submit.active=current()&&!value.isBlank();});
        host.button(tr("hint"),x+164,y+434,148,()->Hk3PhoneScreen.command("hk3phone apps cipher hint")).active=current()&&hint.isEmpty();
        host.button(tr("workbench"),x,y+477,312,()->{workbench=true;host.refresh();});
    }

    private void initRevelation(int x,int y){
        host.button("上件",x,y+399,52,()->selectItem(-1)).active=!inventory.isEmpty();
        host.button(selectedItem(),x+58,y+399,196,()->selectItem(1)).active=!inventory.isEmpty();
        host.button("下件",x+260,y+399,52,()->selectItem(1)).active=!inventory.isEmpty();
        host.button((relicMask&1<<relicPage)!=0?"此页已校读":"用所选实物校读此页",x,y+434,312,
            ()->Hk3PhoneScreen.command("hk3phone apps cipher relic submit "+selectedSlot))
            .active=selectedSlot>=0&&(relicMask&1<<relicPage)==0;
        if(relicMask==15||giftFound)host.button(tr(giftFound?"voyage.letter":"voyage.archive"),x,y+477,148,
            ()->Hk3PhoneScreen.command("hk3phone apps cipher"));
        else host.button("补充依据",x,y+477,148,()->Hk3PhoneScreen.command("hk3phone apps cipher relic hint")).active=hint.isEmpty();
        if(inSeedSea)host.button(tr("voyage.return"),x+164,y+477,148,()->Hk3PhoneScreen.command("hk3phone apps cipher return"));
    }

    private void selectItem(int direction){
        int index=-1;
        for(int i=0;i<inventory.size();i++)if(inventory.get(i).getInt("Slot")==selectedSlot)index=i;
        if(index<0)index=direction>0?0:inventory.size()-1;
        else index=Math.floorMod(index+direction,inventory.size());
        selectedSlot=inventory.get(index).getInt("Slot");host.refresh();
    }

    private String selectedItem(){
        for(var item:inventory)if(item.getInt("Slot")==selectedSlot)
            return (selectedSlot<9?"快捷栏 "+(selectedSlot+1):"背包 "+(selectedSlot-8))+" · "+item.getString("Name");
        return inventory.isEmpty()?"背包中没有可选实物":"选择背包实物";
    }

    private void initWorkbench(int x,int y){
        host.button(tr("bench.return"),x,y+107,312,()->{workbench=false;host.refresh();});
        workBox=host.widget(new MultiLineEditBox(Minecraft.getInstance().font,x+4,y+183,304,138,
            Component.literal(tr("bench.placeholder")),Component.literal(tr("workbench"))){
            @Override public void renderWidget(GuiGraphics g,int mx,int my,float delta){
                if(!visible)return;
                renderBackground(g);host.clip(g,getX()+1,getY()+1,getX()+getWidth()-1,getY()+getHeight()-1);
                g.pose().pushPose();g.pose().translate(0,-scrollAmount(),0);
                renderContents(g,mx,my,delta);g.pose().popPose();g.disableScissor();renderDecorations(g);
            }
        });
        workBox.setCharacterLimit(Math.max(1024,work.length()));workBox.setValue(work);workBox.setValueListener(value->work=value);
        host.button(tr("bench.shiftBack"),x,y+335,100,()->transform(value->shift(value,-1)));
        host.button(tr("bench.shiftForward"),x+106,y+335,100,()->transform(value->shift(value,1)));
        host.button(tr("bench.reverse"),x+212,y+335,100,()->transform(value->new StringBuilder(value).reverse().toString()));
        host.button(tr("bench.group"),x,y+373,148,()->transform(Hk3PhoneCipherPane::group));
        host.button(tr("bench.undo"),x+164,y+373,148,()->{work=HISTORY.pop();host.refresh();}).active=!HISTORY.isEmpty();
        host.button(tr("bench.copy"),x,y+416,312,()->{DRAFTS.put(page,work);workbench=false;host.refresh();}).active=current()&&work.length()<=160;
        host.button(tr("bench.draft"),x,y+455,312,()->transform(value->DRAFTS.getOrDefault(page,"")));
    }

    void render(GuiGraphics g,CompoundTag view,int x,int y){
        var font=Minecraft.getInstance().font;
        if(workbench){
            g.drawWordWrap(font,Component.literal(tr("bench.description")),x,y+145,306,Hk3PhoneStyle.INK);
            g.drawWordWrap(font,Component.literal(tr("bench.note")),x,y+500,306,Hk3PhoneStyle.MUTED);
            return;
        }
        g.drawString(font,font.plainSubstrByWidth(view.getString("Title"),312),x,y+107,Hk3PhoneStyle.GOLD,false);
        g.drawString(font,revelation?"实物校读 "+Integer.bitCount(relicMask)+" / 4 · 残页 "+(relicPage+1):tr("stage",stage,total),x,y+123,Hk3PhoneStyle.MUTED,false);
        g.fill(x,y+174,x+312,y+315,0xFF121827);
        for(int i=0;i<LINES&&textPage*LINES+i<lines.size();i++)
            g.drawString(font,lines.get(textPage*LINES+i),x+6,y+179+i*11,Hk3PhoneStyle.INK,false);
        g.drawString(font,tr("textPage",textPage+1,pages()),x,y+331,Hk3PhoneStyle.MUTED,false);
        String feedback=view.getString("Feedback");
        if(!feedback.isEmpty())g.drawString(font,font.plainSubstrByWidth(tr("feedback",feedback),312),x,y+362,Hk3PhoneStyle.GOLD,false);
        g.drawString(font,revelation?"选择实际槽位，再主动校读当前残页":tr(page==total?"voyage.archive":current()?"answer":"review"),x,y+383,Hk3PhoneStyle.MUTED,false);
        String status=giftFound?"voyage.complete":seaVisited?"voyage.explore":"voyage.ready";
        g.drawString(font,revelation&&relicMask!=15?"实物会保留，校读结果随本人保存。":tr(page==total?status:"draft"),x,y+518,Hk3PhoneStyle.MUTED,false);
    }

    void tick(){if(workbench)workBox.tick();else if(page<total)answerBox.tick();}

    boolean key(int key){
        if(!workbench&&page<total&&(key==257||key==335)&&answerBox.isFocused()){if(submit.active)submit();return true;}
        return false;
    }

    private boolean current(){return page==stage&&!completed;}
    private void submit(){Hk3PhoneScreen.command("hk3phone apps cipher answer "+answerBox.getValue().strip());}
    private void openPage(int target){Hk3PhoneScreen.command("hk3phone apps cipher page "+target);}
    private void transform(UnaryOperator<String> operation){HISTORY.push(work);work=operation.apply(work);host.refresh();}
    private void add(String value){lines.addAll(Minecraft.getInstance().font.split(Component.literal(value),300));}
    private int pages(){return Math.max(1,(lines.size()+LINES-1)/LINES);}
    private static String tr(String key,Object... args){return Component.translatable("hk3gtl.phone.cipher."+key,args).getString();}

    private static String shift(String value,int amount){
        var result=new StringBuilder();
        for(char c:value.toCharArray())result.append(c>='A'&&c<='Z'?(char)('A'+Math.floorMod(c-'A'+amount,26)):
            c>='a'&&c<='z'?(char)('a'+Math.floorMod(c-'a'+amount,26)):c);
        return result.toString();
    }

    private static String group(String value){
        int[] letters=value.replaceAll("\\s+","").codePoints().toArray();
        var result=new StringBuilder();
        for(int i=0;i<letters.length;i++){if(i>0&&i%3==0)result.append(' ');result.appendCodePoint(letters[i]);}
        return result.toString();
    }
}
