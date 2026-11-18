package com.sirin.hk3gtl.common.multiblock.build;

import com.sirin.hk3gtl.common.multiblock.pattern.Hk3LargeArchitectureShapes;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;

import java.io.BufferedInputStream;
import java.io.DataInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.Arrays;
import java.util.ArrayList;
import java.util.List;
import com.sirin.hk3gtl.common.util.Hk3PackedResources;

/** W11按16格分区保存连续Z游程，包围盒坐标使用long，实体逐格提供给建造和完整检查。 */
public final class Hk3W11BuildPlan implements Hk3BuildPlan {
    public record Header(int width,int height,int depth,int cx,int cy,int cz,int blockCount,int runCount,List<String> palette) {}
    private static final class Metadata {
        private static final Header HEADER=loadHeader();
    }
    public static Header header(){return Metadata.HEADER;}
    private final int width,height,depth,cx,cy,cz,count;
    private final long[] positions;
    private final int[] ends;
    private final byte[] lengths;
    private final char[] materials;
    private final BlockState[] palette;
    private final Direction facing;
    private final Block controller;
    private final ThreadLocal<int[]> lookup=ThreadLocal.withInitial(()->new int[]{0,-1,-1});
    private DataInputStream input;
    private int cursor,total;
    private boolean foundController;

    Hk3W11BuildPlan(InputStream compressed,Block controller) {
        this.controller=controller;
        try {
            input=new DataInputStream(new BufferedInputStream(Hk3PackedResources.open(compressed),65536));
            Header header=readHeader(input);
            width=header.width();height=header.height();depth=header.depth();
            cx=header.cx();cy=header.cy();cz=header.cz();count=header.blockCount();
            palette=header.palette().stream().map(Hk3LargeArchitectureShapes::state).toArray(BlockState[]::new);
            facing=Hk3BuildPlans.controllerFacing(palette,controller);
            int runs=header.runCount();
            positions=new long[runs];ends=new int[runs];lengths=new byte[runs];materials=new char[runs];
        } catch(IOException|RuntimeException failure) {
            close();throw new IllegalStateException("读取W11分区蓝图头失败",failure);
        }
    }

    private static Header readHeader(DataInputStream input) throws IOException {
        if(input.readInt()!=0x484B3357||input.readInt()!=1)throw new IOException("W11分区蓝图格式错误");
        int width=input.readInt(),height=input.readInt(),depth=input.readInt();
        int cx=input.readInt(),cy=input.readInt(),cz=input.readInt(),count=input.readInt();
        int runs=input.readInt(),states=input.readUnsignedShort();
        if(width<1||height<1||depth<1||cx<0||cx>=width||cy<0||cy>=height||cz<0||cz>=depth
                ||count<1||count>(long)width*height*depth||runs<1||runs>count||states<1)
            throw new IOException("W11分区蓝图尺寸或数量错误");
        List<String> palette=new ArrayList<>(states);
        for(int i=0;i<states;i++)palette.add(input.readUTF());
        return new Header(width,height,depth,cx,cy,cz,count,runs,List.copyOf(palette));
    }
    private static Header loadHeader() {
        try(var input=new DataInputStream(new BufferedInputStream(Hk3PackedResources.open(Hk3PackedResources.resource(Hk3W11BuildPlan.class,
                "/data/hk3gtl/structures/w11_candidate.bin.gz")),65536))) {
            return readHeader(input);
        }catch(IOException failure){throw new IllegalStateException("读取W11蓝图元数据失败",failure);}
    }

    @Override public boolean prepareStep() {
        if(input==null)return true;
        try {
            int x=input.readInt(),y=input.readInt(),z=input.readInt(),length=input.readUnsignedByte(),state=input.readUnsignedShort();
            long position=linear(x,y,z);
            if(x<0||x>=width||y<0||y>=height||z<0||length<1||length>16||z+length>depth
                    ||(z>>4)!=((z+length-1)>>4)||state>=palette.length||palette[state].isAir()
                    ||cursor>0&&position<positions[cursor-1]+Byte.toUnsignedInt(lengths[cursor-1]))
                throw new IOException("W11分区游程越界或重叠");
            boolean controlState=palette[state].getBlock()==controller;
            long control=linear(cx,cy,cz);
            if(controlState&&(length!=1||position!=control))throw new IOException("W11分区蓝图含额外主控");
            if(control>=position&&control<position+length) {
                if(!controlState)throw new IOException("W11主控位置与定义不符");
                foundController=true;
            }
            positions[cursor]=position;lengths[cursor]=(byte)length;materials[cursor]=(char)state;
            total=Math.addExact(total,length);ends[cursor]=total;
            if(++cursor<positions.length)return false;
            if(total!=count||!foundController||input.read()!=-1)throw new IOException("W11分区蓝图实体数量或结尾错误");
            close();return true;
        } catch(IOException|RuntimeException failure) {
            close();throw new IllegalStateException("读取W11分区游程失败",failure);
        }
    }

    int runCount(){return positions.length;}
    int runStart(int run){return run==0?0:ends[run-1];}
    int runLength(int run){return Byte.toUnsignedInt(lengths[run]);}
    @Override public int size(){return count;}
    @Override public int height(){return height;}
    @Override public int x(int index){return (int)(position(index)/depth/height)-cx;}
    @Override public int y(int index){return (int)(position(index)/depth%height)-cy;}
    @Override public int z(int index){return (int)(position(index)%depth)-cz;}
    @Override public BlockState state(int index){return palette[materials[runAt(index)]];}
    @Override public CompoundTag tag(int index){return null;}
    @Override public Direction sourceFacing(){return facing;}
    @Override public BlockPos minOffset(){return new BlockPos(-cx,-cy,-cz);}
    @Override public BlockPos maxOffset(){return new BlockPos(width-1-cx,height-1-cy,depth-1-cz);}
    @Override public boolean contains(int x,int y,int z) {
        int a=x+cx,b=y+cy,c=z+cz;
        if(a<0||a>=width||b<0||b>=height||c<0||c>=depth)return false;
        long position=linear(a,b,c);
        int at=Arrays.binarySearch(positions,position);
        if(at>=0)return true;
        int previous=-at-2;
        return previous>=0&&position<positions[previous]+Byte.toUnsignedInt(lengths[previous]);
    }
    private long linear(int x,int y,int z){return ((long)x*height+y)*depth+z;}
    private long position(int index){int run=runAt(index);return positions[run]+index-runStart(run);}
    private int runAt(int index) {
        int[] cached=lookup.get();
        if(index<cached[1]||index>=cached[2]) {
            int at=Arrays.binarySearch(ends,index+1);
            int run=at>=0?at:-at-1;
            cached[0]=run;cached[1]=runStart(run);cached[2]=ends[run];
        }
        return cached[0];
    }
    @Override public void close() {
        if(input!=null) {
            try {input.close();}catch(IOException ignored){}
            input=null;
        }
    }
}
