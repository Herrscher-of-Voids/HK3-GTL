package com.sirin.hk3gtl.test.phone;
import com.sirin.hk3gtl.common.phone.*;
import com.sirin.hk3gtl.common.item.Hk3PhoneItem;
import java.util.*;
import net.minecraft.nbt.*;
import net.minecraft.world.item.*;
/**
 * 【变更记录 #1】2026-09-30 18:44:46（内测5修订113）
 * 删除：无；新增：实际电池能力充放电、物品NBT及旧安装迁移、App排列回归。
 * 修改：无；用途：防超充/凭空供电与重复补发，验证拖动无丢失。
 */
/** 【变更记录 #2】2026-09-30 19:06:42（修订114）：删除固定六应用断言；新增11应用交换覆盖；修改读取生产白名单；用途：兼容旧桌面顺序。 */
/** 【变更记录 #3】2026-10-01 01:25:10（修订125）：删除无；新增实际充放电NBT与持物动画判定联测；修改覆盖耗电、充电、耗尽、空NBT及非电量外观变化；用途：修复每秒抖动而不抹掉物品差异。 */
/** 【变更记录 #4】2026-10-31 21:56:49（第4次备注 · 内测5修订191）：删除无；新增LV每次32EU充放电、模拟放电不写NBT、低电压与非法数量拒绝、损坏电量夹取边界；修改测试入口执行电池边界组；用途：覆盖实际GT能力适配的数值契约，原生充电槽与AE菜单仍需实机验收。 */
public final class PhoneDesktopPowerTest {
    private static int checks;
    private static void check(boolean v,String why){if(!v)throw new AssertionError(why);checks++;}
    public static void main(String[] args){
        batteryBoundaries();
        var tag=new CompoundTag();
        var e=new Hk3PhoneBattery(()->tag,()->1);
        check(e.getCharge()==0&&e.getMaxCharge()==128000,"新电池为空、容量确定");
        check(e.charge(1000,0,true,false)==0,"低于LV不能充电");
        check(e.charge(1000,1,true,true)==1000&&e.getCharge()==0,"模拟充电不修改");
        check(e.charge(Long.MAX_VALUE,1,true,false)==128000,"充电不会超过容量");
        check(e.charge(1000,1,true,false)==0,"满电拒绝多余电量");
        check(e.discharge(8,Integer.MAX_VALUE,true,false,false)==8&&e.getCharge()==127992,"亮屏实际扣8EU");
        var initial=tag.copy();
        e.discharge(8,Integer.MAX_VALUE,true,false,false);
        var drained=tag.copy();
        check(!Hk3PhoneVisualState.changed(initial,tag),"真实耗电不触发抬手");
        check(initial.getLong("Charge")==127992&&tag.getLong("Charge")==127984,"比较不修改电量");
        e.charge(8,1,true,false);
        check(!Hk3PhoneVisualState.changed(drained,tag),"真实充电不触发抬手");
        var empty=new CompoundTag();empty.putLong("Charge",0);
        check(!Hk3PhoneVisualState.changed(tag,empty),"耗尽不反复抬手");
        check(!Hk3PhoneVisualState.changed(null,empty),"零电量NBT初始化不抬手");
        check(!Hk3PhoneVisualState.changed(null,null),"空状态稳定");
        var model=tag.copy();model.putInt("CustomModelData",2);
        check(Hk3PhoneVisualState.changed(tag,model),"模型变化仍更新持物");
        var named=tag.copy();var display=new CompoundTag();display.putString("Name","\"我的手机\"");named.put("display",display);
        check(Hk3PhoneVisualState.changed(tag,named),"名称变化不被电量忽略规则吞掉");
        check(e.discharge(8,Integer.MAX_VALUE,true,true,false)==0,"手机不能给外部供电");
        var copy=tag.copy();
        var restored=new Hk3PhoneBattery(()->copy,()->1);
        check(restored.getCharge()==127992,"电量随物品NBT保存");
        check(restored.discharge(999999,Integer.MAX_VALUE,true,false,false)==127992&&restored.getCharge()==0,"放电不能负数");
        check(new Hk3PhoneBattery(()->tag,()->2).charge(1000,1,true,false)==0,"非法堆叠拒绝充电");
        UUID id=UUID.randomUUID();var data=new Hk3PhoneData();data.install(id);
        check(!Hk3PhoneData.load(data.save(new CompoundTag())).needsPhysical(id),"新安装无补发资格");
        var old=data.save(new CompoundTag());old.remove("PhysicalMigration");
        var migrated=Hk3PhoneData.load(old);check(migrated.needsPhysical(id),"旧消耗安装待补发");
        migrated.physicalDelivered(id);
        check(!Hk3PhoneData.load(migrated.save(new CompoundTag())).needsPhysical(id),"补发后重启不再补发");
        List<String> list=Hk3PhoneDesktopOrder.normalize(Arrays.asList("inbox","unknown","inbox",null));
        check(list.size()==Hk3PhoneDesktopOrder.APPS.size()&&new HashSet<>(list).size()==Hk3PhoneDesktopOrder.APPS.size(),"坏配置补全且不重复");
        var before=new ArrayList<>(list);
        for(int from=0;from<list.size();from++)for(int to=0;to<list.size();to++){
            var moved=Hk3PhoneDesktopOrder.move(list,from,to);
            check(moved.get(to).equals(list.get(from))&&new HashSet<>(moved).equals(new HashSet<>(list)),"拖动只交换不丢App");
        }
        check(Hk3PhoneDesktopOrder.move(list,0,-1).equals(before),"越界释放保留原序");
        System.out.println("Phone desktop / power: "+checks+" checks passed; real chargers and AE range need game acceptance");
    }
    private static void batteryBoundaries(){
        var tag=new CompoundTag();var e=new Hk3PhoneBattery(()->tag,()->1);
        check(e.charge(1000,1,false,false)==32&&e.getCharge()==32,"LV充电每次上限32EU");
        check(e.charge(1000,8,false,false)==32&&e.getCharge()==64,"高压充电仍遵守手机传输上限");
        var before=tag.copy();
        check(e.discharge(1000,1,false,false,true)==32&&tag.equals(before),"模拟放电报告32EU且不修改NBT");
        check(e.discharge(1000,0,true,false,false)==0&&tag.equals(before),"低压放电拒绝且保留电量");
        check(e.discharge(1000,1,false,false,false)==32&&e.getCharge()==32,"实际放电遵守32EU传输上限");
        check(new Hk3PhoneBattery(()->tag,()->2).discharge(8,1,true,false,false)==0,"非法堆叠不能绕过放电边界");
        check(new Hk3PhoneBattery(()->tag,()->0).charge(32,1,true,false)==0,"空物品不能获得电量");
        tag.putLong("Charge",Long.MIN_VALUE);
        check(e.getCharge()==0&&e.discharge(8,1,true,false,false)==0,"损坏负电量不产生放电");
        tag.putLong("Charge",Long.MAX_VALUE);
        check(e.getCharge()==Hk3PhoneBattery.CAPACITY&&e.charge(32,1,true,false)==0,"超大电量夹取容量且拒绝超充");
    }
}
