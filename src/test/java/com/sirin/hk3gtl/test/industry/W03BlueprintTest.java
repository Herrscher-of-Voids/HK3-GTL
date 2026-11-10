package com.sirin.hk3gtl.test.industry;

import com.sirin.hk3gtl.common.multiblock.pattern.Hk3StructureStream;
import java.nio.file.*;
import java.io.*;
import java.util.*;
import java.util.zip.GZIPInputStream;

/** 完整蓝图与稀疏渲染遮罩逐格互证，防止错轴、漏块和遮蔽额外世界方块。 */
public final class W03BlueprintTest {
    public static void main(String[] args)throws Exception{
        var root=Path.of("src/main/resources/data/hk3gtl/structures");
        Map<Long,long[]> tiles=new HashMap<>();long bitCount=0;
        try(var f=new DataInputStream(new GZIPInputStream(Files.newInputStream(root.resolve("w03_c9_mask.bin.gz"))))){
            check(f.readInt()==0x5730334d,"遮罩格式");int n=f.readInt();
            for(int i=0;i<n;i++){long key=f.readLong();long[] bits=new long[64];for(int j=0;j<64;j++){bits[j]=f.readLong();bitCount+=Long.bitCount(bits[j]);}check(tiles.put(key,bits)==null,"遮罩重复");}
            check(f.read()==-1,"遮罩尾随数据");
        }
        int previous=-1,count=0,controller=0,ports=0;
        try(var stream=new Hk3StructureStream(Files.newInputStream(root.resolve("w03_c9.bin.gz")))){
            var h=stream.header();check(h.width()==833&&h.height()==636&&h.depth()==833,"完整实际包围盒");
            check(h.cx()==416&&h.cy()==27&&h.cz()==187&&h.count()==6642464,"主控或数量");
            for(int i=0;i<h.count();i++){
                var c=stream.next();check(c.linear()>previous,"顺序重复或未排序");previous=c.linear();
                int x=c.linear()/(636*833),y=c.linear()/833%636,z=c.linear()%833;
                String state=h.palette().get(c.state());check(!state.equals("minecraft:air"),"空气混入蓝图");
                long key=((long)(x>>4)<<38)|((long)(z>>4)<<12)|(y>>4);var bits=tiles.get(key);int bit=((y&15)*16+(z&15))*16+(x&15);
                check(bits!=null&&(bits[bit>>>6]&(1L<<(bit&63)))!=0,"实际方块缺少遮罩");
                if(state.startsWith("hk3gtl:void_anchor_ring")){controller++;check(x==416&&y==27&&z==187,"主控位置");}
                if(y==27&&z==187&&Arrays.binarySearch(new int[]{398,402,406,410,422,426,430,434},x)>=0){check(state.equals("hk3gtl:industrial_port_casing"),"通用舱位");ports++;}
                count++;
            }stream.finish();
        }
        check(count==6642464&&bitCount==count&&controller==1&&ports==8,"实体与遮罩总量或主控接口不符");
        System.out.println("W03 C9完整6642464格、四轴字段、唯一GT主控、八通用舱位与遮罩双向一致通过");
    }
    private static void check(boolean ok,String message){if(!ok)throw new AssertionError(message);}
}
