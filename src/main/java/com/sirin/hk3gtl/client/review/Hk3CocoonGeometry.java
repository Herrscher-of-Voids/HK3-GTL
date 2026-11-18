package com.sirin.hk3gtl.client.review;

import com.google.gson.JsonParser;
import com.google.gson.JsonArray;
import net.minecraft.util.GsonHelper;
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
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.joml.Vector3f;

 






 
@Mod.EventBusSubscriber(modid="hk3gtl", bus=Mod.EventBusSubscriber.Bus.MOD, value=Dist.CLIENT)
public final class Hk3CocoonGeometry implements ResourceManagerReloadListener {
    private static final ResourceLocation RESOURCE=new ResourceLocation("hk3gtl","models/scene/cocoon_review.json");
    private static volatile Scene scene;
    private Hk3CocoonGeometry() {}
    public record Face(float[] xyz, int red, int green, int blue, float nx, float ny, float nz, float[] travel, float[] across) {}
    public record Part(String kind, String group, boolean rock, boolean flow, boolean soft,
                       double x, double y, double z, float bob, float phase, float speed,
                       float intensity, float opacity, float flowWidth, List<Face> faces) {}
    public record Hotspot(double x, double y, double z, float radius, float intensity, float phase, int red, int green, int blue) {}
    public record Scene(double x, double y, double z, int spacing, float bob, float yaw, float period,
                        List<Part> parts, List<Hotspot> hotspots) {}
    private record Section(Vector3f center, Vector3f axis, float half) {}
    public static Scene current(){return scene;}
    @SubscribeEvent public static void register(RegisterClientReloadListenersEvent e){e.registerReloadListener(new Hk3CocoonGeometry());}
    private static float finite(com.google.gson.JsonElement value){
        float n=value.getAsFloat();if(!Float.isFinite(n)||Math.abs(n)>4096)throw new IllegalArgumentException("茧几何参数超出边界");return n;
    }
    private static int color(com.google.gson.JsonElement v){int n=v.getAsInt();if(n<0||n>255)throw new IllegalArgumentException("颜色越界");return n;}
    @Override public void onResourceManagerReload(ResourceManager manager){
        try(var stream=manager.getResourceOrThrow(RESOURCE).open();var reader=new InputStreamReader(stream,StandardCharsets.UTF_8)){
            var root=JsonParser.parseReader(reader).getAsJsonObject();var parts=new ArrayList<Part>();int count=0;
            var definitions=root.getAsJsonArray("parts");if(definitions.size()>512)throw new IllegalArgumentException("分件过多");
            for(var element:definitions){
                var p=element.getAsJsonObject();String kind=p.get("kind").getAsString();
                if(!List.of("solid","pulse","glow").contains(kind))throw new IllegalArgumentException("未知茧材质");
                String group=p.get("group").getAsString();
                boolean rock=GsonHelper.getAsString(p,"material","").equals("rock");
                boolean flow=GsonHelper.getAsBoolean(p,"flow",false),soft=GsonHelper.getAsBoolean(p,"softglow",false);
                var faces=new ArrayList<Face>();var tris=p.getAsJsonArray("triangles");
                var sections=flow?sections(tris):Map.<Float,Section>of();
                if((count+=tris.size())>45000)throw new IllegalArgumentException("三角面过多");
                int faceIndex=0;
                for(var tri:tris){
                    int index=faceIndex++;
                    var values=tri.getAsJsonArray();if(values.size()!=(flow?15:12))throw new IllegalArgumentException("三角面参数错误");
                    float[] xyz=new float[9];for(int i=0;i<9;i++)xyz[i]=finite(values.get(i));
                    float ax=xyz[3]-xyz[0],ay=xyz[4]-xyz[1],az=xyz[5]-xyz[2];
                    float bx=xyz[6]-xyz[0],by=xyz[7]-xyz[1],bz=xyz[8]-xyz[2];
                    float nx=ay*bz-az*by,ny=az*bx-ax*bz,nz=ax*by-ay*bx;
                    float length=(float)Math.sqrt(nx*nx+ny*ny+nz*nz);
                    // 地表裁切的零面积面没有可见贡献，不让它阻断整份模型。
                    if(length<1e-8)continue;
                    float[] travel=new float[3],across=new float[3];
                    for(int i=0;i<3;i++){
                        if(flow){
                            travel[i]=finite(values.get(12+i));var section=sections.get(travel[i]);
                            across[i]=new Vector3f(xyz[i*3],xyz[i*3+1],xyz[i*3+2]).sub(section.center()).dot(section.axis())/section.half();
                        }else if(soft)across[i]=index%2==0?(i==0?-1:1):(i==1?1:-1);
                    }
                    int red=color(values.get(9)),green=color(values.get(10)),blue=color(values.get(11));
                    if(rock){red=(int)(red*1.22+25);green=(int)(green*1.17+20);blue=(int)(blue*1.22+35);}
                    if(group.equals("stream")&&red>green*1.12){green=(int)(green*.62);blue=(int)(blue*.98);}
                    if(group.equals("core")){green=(int)(green*.82);blue=(int)(blue*.96);}
                    faces.add(new Face(xyz,red,green,blue,nx/length,ny/length,nz/length,travel,across));
                }
                var origin=p.getAsJsonArray("origin");if(origin.size()!=3)throw new IllegalArgumentException("原点错误");
                float intensity=GsonHelper.getAsFloat(p,"intensity",1);
                intensity*=group.equals("stream")?.72f:group.equals("core")?.82f:GsonHelper.getAsString(p,"material","").equals("crystal")?.5f:1;
                parts.add(new Part(kind,group,rock,flow,soft,finite(origin.get(0)),finite(origin.get(1)),finite(origin.get(2)),
                        finite(p.get("bob")),finite(p.get("phase")),finite(p.get("speed")),intensity,
                        GsonHelper.getAsFloat(p,"opacity",kind.equals("glow")?.3f:1),GsonHelper.getAsFloat(p,"flowWidth",1),List.copyOf(faces)));
            }
            var center=root.getAsJsonArray("scene_center");if(center.size()!=3)throw new IllegalArgumentException("场景原点错误");
            int spacing=root.get("room_spacing").getAsInt();if(spacing!=512)throw new IllegalArgumentException("审查房间间隔不一致");
            var animation=root.getAsJsonObject("animation");float period=finite(animation.get("period_seconds"));if(period<1)throw new IllegalArgumentException("周期过小");
            var hotspots=new ArrayList<Hotspot>();
            for(var element:root.getAsJsonArray("hotspots")){
                var h=element.getAsJsonObject();var at=h.getAsJsonArray("position");var rgb=h.getAsJsonArray("color");
                hotspots.add(new Hotspot(finite(at.get(0)),finite(at.get(1)),finite(at.get(2)),finite(h.get("radius")),finite(h.get("intensity")),finite(h.get("phase")),color(rgb.get(0)),color(rgb.get(1)),color(rgb.get(2))));
            }
            scene=new Scene(finite(center.get(0)),finite(center.get(1)),finite(center.get(2)),spacing,finite(animation.get("body_bob")),finite(animation.get("yaw_amplitude")),period,List.copyOf(parts),List.copyOf(hotspots));
            com.mojang.logging.LogUtils.getLogger().info("[HK3GTL] 终焉之茧R8嵌地半球加载：{}分件/{}有效三角面/{}原始面",parts.size(),parts.stream().mapToInt(part->part.faces().size()).sum(),count);
        }catch(Exception failure){scene=null;com.mojang.logging.LogUtils.getLogger().error("[HK3GTL] 茧视觉资源加载失败，对话流程继续可用",failure);}
    }
    private static Map<Float,Section> sections(JsonArray triangles){
        var rows=new HashMap<Float,List<Vector3f>>();
        for(var element:triangles){
            var triangle=element.getAsJsonArray();
            for(int i=0;i<3;i++){
                var row=rows.computeIfAbsent(triangle.get(12+i).getAsFloat(),key->new ArrayList<>());
                var point=new Vector3f(triangle.get(i*3).getAsFloat(),triangle.get(i*3+1).getAsFloat(),triangle.get(i*3+2).getAsFloat());
                if(!row.contains(point))row.add(point);
            }
        }
        var result=new HashMap<Float,Section>();
        rows.forEach((distance,points)->{
            float length=0;var left=points.get(0);var right=left;
            for(var a:points)for(var b:points){
                float squared=a.distanceSquared(b);
                if(squared>length){length=squared;left=a;right=b;}
            }
            result.put(distance,new Section(new Vector3f(left).add(right).mul(.5f),new Vector3f(right).sub(left).normalize(),(float)Math.sqrt(length)*.5f));
        });
        return result;
    }
}
