package com.sirin.hk3gtl.test.industry;

import com.sirin.hk3gtl.common.multiblock.pattern.Hk3LiquidLineLayout;
import java.util.ArrayDeque;
import java.util.HashSet;
import java.util.Set;

/**
 * 【变更记录 #1】2026-09-24 16:42:00（内测5修订66）
 * 新增七机真实逐格布局测试；不生成结构、图片或预览。删除：无。
 * 修改：构建时验证规划尺寸、材料、通道、物流分离和建筑连通性；用途：拒绝占位盒与悬空构件。
 */
public final class LiquidLineLayoutTest {
    public static void main(String[] args) throws java.io.IOException {
        int[][] expected={{25,25,29},{21,33,21},{21,29,25},{25,21,33},{19,19,21},{33,29,41},{41,33,45}};
        check(Hk3LiquidLineLayout.VOLTAGE_TIER == com.gregtechceu.gtceu.api.GTValues.MAX,
                "第一条工业线必须以 MAX 电压为结构科技基准");
        check(Hk3LiquidLineLayout.TECHNOLOGY_LEVEL.equals("MAX"), "结构科技等级名称必须为 MAX");
        int index=0;
        for(var kind:Hk3LiquidLineLayout.Kind.values()) {
            var layout=Hk3LiquidLineLayout.create(kind);var counts=layout.counts();var size=expected[index++];
            check(kind.width==size[0]&&kind.height==size[1]&&kind.depth==size[2],"规划尺寸："+kind);
            check(counts.getOrDefault('S',0)==1,"唯一控制器："+kind);
            boolean injection=kind==Hk3LiquidLineLayout.Kind.INJECTION;
            check(counts.getOrDefault('i',0)==(injection?8:2)&&counts.getOrDefault('h',0)==(injection?0:1),"输入与并行接口："+kind);
            check(counts.getOrDefault('o',0)==(kind==Hk3LiquidLineLayout.Kind.INJECTION?0:2),"物品输出："+kind);
            check(counts.getOrDefault('u',0)==(kind==Hk3LiquidLineLayout.Kind.CALIBRATION||injection?0:4),"流体输入："+kind);
            check(counts.getOrDefault('v',0)==(kind==Hk3LiquidLineLayout.Kind.CALIBRATION||kind==Hk3LiquidLineLayout.Kind.INJECTION?0:4),"流体输出："+kind);
            for(char c:counts.keySet())check("#Siouvh".indexOf(c)>=0||layout.materials().containsKey(c),"材料映射："+c);
            for(var material:layout.materials().values())
                check(injection?material.startsWith("gtceu:"):Hk3LiquidLineLayout.MAX_MATERIALS.contains(material),
                        "MAX 结构不得回退到低阶或原版材料："+material);
            check(counts.get('#')>kind.width*kind.height*kind.depth*0.65,"必须保留空腔和空间："+kind);
            for(int z=injection?4:1;z<kind.depth;z++)for(int y=1;y<=3;y++)for(int x=kind.width/2-1;x<=kind.width/2+1;x++)
                check(layout.at(x,y,z)=='#',"三格宽检修通道："+kind+" "+x+","+y+","+z);
            // 建筑所有实体都需以面相邻方式连到基础，不能用悬浮线圈充当复杂造型。
            Set<Integer> visited=new HashSet<>();ArrayDeque<int[]> queue=new ArrayDeque<>();queue.add(new int[]{0,0,injection?4:0});
            while(!queue.isEmpty()) {
                int[] p=queue.remove();int x=p[0],y=p[1],z=p[2];
                if(x<0||x>=kind.width||y<0||y>=kind.height||z<0||z>=kind.depth||layout.at(x,y,z)=='#')continue;
                int key=(z*kind.height+y)*kind.width+x;if(!visited.add(key))continue;
                for(int[] step:new int[][]{{1,0,0},{-1,0,0},{0,1,0},{0,-1,0},{0,0,1},{0,0,-1}})
                    queue.add(new int[]{x+step[0],y+step[1],z+step[2]});
            }
            int solids=kind.width*kind.height*kind.depth-counts.get('#');
            if(visited.size()!=solids)for(int z=0;z<kind.depth;z++)for(int y=0;y<kind.height;y++)for(int x=0;x<kind.width;x++)
                if(layout.at(x,y,z)!='#'&&!visited.contains((z*kind.height+y)*kind.width+x))
                    System.out.println("未连接构件："+kind+" "+x+","+y+","+z+" "+layout.at(x,y,z));
            check(visited.size()==solids,"实体悬空："+kind+" 未连接="+(solids-visited.size()));
            System.out.println(kind+"：尺寸、接口、严格空气、通道、材料与连通性通过；实体方块="+solids);
            if(injection) {
                check(layout.at(20,2,0)=='S',"注入器主控必须居中且位于前面");
                for(int x=19;x<=21;x++)for(int y=1;y<=3;y++) {
                    check(layout.at(x,y,0)==(x==20&&y==2?'S':'i'),"贴身八接口");
                    check(layout.at(x,y,1)=='C',"接口必须有背壳");
                }
                check(counts.get('C')>solids/2,"原生MAX机壳应为主体");
                for(int x:new int[]{2,38})for(int z=7;z<=40;z++)if(layout.at(x,5,z)=='K')
                    for(int y=0;y<=4;y++)check(layout.at(x,y,z)=='C',"散热件须逐柱承托到底座："+x+","+y+","+z);
                if(args.length==1)export(layout,java.nio.file.Path.of(args[0]));
            }
        }
    }
    private static void export(Hk3LiquidLineLayout layout,java.nio.file.Path path) throws java.io.IOException {
        var data=new java.util.LinkedHashMap<String,Object>();
        data.put("key","network_injector");data.put("id","NETWORK_INJECTOR");
        data.put("name","honkai-network-injector-max-v2-20261111");
        data.put("title","崩坏能网络注入器 · 三段谐振入网站");
        data.put("size",new int[]{layout.kind.width,layout.kind.height,layout.kind.depth});
        data.put("controller",new int[]{20,2,0});data.put("controller_face","north");
        data.put("controller_surface","hk3gtl:industrial_port_casing");data.put("tier","MAX");
        var blocks=new java.util.ArrayList<Object>();var ports=new java.util.ArrayList<Object>();
        for(int x=0;x<layout.kind.width;x++)for(int y=0;y<layout.kind.height;y++)for(int z=0;z<layout.kind.depth;z++) {
            char c=layout.at(x,y,z);if(c=='#')continue;
            String state=c=='S'?"minecraft:diamond_block":c=='i'?"hk3gtl:industrial_port_casing":layout.materials().get(c);
            int[] pos={x,y,z};blocks.add(java.util.Map.of("pos",pos,"state",state));
            if(c=='i')ports.add(java.util.Map.of("id","U"+(ports.size()+1),"pos",pos,"face","north",
                    "group","universal","purpose","通用仓口：物品、流体、可选并行或封板","surface_state","hk3gtl:industrial_port_casing"));
        }
        data.put("blocks",blocks);data.put("ports",ports);data.put("materials",layout.materials());
        data.put("game_verified",false);data.put("appearance_approved",false);
        java.nio.file.Files.createDirectories(path.toAbsolutePath().getParent());
        java.nio.file.Files.writeString(path,new com.google.gson.GsonBuilder().setPrettyPrinting().create().toJson(data),java.nio.charset.StandardCharsets.UTF_8);
    }
    private static void check(boolean valid,String reason) {if(!valid)throw new AssertionError(reason);}
}
