package com.sirin.hk3gtl.common.phone;
import com.gregtechceu.gtceu.api.capability.IElectricItem;
import net.minecraft.nbt.CompoundTag;
import java.util.function.Supplier;
import java.util.function.IntSupplier;
/**
 * 【变更记录 #1】2026-09-30 18:44:46（内测5修订113）
 * 删除：无；新增：手机GT电池能力实现，NBT与物品数量由物品提供。
 * 修改：显式限制128000EU、LV32EU传输与禁止外放电；用途：实际充电槽和服务器用电共用可回归实现。
 */
public final class Hk3PhoneBattery implements IElectricItem {
    public static final long CAPACITY=128000;
    private final Supplier<CompoundTag> tag;private final IntSupplier count;
    public Hk3PhoneBattery(Supplier<CompoundTag> tag,IntSupplier count){this.tag=tag;this.count=count;}
    public boolean canProvideChargeExternally(){return false;}
    public boolean chargeable(){return true;}
    public int getTier(){return 1;}
    public long getTransferLimit(){return 32;}
    public long getMaxCharge(){return CAPACITY;}
    public long getCharge(){return Math.max(0,Math.min(CAPACITY,tag.get().getLong("Charge")));}
    public long charge(long amount,int tier,boolean unlimited,boolean simulate){
        if(amount<=0||tier<getTier()||count.getAsInt()!=1)return 0;
        long accepted=Math.min(CAPACITY-getCharge(),unlimited?amount:Math.min(amount,getTransferLimit()));
        if(!simulate)tag.get().putLong("Charge",getCharge()+accepted);return accepted;
    }
    public long discharge(long amount,int tier,boolean unlimited,boolean external,boolean simulate){
        if(amount<=0||tier<getTier()||external||count.getAsInt()!=1)return 0;
        long used=Math.min(getCharge(),unlimited?amount:Math.min(amount,getTransferLimit()));
        if(!simulate)tag.get().putLong("Charge",getCharge()-used);return used;
    }
}
