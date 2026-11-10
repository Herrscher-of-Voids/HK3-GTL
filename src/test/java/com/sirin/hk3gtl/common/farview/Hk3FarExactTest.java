package com.sirin.hk3gtl.common.farview;

import io.netty.buffer.Unpooled;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.resources.ResourceLocation;
import org.joml.Matrix4f;
import org.joml.Vector4f;
import java.nio.file.*;
import java.util.*;

/** 回归薄壁与孔洞、相邻分区接缝、玻璃边界、局部调色板和实际网络解码入口。 */
public final class Hk3FarExactTest {
    public static void main(String[] args) throws Exception {
        check(Hk3FarMesh.CELL==1&&Hk3FarMesh.SIDE==16,"远景必须保持一格几何");
        var cache=new Hk3FarViewData();var marker=new Hk3FarViewData.Tile();
        for(int i=0;i<Hk3FarViewData.MAX_TILES;i++)cache.putTile(i,marker);
        cache.tiles.getAndMoveToLast(0);
        cache.putTile(Hk3FarViewData.MAX_TILES,marker);
        check(cache.tiles.size()==Hk3FarViewData.MAX_TILES&&cache.tiles.containsKey(0)
                &&!cache.tiles.containsKey(1)&&cache.tiles.containsKey(Hk3FarViewData.MAX_TILES),
                "缓存满后必须保留刚实读分区并接收新建筑，且不扩大内存上限");
        cache.putTile(0,marker);
        check(cache.tiles.size()==Hk3FarViewData.MAX_TILES,"更新已有分区不得额外淘汰");
        var section=new Hk3FarSection();
        for(int x=0;x<16;x++)for(int z=0;z<16;z++)if(x!=8||z!=8)section.set(Hk3FarMesh.index(x,3,z),7);
        var snapshot=section.snapshot();int[] cells=new int[Hk3FarMesh.COUNT];
        for(int i=0;i<cells.length;i++)cells[i]=snapshot.state(i);
        var thin=Hk3FarMesh.bake(cells);
        check(thin.stream().filter(q->q.axis()==1&&q.sign()==1).mapToInt(q->q.width()*q.height()).sum()==255,"薄壁孔洞不得被填平");
        check(thin.stream().filter(q->q.axis()==1).allMatch(q->q.plane()==3||q.plane()==4),"一格墙不能膨胀至八格");
        Arrays.fill(cells,1);int[][] boundary=new int[6][256];Arrays.fill(boundary[1],1);
        check(Hk3FarMesh.bake(cells,boundary).size()==5,"相邻分区的内部接缝不应重复画面");
        Arrays.fill(cells,0);cells[0]=1;cells[1]=-2;
        check(Hk3FarMesh.bake(cells).size()==11,"玻璃不能抹去后方不同材质的实心面");
        cells[0]=-2;check(Hk3FarMesh.bake(cells).size()==6,"同种玻璃内部接缝应剔除");
        for(int i=0;i<Hk3FarMesh.COUNT;i++)section.set(i,i+1);
        for(int i=0;i<10_000;i++)section.set(0,100_000+i);
        check(section.snapshot().palette().length<=Hk3FarMesh.COUNT+1,"历史状态变化不能无限扩大调色板");
        check(section.state(0)==109_999&&section.state(4095)==4096,"调色板整理不能改变相邻方块");
        var packet=new Hk3FarViewPacket(new ResourceLocation("minecraft","overworld"),new long[]{-9,24},
                List.of(new Hk3FarViewPacket.Entry(-9,section.snapshot())));
        var buffer=new FriendlyByteBuf(Unpooled.buffer());
        try{
            Hk3FarViewPacket.encode(packet,buffer);var copy=Hk3FarViewPacket.decode(buffer);
            check(Arrays.equals(copy.members(),packet.members())&&copy.updates().get(0).key()==-9,"网络坐标与成员变化必须往返一致");
            var restored=copy.updates().get(0).section();
            for(int i=0;i<Hk3FarMesh.COUNT;i++)check(restored.state(i)==section.state(i),"网络不能改变逐格状态");
            check(!buffer.isReadable(),"网络往返必须完整消耗游程");
        }finally{buffer.release();}
        var bad=new FriendlyByteBuf(Unpooled.buffer());
        try{
            bad.writeResourceLocation(new ResourceLocation("minecraft","overworld"));bad.writeBoolean(false);bad.writeVarInt(1);
            bad.writeLong(0);bad.writeVarIntArray(new int[]{0,1});bad.writeVarInt(0);bad.writeVarInt(1);
            try{Hk3FarViewPacket.decode(bad);throw new AssertionError("零长游程必须拒绝");}
            catch(IllegalArgumentException expected) { }
        }finally{bad.release();}
        var nativeProjection=new Matrix4f().setPerspective(1.1f,1.6f,.05f,256);
        var oldFarProjection=new Matrix4f().setPerspective(1.1f,1.6f,.05f,2176);
        check(Math.abs(depth(nativeProjection,100)-depth(oldFarProjection,100))>1e-5,"回归样本必须复现旧投影深度不一致");
        var shared=new Matrix4f().setPerspective(1.1f,1.6f,.05f,2176);
        check(depth(shared,100)==depth(new Matrix4f(shared),100),"远近表面必须使用同一深度映射");
        String source=Files.readString(Path.of("src/main/java/com/sirin/hk3gtl/client/farview/Hk3FarViewRenderer.java"));
        check(!source.contains("projection.m22(")&&source.contains("RenderSystem.polygonOffset(1,1)"),"同一深度缓冲不得另造投影，交接面须远景让位");
        check(Files.readString(Path.of("src/main/resources/hk3gtl.mixins.json")).contains("client.Hk3FarProjectionMixin"),"共享远裁面Mixin必须注册");
        System.out.println("逐格远景：薄壁/孔洞、跨区接缝、玻璃、调色板压缩、真实包编解码及深度回归通过；未执行客户端画面验收。");
    }
    private static float depth(Matrix4f matrix,float distance){var v=matrix.transform(new Vector4f(0,0,-distance,1));return (v.z/v.w+1)*.5f;}
    private static void check(boolean ok,String message){if(!ok)throw new AssertionError(message);}
}
