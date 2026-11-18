package com.sirin.hk3gtl.common.multiblock.pattern;

import com.sirin.hk3gtl.common.machine.wonder.Hk3WonderCatalog;
import net.minecraft.core.Direction;

import java.io.BufferedInputStream;
import java.io.DataInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.UncheckedIOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import com.sirin.hk3gtl.common.util.Hk3PackedResources;

public final class Hk3WonderPatternSource implements AutoCloseable {
    public record Header(int width,int height,int depth,int cx,int cy,int cz,int count,List<String> palette,Direction facing) {}
    public record Cell(int x,int y,int z,int material) {}

    private final Header header;
    private final Hk3StructureStream stream;
    private final DataInputStream input;
    private final boolean hall;
    private int remaining,runs,runRemaining,runX,runY,runZ,runMaterial;
    private long previous=-1;

    public static Hk3WonderPatternSource open(String role) {
        String file=switch(role) {
            case "W01" -> "w01_hall";
            case "W02" -> "w02_19c_a2";
            case "W03" -> "w03_c9";
            default -> role.toLowerCase(Locale.ROOT)+"_candidate";
        };
        InputStream compressed=Hk3WonderPatternSource.class.getResourceAsStream("/data/hk3gtl/structures/"+file+".bin.gz");
        if(compressed==null)throw new IllegalStateException("缺少奇观正式蓝图："+role);
        try {
            return new Hk3WonderPatternSource(role,compressed);
        } catch(IOException|RuntimeException failure) {
            try {compressed.close();}catch(IOException closing){failure.addSuppressed(closing);}
            if(failure instanceof IOException io)throw new UncheckedIOException("读取奇观蓝图头失败："+role,io);
            throw (RuntimeException)failure;
        }
    }

    private Hk3WonderPatternSource(String role,InputStream compressed) throws IOException {
        hall=role.equals("W01");
        if(!hall&&!role.equals("W11")) {
            input=null;
            stream=new Hk3StructureStream(compressed);
            var source=stream.header();
            header=new Header(source.width(),source.height(),source.depth(),source.cx(),source.cy(),source.cz(),
                    source.count(),source.palette(),facing(role,source.palette()));
        } else {
            stream=null;
            input=new DataInputStream(new BufferedInputStream(Hk3PackedResources.open(compressed),65536));
            if(input.readInt()!=(hall?0x57303141:0x484B3357)||input.readInt()!=1)
                throw new IOException("奇观蓝图格式错误："+role);
            int width=input.readInt(),height=input.readInt(),depth=input.readInt();
            int cx=input.readInt(),cy=input.readInt(),cz=input.readInt(),count=input.readInt();
            if(!hall)runs=input.readInt();
            int materials=input.readUnsignedShort();
            if(width<1||height<1||depth<1||cx<0||cx>=width||cy<0||cy>=height||cz<0||cz>=depth
                    ||count<1||count>(long)width*height*depth||materials<1||!hall&&(runs<1||runs>count))
                throw new IOException("奇观蓝图尺寸或数量错误："+role);
            var palette=new ArrayList<String>(materials);
            for(int i=0;i<materials;i++)palette.add(input.readUTF());
            header=new Header(width,height,depth,cx,cy,cz,count,List.copyOf(palette),hall?Direction.WEST:facing(role,palette));
        }
        remaining=header.count();
    }

    private static Direction facing(String role,List<String> palette) throws IOException {
        String controller="hk3gtl:"+Hk3WonderCatalog.get(role).controller();
        String state=palette.stream().filter(value->value.startsWith(controller+"[")).findFirst()
                .orElseThrow(()->new IOException("奇观蓝图缺少主控状态："+role));
        int at=state.indexOf("facing=");
        if(at<0)throw new IOException("奇观蓝图缺少主控朝向："+role);
        int end=state.indexOf(',',at);
        if(end<0)end=state.indexOf(']',at);
        return Direction.valueOf(state.substring(at+7,end).toUpperCase(Locale.ROOT));
    }

    public Header header(){return header;}
    public boolean hasNext(){return remaining>0;}

    public Cell next() {
        try {
            Cell cell;
            if(stream!=null) {
                var source=stream.next();
                int position=source.linear();
                cell=new Cell(position/header.depth()/header.height(),position/header.depth()%header.height(),
                        position%header.depth(),source.state());
            } else if(hall) {
                long packed=input.readLong();
                int x=(int)(packed>>>36),y=(int)(packed>>>26)&1023,z=(int)(packed>>>16)&1023,material=(int)packed&65535;
                long position=packed>>>16;
                if(x>=header.width()||y>=header.height()||z>=header.depth()||material>=header.palette().size()||position<=previous)
                    throw new IOException("W01蓝图方块坐标或材料错误");
                previous=position;
                cell=new Cell(x,y,z,material);
            } else {
                if(runRemaining==0) {
                    runX=input.readInt();runY=input.readInt();runZ=input.readInt();
                    runRemaining=input.readUnsignedByte();runMaterial=input.readUnsignedShort();
                    long position=((long)runX*header.height()+runY)*header.depth()+runZ;
                    if(runs<1||runX<0||runX>=header.width()||runY<0||runY>=header.height()||runZ<0
                            ||runRemaining<1||runRemaining>16||runRemaining>remaining||runZ+runRemaining>header.depth()
                            ||(runZ>>4)!=((runZ+runRemaining-1)>>4)||runMaterial>=header.palette().size()||position<previous)
                        throw new IOException("W11蓝图游程坐标或材料错误");
                    runs--;previous=position+runRemaining;
                }
                cell=new Cell(runX,runY,runZ++,runMaterial);runRemaining--;
            }
            if(--remaining==0) {
                if(stream!=null)stream.finish();
                else if(runs!=0||runRemaining!=0||input.read()!=-1)throw new IOException("奇观蓝图数量或结尾错误");
            }
            return cell;
        } catch(IOException failure) {
            throw new UncheckedIOException("读取奇观蓝图方块失败",failure);
        }
    }

    @Override public void close() {
        try {
            if(stream!=null)stream.close();else input.close();
        } catch(IOException failure) {
            throw new UncheckedIOException("关闭奇观蓝图失败",failure);
        }
    }
}
