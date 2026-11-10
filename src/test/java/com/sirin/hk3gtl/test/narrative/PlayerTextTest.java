package com.sirin.hk3gtl.test.narrative;

import com.sirin.hk3gtl.common.phone.*;
import com.sirin.hk3gtl.common.narrative.*;
import net.minecraft.nbt.CompoundTag;
import java.util.*;
import java.util.function.Function;

/** 修订155：核验原tier映射、旧收件箱投影及个人账本不变性。 */
/** 【变更记录 #1】2026-10-01 22:50:14（第1次备注 · 内测5修订155）：删除玩家展示中的旧电压及开发说明；新增现行正文投影或对应回归；修改仅限呈现与检索，不改变进度、回执、触发条件或权限；用途：统一发布版玩家文案，历史备注保留。 */
public final class PlayerTextTest {
    private static void check(boolean value,String why){if(!value)throw new AssertionError(why);}
    public static void run(Function<String,String> tr){
        String[] groups={"海渊","虚数","量子","终焉"};
        String[] names={"崩能压","约束压","谐振压","致密压","叠态压","相干压","纠缠压","锚定压","虚数压","耦合压","重构压","织界压","构界压","稳界压","统合压","恒续压"};
        String[][] ordinals={{"I","II","III","IV"},{"Ⅰ","Ⅱ","Ⅲ","Ⅳ"},{"一","二","三","四"},{"1","2","3","4"}};
        for(int g=0;g<4;g++)for(int i=0;i<4;i++)for(var nums:ordinals)
            check(Hk3PhonePresentation.voltage(groups[g]+" "+nums[i]+"级电压").equals(names[g*4+i]),"原tier一一对应");
        String lore="量子之海，虚数之树，终焉之茧，崩坏能/量子/虚数三领域";
        check(lore.equals(Hk3PhonePresentation.voltage(lore)),"剧情专有概念不变");
        check(Hk3PhonePresentation.voltage("Quantum-II").equals("ICV"),"英文旧电压映射");
        UUID actor=UUID.randomUUID(),other=UUID.randomUUID();var data=new Hk3PhoneData();
        var node=Hk3NarrativeNodes.EG_003;String id="narrative_"+node.id();
        data.add(actor,id,"档案解锁｜旧标题","额外收藏不阻断终审。虚数II",73,"chatter",node.id(),true);
        data.read(actor,id);var before=data.save(new CompoundTag());
        var display=Hk3PhonePresentation.current(data.entry(actor,id),tr);
        check(display.title().equals(tr.apply(node.titleKey())),"旧消息完整标题取现行目录");
        check(display.body().equals(Hk3CollectionRecords.body(node,tr)),"旧消息正文同源");
        check(display.time()==73&&display.read()&&display.pending()&&display.id().equals(id)&&display.target().equals(node.id()),"投影保留消息身份与业务状态");
        check(data.search(actor,"all",display.title(),e->Hk3PhonePresentation.current(e,tr)).size()==1,"搜索当前标题");
        check(data.search(actor,"all","档案解锁",e->Hk3PhonePresentation.current(e,tr)).isEmpty(),"搜索不残留旧前缀");
        check(data.search(other,"all",display.title(),e->Hk3PhonePresentation.current(e,tr)).isEmpty(),"搜索不泄露他人记录");
        check(before.equals(data.save(new CompoundTag())),"呈现与搜索不写回存档");
        var restored=Hk3PhoneData.load(before);
        check(Hk3PhonePresentation.current(restored.entry(actor,id),tr).equals(display),"重载后继续使用当前正文");
        var note=new Hk3PhoneData.Entry("note","虚数II","档案解锁",1,false,"note","",false);
        check(Hk3PhonePresentation.current(note,tr)==note,"不改写玩家笔记");
        System.out.println("Player text: 16 tiers, preserved lore, current titles/search and unchanged inbox verified");
    }
}
