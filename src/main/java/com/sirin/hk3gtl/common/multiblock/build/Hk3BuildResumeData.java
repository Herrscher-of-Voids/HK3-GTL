package com.sirin.hk3gtl.common.multiblock.build;

import com.gregtechceu.gtceu.api.machine.multiblock.MultiblockControllerMachine;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.core.GlobalPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.saveddata.SavedData;
import org.gtlcore.gtlcore.common.item.UltimateTerminalBehavior.AutoBuildSetting;

import java.util.UUID;

final class Hk3BuildResumeData extends SavedData {
    private static final String NAME = "hk3gtl_build_resume";
    private CompoundTag task = new CompoundTag();

    static Hk3BuildResumeData get(MinecraftServer server) {
        return com.sirin.hk3gtl.common.util.Hk3SavedDataGuard.get(server, NAME,
                Hk3BuildResumeData::load, Hk3BuildResumeData::new);
    }

    boolean pending() { return task.hasUUID("Owner"); }
    UUID owner() { return task.getUUID("Owner"); }
    ResourceKey<Level> dimension() {
        return ResourceKey.create(Registries.DIMENSION, new ResourceLocation(task.getString("Dimension")));
    }
    BlockPos position() { return BlockPos.of(task.getLong("Position")); }
    boolean paused() { return task.getBoolean("Paused"); }
    AutoBuildSetting setting() {
        var setting = new AutoBuildSetting();
        setting.setAeMode(task.getBoolean("AeMode"));
        if (task.contains("AeDimension")) setting.setBoundAE(GlobalPos.of(
                ResourceKey.create(Registries.DIMENSION, new ResourceLocation(task.getString("AeDimension"))),
                BlockPos.of(task.getLong("AePosition"))));
        return setting;
    }

    boolean matches(ServerPlayer owner, MultiblockControllerMachine controller) {
        return pending() && this.owner().equals(owner.getUUID()) && sameController(controller);
    }

    boolean sameController(MultiblockControllerMachine controller) {
        return task.getString("Dimension").equals(controller.getLevel().dimension().location().toString())
                && task.getLong("Position") == controller.getPos().asLong()
                && task.getString("Machine").equals(controller.self().getDefinition().getId().toString())
                && task.getString("Facing").equals(controller.getFrontFacing().getName());
    }

    void remember(UUID owner, ServerLevel level, MultiblockControllerMachine controller,
                  AutoBuildSetting setting, boolean paused) {
        task = new CompoundTag();
        task.putUUID("Owner", owner);
        task.putString("Dimension", level.dimension().location().toString());
        task.putLong("Position", controller.getPos().asLong());
        task.putString("Machine", controller.self().getDefinition().getId().toString());
        task.putString("Facing", controller.getFrontFacing().getName());
        task.putBoolean("Paused", paused);
        task.putBoolean("AeMode", setting.isAeMode());
        GlobalPos boundAE = setting.getBoundAE();
        if (boundAE != null) {
            task.putString("AeDimension", boundAE.dimension().location().toString());
            task.putLong("AePosition", boundAE.pos().asLong());
        }
        setDirty();
    }

    void clear() {
        task = new CompoundTag();
        setDirty();
    }

    private static Hk3BuildResumeData load(CompoundTag tag) {
        var data = new Hk3BuildResumeData();
        data.task = tag.getCompound("Task");
        return data;
    }

    @Override public CompoundTag save(CompoundTag tag) {
        tag.put("Task", task.copy());
        return tag;
    }
}
