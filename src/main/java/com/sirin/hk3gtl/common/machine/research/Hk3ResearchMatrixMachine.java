package com.sirin.hk3gtl.common.machine.research;

import com.gregtechceu.gtceu.api.machine.IMachineBlockEntity;
import com.sirin.hk3gtl.common.constants.Hk3Constants;
import com.sirin.hk3gtl.common.machine.Hk3WorkableMultiblockMachine;
import com.sirin.hk3gtl.common.research.Hk3ResearchData;
import com.sirin.hk3gtl.common.research.Hk3ResearchManager;
import com.sirin.hk3gtl.common.research.Hk3ResearchNode;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;

import javax.annotation.Nullable;

/** 旧研究矩阵只保留原任务与进度档案，不再扣电、扣材料或执行随机失败。 */
public class Hk3ResearchMatrixMachine extends Hk3WorkableMultiblockMachine {
    private static final String TAG_ACTIVE = "hk3gtl_active_research";
    private CompoundTag legacyTask = new CompoundTag();

    public Hk3ResearchMatrixMachine(IMachineBlockEntity holder) { super(holder); }
    @Override protected boolean enableMultiRecipe() { return false; }

    @Override public void onLoad() {
        super.onLoad();
        archiveLegacyTask();
    }

    @Override public void onUnload() {
        archiveLegacyTask();
        super.onUnload();
    }

    @Override public void onStructureInvalid() {
        archiveLegacyTask();
        super.onStructureInvalid();
    }

    @Override public void saveCustomPersistedData(CompoundTag tag, boolean forDrop) {
        super.saveCustomPersistedData(tag, forDrop);
        saveActiveResearch(tag);
    }

    @Override public void loadCustomPersistedData(CompoundTag tag) {
        super.loadCustomPersistedData(tag);
        loadActiveResearch(tag);
    }

    private void archiveLegacyTask() {
        if (getLevel() instanceof ServerLevel level && !legacyTask.isEmpty())
            Hk3ResearchData.get(level.getServer()).archiveLegacyTask(
                    level.dimension().location() + "@" + getPos().asLong(), legacyTask);
    }

    private void saveActiveResearch(CompoundTag tag) {
        if (!legacyTask.isEmpty()) tag.put(TAG_ACTIVE, legacyTask.copy());
    }

    private void loadActiveResearch(CompoundTag tag) { legacyTask = tag.getCompound(TAG_ACTIVE).copy(); }
    public CompoundTag saveCustomData(CompoundTag tag) { saveActiveResearch(tag); return tag; }
    public void loadCustomData(CompoundTag tag) { loadActiveResearch(tag); }
    public CompoundTag writeAdditional(CompoundTag tag) { saveActiveResearch(tag); return tag; }
    public void readAdditional(CompoundTag tag) { loadActiveResearch(tag); }

    public boolean tryStart(ServerPlayer player, Hk3ResearchNode node) {
        Hk3ResearchManager.submitResearchById(player, node.id());
        return false;
    }

    public void cancel() { archiveLegacyTask(); }
    public boolean isBusy() { return false; }
    public CompoundTag retiredTask() { return legacyTask.copy(); }

    @Nullable public Snapshot snapshot() {
        return legacyTask.isEmpty() ? null : new Snapshot(legacyTask.getString("research"),
                legacyTask.getInt("progress"), legacyTask.getInt("total"), legacyTask.getLong("extra"),
                legacyTask.getDouble("speedFactor"));
    }

    @Nullable public static Hk3ResearchMatrixMachine findNearest(Player player) {
        var center = player.blockPosition();
        int radius = Hk3Constants.RESEARCH_MATRIX_SEARCH_RADIUS, chunks = (radius >> 4) + 1;
        double distance = (long) radius * radius;
        Hk3ResearchMatrixMachine nearest = null;
        for (int dx = -chunks; dx <= chunks; dx++) for (int dz = -chunks; dz <= chunks; dz++) {
            var chunk = player.level().getChunkSource().getChunkNow((center.getX() >> 4) + dx, (center.getZ() >> 4) + dz);
            if (chunk == null) continue;
            for (var holder : chunk.getBlockEntities().values()) {
                double next = holder.getBlockPos().distSqr(center);
                if (next > distance || !(holder instanceof IMachineBlockEntity machine)
                        || !(machine.getMetaMachine() instanceof Hk3ResearchMatrixMachine matrix) || !matrix.isFormed()) continue;
                nearest = matrix;
                distance = next;
            }
        }
        return nearest;
    }

    public record Snapshot(String researchId, int progress, int totalTicks, long extraEutPerTick, double speedFactor) {
        public double ratio() { return totalTicks <= 0 ? 0.0 : (double) progress / totalTicks; }
    }
}
