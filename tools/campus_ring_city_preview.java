import com.google.gson.*;
import com.gtl.enhancedcore.common.world.plot.*;
import com.sirin.hk3gtl.common.campus.*;
import net.minecraft.core.Direction;
import net.minecraft.resources.ResourceLocation;

import javax.imageio.ImageIO;
import java.awt.*;
import java.awt.image.BufferedImage;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.security.MessageDigest;
import java.time.Instant;
import java.util.*;
import java.util.List;
import java.util.function.IntBinaryOperator;

public class campus_ring_city_preview {
    static final Path ROOT = Path.of("").toAbsolutePath();
    static final Path OUTPUT = ROOT.resolve("deliveries/园区环城融合_V5_20261112");
    static final Map<String, Integer> COLORS = new HashMap<>();
    static final Map<String, Map<String, String>> MODELS = new HashMap<>();
    static final Map<String, String> MATERIAL_TEXTURES = new TreeMap<>();
    record Scene(String id, String title, PlannedCampus.Bounds original, int originalPlots, IntBinaryOperator originalColor,
                 Hk3CampusStyle style) {}
    record Region(int minX, int minZ, int maxX, int maxZ) {
        int width() { return maxX - minX + 1; }
        int depth() { return maxZ - minZ + 1; }
    }
    public static void main(String[] args) throws Exception {
        System.setProperty("java.awt.headless", "true");
        Files.createDirectories(OUTPUT);
        var catalog = JsonParser.parseString(Files.readString(ROOT.resolve(
                "logs/campus-architecture-match-20261112/catalog.json"))).getAsJsonObject();
        var entries = new ArrayList<Hk3CampusCatalog.Entry>();
        for (var row : catalog.getAsJsonArray("entries")) {
            var value = row.getAsJsonObject();
            var size = value.getAsJsonArray("size");
            var control = value.getAsJsonArray("controller");
            entries.add(new Hk3CampusCatalog.Entry(new ResourceLocation(value.get("machine").getAsString()),
                    value.get("key").getAsString(), value.get("tier").getAsInt(),
                    size.get(0).getAsInt(), size.get(1).getAsInt(), size.get(2).getAsInt(),
                    control.get(0).getAsInt(), control.get(1).getAsInt(), control.get(2).getAsInt(),
                    Direction.valueOf(value.get("front").getAsString().toUpperCase(Locale.ROOT)), null));
        }
        var pink = FileCampus.of("pink_dream_home_v1");
        var scenes = List.of(new Scene("quartz_works", "石英工厂", FactoryCampus.bounds(), FactoryCampus.plots().size(),
                        FactoryCampus::previewColorAt, fileStyle("quartz_works", Hk3CampusStyle.Kind.FACTORY)),
                new Scene("woodland", "林地园区", PlannedCampus.bounds(), PlannedCampus.plots().size(), PlannedCampus::previewColorAt,
                        new Hk3CampusStyle("WOODLAND", "minecraft:polished_andesite", "minecraft:stone_bricks",
                                "minecraft:smooth_quartz", "minecraft:polished_andesite", "minecraft:cyan_concrete",
                                "minecraft:quartz_pillar[axis=y]", "minecraft:oak_leaves[persistent=true]",
                                "minecraft:sea_lantern", "minecraft:grass_block", Hk3CampusStyle.Kind.WOODLAND, null)),
                new Scene("pink", "粉色梦境", pink.bounds(), pink.plots().size(), pink::previewColorAt,
                        fileStyle("pink_dream_home_v1", Hk3CampusStyle.Kind.PINK)));
        var sections = new StringBuilder();
        var sceneMetadata = new JsonArray();
        for (var scene : scenes) {
            if (args.length > 0 && !scene.id.equals(args[0])) continue;
            var bounds = scene.original;
            var oldPlan = Hk3CampusExpansion.layout(entries, scene.id, bounds.minX(), bounds.minZ(),
                    bounds.maxX(), bounds.maxZ(), -53, scene.style, 4);
            var plan = Hk3CampusExpansion.layout(entries, scene.id, bounds.minX(), bounds.minZ(),
                    bounds.maxX(), bounds.maxZ(), -53, scene.style, 5);
            var region = new Region(Math.min(bounds.minX(), Math.min(plan.minX(), oldPlan.minX())) - 24,
                    Math.min(bounds.minZ(), Math.min(plan.minZ(), oldPlan.minZ())) - 24,
                    Math.max(bounds.maxX(), Math.max(plan.maxX(), oldPlan.maxX())) + 24,
                    Math.max(bounds.maxZ(), Math.max(plan.maxZ(), oldPlan.maxZ())) + 24);
            top(scene, oldPlan, region, scene.id + "-v4-top.png", "V4 · 原布局对照", false);
            top(scene, plan, region, scene.id + "-v5-top.png", "V5 · 环城布局候选", false);
            var city = new Region(plan.minX() - 24, plan.minZ() - 24, plan.maxX() + 24, plan.maxZ() + 24);
            top(scene, plan, city, scene.id + "-v5-city.png", "V5 · 原园区中心与外围整合城区", true);
            var distribution = distribution(plan, bounds);
            sections.append(section(scene, plan, region, city, distribution));
            var sceneInfo = new Gson().toJsonTree(Map.of("id", scene.id, "originalBounds", bounds,
                    "originalPlotCount", scene.originalPlots, "appendedPlotCount", plan.plots().size(),
                    "v4Bounds", new Region(oldPlan.minX(), oldPlan.minZ(), oldPlan.maxX(), oldPlan.maxZ()),
                    "v5Bounds", new Region(plan.minX(), plan.minZ(), plan.maxX(), plan.maxZ()),
                    "sharedTopViewBounds", region, "cityViewBounds", city,
                    "cardinalPlotCounts", distribution, "style", scene.style)).getAsJsonObject();
            sceneInfo.add("v4SizeXZ", new Gson().toJsonTree(List.of(oldPlan.maxX() - oldPlan.minX() + 1, oldPlan.maxZ() - oldPlan.minZ() + 1)));
            sceneInfo.add("v5SizeXZ", new Gson().toJsonTree(List.of(plan.maxX() - plan.minX() + 1, plan.maxZ() - plan.minZ() + 1)));
            sceneInfo.add("sharedTopViewSizeXZ", new Gson().toJsonTree(List.of(region.width(), region.depth())));
            sceneInfo.add("cityViewSizeXZ", new Gson().toJsonTree(List.of(city.width(), city.depth())));
            sceneInfo.add("innerRing", new Gson().toJsonTree(plan.urban().roads().subList(0, 4)));
            sceneInfo.add("outerRing", new Gson().toJsonTree(plan.urban().roads().subList(4, 8)));
            sceneInfo.add("radialRoads", new Gson().toJsonTree(plan.urban().roads().stream().skip(8).filter(road -> road.halfWidth() >= 8).toList()));
            sceneInfo.add("serviceConnections", new Gson().toJsonTree(plan.urban().roads().stream().filter(road -> road.halfWidth() == 2).toList()));
            sceneInfo.add("plots", new Gson().toJsonTree(plan.plots().stream().map(plot -> Map.of(
                    "machine", plot.entry().machineId().toString(), "key", plot.entry().key(), "tier", plot.entry().tier(),
                    "bounds", new Region(plot.minX(), plot.minZ(), plot.maxX(), plot.maxZ()),
                    "controller", List.of(plot.controllerX(), plot.controllerY(), plot.controllerZ()),
                    "arrival", List.of(plot.arrivalX(), plot.arrivalY(), plot.arrivalZ()),
                    "structureSize", List.of(plot.entry().sizeX(), plot.entry().sizeY(), plot.entry().sizeZ()),
                    "front", plot.entry().front().name())).toList()));
            sceneMetadata.add(sceneInfo);
            System.out.printf(Locale.ROOT, "%s: original=%s; V4=%dx%d; V5=%dx%d; originalPlots=%d; appendedPlots=%d; sides=%s;%n",
                    scene.id, bounds, oldPlan.maxX() - oldPlan.minX() + 1, oldPlan.maxZ() - oldPlan.minZ() + 1,
                    plan.maxX() - plan.minX() + 1, plan.maxZ() - plan.minZ() + 1, scene.originalPlots, plan.plots().size(), distribution);
        }
        Files.writeString(OUTPUT.resolve("index.html"), html(sections.toString()), StandardCharsets.UTF_8);
        manifest(sceneMetadata);
        for (var texture : MATERIAL_TEXTURES.entrySet()) System.out.println("texture " + texture.getKey() + " -> " + texture.getValue());
        System.out.println(OUTPUT.resolve("index.html").toUri().toASCIIString());
    }

    static Hk3CampusStyle fileStyle(String id, Hk3CampusStyle.Kind kind) {
        var definition = CampusPresetRegistry.get(id);
        var materials = definition.materials();
        return new Hk3CampusStyle(id, materials.get("floor"), materials.get("road"), materials.get("quartz"),
                materials.get("dark"), materials.get("accent"), materials.get("column"), materials.get("leaves"),
                materials.get("light"), materials.get("green"), kind, definition.architectureResource());
    }

    static void manifest(JsonArray scenes) throws Exception {
        var manifest = new JsonObject();
        manifest.addProperty("schema", "hk3gtl-campus-ring-city-preview-1");
        manifest.addProperty("generatedAtUtc", Instant.now().toString());
        manifest.addProperty("javaRuntime", System.getProperty("java.runtime.version"));
        manifest.addProperty("topViewWidthPixels", Integer.getInteger("preview.width", 1600));
        manifest.addProperty("surfaceY", -53);
        manifest.addProperty("appearanceStatus", "待外观评审，风格匹配未获认可");
        manifest.add("scenes", scenes);
        manifest.add("inputHashes", hashes(List.of(ROOT.resolve("tools/campus_ring_city_preview.java"),
                ROOT.resolve("logs/campus-ring-city-20261112/export-command.ps1"),
                ROOT.resolve("logs/campus-architecture-match-20261112/catalog.json"),
                ROOT.resolve("libs/GTL-Enhancedcore-5.1.1.jar"),
                ROOT.resolve("logs/campus-architecture-match-20261112/HK3GTL-r258-campus-architecture-r262.jar"),
                ROOT.resolve("src/main/java/com/sirin/hk3gtl/common/campus/Hk3CampusExpansion.java"),
                ROOT.resolve("src/main/java/com/sirin/hk3gtl/common/campus/Hk3CampusArchitecture.java"),
                ROOT.resolve("src/main/java/com/sirin/hk3gtl/common/campus/Hk3CampusDecoration.java"),
                ROOT.resolve("src/main/java/com/sirin/hk3gtl/common/campus/Hk3CampusStyle.java"),
                ROOT.resolve("src/main/java/com/sirin/hk3gtl/common/campus/Hk3CampusIntegratedLayout.java"),
                ROOT.resolve("src/main/java/com/sirin/hk3gtl/common/campus/Hk3CampusRoadLinks.java"),
                ROOT.resolve("src/main/java/com/sirin/hk3gtl/common/campus/Hk3CampusRoadProfile.java"))));
        try (var classes = Files.walk(ROOT.resolve("build/classes/java/main/com/sirin/hk3gtl/common/campus"))) {
            manifest.add("compiledCampusHashes", hashes(classes.filter(path -> path.toString().endsWith(".class")).sorted().toList()));
        }
        var images = new JsonArray();
        try (var files = Files.list(OUTPUT)) {
            for (var path : files.filter(path -> path.toString().endsWith(".png")).sorted().toList()) {
                var image = ImageIO.read(path.toFile());
                images.add(new Gson().toJsonTree(Map.of("path", relative(path), "sha256", hash(path),
                        "width", image.getWidth(), "height", image.getHeight())));
            }
        }
        manifest.add("pngFiles", images);
        manifest.addProperty("htmlSha256", hash(OUTPUT.resolve("index.html")));
        var vanillaTextureUrl = (java.net.JarURLConnection) campus_ring_city_preview.class.getResource(
                "/assets/minecraft/textures/block/quartz_block_bottom.png").openConnection();
        var vanillaTextureJar = Path.of(vanillaTextureUrl.getJarFileURL().toURI());
        manifest.add("vanillaTextureArchive", new Gson().toJsonTree(Map.of("path", vanillaTextureJar.toString(),
                "sha256", hash(vanillaTextureJar))));
        manifest.addProperty("v4Comparison", "当前Java version=4路径与同一57条真实目录重建V4布局；不是活动世界回放。V4归档JAR只记录哈希，未作为本次执行classpath。");
        manifest.addProperty("sampling", "原园区直接调用FactoryCampus/FileCampus/PlannedCampus.previewColorAt；V4/V5顶面按输出像素采样Plan.topAt及blockAt。V5仅对真实生成位置覆盖原预览。机器实体结构未注入预览。");
        manifest.addProperty("roadOverlay", "细虚线直接取自V5 Plan.urban().roads()真实道路中心线，不绘制计划外道路；前4条为内环、后4条为外环，其余halfWidth>=8为放射道路，halfWidth=2单列检修连接。原core仅文字定位，不另加分离园区外框。");
        manifest.addProperty("cardinalCountRule", "先按用地整体位于原core北侧或南侧计数，其余按西侧或东侧计数；角区归南北侧。每个真实新增plot只计一次。");
        manifest.addProperty("materials", "原模型纹理首帧均色及固定默认生物群系叶草/水色；顶面图不还原台阶、栅栏、透明混合等游戏模型。");
        manifest.add("materialTextureSources", new Gson().toJsonTree(MATERIAL_TEXTURES));
        manifest.add("executionBoundary", new Gson().toJsonTree(Map.of("gameStarted", false,
                "desktopOperated", false, "instanceChanged", false, "saveChanged", false,
                "jarInstalled", false, "inGameFormationAccepted", false, "inGameOperationAccepted", false,
                "performanceAccepted", false, "note", "仅仓库构建与离线预览，未进行新增实机验收。")));
        Files.writeString(ROOT.resolve("logs/campus-ring-city-20261112/preview-manifest.json"),
                new GsonBuilder().setPrettyPrinting().disableHtmlEscaping().create().toJson(manifest), StandardCharsets.UTF_8);
    }

    static JsonObject hashes(List<Path> paths) throws Exception {
        var result = new JsonObject();
        for (var path : paths) result.addProperty(relative(path), hash(path));
        return result;
    }

    static String relative(Path path) { return ROOT.relativize(path).toString().replace('\\', '/'); }
    static String hash(Path path) throws Exception {
        return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(Files.readAllBytes(path)));
    }

    static void top(Scene scene, Hk3CampusExpansion.Plan plan, Region region, String name, String title, boolean annotated) throws Exception {
        int width = Integer.getInteger("preview.width", 1600), height = (int) Math.ceil((double) region.depth() / region.width() * width);
        var image = new BufferedImage(width, height + 76, BufferedImage.TYPE_INT_RGB);
        var graphics = image.createGraphics();
        header(graphics, width, title, scene.title + " · X/Z同尺度 · 原园区原生预览色 / 新城区真实顶层方块纹理均色");
        double step = (double) region.width() / width;
        for (int py = 0; py < height; py++) {
            int z = region.minZ + (int) ((py + 0.5) * step);
            for (int px = 0; px < width; px++) {
                int x = region.minX + (int) ((px + 0.5) * step), rgb = 0x17212A;
                if (scene.original.contains(x, z)) rgb = scene.originalColor.applyAsInt(x, z);
                if (plan.terrainAt(x, z)) {
                    int y = plan.topAt(x, z);
                    String block = plan.blockAt(x, y, z);
                    while ((block == null || block.equals("minecraft:air")) && y > plan.surfaceY()) block = plan.blockAt(x, --y, z);
                    if (block != null && !block.equals("minecraft:air")) {
                        rgb = color(block);
                        if (plan.topAt(x - (int) Math.ceil(step), z) < y) rgb = shade(rgb, 0.82);
                    }
                }
                image.setRGB(px, py + 76, rgb);
            }
        }
        if (annotated) annotate(graphics, scene, plan, region, step);
        graphics.dispose();
        ImageIO.write(image, "png", OUTPUT.resolve(name).toFile());
    }

    static Map<String, Integer> distribution(Hk3CampusExpansion.Plan plan, PlannedCampus.Bounds original) {
        var counts = new LinkedHashMap<String, Integer>();
        for (var side : List.of("north", "east", "south", "west")) counts.put(side, 0);
        for (var plot : plan.plots()) {
            String side = plot.maxZ() < original.minZ() ? "north" : plot.minZ() > original.maxZ() ? "south"
                    : plot.maxX() < original.minX() ? "west" : "east";
            counts.merge(side, 1, Integer::sum);
        }
        return counts;
    }

    static void annotate(Graphics2D graphics, Scene scene, Hk3CampusExpansion.Plan plan, Region region, double step) {
        var roads = plan.urban().roads();
        for (int i = 0; i < roads.size(); i++) {
            var road = roads.get(i);
            int rgb = i < 4 ? 0x72D9C4 : i < 8 ? 0xF5BC72 : road.halfWidth() == 2 ? 0xB6C7D1 : 0xC4A4FF;
            int x1 = (int) Math.round((road.x1() - region.minX) / step), z1 = 76 + (int) Math.round((road.z1() - region.minZ) / step);
            int x2 = (int) Math.round((road.x2() - region.minX) / step), z2 = 76 + (int) Math.round((road.z2() - region.minZ) / step);
            graphics.setColor(new Color((rgb >> 16) & 255, (rgb >> 8) & 255, rgb & 255, 190));
            graphics.setStroke(new BasicStroke(road.halfWidth() == 2 ? 0.8f : 1.25f,
                    BasicStroke.CAP_BUTT, BasicStroke.JOIN_MITER, 10, new float[]{6, 5}, 0));
            graphics.drawLine(x1, z1, x2, z2);
        }
        var original = scene.original;
        label(graphics, region, step, original.minX() + 500, original.minZ() + 160,
                "原园区中心 · " + scene.originalPlots + "处", 0xEAF6F2);
        var inner = roads.get(0);
        var outer = roads.get(6);
        label(graphics, region, step, inner.x1() + 450, inner.z1() + 300, "内环 · 实际道路", 0x72D9C4);
        label(graphics, region, step, outer.x2() - 450, outer.z1() - 160, "外环 · 实际道路", 0xF5BC72);
        var axis = roads.get(11);
        label(graphics, region, step, (axis.x1() + axis.x2()) / 2, axis.z1() - 200, "放射轴", 0xC4A4FF);
        var counts = distribution(plan, original);
        label(graphics, region, step, 300, (plan.minZ() + original.minZ()) / 2, "北侧 · " + counts.get("north") + "处", 0xEAF6F2);
        label(graphics, region, step, (plan.maxX() + original.maxX()) / 2, 300, "东侧 · " + counts.get("east") + "处", 0xEAF6F2);
        label(graphics, region, step, 300, (plan.maxZ() + original.maxZ()) / 2, "南侧 · " + counts.get("south") + "处", 0xEAF6F2);
        label(graphics, region, step, (plan.minX() + original.minX()) / 2, 300, "西侧 · " + counts.get("west") + "处", 0xEAF6F2);
    }

    static void label(Graphics2D graphics, Region region, double step, int x, int z, String text, int color) {
        graphics.setFont(new Font("Microsoft YaHei", Font.BOLD, 18));
        var metrics = graphics.getFontMetrics();
        int width = metrics.stringWidth(text) + 24, px = (int) Math.round((x - region.minX) / step) - width / 2;
        int py = 76 + (int) Math.round((z - region.minZ) / step) - 17;
        graphics.setColor(new Color(12, 22, 31, 230)); graphics.fillRoundRect(px, py, width, 34, 8, 8);
        graphics.setColor(new Color(color)); graphics.drawString(text, px + 12, py + 23);
    }

    static void header(Graphics2D graphics, int width, String title, String subtitle) {
        graphics.setColor(new Color(0x0F1921)); graphics.fillRect(0, 0, width, 76);
        graphics.setColor(Color.WHITE); graphics.setFont(new Font("Microsoft YaHei", Font.BOLD, 24)); graphics.drawString(title, 24, 32);
        graphics.setColor(new Color(0xA9BCC9)); graphics.setFont(new Font("Microsoft YaHei", Font.PLAIN, 16)); graphics.drawString(subtitle, 24, 59);
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
        try (var stream = campus_ring_city_preview.class.getResourceAsStream("/" + path)) { image = ImageIO.read(stream); }
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
        try (var stream = Objects.requireNonNull(campus_ring_city_preview.class.getResourceAsStream("/" + asset(id.contains("/") ? id : id.replace(":", ":block/"), "models", ".json")), id);
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
        try (var stream = campus_ring_city_preview.class.getResourceAsStream("/" + asset(id, "blockstates", ".json"));
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

    static String section(Scene scene, Hk3CampusExpansion.Plan plan, Region region, Region city, Map<String, Integer> counts) {
        return """
                <section id="%s"><div class="section-head"><div><span class="eyebrow">%s</span><h2>%s</h2></div>
                <p>整合城区 %d × %d格<br>原园区%d处 + 外围新增%d处 = 总%d处<br>新增用地：北%d · 东%d · 南%d · 西%d</p></div>
                <div class="compare"><figure><a href="%s-v4-top.png"><img loading="lazy" src="%s-v4-top.png"></a><figcaption>V4原布局 · 共用世界范围、比例与画幅</figcaption></figure>
                <figure><a href="%s-v5-top.png"><img loading="lazy" src="%s-v5-top.png"></a><figcaption>V5环城候选 · 原园区中心、外围整合城区</figcaption></figure></div>
                <figure><a href="%s-v5-city.png"><img loading="lazy" src="%s-v5-city.png"></a><figcaption>V5全城 · 青绿为内环，橙色为外环，紫色为放射轴，浅灰为检修连接；彩线直接叠加Java实际道路坐标</figcaption></figure>
                <p class="coords">对照图：X %d…%d，Z %d…%d。全城图：X %d…%d，Z %d…%d。地表 Y=-53。四向计数先归北／南，剩余归西／东；角区归南北。</p></section>
                """.formatted(scene.id, scene.id.toUpperCase(Locale.ROOT), scene.title,
                plan.maxX() - plan.minX() + 1, plan.maxZ() - plan.minZ() + 1,
                scene.originalPlots, plan.plots().size(), scene.originalPlots + plan.plots().size(),
                counts.get("north"), counts.get("east"), counts.get("south"), counts.get("west"),
                scene.id, scene.id, scene.id, scene.id, scene.id, scene.id,
                region.minX, region.maxX, region.minZ, region.maxZ, city.minX, city.maxX, city.minZ, city.maxZ);
    }

    static String html(String sections) {
        return """
                <!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
                <title>园区环城融合 V5 · 生成结果对照</title><style>
                :root{color-scheme:dark;font-family:"Microsoft YaHei",sans-serif;background:#0c131b;color:#e9f0f3}*{box-sizing:border-box}body{margin:0}main{max-width:1760px;margin:auto;padding:48px 32px}
                .eyebrow{font-size:12px;letter-spacing:3px;color:#77d9c7}h1{font-size:40px;margin:12px 0 16px}h2{font-size:28px;margin:8px 0}p{line-height:1.8;color:#a8bbc8}.lead{max-width:1050px;font-size:17px}nav{display:flex;gap:12px;margin:28px 0}a{color:#8de3d1}nav a,summary{padding:12px 18px;background:#172633;border:1px solid #2b4353;border-radius:9px;text-decoration:none}
                section{border-top:1px solid #253847;margin-top:46px;padding-top:34px}.section-head{display:flex;justify-content:space-between;align-items:center;gap:24px}.section-head p{font-size:13px;text-align:right}.compare{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin:20px 0}figure{margin:0;border:1px solid #304657;border-radius:10px;overflow:hidden;background:#111f2b}img{display:block;width:100%;height:auto}figcaption{padding:13px 17px;color:#b7c9d6;font-size:13px}.close{align-items:start}details{margin:18px 0}summary{cursor:pointer;width:max-content;margin-bottom:12px}.coords{font-size:12px;color:#819aa9}.note{padding:20px 24px;background:#14232e;border-left:3px solid #dcb47d}.note p{margin:4px 0;font-size:14px}footer{margin-top:40px;font-size:12px;color:#7893a4}@media(max-width:800px){main{padding:28px 16px}h1{font-size:30px}.compare{grid-template-columns:1fr}.section-head{display:block}.section-head p{text-align:left}nav{flex-wrap:wrap}}
                </style><main><span class="eyebrow">HK3GTL / CAMPUS RING CITY V5</span><h1>园区环城融合 V5 · 生成结果对照</h1>
                <p class="lead">原园区位于中央，57台新增机器用地分布在外围城区；双闭合环路与放射轴按Java实际生成。三种预设均与V4共用世界范围对照。当前为待外观评审候选，编译与离线图不代表布局或风格已获认可。</p>
                <nav><a href="#quartz_works">石英工厂</a><a href="#woodland">林地园区</a><a href="#pink">粉色梦境</a></nav>
                <div class="note"><p>图像范围：园区环境、用地与厂房围护；未虚构搭建机器结构。露天巨构用地保持露天；现有园区内部只覆盖真实接通道路。</p>
                <p>原园区使用增强版原生预览色，新城区使用顶层真实方块纹理均色；这是两种原始数据源，不把色差当作外观批准依据。</p>
                <p>V4对照由当前Java的version=4路径与同一真实目录重建，不是活动世界回放。V5全城彩线只标注 <code>Plan.urban().roads()</code> 的真实道路坐标与宽度。</p>
                <p>并排对照保留两版联合世界范围；下方全城图只按V5范围居中取景。浅灰细线为5格检修连接，单列记录，不归入放射轴。</p>
                <p>图像按像素采样 <code>Plan.topAt / blockAt</code>；未改建筑尺寸或重画轮廓。材质为原模型纹理首帧均色，叶草与水采用固定默认色调，面明暗为离线光照。</p>
                <p>这是仓库离线建筑预览；没有启动游戏、修改实例或存档，也没有新增成型、运行与性能验收。</p></div>
                {{sections}}<footer>生成入口：tools/campus_ring_city_preview.java · 证据：logs/campus-ring-city-20261112/preview-manifest.json · 2026-11-12</footer></main></html>
                """.replace("{{sections}}", sections);
    }
}
