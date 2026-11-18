package com.sirin.hk3gtl.client.farview;

import com.sirin.hk3gtl.common.farview.Hk3FarMesh;
import com.sirin.hk3gtl.common.farview.Hk3WorldFarSurface;
import it.unimi.dsi.fastutil.ints.Int2IntMap;
import it.unimi.dsi.fastutil.ints.Int2IntOpenHashMap;
import net.minecraft.world.level.ChunkPos;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Map;

/** 分级横向网格保留多段剖面，区域边缘逐格接合。 */
final class Hk3WorldFarShell {
    record Column(Hk3WorldFarSurface surface,int from,int to,int x,int z,int width,int depth) {}
    private static final Comparator<Hk3FarMesh.Quad> FACE=Comparator.comparingInt(Hk3FarMesh.Quad::axis)
            .thenComparingInt(Hk3FarMesh.Quad::sign).thenComparingInt(Hk3FarMesh.Quad::plane)
            .thenComparingInt(Hk3FarMesh.Quad::color);
    private static final Comparator<Hk3FarMesh.Quad> ALONG_U=FACE.thenComparingInt(Hk3FarMesh.Quad::v)
            .thenComparingInt(Hk3FarMesh.Quad::height).thenComparingInt(Hk3FarMesh.Quad::u);
    private static final Comparator<Hk3FarMesh.Quad> ALONG_V=FACE.thenComparingInt(Hk3FarMesh.Quad::u)
            .thenComparingInt(Hk3FarMesh.Quad::width).thenComparingInt(Hk3FarMesh.Quad::v);

    private Hk3WorldFarShell() {}

    static Hk3FarTileMesh.Shell bake(int originX,int originZ,Map<Long,Hk3WorldFarSurface> chunks,
                                     Map<Integer,Integer> colors,int stride,int maxStride,int maxQuads) {
        Column[][] source=new Column[66][66];
        for(int x=-1;x<=64;x++)for(int z=-1;z<=64;z++) {
            if(Thread.currentThread().isInterrupted())return null;
            int worldX=originX+x,worldZ=originZ+z;
            var surface=chunks.get(ChunkPos.asLong(worldX>>4,worldZ>>4));
            if(surface==null)continue;
            int at=(worldX&15)*16+(worldZ&15);
            source[x+1][z+1]=new Column(surface,surface.offsets()[at],surface.offsets()[at+1],x,z,1,1);
        }
        var palette=new Int2IntOpenHashMap(colors);
        var workspace=new Hk3WorldFarLod.Workspace();
        for(int step=stride;step<=maxStride;step*=2){
            if(Thread.currentThread().isInterrupted())return null;
            var quads=bake(source,palette,step,maxQuads,workspace);
            if(quads!=null)return new Hk3FarTileMesh.Shell(step,quads);
        }
        return null;
    }

    private static List<Hk3FarMesh.Quad> bake(Column[][] source,Int2IntMap colors,int stride,int maxQuads,
                                              Hk3WorldFarLod.Workspace workspace) {
        Column[][] columns=source;
        if(stride>1){
            columns=source.clone();
            for(int x=0;x<columns.length;x++)columns[x]=source[x].clone();
        }
        if(stride>1)for(int x=1;x<63;x+=stride)for(int z=1;z<63;z+=stride) {
            if(Thread.currentThread().isInterrupted())return null;
            int width=Math.min(stride,63-x),depth=Math.min(stride,63-z);
            simplify(source,columns,x,z,width,depth,colors,workspace);
        }
        List<Hk3FarMesh.Quad> faces=new ArrayList<>();
        for(int x=0;x<64;x++)for(int z=0;z<64;z++) {
            if(Thread.currentThread().isInterrupted())return null;
            var column=columns[x+1][z+1];
            if(column==null||column.x!=x||column.z!=z)continue;
            var surface=column.surface;
            for(int i=column.from;i<column.to;i++) {
                int color=colors.get(surface.states()[i]);
                if(color==0)continue;
                int low=surface.starts()[i],high=surface.ends()[i];
                int below=i>column.from&&surface.ends()[i-1]==low?colors.get(surface.states()[i-1]):0;
                int above=i+1<column.to&&surface.starts()[i+1]==high?colors.get(surface.states()[i+1]):0;
                if(!occluded(color,below))faces.add(new Hk3FarMesh.Quad(1,-1,low,z,x,column.depth,column.width,Math.abs(color)));
                if(!occluded(color,above))faces.add(new Hk3FarMesh.Quad(1,1,high,z,x,column.depth,column.width,Math.abs(color)));
            }
            for(int dz=0;dz<column.depth;dz++) {
                sides(faces,column,columns[x][z+dz+1],colors,0,-1,x,z+dz);
                sides(faces,column,columns[x+column.width+1][z+dz+1],colors,0,1,x+column.width,z+dz);
            }
            for(int dx=0;dx<column.width;dx++) {
                sides(faces,column,columns[x+dx+1][z],colors,2,-1,z,x+dx);
                sides(faces,column,columns[x+dx+1][z+column.depth+1],colors,2,1,z+column.depth,x+dx);
            }
            if(faces.size()>maxQuads*2) {
                faces=merge(merge(faces,true),false);
                if(faces.size()>maxQuads*2)return null;
            }
        }
        for(int pass=0;pass<2;pass++) {
            if(Thread.currentThread().isInterrupted())return null;
            int previous=faces.size();
            faces=merge(faces,true);
            faces=merge(faces,false);
            if(faces.size()==previous)break;
        }
        if(Thread.currentThread().isInterrupted())return null;
        return faces.size()>maxQuads?null:faces;
    }

    private static void simplify(Column[][] source,Column[][] columns,int x,int z,int width,int depth,
                                  Int2IntMap colors,Hk3WorldFarLod.Workspace workspace) {
        if(width==1&&depth==1||Thread.currentThread().isInterrupted())return;
        var surface=Hk3WorldFarLod.merge(source,x,z,width,depth,colors,workspace);
        if(surface!=null){
            var column=new Column(surface,0,surface.states().length,x,z,width,depth);
            for(int dx=0;dx<width;dx++)for(int dz=0;dz<depth;dz++)columns[x+dx+1][z+dz+1]=column;
            return;
        }
        int halfWidth=(width+1)/2,halfDepth=(depth+1)/2;
        for(int dx=0;dx<width;dx+=halfWidth)for(int dz=0;dz<depth;dz+=halfDepth)
            simplify(source,columns,x+dx,z+dz,Math.min(halfWidth,width-dx),Math.min(halfDepth,depth-dz),colors,workspace);
    }

    private static void sides(List<Hk3FarMesh.Quad> faces,Column column,Column neighbor,
                              Int2IntMap colors,int axis,int sign,int plane,int across) {
        var source=column.surface;
        int next=neighbor==null?0:neighbor.from;
        for(int i=column.from;i<column.to;i++) {
            int color=colors.get(source.states()[i]);
            if(color==0)continue;
            int low=source.starts()[i],high=source.ends()[i],at=low;
            if(neighbor==null){side(faces,axis,sign,plane,across,low,high,color);continue;}
            var other=neighbor.surface;
            while(next<neighbor.to&&other.ends()[next]<=low)next++;
            for(int n=next;n<neighbor.to&&other.starts()[n]<high;n++) {
                int start=other.starts()[n],end=Math.min(high,other.ends()[n]);
                if(start>at)side(faces,axis,sign,plane,across,at,start,color);
                int begin=Math.max(at,start);
                if(!occluded(color,colors.get(other.states()[n])))side(faces,axis,sign,plane,across,begin,end,color);
                at=end;
            }
            if(at<high)side(faces,axis,sign,plane,across,at,high,color);
        }
    }

    private static boolean occluded(int color,int neighbor) {return neighbor>0||neighbor==color;}

    private static void side(List<Hk3FarMesh.Quad> faces,int axis,int sign,int plane,int across,
                             int low,int high,int color) {
        if(axis==0)faces.add(new Hk3FarMesh.Quad(axis,sign,plane,low,across,high-low,1,Math.abs(color)));
        else faces.add(new Hk3FarMesh.Quad(axis,sign,plane,across,low,1,high-low,Math.abs(color)));
    }

    private static List<Hk3FarMesh.Quad> merge(List<Hk3FarMesh.Quad> faces,boolean alongU) {
        if(faces.size()<2||Thread.currentThread().isInterrupted())return faces;
        faces.sort(alongU?ALONG_U:ALONG_V);
        List<Hk3FarMesh.Quad> merged=new ArrayList<>(faces.size());
        Hk3FarMesh.Quad previous=null;
        int at=0;
        for(var face:faces) {
            if((at++&1023)==0&&Thread.currentThread().isInterrupted())return faces;
            boolean same=previous!=null&&FACE.compare(previous,face)==0;
            if(same&&(alongU?previous.v()==face.v()&&previous.height()==face.height()
                    &&previous.u()+previous.width()==face.u():previous.u()==face.u()
                    &&previous.width()==face.width()&&previous.v()+previous.height()==face.v())) {
                previous=new Hk3FarMesh.Quad(face.axis(),face.sign(),face.plane(),previous.u(),previous.v(),
                        previous.width()+(alongU?face.width():0),previous.height()+(alongU?0:face.height()),face.color());
                merged.set(merged.size()-1,previous);
            }else {
                previous=face;
                merged.add(face);
            }
        }
        return merged;
    }
}
