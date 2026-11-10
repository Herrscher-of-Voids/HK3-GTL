package com.sirin.hk3gtl.common.multiblock.pattern;

import java.io.*;
import java.util.*;
import java.util.zip.GZIPInputStream;

/** HK3P v1/v2: bounded streaming decoder shared by construction, layouts and previews. */
public final class Hk3StructureStream implements AutoCloseable {
    public record Header(int width,int height,int depth,int cx,int cy,int cz,int count,List<String> palette) {
        public int volume() {return Math.multiplyExact(Math.multiplyExact(width,height),depth);}
    }
    public record Cell(int linear,int state,byte[] entity) {}
    private final DataInputStream input;
    private final int version;
    private final Header header;
    private int remaining,runRemaining,runPosition,runStep,runState;

    public Hk3StructureStream(InputStream compressed) throws IOException {
        input=new DataInputStream(new BufferedInputStream(new GZIPInputStream(compressed),65536));
        try {
            if(input.readInt()!=0x484b3350)throw new IOException("结构流格式错误");
            version=input.readInt();if(version!=1&&version!=2)throw new IOException("结构流版本错误");
            int w=input.readInt(),h=input.readInt(),d=input.readInt();
            int x=input.readInt(),y=input.readInt(),z=input.readInt(),count=input.readInt();
            if(w<1||h<1||d<1||x<0||x>=w||y<0||y>=h||z<0||z>=d||count<1)
                throw new IOException("结构流尺寸或主控越界");
            int volume=Math.multiplyExact(Math.multiplyExact(w,h),d);
            if(count>volume)throw new IOException("结构流实体数量越界");
            int n=input.readUnsignedShort();if(n==0)throw new IOException("结构流调色板为空");
            List<String> palette=new ArrayList<>(n);
            for(int i=0;i<n;i++) {String state=input.readUTF();if(state.isBlank())throw new IOException("结构流空状态");palette.add(state);}
            header=new Header(w,h,d,x,y,z,count,List.copyOf(palette));remaining=count;
        }catch(IOException|RuntimeException failure){input.close();throw failure;}
    }
    public Header header(){return header;}
    public Cell next() throws IOException {
        if(remaining==0)throw new EOFException("结构流记录已结束");
        int position,state,bytes=0;
        if(version==1){position=input.readInt();state=input.readUnsignedShort();bytes=input.readInt();}
        else {
            if(runRemaining==0){
                runPosition=input.readInt();runStep=input.readInt();runRemaining=input.readInt();
                runState=input.readUnsignedShort();bytes=input.readInt();
                long end=runPosition+(long)(runRemaining-1)*runStep;
                if(runRemaining<1||runRemaining>remaining||(runRemaining>1&&(runStep==0||bytes!=0))
                        ||end<0||end>=header.volume())throw new IOException("结构流游程越界或无效");
            }
            position=runPosition;state=runState;runRemaining--;
            if(runRemaining>0)runPosition=Math.addExact(runPosition,runStep);
        }
        if(position<0||position>=header.volume()||state<0||state>=header.palette().size()
                ||bytes<0||bytes>1_048_576)throw new IOException("结构流记录越界");
        byte[] entity=bytes==0?null:input.readNBytes(bytes);
        if(entity!=null&&entity.length!=bytes)throw new EOFException("结构流实体数据截断");
        remaining--;
        return new Cell(position,state,entity);
    }
    public void finish() throws IOException {
        if(remaining!=0||runRemaining!=0||input.read()!=-1)throw new IOException("结构流未结束或存在尾随记录");
    }
    @Override public void close() throws IOException {input.close();}
    public static InputStream open(String key) {
        return Hk3StructureStream.class.getResourceAsStream("/data/hk3gtl/structures/compact/"+key+".bin.gz");
    }
}
