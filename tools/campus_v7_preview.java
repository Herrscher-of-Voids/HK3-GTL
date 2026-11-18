import com.google.gson.*;
import com.gtl.enhancedcore.common.world.plot.*;
import com.sirin.hk3gtl.common.campus.*;
import com.sirin.hk3gtl.common.multiblock.pattern.*;
import com.sirin.hk3gtl.common.multiblock.build.Hk3W11BuildPlan;
import com.sirin.hk3gtl.common.machine.ae.Hk3NexusStructure;
import com.sirin.hk3gtl.common.machine.wonder.Hk3WonderCatalog;
import net.minecraft.core.Direction;
import net.minecraft.nbt.*;
import net.minecraft.resources.ResourceLocation;
import javax.imageio.ImageIO;
import java.awt.image.BufferedImage;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.security.MessageDigest;
import java.time.Instant;
import java.util.*;
import java.util.List;
import java.util.function.IntBinaryOperator;

public class campus_v7_preview {
    static final Path ROOT=Path.of("").toAbsolutePath();
    static final Path OUTPUT=ROOT.resolve(System.getProperty("hk3gtl.campus.preview.output","deliveries/0000预设地图_V7_十字路口_20261117"));
    static final Path LOG=ROOT.resolve("logs/0000-campus-junctions-20261117");
    static final Gson GSON=new GsonBuilder().setPrettyPrinting().disableHtmlEscaping().create();
    static final Map<String,Integer> COLORS=new HashMap<>();
    static final Map<String,Map<String,String>> MODELS=new HashMap<>();
    static final Map<String,String> MATERIAL_TEXTURES=new TreeMap<>();
    static final Map<String,String> INPUTS=new TreeMap<>();
    record Scene(String id,String title,PlannedCampus.Bounds original,PlannedCampus.Bounds ae,int originalPlots,
                 IntBinaryOperator originalColor,Hk3CampusStyle style) {}
    record Region(int minX,int minZ,int maxX,int maxZ) {
        int width(){return maxX-minX+1;}
        int depth(){return maxZ-minZ+1;}
    }
    public static void main(String[] args)throws Exception {
        Files.createDirectories(OUTPUT);Files.createDirectories(LOG);
        var entries=catalog();
        var field=Hk3CampusCatalog.class.getDeclaredField("entries");field.setAccessible(true);field.set(null,entries);
        var scenes=new ArrayList<Scene>();
        scenes.add(new Scene("modern","现代园区",bounds(LegacyPlannedCampus.bounds()),bounds(LegacyPlannedCampus.aeCoreBounds()),
                LegacyPlannedCampus.plots().size(),LegacyPlannedCampus::previewColorAt,style(Hk3CampusStyle.Kind.MODERN)));
        scenes.add(new Scene("quartz_works","石英工厂",FileCampus.of("quartz_works").bounds(),FileCampus.of("quartz_works").aeCoreBounds(),
                FileCampus.of("quartz_works").plots().size(),FileCampus.of("quartz_works")::previewColorAt,fileStyle("quartz_works",Hk3CampusStyle.Kind.FACTORY)));
        scenes.add(new Scene("woodland","林地园区",PlannedCampus.bounds(),PlannedCampus.aeCoreBounds(),PlannedCampus.plots().size(),
                PlannedCampus::previewColorAt,style(Hk3CampusStyle.Kind.WOODLAND)));
        var pink=FileCampus.of("pink_dream_home_v1");
        scenes.add(new Scene("pink","粉色梦境",pink.bounds(),pink.aeCoreBounds(),pink.plots().size(),pink::previewColorAt,fileStyle("pink_dream_home_v1",Hk3CampusStyle.Kind.PINK)));
        scenes.add(new Scene("park","公园园区",bounds(ParkPlannedCampus.bounds()),bounds(ParkPlannedCampus.aeCoreBounds()),ParkPlannedCampus.plots().size(),
                ParkPlannedCampus::previewColorAt,style(Hk3CampusStyle.Kind.PARK)));
        scenes.add(new Scene("compact","紧凑园区",bounds(CompactPlannedCampus.bounds()),bounds(CompactPlannedCampus.aeCoreBounds()),CompactPlannedCampus.plots().size(),
                CompactPlannedCampus::previewColorAt,style(Hk3CampusStyle.Kind.COMPACT)));
        scenes.add(new Scene("dense","密集园区",bounds(DensePlannedCampus.bounds()),bounds(DensePlannedCampus.aeCoreBounds()),DensePlannedCampus.plots().size(),
                DensePlannedCampus::previewColorAt,style(Hk3CampusStyle.Kind.DENSE)));
        var metadata=new JsonObject();metadata.addProperty("layoutVersion",7);metadata.addProperty("generatedAt",Instant.now().toString());
        metadata.addProperty("previewKind","离线真实地面与地块俯视，原园区使用原生预览色；新增区采样正式Plan顶面材质均色，机器建筑仅显示占地与主控标记");
        metadata.addProperty("catalogKind","按当前生产目录筛选规则读取正式资源头与注册源码，未启动游戏注册");
        metadata.addProperty("catalogCount",entries.size());
        metadata.addProperty("surfaceY",-53);
        metadata.addProperty("colorSampling","原生预览色与顶面PNG首帧均色；植物、水色采用固定默认生物群系色，模型透明混合与光影未绘入");
        var sceneData=new JsonArray();metadata.add("scenes",sceneData);
        for(var scene:scenes){
            if(args.length>0&&!scene.id.equals(args[0]))continue;
            System.out.println("开始 "+scene.id);System.out.flush();
            var b=scene.original;
            var plan=Hk3CampusExpansion.plan(scene.id+":7",b.minX(),b.minZ(),b.maxX(),b.maxZ(),-53,scene.style,7,scene.ae);
            var region=new Region(Math.min(b.minX(),plan.minX()),Math.min(b.minZ(),plan.minZ()),Math.max(b.maxX(),plan.maxX()),Math.max(b.maxZ(),plan.maxZ()));
            double scale=Math.max(1.0,Math.max(region.width(),region.depth())/2200.0);
            String name=scene.id+"-v7-top.png";render(scene,plan,region,scale,name);
            var row=new JsonObject();row.addProperty("id",scene.id);row.addProperty("title",scene.title);row.addProperty("image",name);
            row.add("bounds",GSON.toJsonTree(region));row.addProperty("blocksPerPixel",scale);
            row.addProperty("originalPlotCount",scene.originalPlots);row.addProperty("addedPlotCount",plan.plots().size());
            row.add("originalBounds",GSON.toJsonTree(b));row.add("aeBounds",GSON.toJsonTree(scene.ae));
            var plots=new JsonArray();
            for(var plot:plan.plots()){
                var p=new JsonObject();p.addProperty("key",plot.entry().key());p.addProperty("machine",plot.entry().machineId().toString());
                p.addProperty("name",displayName(plot.entry().machineId().getPath()));p.addProperty("tier",plot.entry().tier());
                p.addProperty("minX",plot.structureMinX());p.addProperty("minZ",plot.structureMinZ());p.addProperty("maxX",plot.structureMaxX());p.addProperty("maxZ",plot.structureMaxZ());
                p.addProperty("controllerX",plot.controllerX());p.addProperty("controllerZ",plot.controllerZ());plots.add(p);
            }
            row.add("plots",plots);
            if(scene.id.equals("modern"))row.add("detailImages",details(scene,plan));
            sceneData.add(row);Files.writeString(OUTPUT.resolve("preview.json"),GSON.toJson(metadata),StandardCharsets.UTF_8);
            System.out.println("完成 "+scene.id+" "+region+" 新增="+plan.plots().size());System.out.flush();
        }
        metadata.add("inputHashes",GSON.toJsonTree(INPUTS));metadata.add("materialTextures",GSON.toJsonTree(MATERIAL_TEXTURES));
        metadata.addProperty("gameStarted",false);metadata.addProperty("jarBuilt",false);metadata.addProperty("instanceChanged",false);
        Files.writeString(OUTPUT.resolve("preview.json"),GSON.toJson(metadata),StandardCharsets.UTF_8);
    }
    static List<Hk3CampusCatalog.Entry> catalog()throws Exception {
        var entries=new ArrayList<Hk3CampusCatalog.Entry>();var approved=new HashSet<String>();
        var voltages=List.of("ULV","LV","MV","HV","EV","IV","LuV","ZPM","UV","UHV","UEV","UIV","UXV","OpV","MAX","HBV","HCV","HRV","HDV","QSV","QCV","QEV","QAV","IMV","ICV","IRV","IWV","WFV","WSV","CIV","CEV");
        for(String key:Hk3ApprovedArchitecture.IDS){
            String path="/data/hk3gtl/compact_architecture/"+key+".json";
            JsonObject json;try(var stream=campus_v7_preview.class.getResourceAsStream(path)){json=JsonParser.parseReader(new InputStreamReader(stream,StandardCharsets.UTF_8)).getAsJsonObject();}
            resourceHash(path);var size=json.getAsJsonArray("size");var control=json.getAsJsonArray("controller");String id=json.get("machine").getAsString();approved.add(id);
            int tier=json.has("target_voltage")?voltages.indexOf(json.get("target_voltage").getAsString()):14;
            entries.add(new Hk3CampusCatalog.Entry(new ResourceLocation(id),key,tier,size.get(0).getAsInt(),size.get(1).getAsInt(),size.get(2).getAsInt(),
                    control.get(0).getAsInt(),control.get(1).getAsInt(),control.get(2).getAsInt(),Direction.NORTH,null));
        }
        for(String id:Hk3SparsePreviewData.machines()){
            if(approved.contains(id))continue;
            var source=Hk3SparsePreviewData.source(id);String key=source.key();
            int tier=id.equals("hk3gtl:hyperion_flagship")?28:Hk3WonderCatalog.ALL.stream().filter(w->id.equals("hk3gtl:"+w.controller())&&Hk3WonderCatalog.hasBlueprint(w.role())).findFirst().orElseThrow().runtimeTier();
            String path="/data/hk3gtl/structures/"+(key.equals("w01")?"w01_hall":key)+".bin.gz";resourceHash(path);
            int[] h;
            if(key.equals("w11_candidate")){var header=Hk3W11BuildPlan.header();h=new int[]{header.width(),header.height(),header.depth(),header.cx(),header.cy(),header.cz()};}
            else try(var input=new DataInputStream(new java.util.zip.GZIPInputStream(campus_v7_preview.class.getResourceAsStream(path)))){input.readInt();input.readInt();h=new int[]{input.readInt(),input.readInt(),input.readInt(),input.readInt(),input.readInt(),input.readInt()};}
            entries.add(new Hk3CampusCatalog.Entry(new ResourceLocation(id),key,tier,h[0],h[1],h[2],h[3],h[4],h[5],source.front(),null));
        }
        var template=Hk3NexusStructure.template();var size=template.getList("size",Tag.TAG_INT);var palette=template.getList("palette",Tag.TAG_COMPOUND);
        for(var raw:template.getList("blocks",Tag.TAG_COMPOUND)){
            var block=(CompoundTag)raw;var state=palette.getCompound(block.getInt("state"));
            if(!state.getString("Name").equals("hk3gtl:ae_nexus"))continue;
            var pos=block.getList("pos",Tag.TAG_INT);entries.add(new Hk3CampusCatalog.Entry(new ResourceLocation("hk3gtl:ae_nexus"),"ae_nexus_a1",14,size.getInt(0),size.getInt(1),size.getInt(2),pos.getInt(0),pos.getInt(1),pos.getInt(2),Direction.byName(state.getCompound("Properties").getString("facing")),null));
        }
        resourceHash("/data/hk3gtl/structures/ae_nexus_a1.nbt");
        var kind=Hk3LiquidLineLayout.Kind.INJECTION;var injection=Hk3LiquidLineLayout.create(kind);
        for(int x=0;x<kind.width;x++)for(int y=0;y<kind.height;y++)for(int z=0;z<kind.depth;z++)if(injection.at(x,y,z)=='S')
            entries.add(new Hk3CampusCatalog.Entry(new ResourceLocation("hk3gtl:honkai_network_injector"),"network_injector_v2",14,kind.width,kind.height,kind.depth,x,y,z,Direction.NORTH,null));
        entries.sort(Comparator.comparingInt(Hk3CampusCatalog.Entry::tier).thenComparing(Hk3CampusCatalog.Entry::key));
        Files.writeString(LOG.resolve("catalog.json"),GSON.toJson(entries.stream().map(e->Map.of("machine",e.machineId().toString(),"key",e.key(),"tier",e.tier(),"size",List.of(e.sizeX(),e.sizeY(),e.sizeZ()),"controller",List.of(e.controllerX(),e.controllerY(),e.controllerZ()),"front",e.front().name())).toList()),StandardCharsets.UTF_8);
        for(String path:List.of("src/main/java/com/sirin/hk3gtl/common/campus/Hk3CampusCatalog.java","src/main/java/com/sirin/hk3gtl/common/campus/Hk3CampusNativeRoad.java","src/main/java/com/sirin/hk3gtl/common/campus/Hk3CampusExpansion.java","src/main/java/com/sirin/hk3gtl/common/campus/Hk3EnhancedCampusBridge.java","src/main/java/com/sirin/hk3gtl/common/machine/wonder/Hk3WonderCatalog.java","src/main/java/com/sirin/hk3gtl/common/multiblock/pattern/Hk3ApprovedArchitecture.java","src/main/java/com/sirin/hk3gtl/common/multiblock/pattern/Hk3SparsePreviewData.java","src/main/java/com/sirin/hk3gtl/common/machine/Hk3IndustrialExtensionMachines.java","src/main/java/com/sirin/hk3gtl/common/machine/ae/Hk3NexusMachines.java","src/main/java/com/sirin/hk3gtl/common/machine/hyperion/Hk3HyperionMachines.java","tools/campus_v7_preview.java","logs/0000-campus-junctions-20261117/export-command.ps1","libs/GTL-Enhancedcore-5.2.6.jar"))INPUTS.put(path,hash(Files.readAllBytes(ROOT.resolve(path))));
        try(var files=Files.walk(ROOT.resolve("logs/0000-campus-junctions-20261117/compile-output/classes/java/main/com/sirin/hk3gtl/common/campus"))){for(var path:files.filter(p->p.toString().endsWith(".class")).toList())INPUTS.put(ROOT.relativize(path).toString().replace('\\','/'),hash(Files.readAllBytes(path)));}
        return List.copyOf(entries);
    }
    static void resourceHash(String path)throws Exception{try(var stream=campus_v7_preview.class.getResourceAsStream(path)){INPUTS.put(path,hash(stream.readAllBytes()));}}
    static String hash(byte[] bytes)throws Exception{return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes));}
    static PlannedCampus.Bounds bounds(Object b)throws Exception{
        var type=b.getClass();return new PlannedCampus.Bounds((int)type.getMethod("minX").invoke(b),(int)type.getMethod("minZ").invoke(b),(int)type.getMethod("maxX").invoke(b),(int)type.getMethod("maxZ").invoke(b));
    }
    static String displayName(String id)throws IOException{
        try(var reader=Files.newBufferedReader(ROOT.resolve("src/main/resources/assets/hk3gtl/lang/zh_cn.json"))){var lang=JsonParser.parseReader(reader).getAsJsonObject();String key="block.hk3gtl."+id;return lang.has(key)?lang.get(key).getAsString():id;}
    }
    static Hk3CampusStyle style(Hk3CampusStyle.Kind kind){
        String floor=switch(kind){case PARK,WOODLAND->"polished_andesite";case COMPACT->"smooth_stone";default->"light_gray_concrete";};
        String road=switch(kind){case PARK,DENSE->"smooth_quartz";case COMPACT->"polished_andesite";case WOODLAND->"stone_bricks";default->"black_concrete";};
        String leaves=switch(kind){case MODERN,WOODLAND->"oak_leaves";case DENSE->"birch_leaves";default->"azalea_leaves";};
        return new Hk3CampusStyle(kind.name(),"minecraft:"+floor,"minecraft:"+road,"minecraft:smooth_quartz","minecraft:polished_andesite","minecraft:cyan_concrete","minecraft:quartz_pillar[axis=y]","minecraft:"+leaves+"[persistent=true]","minecraft:sea_lantern",kind==Hk3CampusStyle.Kind.MODERN?"minecraft:green_concrete":"minecraft:grass_block",kind,null);
    }
    static Hk3CampusStyle fileStyle(String id,Hk3CampusStyle.Kind kind){var d=CampusPresetRegistry.get(id);var m=d.materials();return new Hk3CampusStyle(id,m.get("floor"),m.get("road"),m.get("quartz"),m.get("dark"),m.get("accent"),m.get("column"),m.get("leaves"),m.get("light"),m.get("green"),kind,d.architectureResource());}
    static void render(Scene scene,Hk3CampusExpansion.Plan plan,Region region,double scale,String name)throws Exception{
        int width=(int)Math.ceil(region.width()/scale),height=(int)Math.ceil(region.depth()/scale);var image=new BufferedImage(width,height,BufferedImage.TYPE_INT_RGB);
        for(int py=0;py<height;py++)for(int px=0;px<width;px++){
            int x=region.minX+(int)((px+0.5)*scale),z=region.minZ+(int)((py+0.5)*scale);
            int rgb=scene.originalColor.applyAsInt(x,z);
            if(plan.terrainAt(x,z)){String block=plan.blockAt(x,plan.topAt(x,z),z);rgb=color(block);}
            image.setRGB(px,py,rgb);
        }
        ImageIO.write(image,"png",OUTPUT.resolve(name).toFile());
    }
    static JsonArray details(Scene scene,Hk3CampusExpansion.Plan plan)throws Exception{
        var field=Hk3CampusExpansion.Plan.class.getDeclaredField("nativeDecoration");field.setAccessible(true);Object decoration=field.get(plan);
        var cells=decoration.getClass().getDeclaredField("cells");cells.setAccessible(true);var placements=(Map<?,?>)cells.get(decoration);
        Object placement=((List<?>)placements.values().iterator().next()).get(0);var type=placement.getClass();
        var mx=type.getDeclaredMethod("minX");mx.setAccessible(true);var mz=type.getDeclaredMethod("minZ");mz.setAccessible(true);
        int x=(int)mx.invoke(placement),z=(int)mz.invoke(placement);
        int minX=Math.max(plan.minX(),Math.min(plan.maxX()-799,x-260)),minZ=Math.max(plan.minZ(),Math.min(plan.maxZ()-799,z-260));
        var region=new Region(minX,minZ,minX+799,minZ+799);
        String name="modern-v7-native-detail.png";render(scene,plan,region,1,name);var row=new JsonObject();
        row.addProperty("title","新增区原生花园与道路，1格/像素");row.addProperty("image",name);row.add("bounds",GSON.toJsonTree(region));row.addProperty("blocksPerPixel",1);
        var junction=new Region(-64,-1592,63,-1465);
        String junctionName="modern-v7-junction-detail.png";render(scene,plan,junction,1,junctionName);
        var crossing=new JsonObject();crossing.addProperty("title","十字路口近景");crossing.addProperty("image",junctionName);
        crossing.add("bounds",GSON.toJsonTree(junction));crossing.addProperty("blocksPerPixel",1);
        var sideJunction=new Region(-1584,-1460,-1457,-1333);
        String sideName="modern-v7-side-junction-detail.png";render(scene,plan,sideJunction,1,sideName);
        var side=new JsonObject();side.addProperty("title","主副路接驳近景");side.addProperty("image",sideName);
        side.add("bounds",GSON.toJsonTree(sideJunction));side.addProperty("blocksPerPixel",1);
        var result=new JsonArray();result.add(crossing);result.add(side);result.add(row);return result;
    }
    static int color(String block) throws IOException {
        Integer cached = COLORS.get(block);
        if (cached != null) return cached;
        String id = block.split("\\[", 2)[0], texture;
        var textures = materialModel(id);
        texture = List.of("top", "end", "all", "up", "side", "texture", "particle", "cross").stream()
                .filter(textures::containsKey).map(textures::get).findFirst().orElseThrow();
        while (texture.startsWith("#")) texture = textures.get(texture.substring(1));
        String path = asset(texture, "textures", ".png");
        BufferedImage image;
        try (var stream = campus_v7_preview.class.getResourceAsStream("/" + path)) { image = ImageIO.read(stream); }
        long red = 0, green = 0, blue = 0, count = 0;
        for (int y = 0; y < Math.min(image.getHeight(), image.getWidth()); y++) for (int x = 0; x < image.getWidth(); x++) {
            int rgba = image.getRGB(x, y), alpha = rgba >>> 24;
            if (alpha < 32) continue;
            red += (rgba >> 16 & 255) * alpha; green += (rgba >> 8 & 255) * alpha; blue += (rgba & 255) * alpha; count += alpha;
        }
        int rgb = (int) (red / count) << 16 | (int) (green / count) << 8 | (int) (blue / count);
        if (Set.of("minecraft:oak_leaves", "minecraft:jungle_leaves", "minecraft:acacia_leaves", "minecraft:dark_oak_leaves",
                "minecraft:mangrove_leaves").contains(id)) rgb = multiply(rgb, 0x77AB2F);
        if (id.equals("minecraft:birch_leaves")) rgb = multiply(rgb, 0x80A755);
        if (id.equals("minecraft:spruce_leaves")) rgb = multiply(rgb, 0x619961);
        if (id.equals("minecraft:grass_block") || id.equals("minecraft:fern")) rgb = multiply(rgb, 0x91BD59);
        if (id.equals("minecraft:water")) rgb = multiply(rgb, 0x3F76E4);
        COLORS.put(block, rgb); MATERIAL_TEXTURES.put(block, path);
        return rgb;
    }

    static Map<String, String> model(String id) throws IOException {
        var cached = MODELS.get(id);
        if (cached != null) return cached;
        JsonObject json;
        try (var stream = Objects.requireNonNull(campus_v7_preview.class.getResourceAsStream("/" + asset(id.contains("/") ? id : id.replace(":", ":block/"), "models", ".json")), id);
             var reader = new InputStreamReader(stream, StandardCharsets.UTF_8)) { json = JsonParser.parseReader(reader).getAsJsonObject(); }
        var result = new LinkedHashMap<String, String>();
        if (json.has("parent") && !json.get("parent").getAsString().equals("builtin/generated")) result.putAll(model(json.get("parent").getAsString()));
        if (json.has("textures")) for (var entry : json.getAsJsonObject("textures").entrySet()) result.put(entry.getKey(), entry.getValue().getAsString());
        MODELS.put(id, result);
        return result;
    }

    static Map<String, String> materialModel(String id) throws IOException {
        if (id.equals("minecraft:water")) return Map.of("all", "minecraft:block/water_still");
        if (id.equals("minecraft:lava")) return Map.of("all", "minecraft:block/lava_still");
        JsonObject state;
        try (var stream = campus_v7_preview.class.getResourceAsStream("/" + asset(id, "blockstates", ".json"));
             var reader = new InputStreamReader(stream, StandardCharsets.UTF_8)) { state = JsonParser.parseReader(reader).getAsJsonObject(); }
        var choice = state.has("variants") ? state.getAsJsonObject("variants").entrySet().iterator().next().getValue()
                : state.getAsJsonArray("multipart").get(0).getAsJsonObject().get("apply");
        if (choice.isJsonArray()) choice = choice.getAsJsonArray().get(0);
        return model(choice.getAsJsonObject().get("model").getAsString());
    }

    static String asset(String id, String type, String extension) {
        var parts = id.split(":", 2);
        return "assets/" + (parts.length == 1 ? "minecraft" : parts[0]) + "/" + type + "/" + parts[parts.length - 1] + extension;
    }

    static int multiply(int rgb, int tint) {
        return (rgb >> 16 & 255) * (tint >> 16 & 255) / 255 << 16 |
                (rgb >> 8 & 255) * (tint >> 8 & 255) / 255 << 8 | (rgb & 255) * (tint & 255) / 255;
    }

    static int shade(int rgb, double factor) {
        return (int) ((rgb >> 16 & 255) * factor) << 16 | (int) ((rgb >> 8 & 255) * factor) << 8 | (int) ((rgb & 255) * factor);
    }

}
