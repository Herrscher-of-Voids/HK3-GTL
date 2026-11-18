package com.sirin.hk3gtl.common.dispatch;

import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.sirin.hk3gtl.common.machine.Hk3WorkableMultiblockMachine;
import com.sirin.hk3gtl.common.machine.research.Hk3LateIndustrialMachine;
import com.sirin.hk3gtl.common.research.Hk3ProcessReceipts;
import com.sirin.hk3gtl.common.research.Hk3ResearchData;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.block.entity.BlockEntity;

import java.math.BigInteger;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

public final class Hk3EnergyDispatch {
    private static final String KEY = "hk3gtlEnergyDispatch";
    private Hk3EnergyDispatch() {}

    private static CompoundTag state(Hk3WorkableMultiblockMachine machine) {
        return ((BlockEntity) machine.getHolder()).getPersistentData().getCompound(KEY);
    }
    private static void save(Hk3WorkableMultiblockMachine machine, CompoundTag state) {
        var block = (BlockEntity) machine.getHolder();
        block.getPersistentData().put(KEY, state);
        block.setChanged();
    }
    private static String facility(Hk3WorkableMultiblockMachine machine) {
        return machine.getLevel().dimension().location() + "@" + machine.getPos().asLong();
    }
    private static Hk3WorkableMultiblockMachine target(Hk3LateIndustrialMachine hub, String dimension, BlockPos pos) {
        var level = hub.getLevel().getServer().getLevel(ResourceKey.create(Registries.DIMENSION, new ResourceLocation(dimension)));
        return level != null && level.hasChunkAt(pos)
                && MetaMachine.getMachine(level, pos) instanceof Hk3WorkableMultiblockMachine machine ? machine : null;
    }
    private static boolean access(Hk3LateIndustrialMachine hub, ServerPlayer actor) {
        return actor.level() == hub.getLevel() && actor.distanceToSqr(hub.getPos().getCenter()) <= 64
                && actor.getUUID().equals(hub.getOwnerUUID()) && hub.isFormed()
                && MetaMachine.getMachine(hub.getLevel(), hub.getPos()) == hub
                && Hk3ResearchData.get(actor.server).completed(hub.getResearchTeamUUID(), "RN-CED");
    }
    private static boolean owns(Hk3LateIndustrialMachine hub, Hk3WorkableMultiblockMachine load) {
        return load != null && load != hub && hub.getOwnerUUID().equals(load.getOwnerUUID())
                && hub.getResearchTeamUUID().equals(load.getResearchTeamUUID());
    }
    private static Hk3LateIndustrialMachine boundHub(Hk3WorkableMultiblockMachine load, CompoundTag binding) {
        if (!binding.hasUUID("Owner") || !binding.getUUID("Owner").equals(load.getOwnerUUID())
                || !binding.getUUID("Team").equals(load.getResearchTeamUUID())) return null;
        var server = load.getLevel().getServer();
        var level = server.getLevel(ResourceKey.create(Registries.DIMENSION,
                new ResourceLocation(binding.getString("HubDimension"))));
        var pos = BlockPos.of(binding.getLong("HubPosition"));
        if (level == null || !level.hasChunkAt(pos)
                || !(MetaMachine.getMachine(level, pos) instanceof Hk3LateIndustrialMachine hub)
                || !hub.researchRole().equals("I41") || !hub.isFormed() || !owns(hub, load)
                || !Hk3ResearchData.get(server).completed(hub.getResearchTeamUUID(), "RN-CED")
                || !state(hub).getCompound("Loads").contains(facility(load))) return null;
        return hub;
    }

    public static CompoundTag registration(Hk3WorkableMultiblockMachine load) {
        var binding = state(load).getCompound("Binding");
        var hub = boundHub(load, binding);
        if (hub == null) return new CompoundTag();
        var result = binding.copy();
        var hubState = state(hub);
        if (result.hasUUID("Order") && (!hubState.hasUUID("Order")
                || !result.getUUID("Order").equals(hubState.getUUID("Order")))) result.remove("Order");
        return result;
    }

    public static String register(Hk3LateIndustrialMachine hub, ServerPlayer actor, String dimension, BlockPos pos) {
        if (!access(hub, actor)) return "仅主控本人可在成型I41上使用RN-CED调度权限";
        var load = target(hub, dimension, pos);
        if (!owns(hub, load)) return "只能登记本人账户、同一研究团队的已加载负载";
        var binding = new CompoundTag();
        binding.putString("Hub", facility(hub));
        binding.putString("HubDimension", hub.getLevel().dimension().location().toString());
        binding.putLong("HubPosition", hub.getPos().asLong());
        binding.putUUID("Owner", actor.getUUID());
        binding.putUUID("Team", hub.getResearchTeamUUID());
        binding.putLong("RegisteredAt", actor.server.overworld().getGameTime());
        var loadState = state(load);
        loadState.put("Binding", binding);
        loadState.remove("Run");
        save(load, loadState);
        var hubState = state(hub);
        var loads = hubState.getCompound("Loads");
        var location = new CompoundTag();
        location.putString("Dimension", dimension);
        location.putLong("Position", pos.asLong());
        loads.put(facility(load), location);
        hubState.put("Loads", loads);
        save(hub, hubState);
        return "已登记本人负载：" + pos.toShortString();
    }

    public static List<CompoundTag> registered(Hk3LateIndustrialMachine hub) {
        var loads = state(hub).getCompound("Loads");
        return loads.getAllKeys().stream().sorted().map(key -> loads.getCompound(key).copy()).toList();
    }

    public static String unregister(Hk3LateIndustrialMachine hub, ServerPlayer actor, String dimension, BlockPos pos) {
        if (!access(hub, actor)) return "只有主控本人可撤销登记";
        var load = target(hub, dimension, pos);
        if (!owns(hub, load) || !registration(load).getString("Hub").equals(facility(hub))) return "目标不是本主控的登记负载";
        var current = state(load);
        current.remove("Binding");
        current.remove("Run");
        save(load, current);
        var hubState = state(hub);
        hubState.getCompound("Loads").remove(facility(load));
        save(hub, hubState);
        return "已撤销登记，负载当前启停状态保持";
    }

    public static String control(Hk3LateIndustrialMachine hub, ServerPlayer actor, String dimension, BlockPos pos, boolean enabled) {
        if (!access(hub, actor)) return "仅主控本人可在成型I41上使用RN-CED调度权限";
        var load = target(hub, dimension, pos);
        if (!owns(hub, load) || !registration(load).getString("Hub").equals(facility(hub))) return "负载未登记或账户／团队授权已改变";
        if (load.getRecipeLogic().isWorkingEnabled() == enabled) return enabled ? "负载已经启用" : "负载已经暂停";
        if (enabled && !load.isFormed()) return "负载尚未成型";
        var current = state(load);
        long now = actor.server.overworld().getGameTime();
        load.getRecipeLogic().setWorkingEnabled(enabled);
        if (enabled) {
            var run = new CompoundTag();
            run.putUUID("Session", UUID.randomUUID());
            run.putLong("StartedAt", now);
            run.putString("HonkaiPaid", "0");
            run.putBoolean("Active", true);
            current.put("Run", run);
        } else {
            var run = current.getCompound("Run");
            if (run.getBoolean("Active")) {
                run.putBoolean("Active", false);
                run.putLong("StoppedAt", now);
                finish(hub, load, run);
                current.put("Run", run);
            }
        }
        save(load, current);
        return enabled ? "已手动启用本人负载" : "已手动暂停本人负载";
    }

    public static String status(Hk3LateIndustrialMachine hub, ServerPlayer actor, String dimension, BlockPos pos) {
        if (!actor.getUUID().equals(hub.getOwnerUUID())) return "此主控绑定其他玩家账户";
        var load = target(hub, dimension, pos);
        if (!owns(hub, load)) return "目标未加载或不属于本人账户与团队";
        var run = state(load).getCompound("Run");
        return (load.getRecipeLogic().isWorkingEnabled() ? "启用" : "暂停") + " · HW成功工作 "
                + run.getLong("WorkingTicks") + " tick · 出料 " + (run.contains("Produced") ? "已确认" : "待完成");
    }

    public static UUID newOrder(Hk3LateIndustrialMachine hub, ServerPlayer actor) {
        if (!access(hub, actor)) return reject(actor, "只有主控本人可建立交接工单");
        var loads = new ArrayList<Hk3WorkableMultiblockMachine>();
        for (var row : registered(hub)) {
            var load = target(hub, row.getString("Dimension"), BlockPos.of(row.getLong("Position")));
            if (!owns(hub, load) || !registration(load).getString("Hub").equals(facility(hub))) continue;
            if (load.getRecipeLogic().isWorkingEnabled() || load.getRecipeLogic().getProgress() > 0)
                return reject(actor, "请先完成在途批次并手动暂停登记负载，再建立新工单");
            loads.add(load);
        }
        if (loads.size() < 2) return reject(actor, "交接工单至少需要两台已加载、本人授权的登记负载");
        var order = UUID.randomUUID();
        var hubState = state(hub);
        hubState.putUUID("Order", order);
        hubState.putLong("OrderCreatedAt", actor.server.overworld().getGameTime());
        save(hub, hubState);
        for (var load : loads) {
            var current = state(load);
            current.getCompound("Binding").putUUID("Order", order);
            save(load, current);
        }
        return order;
    }
    private static UUID reject(ServerPlayer actor, String message) {
        actor.sendSystemMessage(Component.literal(message));
        return null;
    }

    public static void paid(MetaMachine machine, UUID owner, BigInteger amount, GTRecipe recipe) {
        if (!(machine instanceof Hk3WorkableMultiblockMachine load)) return;
        var current = state(load);
        var run = current.getCompound("Run");
        if (!run.getBoolean("Active") || !owner.equals(load.getOwnerUUID()) || registration(load).isEmpty()) return;
        recipe.data.putUUID("hk3gtlDispatchSession", run.getUUID("Session"));
        run.putString("HonkaiPaid", new BigInteger(run.getString("HonkaiPaid")).add(amount).toString());
        run.putLong("WorkingTicks", run.getLong("WorkingTicks") + 1);
        run.putLong("LastPaidAt", load.getLevel().getServer().overworld().getGameTime());
        current.put("Run", run);
        save(load, current);
    }

    public static void settled(Hk3WorkableMultiblockMachine load, GTRecipe recipe) {
        var current = state(load);
        var run = current.getCompound("Run");
        if (!run.getBoolean("Active") || !recipe.data.hasUUID("hk3gtlDispatchSession")
                || !recipe.data.getUUID("hk3gtlDispatchSession").equals(run.getUUID("Session")) || registration(load).isEmpty()) return;
        run.put("Produced", Hk3ProcessReceipts.settle(Hk3ProcessReceipts.snapshot(recipe), facility(load),
                load.getLevel().getServer().overworld().getGameTime()));
        current.put("Run", run);
        save(load, current);
    }

    private static void finish(Hk3LateIndustrialMachine hub, Hk3WorkableMultiblockMachine load, CompoundTag run) {
        if (run.getLong("WorkingTicks") == 0 || !run.contains("Produced", Tag.TAG_COMPOUND)) return;
        var receipt = new CompoundTag();
        receipt.putUUID("Batch", run.getUUID("Session"));
        receipt.putString("Facility", facility(hub));
        receipt.putString("Recipe", "hk3gtl:manual_energy_dispatch");
        receipt.putLong("Tick", run.getLong("StoppedAt"));
        receipt.putUUID("Owner", load.getOwnerUUID());
        receipt.putUUID("Team", load.getResearchTeamUUID());
        var inputs = registration(load);
        inputs.putString("Load", facility(load));
        inputs.putLong("StartedAt", run.getLong("StartedAt"));
        receipt.put("Inputs", inputs);
        receipt.put("Outputs", run.copy());
        var server = hub.getLevel().getServer();
        var data = Hk3ResearchData.get(server);
        data.recordProcessFact(hub.getResearchTeamUUID(), "manual_dispatch", receipt);
        var hubState = state(hub);
        var timelines = hubState.getCompound("Timelines");
        timelines.put(facility(load), receipt);
        hubState.put("Timelines", timelines);
        save(hub, hubState);
        var authorized = timelines.getAllKeys().stream().map(timelines::getCompound)
                .filter(row -> row.getUUID("Owner").equals(hub.getOwnerUUID())
                        && row.getUUID("Team").equals(hub.getResearchTeamUUID())).limit(2).toList();
        if (authorized.size() < 2) return;
        var multiple = receipt.copy();
        multiple.putString("Recipe", "hk3gtl:manual_energy_dispatch_multiple");
        var outputs = new CompoundTag();
        var rows = new ListTag();
        authorized.forEach(row -> rows.add(row.copy()));
        outputs.put("LoadTimelines", rows);
        multiple.put("Outputs", outputs);
        data.recordProcessFact(hub.getResearchTeamUUID(), "manual_dispatch_multiple", multiple);
    }
}
