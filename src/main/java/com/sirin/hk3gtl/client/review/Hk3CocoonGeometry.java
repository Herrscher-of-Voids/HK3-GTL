package com.sirin.hk3gtl.client.review;

import com.google.gson.JsonParser;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.packs.resources.ResourceManager;
import net.minecraft.server.packs.resources.ResourceManagerReloadListener;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RegisterClientReloadListenersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

/**
 * 【文件职责】资源重载时读取茧的球壳与碎片几何，向场景渲染器发布不可变快照。
 * 【变更记录 #1】2026-10-01 20:00:40（内测5修订146）
 * - 删除：无；新增：独立几何资源及客户端重载监听，限制面数并拒绝非有限坐标。
 * - 修改：不涉及服务端状态；用途：预览与游戏读取同源球体，避免逐帧解析及残留旧缓存。
 * - 边界：资源损坏时清空并记日志，不阻塞一审对话和返回。
 */
/** 【变更记录 #2】2026-10-01 20:04:51（修订146追加）：删除：小尺度展示假设；新增：200格球体支持；修改：面数上限45000及场景512格距离边界，渲染器临时延长远裁面并还原雾与投影；用途：落实玩家百倍尺度与菱形核心，不让低视距截断球体。 */
@Mod.EventBusSubscriber(modid="hk3gtl", bus=Mod.EventBusSubscriber.Bus.MOD, value=Dist.CLIENT)
public final class Hk3CocoonGeometry implements ResourceManagerReloadListener {
    private static final ResourceLocation RESOURCE=new ResourceLocation("hk3gtl","models/scene/cocoon_review.json");
    private static volatile Scene scene;
    private Hk3CocoonGeometry() {}
    public record Face(float[] xyz, int red, int green, int blue, float nx, float ny, float nz) {}
    public record Part(String kind, double x, double y, double z, float bob, float phase, float speed, List<Face> faces) {}
    public record Scene(double x, double y, double z, int spacing, float bob, float yaw, float period, List<Part> parts) {}
    public static Scene current(){return scene;}
    @SubscribeEvent public static void register(RegisterClientReloadListenersEvent e){e.registerReloadListener(new Hk3CocoonGeometry());}
    private static float finite(com.google.gson.JsonElement value){
        float n=value.getAsFloat();if(!Float.isFinite(n)||Math.abs(n)>4096)throw new IllegalArgumentException("茧几何参数超出边界");return n;
    }
    private static int color(com.google.gson.JsonElement v){int n=v.getAsInt();if(n<0||n>255)throw new IllegalArgumentException("颜色越界");return n;}
    @Override public void onResourceManagerReload(ResourceManager manager){
        try(var stream=manager.getResourceOrThrow(RESOURCE).open();var reader=new InputStreamReader(stream,StandardCharsets.UTF_8)){
            var root=JsonParser.parseReader(reader).getAsJsonObject();var parts=new ArrayList<Part>();int count=0;
            var definitions=root.getAsJsonArray("parts");if(definitions.size()>128)throw new IllegalArgumentException("分件过多");
            for(var element:definitions){
                var p=element.getAsJsonObject();String kind=p.get("kind").getAsString();
                if(!List.of("solid","pulse","glow").contains(kind))throw new IllegalArgumentException("未知茧材质");
                var faces=new ArrayList<Face>();var tris=p.getAsJsonArray("triangles");
                if((count+=tris.size())>45000)throw new IllegalArgumentException("三角面过多");
                for(var tri:tris){
                    var values=tri.getAsJsonArray();if(values.size()!=12)throw new IllegalArgumentException("三角面参数错误");
                    float[] xyz=new float[9];for(int i=0;i<9;i++)xyz[i]=finite(values.get(i));
                    float ax=xyz[3]-xyz[0],ay=xyz[4]-xyz[1],az=xyz[5]-xyz[2];
                    float bx=xyz[6]-xyz[0],by=xyz[7]-xyz[1],bz=xyz[8]-xyz[2];
                    float nx=ay*bz-az*by,ny=az*bx-ax*bz,nz=ax*by-ay*bx;
                    float length=(float)Math.sqrt(nx*nx+ny*ny+nz*nz);
                    if(length<1e-8)throw new IllegalArgumentException("退化三角面");
                    faces.add(new Face(xyz,color(values.get(9)),color(values.get(10)),color(values.get(11)),nx/length,ny/length,nz/length));
                }
                var origin=p.getAsJsonArray("origin");if(origin.size()!=3)throw new IllegalArgumentException("原点错误");
                parts.add(new Part(kind,finite(origin.get(0)),finite(origin.get(1)),finite(origin.get(2)),finite(p.get("bob")),finite(p.get("phase")),finite(p.get("speed")),List.copyOf(faces)));
            }
            var center=root.getAsJsonArray("scene_center");if(center.size()!=3)throw new IllegalArgumentException("场景原点错误");
            int spacing=root.get("room_spacing").getAsInt();if(spacing!=512)throw new IllegalArgumentException("审查房间间隔不一致");
            var animation=root.getAsJsonObject("animation");float period=finite(animation.get("period_seconds"));if(period<1)throw new IllegalArgumentException("周期过小");
            scene=new Scene(finite(center.get(0)),finite(center.get(1)),finite(center.get(2)),spacing,finite(animation.get("body_bob")),finite(animation.get("yaw_amplitude")),period,List.copyOf(parts));
            com.mojang.logging.LogUtils.getLogger().info("[HK3GTL] 终焉之茧球体加载：{}分件/{}三角面",parts.size(),count);
        }catch(Exception failure){scene=null;com.mojang.logging.LogUtils.getLogger().error("[HK3GTL] 茧视觉资源加载失败，对话流程继续可用",failure);}
    }
}
