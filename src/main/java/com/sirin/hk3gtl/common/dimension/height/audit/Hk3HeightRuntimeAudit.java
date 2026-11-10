package com.sirin.hk3gtl.common.dimension.height.audit;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.mojang.logging.LogUtils;
import com.sirin.hk3gtl.common.dimension.height.Hk3HeightService;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.entity.ChestBlockEntity;
import net.minecraft.world.level.chunk.LevelChunk;
import net.minecraft.world.level.storage.LevelResource;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.event.server.ServerStartedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.loading.FMLPaths;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.time.OffsetDateTime;
import java.time.format.DateTimeFormatter;
import java.util.UUID;

/**
 * 【文件职责】导出当前服务器实际高度；隔离测试档可选探针验证高区段与方块实体的保存。
 * 【变更记录 #1】2026-10-17 21:11:26（第1次备注 · 修订166）
 * 删除：无。新增：自动只读导出、管理员导出和受限的新档放置/持久化核验命令。
 * 修改：无既有世界高度或玩家内容修改；探针只准在已启用合同的指定新创造作弊档执行。
 * 用途：验证实际Level、区段、坐标与保存内容，不把类型JSON或单次放置成功当作重启通过。
 * 【变更记录 #2】2026-10-17 21:48:34（第2次备注 · 修订166）
 * 删除：高度图字段将最高方块误称首个可用空位的名称。
 * 新增：世界合同身份、逐类型原始与扩展边界、探针高度图精确比对。
 * 修改：导出同时保留冻结来源与当前结果；用途：证明原下界和逻辑高度不变，并发现保存后高度图漂移。
 * 【变更记录 #3】2026-10-29 23:13:43（第3次备注 · 修订182）
 * 删除：回执固定修订166的身份；新增：无；修改：回执修订为182。
 * 用途：为本轮精确名单旧档扩高保存独立真实运行证据；探针写入仍受原隔离档限制。
 */
@Mod.EventBusSubscriber(modid = "hk3gtl")
public final class Hk3HeightRuntimeAudit {
    private static final Gson JSON = new GsonBuilder().setPrettyPrinting().disableHtmlEscaping().create();
    private static final String TEST_WORLD = "hk3gtl-height-r166-review";
    private static final String PROBES = "hk3gtl-height-probes.json";

    private Hk3HeightRuntimeAudit() {}

    @SubscribeEvent
    public static void started(ServerStartedEvent event) {
        try { export(event.getServer()); }
        catch (Exception failure) { LogUtils.getLogger().error("[HK3GTL-HEIGHT-AUDIT] 高度只读导出失败", failure); }
    }

    @SubscribeEvent
    public static void commands(RegisterCommandsEvent event) {
        event.getDispatcher().register(Commands.literal("hk3heightaudit").requires(s -> s.hasPermission(2))
                .then(Commands.literal("export").executes(c -> run(c.getSource(), false)))
                .then(Commands.literal("probe").executes(c -> run(c.getSource(), true))));
    }

    private static int run(CommandSourceStack source, boolean probe) {
        try {
            if (probe) placeProbes(source);
            Path path = export(source.getServer());
            source.sendSuccess(() -> Component.literal("高度核验已导出：" + path), false);
            return 1;
        } catch (Exception failure) {
            source.sendFailure(Component.literal("高度核验拒绝或失败：" + failure.getMessage()));
            LogUtils.getLogger().error("[HK3GTL-HEIGHT-AUDIT] 命令未通过", failure);
            return 0;
        }
    }

    /** 只读快照不生成区块；探针核验仅加载之前明确写入的测试区块。 */
    private static Path export(MinecraftServer server) throws IOException {
        JsonObject result = new JsonObject();
        result.addProperty("schema", 1);
        result.addProperty("revision", 182);
        result.addProperty("captured_at", OffsetDateTime.now().toString());
        result.addProperty("boundary", "实际服务器高度与探针；未证明全部模组渲染、机器加工或多人兼容");
        result.addProperty("contract_enabled", Hk3HeightService.state(server).map(s -> s.enabled()).orElse(false));
        Hk3HeightService.state(server).ifPresent(state -> {
            result.addProperty("contract_version", state.contractVersion());
            result.addProperty("world_id", state.worldId().toString());
            result.addProperty("contract_top_exclusive", state.topExclusive());
            JsonArray contracts = new JsonArray();
            state.dimensions().forEach((id, bounds) -> {
                JsonObject row = new JsonObject();
                row.addProperty("id", id);
                row.addProperty("original_min_y", bounds.originalMinY());
                row.addProperty("original_height", bounds.originalHeight());
                row.addProperty("logical_height", bounds.logicalHeight());
                row.addProperty("new_height", bounds.newHeight());
                row.addProperty("new_top_exclusive", bounds.newTopExclusive());
                contracts.add(row);
            });
            result.add("dimension_type_contracts", contracts);
        });
        result.addProperty("world_directory", worldRoot(server).getFileName().toString());
        JsonArray dimensions = new JsonArray();
        for (ServerLevel level : server.getAllLevels()) {
            JsonObject row = new JsonObject();
            row.addProperty("id", level.dimension().location().toString());
            row.addProperty("type", level.dimensionTypeId().location().toString());
            row.addProperty("min_y", level.getMinBuildHeight());
            row.addProperty("height", level.getHeight());
            row.addProperty("top_exclusive", level.getMaxBuildHeight());
            row.addProperty("logical_height", level.dimensionType().logicalHeight());
            row.addProperty("sections", level.getSectionsCount());
            row.addProperty("first_section", level.getMinSection());
            row.addProperty("last_section_exclusive", level.getMaxSection());
            row.addProperty("below_rejected", level.isOutsideBuildHeight(level.getMinBuildHeight() - 1));
            row.addProperty("top_rejected", level.isOutsideBuildHeight(level.getMaxBuildHeight()));
            row.addProperty("last_allowed", !level.isOutsideBuildHeight(level.getMaxBuildHeight() - 1));
            BlockPos position = new BlockPos(8, level.getMaxBuildHeight() - 1, 8);
            row.addProperty("last_coordinate_roundtrip", BlockPos.of(position.asLong()).equals(position));
            int lastSection = level.getSectionYFromSectionIndex(level.getSectionsCount() - 1);
            row.addProperty("last_section_byte_roundtrip", (int) (byte) lastSection == lastSection);
            dimensions.add(row);
        }
        result.add("dimensions", dimensions);
        result.add("probe_verification", verifyProbes(server));
        Path directory = FMLPaths.GAMEDIR.get().resolve("logs/hk3gtl-height-audit");
        Files.createDirectories(directory);
        Path target = directory.resolve("server-" + DateTimeFormatter.ofPattern("yyyyMMdd-HHmmss").format(OffsetDateTime.now()) + "-" + UUID.randomUUID() + ".json");
        Files.writeString(target, JSON.toJson(result), StandardCharsets.UTF_8);
        LogUtils.getLogger().info("[HK3GTL-HEIGHT-AUDIT] 高度实际导出：{}", target);
        return target;
    }

    /** 先完整预检并落计划，避免碰到非空气或已有探针后部分覆盖用户方块。 */
    private static void placeProbes(CommandSourceStack source) throws IOException {
        MinecraftServer server = source.getServer();
        if (!TEST_WORLD.equals(worldRoot(server).getFileName().toString())
                || source.getPlayer() == null || !source.getPlayer().isCreative()
                || !server.getWorldData().getAllowCommands()
                || !Hk3HeightService.state(server).map(s -> s.enabled()).orElse(false)) {
            throw new IllegalStateException("写入仅限本次已启用高度合同的专用新平坦创造作弊测试档");
        }
        Path manifest = worldRoot(server).resolve(PROBES);
        if (Files.exists(manifest)) throw new IllegalStateException("探针清单已存在，请仅用export核对持久化，不重复放置");
        JsonArray planned = new JsonArray();
        int[] heights = {768, 1007, 1023};
        String[] blocks = {"minecraft:glass", "minecraft:chest", "minecraft:sea_lantern"};
        for (ServerLevel level : server.getAllLevels()) {
            for (int i = 0; i < heights.length; i++) {
                BlockPos position = new BlockPos(8 + i, heights[i], 8);
                if (level.isOutsideBuildHeight(position) || !level.getBlockState(position).isAir()) {
                    throw new IllegalStateException("探针位置越界或非空气，停止写入：" + level.dimension().location() + " " + position);
                }
                JsonObject row = new JsonObject();
                row.addProperty("dimension", level.dimension().location().toString());
                row.addProperty("x", position.getX()); row.addProperty("y", position.getY()); row.addProperty("z", position.getZ());
                row.addProperty("block", blocks[i]);
                planned.add(row);
            }
        }
        JsonObject receipt = new JsonObject();
        receipt.addProperty("schema", 1); receipt.addProperty("revision", 166);
        receipt.addProperty("created_at", OffsetDateTime.now().toString());
        receipt.addProperty("boundary", "仅本次新测试世界的空位，先预检全部位置；重启后读取相同清单，不清除和覆写");
        receipt.add("positions", planned);
        writeAtomic(manifest, receipt);
        for (var element : planned) {
            JsonObject row = element.getAsJsonObject();
            ServerLevel level = resolveLevel(server, row);
            BlockPos position = position(row);
            var block = BuiltInRegistries.BLOCK.get(new ResourceLocation(row.get("block").getAsString()));
            if (!level.setBlock(position, block.defaultBlockState(), 3)) throw new IllegalStateException("放置被拒绝：" + position);
            if (level.getBlockEntity(position) instanceof ChestBlockEntity chest) {
                chest.setCustomName(Component.literal("HK3GTL高度持久化探针"));
                chest.setChanged();
            }
        }
    }

    private static JsonObject verifyProbes(MinecraftServer server) throws IOException {
        JsonObject result = new JsonObject();
        Path manifest = worldRoot(server).resolve(PROBES);
        result.addProperty("present", Files.isRegularFile(manifest));
        if (!Files.isRegularFile(manifest)) return result;
        if (!TEST_WORLD.equals(worldRoot(server).getFileName().toString())) {
            result.addProperty("refused", "非指定新测试世界，不加载探针区块");
            return result;
        }
        JsonObject planned = JsonParser.parseString(Files.readString(manifest, StandardCharsets.UTF_8)).getAsJsonObject();
        result.addProperty("created_at", planned.get("created_at").getAsString());
        JsonArray checks = new JsonArray();
        boolean all = true;
        for (var element : planned.getAsJsonArray("positions")) {
            JsonObject input = element.getAsJsonObject();
            JsonObject row = input.deepCopy();
            ServerLevel level = resolveLevel(server, input);
            BlockPos position = position(input);
            boolean match = level != null && !level.isOutsideBuildHeight(position)
                    && BuiltInRegistries.BLOCK.getKey(level.getBlockState(position).getBlock()).toString().equals(input.get("block").getAsString());
            row.addProperty("block_matches", match);
            if (level != null) {
                LevelChunk chunk = level.getChunkAt(position);
                boolean sections = chunk.getSections().length == level.getSectionsCount();
                row.addProperty("chunk_sections_match_level", sections);
                int heightmap = chunk.getHeight(net.minecraft.world.level.levelgen.Heightmap.Types.WORLD_SURFACE, position.getX() & 15, position.getZ() & 15);
                row.addProperty("heightmap_top_block_y", heightmap);
                row.addProperty("heightmap_matches_probe", heightmap == position.getY());
                match &= sections && heightmap == position.getY();
                if (input.get("block").getAsString().equals("minecraft:chest")) {
                    boolean chest = level.getBlockEntity(position) instanceof ChestBlockEntity entity
                            && entity.hasCustomName() && entity.getCustomName().getString().equals("HK3GTL高度持久化探针");
                    row.addProperty("chest_name_persisted", chest);
                    match &= chest;
                }
            }
            all &= match;
            checks.add(row);
        }
        result.addProperty("passed", all);
        result.add("checks", checks);
        return result;
    }

    private static ServerLevel resolveLevel(MinecraftServer server, JsonObject row) {
        String key = row.has("dimension") ? "dimension" : "id";
        return server.getLevel(ResourceKey.create(Registries.DIMENSION, new ResourceLocation(row.get(key).getAsString())));
    }

    private static BlockPos position(JsonObject row) {
        return new BlockPos(row.get("x").getAsInt(), row.get("y").getAsInt(), row.get("z").getAsInt());
    }

    private static Path worldRoot(MinecraftServer server) { return server.getWorldPath(LevelResource.ROOT).toAbsolutePath().normalize(); }

    private static void writeAtomic(Path target, JsonObject value) throws IOException {
        Path temporary = target.resolveSibling(target.getFileName() + ".tmp");
        Files.writeString(temporary, JSON.toJson(value), StandardCharsets.UTF_8);
        Files.move(temporary, target, StandardCopyOption.ATOMIC_MOVE);
    }
}
