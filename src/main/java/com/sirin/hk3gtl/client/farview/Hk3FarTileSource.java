package com.sirin.hk3gtl.client.farview;

import com.sirin.hk3gtl.common.farview.Hk3FarSection;
import java.util.BitSet;
import java.util.function.IntPredicate;

/** 两条来源各自失效，HK结构的已知方块优先，撤销后恢复同格世界快照。 */
public final class Hk3FarTileSource {
    private Hk3FarSection.Snapshot structure;
    private Hk3WorldFarCache.Packed world;
    private BitSet observedAir;
    public void structure(Hk3FarSection.Snapshot value){
        if(value==null){structure=null;observedAir=null;return;}
        if(structure!=null)for(int i=0;i<Hk3WorldFarCache.CELLS;i++){
            if(value.state(i)!=0){if(observedAir!=null)observedAir.clear(i);}
            else if(structure.state(i)!=0){if(observedAir==null)observedAir=new BitSet();observedAir.set(i);}
        }
        structure=value;
    }
    public void world(Hk3WorldFarCache.Packed value){world=value;}
    public boolean hasStructure(){return structure!=null;}
    public boolean structureAt(int index){return structure!=null&&structure.state(index)!=0;}
    public boolean known(int index){return world!=null||structureAt(index)||observedAir!=null&&observedAir.get(index);}
    public boolean empty(){return structure==null&&world==null;}
    public int state(int index){
        int known=structure==null?0:structure.state(index);
        if(known==0&&observedAir!=null&&observedAir.get(index))return 0;
        return known!=0?known:world==null?0:world.state(index);
    }
    public Hk3FarSection.Snapshot snapshot(IntPredicate excluded){
        if(world==null&&structure!=null&&excluded==null)return structure;
        var combined=new Hk3FarSection();
        int[] cells=new int[Hk3WorldFarCache.CELLS];
        if(world!=null)world.unpack(cells);
        for(int i=0;i<Hk3WorldFarCache.CELLS;i++){
            int known=structure==null?0:structure.state(i);
            int state=known!=0?known:observedAir!=null&&observedAir.get(i)?0:cells[i];
            if(state!=0&&(excluded==null||!excluded.test(i)))combined.set(i,state);
        }
        return combined.snapshot();
    }
}
