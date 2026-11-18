package com.sirin.hk3gtl.test.industry;

import com.sirin.hk3gtl.common.multiblock.pattern.Hk3StructureStream;
import java.nio.file.*;
import java.util.Arrays;

/** A2完整实体、唯一控制器、八通用接口及严格有序记录回归。 */
public final class W02BlueprintTest {
    public static void main(String[] args)throws Exception{
        try(var in=new Hk3StructureStream(Files.newInputStream(Path.of("src/main/resources/data/hk3gtl/structures/w02_19c_a2.bin.gz")))){
            var h=in.header();check(h.width()==649&&h.height()==368&&h.depth()==493,"完整几何边界");
            check(h.cx()==324&&h.cy()==23&&h.cz()==482,"前方控制器位置");
            int previous=-1,control=0,ports=0;
            for(int i=0;i<h.count();i++){
                var cell=in.next();check(cell.linear()>previous,"记录重复或错序");previous=cell.linear();
                String state=h.palette().get(cell.state());check(!state.endsWith(":air"),"空气不能写入结构");
                int x=cell.linear()/h.depth()/h.height(),y=cell.linear()/h.depth()%h.height(),z=cell.linear()%h.depth();
                if(state.startsWith("hk3gtl:omnia_autonomous_industrial_matrix")){
                    control++;check(x==h.cx()&&y==h.cy()&&z==h.cz()&&state.contains("facing=south"),"主控朝向和坐标");
                }
                if(state.equals("hk3gtl:industrial_port_casing")){
                    int dx=x-h.cx(),dy=y-h.cy();
                    check(z==h.cz()&&Math.abs(dx)<=1&&Math.abs(dy)<=1&&(dx!=0||dy!=0),"接口必须原位替换主控三乘三八邻位");ports++;
                }
            }
            in.finish();check(control==1&&ports==8&&h.count()==6072490,"完整实体总数与真实接口");
        }
        System.out.println("W02 A2完整实体、唯一真实GT主控、八通用接口及无空气记录通过");
    }
    private static void check(boolean ok,String message){if(!ok)throw new AssertionError(message);}
}
