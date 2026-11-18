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

public class campus_architecture_preview {
    static final Path ROOT = Path.of("").toAbsolutePath();
    static final Path OUTPUT = ROOT.resolve("deliveries/园区建筑同风格_V4_20261112");
    static final Map<String, Integer> COLORS = new HashMap<>();
    static final Map<String, Map<String, String>> MODELS = new HashMap<>();
    static final Map<String, String> MATERIAL_TEXTURES = new TreeMap<>();
    record Scene(String id, String title, PlannedCampus.Bounds original, int originalPlots, IntBinaryOperator originalColor,
                 Hk3CampusStyle style) {}
    record Region(int minX, int minZ, int maxX, int maxZ) {
        int width() { return maxX - minX + 1; }
        int depth() { return maxZ - minZ + 1; }
    }
    record VoxelGrid(int x, int z, int y, int width, int depth, int height, String[] blocks) {
        String at(int dx, int dy, int dz) {
            return dx < 0 || dy < 0 || dz < 0 || dx >= width || dy >= height || dz >= depth
                    ? null : blocks[(dz * width + dx) * height + dy];
        }
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
                    bounds.maxX(), bounds.maxZ(), -53, scene.style, 3);
            var plan = Hk3CampusExpansion.layout(entries, scene.id, bounds.minX(), bounds.minZ(),
                    bounds.maxX(), bounds.maxZ(), -53, scene.style, 4);
            var region = new Region(Math.min(bounds.minX(), Math.min(plan.minX(), oldPlan.minX())) - 24,
                    Math.min(bounds.minZ(), Math.min(plan.minZ(), oldPlan.minZ())) - 24,
                    Math.max(bounds.maxX(), Math.max(plan.maxX(), oldPlan.maxX())) + 24,
                    Math.max(bounds.maxZ(), Math.max(plan.maxZ(), oldPlan.maxZ())) + 24);
            top(scene, oldPlan, region, scene.id + "-r261-top.png", "R261 · 原布局与附区");
            top(scene, plan, region, scene.id + "-v4-top.png", "V4 · 原园区与新增附区");
            var annex = new Region(plan.minX() - 8, plan.minZ() - 8, plan.maxX() + 8, plan.maxZ() + 8);
            top(scene, plan, annex, scene.id + "-v4-annex.png", "V4 · 57处附区全景");
            var plot = plan.plots().stream().filter(p -> p.entry().key().equals("i02")).findFirst().orElseThrow();
            var close = new Region(plot.minX() - 3, plot.minZ() - 3, plot.maxX() + 3, plot.maxZ() + 3);
            var grid = voxels(plan, close);
            iso(scene, grid, scene.id + "-v4-hall-iso.png", "I02 · 逐格厂房等距图");
            side(scene, grid, scene.id + "-v4-hall-side.png", "I02 · 沿 +Z 方向观看的立面");
            sections.append(section(scene, plan, oldPlan, region, close));
            var sceneInfo = new Gson().toJsonTree(Map.of("id", scene.id, "originalBounds", bounds,
                    "originalPlotCount", scene.originalPlots, "appendedPlotCount", plan.plots().size(),
                    "v3AnnexBounds", new Region(oldPlan.minX(), oldPlan.minZ(), oldPlan.maxX(), oldPlan.maxZ()),
                    "v4AnnexBounds", new Region(plan.minX(), plan.minZ(), plan.maxX(), plan.maxZ()),
                    "sharedTopViewBounds", region, "nearViewBounds", close,
                    "nearViewVoxelDimensions", List.of(grid.width, grid.height, grid.depth), "style", scene.style)).getAsJsonObject();
            sceneInfo.add("v3AnnexSizeXZ", new Gson().toJsonTree(List.of(oldPlan.maxX() - oldPlan.minX() + 1, oldPlan.maxZ() - oldPlan.minZ() + 1)));
            sceneInfo.add("v4AnnexSizeXZ", new Gson().toJsonTree(List.of(plan.maxX() - plan.minX() + 1, plan.maxZ() - plan.minZ() + 1)));
            sceneInfo.add("sharedTopViewSizeXZ", new Gson().toJsonTree(List.of(region.width(), region.depth())));
            sceneMetadata.add(sceneInfo);
            System.out.printf(Locale.ROOT, "%s: original=%s; R261=%dx%d; V4=%dx%d; originalPlots=%d; appendedPlots=%d; near=%s;%n",
                    scene.id, bounds, oldPlan.maxX() - oldPlan.minX() + 1, oldPlan.maxZ() - oldPlan.minZ() + 1,
                    plan.maxX() - plan.minX() + 1, plan.maxZ() - plan.minZ() + 1, scene.originalPlots, plan.plots().size(), close);
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
        manifest.addProperty("schema", "hk3gtl-campus-preview-1");
        manifest.addProperty("generatedAtUtc", Instant.now().toString());
        manifest.addProperty("javaRuntime", System.getProperty("java.runtime.version"));
        manifest.addProperty("topViewWidthPixels", Integer.getInteger("preview.width", 1600));
        manifest.addProperty("surfaceY", -53);
        manifest.addProperty("appearanceStatus", "待外观评审，风格匹配未获认可");
        manifest.add("scenes", scenes);
        manifest.add("inputHashes", hashes(List.of(ROOT.resolve("tools/campus_architecture_preview.java"),
                ROOT.resolve("logs/campus-architecture-match-20261112/export-command.ps1"),
                ROOT.resolve("logs/campus-architecture-match-20261112/catalog.json"),
                ROOT.resolve("libs/GTL-Enhancedcore-5.1.1.jar"),
                ROOT.resolve("logs/campus-style-match-20261112/HK3GTL-r258-campus-style-r261.jar"),
                ROOT.resolve("src/main/java/com/sirin/hk3gtl/common/campus/Hk3CampusExpansion.java"),
                ROOT.resolve("src/main/java/com/sirin/hk3gtl/common/campus/Hk3CampusArchitecture.java"),
                ROOT.resolve("src/main/java/com/sirin/hk3gtl/common/campus/Hk3CampusDecoration.java"),
                ROOT.resolve("src/main/java/com/sirin/hk3gtl/common/campus/Hk3CampusStyle.java"))));
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
        var vanillaTextureUrl = (java.net.JarURLConnection) campus_architecture_preview.class.getResource(
                "/assets/minecraft/textures/block/quartz_block_bottom.png").openConnection();
        var vanillaTextureJar = Path.of(vanillaTextureUrl.getJarFileURL().toURI());
        manifest.add("vanillaTextureArchive", new Gson().toJsonTree(Map.of("path", vanillaTextureJar.toString(),
                "sha256", hash(vanillaTextureJar))));
        manifest.addProperty("v3Comparison", "当前Java version=3兼容路径，使用同一57条真实目录重建R261布局与装饰算法；不是活动世界回放。R261归档JAR只记录哈希，未作为本次执行classpath。");
        manifest.addProperty("sampling", "原园区直接调用FactoryCampus/FileCampus/PlannedCampus.previewColorAt；附区顶面按输出像素采样Plan.topAt及blockAt，近景逐格采样blockAt。机器实体结构未注入预览。");
        manifest.addProperty("materials", "原模型纹理首帧均色及固定默认生物群系叶草/水色；近景为方块格占位，不还原台阶、栅栏、透明混合等游戏模型。");
        manifest.add("materialTextureSources", new Gson().toJsonTree(MATERIAL_TEXTURES));
        manifest.add("executionBoundary", new Gson().toJsonTree(Map.of("gameStarted", false,
                "desktopOperated", false, "instanceChanged", false, "saveChanged", false,
                "jarInstalled", false, "inGameFormationAccepted", false, "inGameOperationAccepted", false,
                "performanceAccepted", false, "note", "仅仓库构建与离线预览，未进行新增实机验收。")));
        Files.writeString(ROOT.resolve("logs/campus-architecture-match-20261112/preview-manifest.json"),
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

    static void top(Scene scene, Hk3CampusExpansion.Plan plan, Region region, String name, String title) throws Exception {
        int width = Integer.getInteger("preview.width", 1600), height = (int) Math.ceil((double) region.depth() / region.width() * width);
        var image = new BufferedImage(width, height + 76, BufferedImage.TYPE_INT_RGB);
        var graphics = image.createGraphics();
        header(graphics, width, title, scene.title + " · X/Z同尺度 · 原园区原生预览色 / 附区真实顶层方块纹理均色");
        double step = (double) region.width() / width;
        for (int py = 0; py < height; py++) {
            int z = region.minZ + (int) ((py + 0.5) * step);
            for (int px = 0; px < width; px++) {
                int x = region.minX + (int) ((px + 0.5) * step), rgb = 0x17212A;
                if (scene.original.contains(x, z)) rgb = scene.originalColor.applyAsInt(x, z);
                if (plan.terrainAt(x, z)) {
                    int y = plan.topAt(x, z);
                    String block = plan.blockAt(x, y, z);
                    while (block == null && y > plan.surfaceY()) block = plan.blockAt(x, --y, z);
                    rgb = color(block);
                    if (plan.topAt(x - (int) Math.ceil(step), z) < y) rgb = shade(rgb, 0.82);
                }
                image.setRGB(px, py + 76, rgb);
            }
        }
        graphics.setStroke(new BasicStroke(2));
        graphics.setColor(new Color(0x9FDCD4));
        outline(graphics, scene.original.minX(), scene.original.minZ(), scene.original.maxX(), scene.original.maxZ(), region, step);
        graphics.setColor(new Color(0xF8C27B));
        outline(graphics, plan.minX(), plan.minZ(), plan.maxX(), plan.maxZ(), region, step);
        graphics.dispose();
        ImageIO.write(image, "png", OUTPUT.resolve(name).toFile());
    }

    static void outline(Graphics2D graphics, int x1, int z1, int x2, int z2, Region region, double step) {
        graphics.drawRect((int) ((x1 - region.minX) / step), 76 + (int) ((z1 - region.minZ) / step),
                (int) ((x2 - x1) / step), (int) ((z2 - z1) / step));
    }

    static VoxelGrid voxels(Hk3CampusExpansion.Plan plan, Region region) {
        int bottom = plan.surfaceY() - 3, top = plan.surfaceY();
        for (int z = region.minZ; z <= region.maxZ; z++) for (int x = region.minX; x <= region.maxX; x++)
            top = Math.max(top, plan.topAt(x, z));
        int height = top - bottom + 1;
        var blocks = new String[region.width() * region.depth() * height];
        for (int dz = 0; dz < region.depth(); dz++) for (int dx = 0; dx < region.width(); dx++)
            for (int dy = 0; dy < height; dy++)
                blocks[(dz * region.width() + dx) * height + dy] = plan.blockAt(region.minX + dx, bottom + dy, region.minZ + dz);
        return new VoxelGrid(region.minX, region.minZ, bottom, region.width(), region.depth(), height, blocks);
    }

    static void iso(Scene scene, VoxelGrid grid, String name, String title) throws Exception {
        double scale = Math.min(7.0, 1500.0 / ((grid.width + grid.depth) * 0.866));
        int width = 1600, height = (int) Math.ceil((grid.width + grid.depth) * scale * 0.5 + grid.height * scale + 140);
        var image = new BufferedImage(width, height, BufferedImage.TYPE_INT_RGB);
        var graphics = image.createGraphics();
        header(graphics, width, title, scene.title + " · 真正调用V4 Plan.blockAt · 逐格体素占位，非游戏模型渲染");
        graphics.setColor(new Color(0x17212A)); graphics.fillRect(0, 76, width, height - 76);
        double originX = width / 2.0 - (grid.width - grid.depth) * scale * 0.433;
        double originY = 105 + grid.height * scale;
        for (int z = 0; z < grid.depth; z++) for (int x = 0; x < grid.width; x++) for (int y = 0; y < grid.height; y++) {
            var block = grid.at(x, y, z);
            if (block == null || block.endsWith(":air")) continue;
            int rgb = color(block);
            double sx = originX + (x - z) * scale * 0.866;
            double sy = originY + (x + z) * scale * 0.5 - y * scale;
            double a = scale * 0.866, b = scale * 0.5;
            if (grid.at(x + 1, y, z) == null) polygon(graphics, shade(rgb, 0.72),
                    sx + a, sy - scale + b, sx, sy - scale + 2 * b, sx, sy + 2 * b, sx + a, sy + b);
            if (grid.at(x, y, z + 1) == null) polygon(graphics, shade(rgb, 0.53),
                    sx - a, sy - scale + b, sx, sy - scale + 2 * b, sx, sy + 2 * b, sx - a, sy + b);
            if (grid.at(x, y + 1, z) == null) polygon(graphics, rgb,
                    sx, sy - scale, sx + a, sy - scale + b, sx, sy - scale + 2 * b, sx - a, sy - scale + b);
        }
        graphics.dispose();
        ImageIO.write(image, "png", OUTPUT.resolve(name).toFile());
    }

    static void side(Scene scene, VoxelGrid grid, String name, String title) throws Exception {
        int scale = Math.max(4, Math.min(16, 1500 / grid.width));
        int width = 1600, height = grid.height * scale + 126;
        var image = new BufferedImage(width, height, BufferedImage.TYPE_INT_RGB);
        var graphics = image.createGraphics();
        header(graphics, width, title, scene.title + " · 真实方块采样 · 1格=" + scale + "像素 · 各列取最近非空方块");
        graphics.setColor(new Color(0x17212A)); graphics.fillRect(0, 76, width, height - 76);
        int startX = (width - grid.width * scale) / 2;
        for (int x = 0; x < grid.width; x++) for (int y = 0; y < grid.height; y++) {
            for (int z = grid.depth - 1; z >= 0; z--) {
                var block = grid.at(x, y, z);
                if (block == null || block.endsWith(":air")) continue;
                graphics.setColor(new Color(shade(color(block), 0.85)));
                graphics.fillRect(startX + x * scale, 98 + (grid.height - y - 1) * scale, scale, scale);
                if (scale >= 8) {
                    graphics.setColor(new Color(0, 0, 0, 28));
                    graphics.drawRect(startX + x * scale, 98 + (grid.height - y - 1) * scale, scale - 1, scale - 1);
                }
                break;
            }
        }
        graphics.dispose();
        ImageIO.write(image, "png", OUTPUT.resolve(name).toFile());
    }

    static void polygon(Graphics2D graphics, int color, double... coordinates) {
        var polygon = new Polygon();
        for (int i = 0; i < coordinates.length; i += 2) polygon.addPoint((int) Math.round(coordinates[i]), (int) Math.round(coordinates[i + 1]));
        graphics.setColor(new Color(color)); graphics.fillPolygon(polygon);
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
        try (var stream = campus_architecture_preview.class.getResourceAsStream("/" + path)) { image = ImageIO.read(stream); }
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
        try (var stream = Objects.requireNonNull(campus_architecture_preview.class.getResourceAsStream("/" + asset(id.contains("/") ? id : id.replace(":", ":block/"), "models", ".json")), id);
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
        try (var stream = campus_architecture_preview.class.getResourceAsStream("/" + asset(id, "blockstates", ".json"));
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

    static String section(Scene scene, Hk3CampusExpansion.Plan plan, Hk3CampusExpansion.Plan oldPlan, Region region, Region close) {
        return """
                <section id="%s"><div class="section-head"><div><span class="eyebrow">%s</span><h2>%s</h2></div>
                <p>原园区 %s<br>V4附区 %d × %d格 · %d处真实机器用地<br>原园区%d处 + 附区%d处 = 总%d处</p></div>
                <div class="compare"><figure><a href="%s-r261-top.png"><img loading="lazy" src="%s-r261-top.png"></a><figcaption>R261原路径 · 相同世界坐标与尺度</figcaption></figure>
                <figure><a href="%s-v4-top.png"><img loading="lazy" src="%s-v4-top.png"></a><figcaption>V4建筑路径 · 青色框为原园区，金色框为附区</figcaption></figure></div>
                <details><summary>展开57处附区全图</summary><a href="%s-v4-annex.png"><img loading="lazy" src="%s-v4-annex.png"></a></details>
                <div class="compare close"><figure><a href="%s-v4-hall-iso.png"><img loading="lazy" src="%s-v4-hall-iso.png"></a><figcaption>I02厂房 · 真实方块等距图</figcaption></figure>
                <figure><a href="%s-v4-hall-side.png"><img loading="lazy" src="%s-v4-hall-side.png"></a><figcaption>I02厂房 · 同一区域正交立面</figcaption></figure></div>
                <p class="coords">总图：X %d…%d，Z %d…%d。近景：X %d…%d，Z %d…%d。附区地表 Y=-53。</p></section>
                """.formatted(scene.id, scene.id.toUpperCase(Locale.ROOT), scene.title, scene.original,
                plan.maxX() - plan.minX() + 1, plan.maxZ() - plan.minZ() + 1, plan.plots().size(),
                scene.originalPlots, plan.plots().size(), scene.originalPlots + plan.plots().size(),
                scene.id, scene.id, scene.id, scene.id, scene.id, scene.id,
                scene.id, scene.id, scene.id, scene.id, region.minX, region.maxX, region.minZ, region.maxZ,
                close.minX, close.maxX, close.minZ, close.maxZ);
    }

    static String html(String sections) {
        return """
                <!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
                <title>园区V4 · 真实生成器离线建筑预览</title><style>
                :root{color-scheme:dark;font-family:"Microsoft YaHei",sans-serif;background:#0c131b;color:#e9f0f3}*{box-sizing:border-box}body{margin:0}main{max-width:1760px;margin:auto;padding:48px 32px}
                .eyebrow{font-size:12px;letter-spacing:3px;color:#77d9c7}h1{font-size:40px;margin:12px 0 16px}h2{font-size:28px;margin:8px 0}p{line-height:1.8;color:#a8bbc8}.lead{max-width:1050px;font-size:17px}nav{display:flex;gap:12px;margin:28px 0}a{color:#8de3d1}nav a,summary{padding:12px 18px;background:#172633;border:1px solid #2b4353;border-radius:9px;text-decoration:none}
                section{border-top:1px solid #253847;margin-top:46px;padding-top:34px}.section-head{display:flex;justify-content:space-between;align-items:center;gap:24px}.section-head p{font-size:13px;text-align:right}.compare{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin:20px 0}figure{margin:0;border:1px solid #304657;border-radius:10px;overflow:hidden;background:#111f2b}img{display:block;width:100%;height:auto}figcaption{padding:13px 17px;color:#b7c9d6;font-size:13px}.close{align-items:start}details{margin:18px 0}summary{cursor:pointer;width:max-content;margin-bottom:12px}.coords{font-size:12px;color:#819aa9}.note{padding:20px 24px;background:#14232e;border-left:3px solid #dcb47d}.note p{margin:4px 0;font-size:14px}footer{margin-top:40px;font-size:12px;color:#7893a4}@media(max-width:800px){main{padding:28px 16px}h1{font-size:30px}.compare{grid-template-columns:1fr}.section-head{display:block}.section-head p{text-align:left}nav{flex-wrap:wrap}}
                </style><main><span class="eyebrow">HK3GTL / CAMPUS ARCHITECTURE V4</span><h1>园区建筑 V4 · 生成结果对照</h1>
                <p class="lead">三个真实园区，同一份57台正式机器目录。原园区直接使用增强版原生预览颜色；V4附区由当前Java布局与建筑生成代码逐格采样。当前为待外观评审候选，编译与离线图不代表风格匹配已获认可。</p>
                <nav><a href="#quartz_works">石英工厂</a><a href="#woodland">林地园区</a><a href="#pink">粉色梦境</a></nav>
                <div class="note"><p>图像范围：只显示园区环境、用地与厂房围护；未在预览中虚构搭建机器结构。露天巨构用地保持露天。</p>
                <p>R261对照由当前Java的version=3兼容路径与同一真实目录重建旧布局及装饰，不是活动世界回放；原R261归档与当前生成器哈希见证据清单。</p>
                <p>R261与V4各组总图共用世界坐标、比例与画幅。总图按输出像素采样顶层方块；I02近景逐格读取 <code>Plan.blockAt</code>，未缩放建筑或重画轮廓。</p>
                <p>材质来自Minecraft原模型引用的纹理首帧均色；叶片及草采用固定默认生物群系色调，面明暗为离线光照。近景呈现方块体素占位，不还原台阶、栅栏、透明混合等游戏模型细节。</p>
                <p>这是仓库离线建筑预览；没有启动游戏、修改实例或存档，也没有新增成型、运行与性能验收。</p></div>
                {{sections}}<footer>生成入口：tools/campus_architecture_preview.java · 机器目录：logs/campus-architecture-match-20261112/catalog.json · 2026-11-12</footer></main></html>
                """.replace("{{sections}}", sections);
    }
}
