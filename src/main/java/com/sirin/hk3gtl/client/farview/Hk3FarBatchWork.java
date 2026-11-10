package com.sirin.hk3gtl.client.farview;

import com.sirin.hk3gtl.common.farview.*;
import net.minecraft.core.BlockPos;
import java.util.*;
import java.util.concurrent.CompletableFuture;
import java.util.function.LongFunction;

/** 64格绘制批次仍逐个准备16格精确分区；每帧最多推进两个步骤。 */
final class Hk3FarBatchWork {
    record Section(long key,Hk3FarSection.Snapshot data) {}
    final long key,revision;
    final List<Hk3FarTileMesh.Piece> pieces=new ArrayList<>();
    private final List<Section> sections;
    private int cursor;
    private CompletableFuture<List<Hk3FarMesh.Quad>> pending;
    Hk3FarBatchWork(long key,long revision,List<Section> sections) {
        this.key=key;this.revision=revision;this.sections=List.copyOf(sections);
    }
    boolean advance(Hk3FarMaterials materials,LongFunction<int[][]> boundaries) {
        long until=System.nanoTime()+1_000_000L;
        for(int step=0;step<2&&cursor<sections.size()&&System.nanoTime()<until;step++) {
            var section=sections.get(cursor);
            if(pending==null) {
                pending=Hk3FarTileMesh.prepare(Hk3FarTileMesh.cubes(section.data(),materials),boundaries.apply(section.key()));
                if(pending==null)return false;
            } else if(pending.isDone()) {
                int x=(BlockPos.getX(section.key())-BlockPos.getX(key)*4)*16;
                int y=(BlockPos.getY(section.key())-BlockPos.getY(key)*4)*16;
                int z=(BlockPos.getZ(section.key())-BlockPos.getZ(key)*4)*16;
                pieces.add(new Hk3FarTileMesh.Piece(section.data(),pending.join(),x,y,z));cursor++;pending=null;
            } else return false;
        }
        return cursor==sections.size();
    }
}
