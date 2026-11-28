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
import net.minecraft.world.level.Level;
import net.minecraft.world.level.saveddata.SavedData;
import org.gtlcore.gtlcore.common.item.UltimateTerminalBehavior.AutoBuildSetting;

import java.util.UUID;

final class Hk3BuildResumeData extends SavedData {
    private static final String NAME = "hk3gtl_build_resume";
    private CompoundTag tasks = new CompoundTag();

    static Task get(MinecraftServer server, UUID owner) {
        var data = com.sirin.hk3gtl.common.util.Hk3SavedDataGuard.get(server, NAME,
                Hk3BuildResumeData::load, Hk3BuildResumeData::new);
        return data.new Task(owner.toString());
    }

    final class Task {
        private final String key;
        private Task(String key) { this.key = key; }
        private CompoundTag task() { return tasks.getCompound(key); }

        boolean pending() { return tasks.contains(key); }
        ResourceKey<Level> dimension() {
            return ResourceKey.create(Registries.DIMENSION, new ResourceLocation(task().getString("Dimension")));
        }
        BlockPos position() { return BlockPos.of(task().getLong("Position")); }
        boolean paused() { return task().getBoolean("Paused"); }
        AutoBuildSetting setting() {
            var task = task();
            var setting = new AutoBuildSetting();
            setting.setAeMode(task.getBoolean("AeMode"));
            if (task.contains("AeDimension")) setting.setBoundAE(GlobalPos.of(
                    ResourceKey.create(Registries.DIMENSION, new ResourceLocation(task.getString("AeDimension"))),
                    BlockPos.of(task.getLong("AePosition"))));
            return setting;
        }

        boolean matches(MultiblockControllerMachine controller) {
            return pending() && sameController(controller);
        }

        boolean sameController(MultiblockControllerMachine controller) {
            var task = task();
            return task.getString("Dimension").equals(controller.getLevel().dimension().location().toString())
                    && task.getLong("Position") == controller.getPos().asLong()
                    && task.getString("Machine").equals(controller.self().getDefinition().getId().toString())
                    && task.getString("Facing").equals(controller.getFrontFacing().getName());
        }

        void remember(ServerLevel level, MultiblockControllerMachine controller,
                      AutoBuildSetting setting, boolean paused) {
            var task = new CompoundTag();
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
            tasks.put(key, task);
            setDirty();
        }

        void clear() {
            tasks.remove(key);
            setDirty();
        }

    }

    private static Hk3BuildResumeData load(CompoundTag tag) {
        var data = new Hk3BuildResumeData();
        data.tasks = tag.getCompound("Tasks");
        var legacy = tag.getCompound("Task");
        if (legacy.hasUUID("Owner")) data.tasks.put(legacy.getUUID("Owner").toString(), legacy);
        return data;
    }

    @Override public CompoundTag save(CompoundTag tag) {
        tag.put("Tasks", tasks.copy());
        return tag;
    }
}
