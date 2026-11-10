package com.sirin.hk3gtl.test.phone;

import com.sirin.hk3gtl.common.event.Hk3VoidGiftData;
import net.minecraft.nbt.*;
import java.util.*;

/** 【变更记录 #1】2026-10-01 01:36:39（修订126）：删除无；新增名字匹配、全部逐件失败组合、重登、换名、重生后账本恢复和精确电量测试；修改无；用途：外部物品和满背包不被误记为领取，不以测试代替实际入服。 */
public final class VoidGiftTest {
    private static int checks;
    private static void check(boolean v,String message){if(!v)throw new AssertionError(message);checks++;}
    public static void main(String[] args){
        check(Hk3VoidGiftData.matches("Herrscher_Void")&&Hk3VoidGiftData.matches("herrscher_void"),"名字忽略大小写");
        for(String name:Arrays.asList("xiguamao","Herrscher_Void_","Other",null))check(!Hk3VoidGiftData.matches(name),"其他名字不触发");
        check(Hk3VoidGiftData.GIFTS.size()==3,"仅三件物品");
        check(Hk3VoidGiftData.GIFTS.stream().map(Hk3VoidGiftData.Gift::item).toList().equals(List.of("hk3gtl:personal_phone","sov:spear_of_void","sov:spear_of_void_5x")),"精确物品ID");
        var tag=Hk3VoidGiftData.GIFTS.get(0).tag();check(tag.contains("Charge",Tag.TAG_LONG)&&tag.getLong("Charge")==128000L,"满电必须是long NBT");
        tag.putLong("Charge",0);check(Hk3VoidGiftData.GIFTS.get(0).tag().getLong("Charge")==128000L,"NBT生成不共用可变对象");
        check(Hk3VoidGiftData.GIFTS.get(1).tag().isEmpty()&&Hk3VoidGiftData.GIFTS.get(2).tag().isEmpty(),"长矛不附加手机NBT");
        for(int mask=0;mask<8;mask++){
            UUID id=UUID.randomUUID(),other=UUID.randomUUID();var data=new Hk3VoidGiftData();final int allowed=mask;
            check(!data.enroll(other,"xiguamao")&&data.deliver(other,i->true)==0,"不干扰旧彩蛋");
            check(data.enroll(id,"Herrscher_Void")&&!data.enroll(id,"Herrscher_Void"),"同一玩家只登记一次");
            var awarded=new HashSet<Integer>();int amount=data.deliver(id,i->{if((allowed&(1<<i))==0)return false;check(awarded.add(i),"首次不重复");return true;});
            check(amount==Integer.bitCount(mask),"满背包或缺模组未发出的不记领取");
            var restored=Hk3VoidGiftData.load(data.save(new CompoundTag()));
            check(!restored.enroll(id,"DifferentName")&&!restored.enroll(id,"Herrscher_Void"),"换名重登不重置");
            restored.deliver(id,i->{check(awarded.add(i),"恢复只补未发项");return true;});
            check(awarded.size()==3&&!restored.pending(id),"最终正好三件");
            var afterDeath=Hk3VoidGiftData.load(restored.save(new CompoundTag()));
            check(afterDeath.deliver(id,i->{throw new AssertionError("死亡/重登不能再发");})==0,"按存档UUID而非玩家实体去重");
            check(!afterDeath.enrolled(other),"玩家隔离");
        }
        UUID id=UUID.randomUUID();var data=new Hk3VoidGiftData();data.enroll(id,"Herrscher_Void");
        try{data.deliver(id,i->{if(i==1)throw new IllegalStateException("模拟第二件失败");return true;});}catch(IllegalStateException expected){}
        var seen=new ArrayList<Integer>();data.deliver(id,i->{seen.add(i);return true;});check(seen.equals(List.of(1,2)),"部分异常不重复送第一件");
        var guard=new Hk3VoidGiftData();guard.enroll(id,"Herrscher_Void");boolean blocked=false;
        try{guard.deliver(id,i->{guard.deliver(id,k->true);return true;});}catch(IllegalStateException expected){blocked=true;}check(blocked&&guard.pending(id),"重入拒绝并可恢复");
        for(int corrupt:List.of(-1,8)){
            var raw=guard.save(new CompoundTag());raw.getCompound("Players").putInt(id.toString(),corrupt);boolean bad=false;
            try{Hk3VoidGiftData.load(raw);}catch(IllegalArgumentException expected){bad=true;}check(bad,"损坏掩码不重置发奖");
        }
        var raw=guard.save(new CompoundTag());raw.putString("Players","bad");boolean bad=false;
        try{Hk3VoidGiftData.load(raw);}catch(IllegalArgumentException expected){bad=true;}check(bad,"坏账本根不重置");
        System.out.println("Void gift: "+checks+" checks passed; inventory insertion and external items need game runtime");
    }
}
