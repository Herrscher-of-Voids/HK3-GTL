package com.sirin.hk3gtl.client.farview;

import com.sirin.hk3gtl.common.farview.*;
import net.minecraft.core.BlockPos;
import java.util.*;
import java.util.concurrent.CompletableFuture;
import java.util.function.LongFunction;
import java.util.function.Supplier;

final class Hk3FarBatchWork {
    record Section(long key,Supplier<Hk3FarSection.Snapshot> data) {}
    final long key,revision;
    final List<Hk3FarTileMesh.Piece> pieces=new ArrayList<>();
    Hk3FarTileMesh.Upload upload;
    long required;
    private final List<Section> sections;
    private record Pending(Section section,Hk3FarSection.Snapshot snapshot,
                           Map<Integer,Hk3FarMaterials.Material> materials,CompletableFuture<List<Hk3FarMesh.Quad>> future) {}
    private final List<Pending> pending=new ArrayList<>();
    private int cursor;
    Hk3FarBatchWork(long key,long revision,List<Section> sections) {
        this.key=key;this.revision=revision;this.sections=List.copyOf(sections);
    }
    boolean advance(Hk3FarMaterials materials,LongFunction<int[][]> boundaries,long until,int limit) {
        for(var iterator=pending.iterator();iterator.hasNext()&&System.nanoTime()<until;) {
            var task=iterator.next();if(!task.future().isDone())continue;
            var section=task.section();
            int x=(BlockPos.getX(section.key())-BlockPos.getX(key)*4)*16;
            int y=(BlockPos.getY(section.key())-BlockPos.getY(key)*4)*16;
            int z=(BlockPos.getZ(section.key())-BlockPos.getZ(key)*4)*16;
            var piece=new Hk3FarTileMesh.Piece(task.snapshot(),task.future().join(),x,y,z,task.materials());
            pieces.add(piece);required+=Hk3FarTileMesh.estimate(piece);iterator.remove();
        }
        while(cursor<sections.size()&&pending.size()<limit&&Hk3FarTileMesh.availableSlots()>0&&System.nanoTime()<until) {
            var section=sections.get(cursor);var snapshot=section.data().get();
            Map<Integer,Hk3FarMaterials.Material> models=new HashMap<>();
            for(int state:snapshot.palette())if(state!=0)models.put(state,materials.get(state));
            var palette=Hk3FarTileMesh.cubePalette(snapshot,models);
            var future=Hk3FarTileMesh.prepare(snapshot,palette,boundaries.apply(section.key()));
            if(future==null)return false;
            pending.add(new Pending(section,snapshot,models,future));cursor++;
        }
        return cursor==sections.size()&&pending.isEmpty();
    }
    void cancel(){pending.forEach(task->task.future().cancel(false));pending.clear();if(upload!=null)upload.close();}
}
