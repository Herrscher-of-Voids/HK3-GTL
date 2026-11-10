package com.sirin.hk3gtl.client.farview;

import com.mojang.blaze3d.vertex.*;
import com.sirin.hk3gtl.common.farview.*;
import net.minecraft.core.Direction;
import java.util.*;
import java.util.concurrent.*;

/** 后台只计算整数表面；模型访问、材质读取和显存上传始终留在渲染线程。 */
final class Hk3FarTileMesh implements AutoCloseable {
    private static final ThreadPoolExecutor WORKER=new ThreadPoolExecutor(1,1,30,TimeUnit.SECONDS,
            new ArrayBlockingQueue<>(1),task->{Thread t=new Thread(task,"hk3gtl-far-mesh");t.setDaemon(true);t.setPriority(Thread.NORM_PRIORITY-1);return t;});
    private static final BufferBuilder BUILDER=new BufferBuilder(65536);
    final VertexBuffer[] buffers=new VertexBuffer[2];
    int bytes;
    record Piece(Hk3FarSection.Snapshot section,List<Hk3FarMesh.Quad> quads,int x,int y,int z) {}
    static CompletableFuture<List<Hk3FarMesh.Quad>> prepare(int[] cells,int[][] boundaries) {
        if(WORKER.getActiveCount()+WORKER.getQueue().size()>=2)return null;
        try{return CompletableFuture.supplyAsync(()->Hk3FarMesh.bake(cells,boundaries),WORKER);}
        catch(RejectedExecutionException busy){return null;}
    }
    static int[] cubes(Hk3FarSection.Snapshot section,Hk3FarMaterials materials) {
        int[] ids=new int[section.palette().length],result=new int[Hk3FarMesh.COUNT];
        for(int i=1;i<ids.length;i++) {
            int state=section.palette()[i];if(state==0)continue;
            var model=materials.get(state);if(model.cube())ids[i]=model.opaque()?state:-state;
        }
        for(int i=0;i<result.length;i++)result[i]=ids[Short.toUnsignedInt(section.cells()[i])];
        return result;
    }
    static Hk3FarTileMesh upload(List<Piece> pieces,Hk3FarMaterials materials,long limit) {
        if(estimate(pieces,materials)>limit)return null;
        var mesh=new Hk3FarTileMesh();
        try {
            for(int pass=0;pass<2;pass++) {
                int count=0;BUILDER.begin(VertexFormat.Mode.QUADS,DefaultVertexFormat.POSITION_COLOR_TEX);
                for(var piece:pieces) {
                    var section=piece.section();
                    for(var q:piece.quads()) {
                        var model=materials.get(Math.abs(q.color()));if(model.translucent()!=(pass==1))continue;
                        Direction direction=Direction.fromAxisAndDirection(Direction.Axis.values()[q.axis()],q.sign()>0?Direction.AxisDirection.POSITIVE:Direction.AxisDirection.NEGATIVE);
                        var face=model.side(direction);float[] offset=new float[3],span={1,1,1};
                        offset[q.axis()]=q.plane();int u=(q.axis()+1)%3,v=(q.axis()+2)%3;
                        offset[u]=q.u();offset[v]=q.v();span[q.axis()]=0;span[u]=q.width();span[v]=q.height();
                        offset[0]+=piece.x();offset[1]+=piece.y();offset[2]+=piece.z();
                        emit(face,offset,span,direction);count++;
                    }
                    for(int i=0;i<Hk3FarMesh.COUNT;i++) {
                        int state=section.state(i);if(state==0)continue;var model=materials.get(state);
                        if(model.cube()||model.translucent()!=(pass==1))continue;
                        float[] offset={piece.x()+i/256,piece.y()+i/16%16,piece.z()+i%16},span={1,1,1};
                        for(var face:model.faces())if(exposed(section,i,face,materials)){emit(face,offset,span,face.cull());count++;}
                    }
                }
                var rendered=BUILDER.end();
                if(count==0){rendered.release();continue;}
                var buffer=new VertexBuffer(VertexBuffer.Usage.STATIC);mesh.buffers[pass]=buffer;
                buffer.bind();buffer.upload(rendered);mesh.bytes+=count*4*24;
            }
            return mesh;
        } catch(RuntimeException failure){mesh.close();throw failure;}
        finally{VertexBuffer.unbind();}
    }
    static long estimate(List<Piece> pieces,Hk3FarMaterials materials) {
        long bytes=0;for(var piece:pieces)bytes=Math.addExact(bytes,estimate(piece.section(),piece.quads(),materials));return bytes;
    }
    static long estimate(Hk3FarSection.Snapshot section,List<Hk3FarMesh.Quad> quads,Hk3FarMaterials materials) {
        int faces=quads.size();
        for(int i=0;i<Hk3FarMesh.COUNT;i++) {
            int state=section.state(i);if(state==0)continue;var model=materials.get(state);
            if(!model.cube())faces=Math.addExact(faces,model.faces().size());
        }
        return (long)faces*4*24;
    }
    private static boolean exposed(Hk3FarSection.Snapshot section,int i,Hk3FarMaterials.Face face,Hk3FarMaterials materials) {
        var direction=face.cull();if(direction==null)return true;
        int x=i/256+direction.getStepX(),y=i/16%16+direction.getStepY(),z=i%16+direction.getStepZ();
        if(x<0||x>=16||y<0||y>=16||z<0||z>=16)return true;
        int state=section.state(Hk3FarMesh.index(x,y,z));if(state==0)return true;
        var neighbor=materials.get(state);return !neighbor.cube()||!neighbor.opaque();
    }
    private static void emit(Hk3FarMaterials.Face face,float[] offset,float[] span,Direction direction) {
        float shade=direction==Direction.UP?1:direction==Direction.DOWN?.55f:direction!=null&&direction.getAxis()==Direction.Axis.X?.78f:.88f;
        float[] v=face.vertices();
        for(int i=0;i<4;i++)BUILDER.vertex(offset[0]+v[i*5]*span[0],offset[1]+v[i*5+1]*span[1],offset[2]+v[i*5+2]*span[2])
                .color(face.slot()&255,face.slot()>>8,(int)(shade*255),255)
                .uv(v[i*5+3]*Math.max(1,span[face.uAxis()]),v[i*5+4]*Math.max(1,span[face.vAxis()])).endVertex();
    }
    @Override public void close(){for(int i=0;i<buffers.length;i++)if(buffers[i]!=null){buffers[i].close();buffers[i]=null;}}
}
