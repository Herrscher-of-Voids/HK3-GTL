package com.sirin.hk3gtl.common.finale;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.saveddata.SavedData;

/** 【变更记录 #1】2026-10-01 16:49:18（修订135）：删除无；新增终审会面存盘壳；修改只在副本事务成功后替换；用途：重启保留快照与检查点，不读取玩家可编辑物品NBT。 */
public final class Hk3FinaleData extends SavedData {
    private Hk3FinaleLedger ledger=new Hk3FinaleLedger();
    private boolean changing;
    public static Hk3FinaleData get(MinecraftServer server){return com.sirin.hk3gtl.common.util.Hk3SavedDataGuard.get(server,"hk3gtl_finale_admission_v5",Hk3FinaleData::load,Hk3FinaleData::new);}
    public Hk3FinaleLedger snapshot(){return Hk3FinaleLedger.load(ledger.save());}
    public <T> T change(java.util.function.Function<Hk3FinaleLedger,T> operation){
        if(changing)throw new IllegalStateException("终审会面事务不能重入");changing=true;
        try{var copy=snapshot();T result=operation.apply(copy);ledger=Hk3FinaleLedger.load(copy.save());setDirty();return result;}finally{changing=false;}
    }
    public static Hk3FinaleData load(CompoundTag tag){var data=new Hk3FinaleData();data.ledger=Hk3FinaleLedger.load(tag);return data;}
    @Override public CompoundTag save(CompoundTag tag){return tag.merge(ledger.save());}
}
