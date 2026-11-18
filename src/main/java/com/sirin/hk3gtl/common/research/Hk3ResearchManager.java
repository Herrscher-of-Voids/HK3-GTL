package com.sirin.hk3gtl.common.research;

import com.sirin.hk3gtl.common.constants.Hk3Constants;
import com.sirin.hk3gtl.common.machine.research.Hk3ResearchMatrixMachine;
import com.sirin.hk3gtl.common.network.Hk3Network;
import com.sirin.hk3gtl.common.network.ResearchOpenS2CPacket;
import com.sirin.hk3gtl.common.network.ResearchStateSyncS2CPacket;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.network.PacketDistributor;

import java.util.List;

/** 现行RN权限与同步；旧77题只读归档，不自动换算为新课题或继续扣费。 */
@Mod.EventBusSubscriber(modid = Hk3Constants.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public class Hk3ResearchManager {
    private static final String TAG_PREFIX = "hk3gtl_res_";
    private static final String SELECTED_RESEARCH_TAG = "hk3gtl_res_selected";
    private static final ResourceLocation ABYSS_RESEARCH_MATRIX_ID =
            new ResourceLocation(Hk3Constants.MOD_ID, "abyss_research_analysis_matrix");

    public static void onPlayerSecond(ServerPlayer player) {}
    public static void onEventTriggered(ServerPlayer player, String eventId) {}

    @SubscribeEvent
    public static void onPlayerLoggedIn(PlayerEvent.PlayerLoggedInEvent event) {
        if (event.getEntity() instanceof ServerPlayer player) syncClientResearchState(player);
    }

    @SubscribeEvent
    public static void onResearchMatrixInteract(PlayerInteractEvent.RightClickBlock event) {
        if (event.getHand() != InteractionHand.MAIN_HAND || event.getLevel().isClientSide()
                || !(event.getEntity() instanceof ServerPlayer player) || player.isShiftKeyDown()) return;
        var id = BuiltInRegistries.BLOCK.getKey(event.getLevel().getBlockState(event.getPos()).getBlock());
        if (!ABYSS_RESEARCH_MATRIX_ID.equals(id)) return;
        if (event.getLevel().getBlockEntity(event.getPos()) instanceof com.gregtechceu.gtceu.api.machine.IMachineBlockEntity be
                && be.getMetaMachine() instanceof com.sirin.hk3gtl.common.machine.research.Hk3ResearchInstituteMachine) return;
        event.setCanceled(true);
        event.setCancellationResult(InteractionResult.SUCCESS);
        retiredResearch(player);
        syncClientResearchState(player);
        Hk3Network.CHANNEL.send(PacketDistributor.PLAYER.with(() -> player), new ResearchOpenS2CPacket());
    }

    public static boolean isCompleted(ServerPlayer player, String researchId) {
        var data = Hk3ResearchData.get(player);
        if (researchId.startsWith("RN-")) return data.permits(data.scope(player.getUUID()), researchId);
        return Hk3ResearchNodes.get(researchId) != null && (player.getPersistentData().getBoolean(TAG_PREFIX + researchId)
                || data.legacyCompleted(player.getUUID(), researchId));
    }

    public static boolean isCompleted(Player player, String researchId) {
        if (player instanceof ServerPlayer serverPlayer) return isCompleted(serverPlayer, researchId);
        return (researchId.startsWith("RN-") || Hk3ResearchNodes.get(researchId) != null)
                && player.getPersistentData().getBoolean(TAG_PREFIX + researchId);
    }

    public static boolean isCompleted(CompoundTag data, String researchId) {
        return Hk3ResearchNodes.get(researchId) != null && data.getBoolean(TAG_PREFIX + researchId);
    }

    public static List<Hk3ResearchNode> getManualResearchNodes() {
        return Hk3ResearchNodes.ordered().stream().filter(Hk3ResearchNode::isManualResearch).toList();
    }

    public static boolean prerequisitesMetForDisplay(Player player, Hk3ResearchNode node) { return false; }
    public static boolean hasRequirementsForDisplay(Player player, Hk3ResearchNode node) { return false; }

    public static void submitResearchById(ServerPlayer player, String researchId) { retiredResearch(player); }
    public static boolean forceCompleteResearch(ServerPlayer player, String researchId) {
        retiredResearch(player);
        return false;
    }

    private static void retiredResearch(ServerPlayer player) {
        player.sendSystemMessage(Component.literal("旧版77题已归档；请使用当前研究所办理现行研究，旧成果不自动兑换新课题。"));
    }

    public static void syncClientResearchState(ServerPlayer player) {
        CompoundTag playerData = player.getPersistentData();
        Hk3ResearchData industrial = Hk3ResearchData.get(player);
        industrial.archiveLegacyResearch(player.getUUID(), playerData);
        CompoundTag syncTag = new CompoundTag();
        for (String key : playerData.getAllKeys()) {
            if (key.startsWith(TAG_PREFIX)
                    || key.startsWith("hk3gtl_evt_")
                    || key.startsWith("hk3gtl_nar_")
                    || "hk3gtl_gaze_level".equals(key)
                    || "hk3gtl_civ_level".equals(key)
                    || "hk3gtl_voltage_tier".equals(key)
                    || SELECTED_RESEARCH_TAG.equals(key)) {
                syncTag.put(key, playerData.get(key).copy());
            }
        }
        for (var node : Hk3ResearchNodes.ordered())
            if (industrial.legacyCompleted(player.getUUID(), node.id()))
                syncTag.putBoolean(TAG_PREFIX + node.id(), true);
        appendNearestMatrixSnapshot(player, syncTag);
        // 覆盖旧玩家标签中可能存在的RN伪造值，仅同步账本算出的只读结果。
        for (String key : java.util.List.copyOf(syncTag.getAllKeys())) {
            if (key.startsWith(TAG_PREFIX + "RN-")) syncTag.remove(key);
        }
        for (String id : Hk3ResearchCatalog.bundled().topics().keySet()) {
            if (industrial.completed(industrial.scope(player.getUUID()), id)) syncTag.putBoolean(TAG_PREFIX + id, true);
        }
        for (String tier : Hk3ResearchData.CIRCUIT_TIERS) {
            if (industrial.canReconstruct(industrial.scope(player.getUUID()), tier)) syncTag.putBoolean(TAG_PREFIX + Hk3ResearchData.CIRCUIT_PREFIX + tier, true);
        }

        Hk3Network.CHANNEL.send(
                PacketDistributor.PLAYER.with(() -> player),
                new ResearchStateSyncS2CPacket(syncTag)
        );
    }

    private static void appendNearestMatrixSnapshot(ServerPlayer player, CompoundTag syncTag) {
        Hk3ResearchMatrixMachine matrix = Hk3ResearchMatrixMachine.findNearest(player);
        CompoundTag matrixTag = new CompoundTag();
        matrixTag.putBoolean("present", matrix != null);
        if (matrix != null) {
            matrixTag.putBoolean("busy", matrix.isBusy());
            matrixTag.putBoolean("retired", true);
            matrixTag.put("legacyTask", matrix.retiredTask());
            Hk3ResearchMatrixMachine.Snapshot snapshot = matrix.snapshot();
            if (snapshot != null) {
                matrixTag.putString("research", snapshot.researchId());
                matrixTag.putInt("progress", snapshot.progress());
                matrixTag.putInt("total", snapshot.totalTicks());
                matrixTag.putLong("extra", snapshot.extraEutPerTick());
                matrixTag.putDouble("speedFactor", snapshot.speedFactor());
                matrixTag.putLong("gameTime", player.serverLevel().getGameTime());
            }
        }
        syncTag.put("hk3gtl_research_matrix", matrixTag);
    }
}

