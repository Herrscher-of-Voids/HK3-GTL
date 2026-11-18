package com.sirin.hk3gtl.client.farview;

import com.mojang.blaze3d.vertex.*;
import com.sirin.hk3gtl.common.farview.*;
import net.minecraft.core.Direction;
import java.util.*;
import java.util.concurrent.*;
import java.util.function.Supplier;

/** 后台只计算整数表面；模型访问、材质读取和显存上传始终留在渲染线程。 */
final class Hk3FarTileMesh implements AutoCloseable {
    private static final int WORKERS=Math.max(1,Math.min(4,Runtime.getRuntime().availableProcessors()/4));
    private static final int MAX_IN_FLIGHT=WORKERS*2;
    private static final ThreadPoolExecutor WORKER=new ThreadPoolExecutor(WORKERS,WORKERS,30,TimeUnit.SECONDS,
            new ArrayBlockingQueue<>(WORKERS),task->{Thread t=new Thread(task,"hk3gtl-far-mesh");t.setDaemon(true);t.setPriority(Thread.NORM_PRIORITY-1);return t;});
    private static final BufferBuilder BUILDER=new BufferBuilder(65536);
    private static final int UPLOAD_FACES=8192;
    private static final ArrayDeque<Upload> UPLOADS=new ArrayDeque<>();
    private static boolean uploaded;
    private static final Direction.Axis[] AXES=Direction.Axis.values();
    final List<List<VertexBuffer>> buffers=List.of(new ArrayList<>(),new ArrayList<>());
    int bytes;
    final int[] minY={Integer.MAX_VALUE,Integer.MAX_VALUE},maxY={Integer.MIN_VALUE,Integer.MIN_VALUE};
    record Model(int state,int x,int y,int z,int stride) {}
    record Shell(int stride,List<Hk3FarMesh.Quad> quads) {}
    record Piece(Hk3FarSection.Snapshot section,List<Hk3FarMesh.Quad> quads,List<Model> models,int x,int y,int z,
                 Map<Integer,Hk3FarMaterials.Material> materials) {
        Piece {materials=Map.copyOf(materials);}
        Piece(Hk3FarSection.Snapshot section,List<Hk3FarMesh.Quad> quads,int x,int y,int z,
              Map<Integer,Hk3FarMaterials.Material> materials){this(section,quads,List.of(),x,y,z,materials);}
    }
    static int workers(){return WORKERS;}
    static int availableSlots(){return Math.max(0,MAX_IN_FLIGHT-WORKER.getActiveCount()-WORKER.getQueue().size());}
    static String workerStatus(){return WORKER.getActiveCount()+"/"+WORKERS+"+"+WORKER.getQueue().size();}
    static CompletableFuture<List<Hk3FarMesh.Quad>> prepare(Hk3FarSection.Snapshot section,int[] palette,int[][] boundaries) {
        return enqueue(()->{
            int[] cells=new int[Hk3FarMesh.COUNT];
            for(int i=0;i<cells.length;i++){
                if((i&255)==0&&Thread.currentThread().isInterrupted())return null;
                cells[i]=palette[Short.toUnsignedInt(section.cells()[i])];
            }
            return Hk3FarMesh.bake(cells,boundaries);
        });
    }
    static CompletableFuture<Shell> prepareShell(int x,int z,Map<Long,Hk3WorldFarSurface> chunks,
                                                Map<Integer,Integer> colors,int stride,int maxStride,int maxQuads) {
        return enqueue(()->Hk3WorldFarShell.bake(x,z,chunks,colors,stride,maxStride,maxQuads));
    }
    static CompletableFuture<Hk3WorldFarSurface> prepareSurface(Supplier<Hk3WorldFarSurface> snapshot) {
        return enqueue(snapshot);
    }
    private static <T> CompletableFuture<T> enqueue(Supplier<T> task) {
        if(availableSlots()==0)return null;
        var future=new CompletableFuture<T>();
        var work=new FutureTask<Void>(()->{future.completeAsync(task,Runnable::run);return null;});
        // 取消结果时同时停止计算，避免失效网格继续占用工作线程。
        future.whenComplete((value,failure)->{
            if(future.isCancelled()){work.cancel(true);WORKER.remove(work);}
        });
        try{WORKER.execute(work);return future;}
        catch(RejectedExecutionException busy){return null;}
    }
    static int[] cubePalette(Hk3FarSection.Snapshot section,Map<Integer,Hk3FarMaterials.Material> materials) {
        int[] ids=new int[section.palette().length];
        for(int i=1;i<ids.length;i++) {
            int state=section.palette()[i];if(state==0)continue;
            var model=materials.get(state);if(model.cube())ids[i]=model.opaque()?state:-state;
        }
        return ids;
    }
    static void beginFrame(){uploaded=false;}
    static Upload beginUpload(List<Piece> pieces,long required){
        var upload=new Upload(pieces,required);UPLOADS.addLast(upload);return upload;
    }
    static final class Upload implements AutoCloseable {
        final long required;
        private final List<Piece> pieces;
        private final float[] offset=new float[3],span=new float[3];
        private Hk3FarTileMesh mesh=new Hk3FarTileMesh();
        private int pass,piece,quad,placed,cell,face,count;
        private boolean building;
        Upload(List<Piece> pieces,long required){this.pieces=pieces;this.required=required;}
        boolean active(){return UPLOADS.peekFirst()==this;}
        boolean advance(long deadline){
            if(!active()||uploaded||System.nanoTime()>=deadline)return false;
            int work=0;
            while(pass<2){
                if(piece==pieces.size()){
                    boolean flush=building;
                    if(flush)flush();
                    pass++;piece=quad=placed=cell=face=0;
                    if(flush)return pass==2;
                    continue;
                }
                step();
                if(count==UPLOAD_FACES){flush();return false;}
                if((++work&63)==0&&System.nanoTime()>=deadline)return false;
            }
            return pass==2;
        }
        private void step(){
            var current=pieces.get(piece);
            if(quad<current.quads().size()){
                var q=current.quads().get(quad++);
                var model=current.materials().get(Math.abs(q.color()));
                if(model.translucent()!=(pass==1))return;
                Direction direction=Direction.fromAxisAndDirection(AXES[q.axis()],q.sign()>0?Direction.AxisDirection.POSITIVE:Direction.AxisDirection.NEGATIVE);
                offset[q.axis()]=q.plane();int u=(q.axis()+1)%3,v=(q.axis()+2)%3;
                offset[u]=q.u();offset[v]=q.v();span[q.axis()]=0;span[u]=q.width();span[v]=q.height();
                offset[0]+=current.x();offset[1]+=current.y();offset[2]+=current.z();
                emit(model.side(direction),direction);return;
            }
            if(placed<current.models().size()){
                var position=current.models().get(placed);var model=current.materials().get(position.state());
                if(model.translucent()!=(pass==1)||face==model.faces().size()){placed++;face=0;return;}
                offset[0]=current.x()+position.x();offset[1]=current.y()+position.y();offset[2]=current.z()+position.z();
                span[0]=span[2]=position.stride();span[1]=1;
                var next=model.faces().get(face++);emit(next,next.cull());return;
            }
            var section=current.section();
            if(section!=null&&cell<Hk3FarMesh.COUNT){
                int state=section.state(cell);
                if(state==0){cell++;return;}
                var model=current.materials().get(state);
                if(model.cube()||model.translucent()!=(pass==1)||face==model.faces().size()){cell++;face=0;return;}
                var next=model.faces().get(face++);
                if(!exposed(section,cell,next,current.materials()))return;
                offset[0]=current.x()+cell/256;offset[1]=current.y()+cell/16%16;offset[2]=current.z()+cell%16;
                span[0]=span[1]=span[2]=1;emit(next,next.cull());return;
            }
            piece++;quad=placed=cell=face=0;
        }
        private void emit(Hk3FarMaterials.Face face,Direction direction){
            if(!building){BUILDER.begin(VertexFormat.Mode.QUADS,DefaultVertexFormat.POSITION_COLOR_TEX);building=true;}
            mesh.emit(face,offset,span,direction,pass);count++;
        }
        private void flush(){
            var rendered=BUILDER.end();building=false;
            var buffer=new VertexBuffer(VertexBuffer.Usage.STATIC);mesh.buffers.get(pass).add(buffer);
            try{buffer.bind();buffer.upload(rendered);mesh.bytes+=count*4*24;count=0;uploaded=true;}
            finally{VertexBuffer.unbind();}
        }
        Hk3FarTileMesh finish(){
            UPLOADS.removeFirst();var result=mesh;mesh=null;return result;
        }
        @Override public void close(){
            UPLOADS.remove(this);
            if(building){BUILDER.end().release();building=false;}
            if(mesh!=null){mesh.close();mesh=null;}
        }
    }
    static long estimate(Piece piece) {
        long bytes=estimate(piece.section(),piece.quads(),piece.materials());
        for(var model:piece.models())bytes+=piece.materials().get(model.state()).faces().size()*4L*24;
        return bytes;
    }
    private static long estimate(Hk3FarSection.Snapshot section,List<Hk3FarMesh.Quad> quads,Map<Integer,Hk3FarMaterials.Material> materials) {
        int faces=quads.size();
        for(int i=0;section!=null&&i<Hk3FarMesh.COUNT;i++) {
            int state=section.state(i);if(state==0)continue;var model=materials.get(state);
            if(!model.cube())faces=Math.addExact(faces,model.faces().size());
        }
        return (long)faces*4*24;
    }
    private static boolean exposed(Hk3FarSection.Snapshot section,int i,Hk3FarMaterials.Face face,Map<Integer,Hk3FarMaterials.Material> materials) {
        var direction=face.cull();if(direction==null)return true;
        int x=i/256+direction.getStepX(),y=i/16%16+direction.getStepY(),z=i%16+direction.getStepZ();
        if(x<0||x>=16||y<0||y>=16||z<0||z>=16)return true;
        int state=section.state(Hk3FarMesh.index(x,y,z));if(state==0)return true;
        var neighbor=materials.get(state);return !neighbor.cube()||!neighbor.opaque();
    }
    private void emit(Hk3FarMaterials.Face face,float[] offset,float[] span,Direction direction,int pass) {
        float shade=direction==Direction.UP?1:direction==Direction.DOWN?.55f:direction!=null&&direction.getAxis()==Direction.Axis.X?.78f:.88f;
        float[] v=face.vertices();
        for(int i=0;i<4;i++){
            float y=offset[1]+v[i*5+1]*span[1];
            minY[pass]=Math.min(minY[pass],(int)Math.floor(y));maxY[pass]=Math.max(maxY[pass],(int)Math.ceil(y));
            BUILDER.vertex(offset[0]+v[i*5]*span[0],y,offset[2]+v[i*5+2]*span[2])
                .color(face.slot()&255,face.slot()>>8,(int)(shade*255),255)
                .uv(v[i*5+3]*Math.max(1,span[face.uAxis()]),v[i*5+4]*Math.max(1,span[face.vAxis()])).endVertex();
        }
    }
    @Override public void close(){for(var pass:buffers){pass.forEach(VertexBuffer::close);pass.clear();}}
}
