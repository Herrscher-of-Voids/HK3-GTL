package com.sirin.hk3gtl.test.industry;

import com.sirin.hk3gtl.common.farview.Hk3FarMesh;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3StructureStream;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3ApprovedArchitecture;
import com.google.gson.JsonParser;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;
import java.util.zip.GZIPOutputStream;

public final class NativeFarViewTest {
    public static void main(String[] args) throws Exception {
        int[] full=new int[Hk3FarMesh.COUNT];Arrays.fill(full,1);
        check(Hk3FarMesh.bake(full).size()==6,"实心采样块未合并为六面");
        check(Hk3FarMesh.bake(new int[Hk3FarMesh.COUNT]).isEmpty(),"空气生成表面");
        var random=new Random(219);
        for(int test=0;test<50;test++) {
            int[] cells=new int[Hk3FarMesh.COUNT];
            for(int i=0;i<cells.length;i++)if(random.nextBoolean())cells[i]=1+random.nextInt(3);
            Set<String> expected=new HashSet<>(),actual=new HashSet<>();
            for(int x=0;x<Hk3FarMesh.SIDE;x++)for(int y=0;y<Hk3FarMesh.SIDE;y++)for(int z=0;z<Hk3FarMesh.SIDE;z++) {
                int color=cells[Hk3FarMesh.index(x,y,z)];if(color==0)continue;
                for(int axis=0;axis<3;axis++)for(int sign:new int[]{-1,1}) {
                    int[] p={x,y,z};p[axis]+=sign;
                    if(p[axis]>=0&&p[axis]<Hk3FarMesh.SIDE&&cells[Hk3FarMesh.index(p[0],p[1],p[2])]!=0)continue;
                    int plane=(axis==0?x:axis==1?y:z)+(sign>0?1:0);
                    int u=axis==0?y:axis==1?z:x,v=axis==0?z:axis==1?x:y;
                    expected.add(axis+":"+sign+":"+plane+":"+u+":"+v+":"+color);
                }
            }
            for(var q:Hk3FarMesh.bake(cells))for(int u=0;u<q.width();u++)for(int v=0;v<q.height();v++)
                check(actual.add(q.axis()+":"+q.sign()+":"+q.plane()+":"+(q.u()+u)+":"+(q.v()+v)+":"+q.color()),"面重复");
            check(expected.equals(actual),"贪心合面改变可见面或材质");
        }
        for(int[] run:new int[][]{{0,1,5,0,0},{0,0,2,0,0},{7,2,2,0,0},{0,1,2,1,0},{0,1,2,0,3}}) {
            boolean failed=false;
            try(var input=new Hk3StructureStream(sample(run))) {input.next();input.next();input.finish();}
            catch(IOException|IllegalArgumentException failure){failed=true;}
            check(failed,"非法游程未拒绝");
        }
        long blocks=0,bytes=0;
        for(String key:Hk3ApprovedArchitecture.IDS) {
            var metadata=JsonParser.parseReader(new InputStreamReader(Objects.requireNonNull(NativeFarViewTest.class.getResourceAsStream(
                    "/data/hk3gtl/compact_architecture/"+key+".json")),StandardCharsets.UTF_8)).getAsJsonObject();
            var digest=MessageDigest.getInstance("SHA-256");
            try(var resource=Hk3StructureStream.open(key);var input=new Hk3StructureStream(resource)) {
                var h=input.header();BitSet seen=new BitSet(h.volume());
                var hashed=new DataOutputStream(new java.security.DigestOutputStream(OutputStream.nullOutputStream(),digest));
                check(h.count()==metadata.get("blocks").getAsInt(),"方块数量不符");
                for(int i=0;i<h.count();i++) {
                    var cell=input.next();check(!seen.get(cell.linear()),"紧凑资源重复坐标");seen.set(cell.linear());
                    hashed.writeInt(cell.linear());hashed.writeShort(cell.state());hashed.writeInt(cell.entity()==null?0:cell.entity().length);
                    if(cell.entity()!=null)hashed.write(cell.entity());
                }
                check(seen.get((h.cx()*h.height()+h.cy())*h.depth()+h.cz()),"缺少主控");input.finish();
                check(HexFormat.of().formatHex(digest.digest()).equals(metadata.get("compact_records_sha256").getAsString()),"Java解码与源记录哈希不符："+key);
                blocks+=h.count();bytes+=h.count()*10L;
            }
        }
        System.out.println("原生远景：50组独立面集合对照；52份结构Java解码/逐记录哈希通过，blocks="+blocks+", rawRecords="+bytes);
    }
    private static ByteArrayInputStream sample(int[] run) throws IOException {
        var bytes=new ByteArrayOutputStream();
        try(var out=new DataOutputStream(new GZIPOutputStream(bytes))) {
            out.writeInt(0x484b3350);out.writeInt(2);
            for(int i:new int[]{2,2,2,0,0,0,2})out.writeInt(i);
            out.writeShort(1);out.writeUTF("minecraft:stone");
            out.writeInt(run[0]);out.writeInt(run[1]);out.writeInt(run[2]);out.writeShort(run[3]);out.writeInt(run[4]);
        }
        return new ByteArrayInputStream(bytes.toByteArray());
    }
    private static void check(boolean value,String message){if(!value)throw new AssertionError(message);}
}
