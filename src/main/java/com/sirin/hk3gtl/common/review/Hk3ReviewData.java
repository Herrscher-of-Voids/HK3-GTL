package com.sirin.hk3gtl.common.review;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.saveddata.SavedData;
/** 【变更记录 #1】2026-09-30 20:31:18（修订117）：删除无；新增审查账本持久化壳；修改无；用途：损坏数据拒绝当空存档，读写副本且重启会面暂停，真实资格验证器接入前不会产生许可。 */
public final class Hk3ReviewData extends SavedData {
    private Hk3ReviewLedger ledger=new Hk3ReviewLedger();
    private boolean changing;
    public static Hk3ReviewData get(MinecraftServer server){return com.sirin.hk3gtl.common.util.Hk3SavedDataGuard.get(server,"hk3gtl_reviews_v5",Hk3ReviewData::load,Hk3ReviewData::new);}
    public Hk3ReviewLedger snapshot(){return Hk3ReviewLedger.load(ledger.save());}
    /** 业务适配器在服务端线程操作副本，操作异常时原账本保留。 */
    public <T> T change(java.util.function.Function<Hk3ReviewLedger,T> operation){
        if(changing)throw new IllegalStateException("审查结算不能重入");changing=true;
        try{var copy=snapshot();T result=operation.apply(copy);ledger=Hk3ReviewLedger.load(copy.save());setDirty();return result;}finally{changing=false;}
    }
    public java.util.UUID settlement(java.util.UUID scope,Hk3ReviewLedger.Kind kind){return ledger.settlement(scope,kind);}
    public boolean settled(java.util.UUID scope,Hk3ReviewLedger.Kind kind){return ledger.settled(scope,kind);}
    public boolean experienced(java.util.UUID player,Hk3ReviewLedger.Kind kind){return ledger.experienced(player,kind);}
    public static Hk3ReviewData load(CompoundTag n){var data=new Hk3ReviewData();data.ledger=Hk3ReviewLedger.load(n);data.ledger.suspendAll();return data;}
    @Override public CompoundTag save(CompoundTag n){n.merge(ledger.save());return n;}
}
