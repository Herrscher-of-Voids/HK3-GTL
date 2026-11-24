package com.sirin.hk3gtl.common.integration.ae.nexus.crafting;

import appeng.api.stacks.AEKey;

import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ProbabilityOrderService;
import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ProbabilityOrderService.NexusQuote;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;

import java.math.BigInteger;
import java.nio.charset.StandardCharsets;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

final class Hk3NexusProbabilityRun {
    final List<NexusQuote> routes;
    final boolean direct;
    final Map<AEKey, BigInteger> desiredStock = new LinkedHashMap<>();
    long pass;
    BigInteger budget;
    int index;
    UUID child;

    Hk3NexusProbabilityRun(List<NexusQuote> routes, BigInteger budget, boolean direct, Map<AEKey, BigInteger> stockAtQuote) {
        this.routes = routes;
        this.budget = budget;
        this.direct = direct;
        if (!direct) for (var route : routes)
            desiredStock.put(route.key(), stockAtQuote.getOrDefault(route.key(), BigInteger.ZERO).add(route.amount()));
    }

    void start(Hk3NexusJob job, ServerPlayer player, boolean firstSubmission) {
        while (index < routes.size()) {
            var route = routes.get(index);
            if (!direct && !desiredStock.containsKey(route.key())) { index++; continue; }
            var token = pass == 0 ? job.id + ":" + index : job.id + ":" + pass + ":" + index;
            var id = UUID.nameUUIDFromBytes(token.getBytes(StandardCharsets.UTF_8));
            // 子单账本可先于主机存档写入。必须先认回该批回执，再检查库存。
            if (!Hk3ProbabilityOrderService.hasNexusChild(player.server, job.id, id)) {
                var demand = direct ? route.amount() : job.host.missingAmount(route.key(), desiredStock.get(route.key())).min(route.amount());
                if (demand.signum() == 0) { index++; continue; }
                if (budget.signum() <= 0) throw new IllegalArgumentException("共享尝试次数已用完");
                child = id;
                job.state = "WAITING_PROBABILITY";
                CompoundTag start = null;
                if (firstSubmission) {
                    start = job.write();
                    start.putUUID("Host", job.host.identity());
                }
                route.start(player, job.host.grid(), budget, demand, id, job.id, start);
            }
            child = id;
            job.state = "WAITING_PROBABILITY";
            job.host.changed();
            return;
        }
        finish(job);
    }

    private void finish(Hk3NexusJob job) {
        if (direct) { job.probability = null; job.state = "DONE"; job.link.markDone(); }
        else { job.state = "PLANNING"; job.retryAt = 0; }
        job.host.changed();
    }

    void refill(Hk3NexusJob job) {
        desiredStock.clear();
        for (var route : routes) {
            var missing = job.missing.get(route.key());
            if (missing != null) desiredStock.put(route.key(), job.previousMissingStock.get(route.key()).add(missing));
        }
        if (desiredStock.size() != job.missing.size()) {
            stop(job, job.host.level().getServer().getPlayerList().getPlayer(job.owner), "缺料需要新的概率路线，请重新确认");
            return;
        }
        pass++;
        index = 0;
        job.state = "WAITING_PROBABILITY";
    }

    void tick(Hk3NexusJob job) {
        if (job.ticks % 20 != 0) return;
        var server = job.host.level().getServer();
        var player = server.getPlayerList().getPlayer(job.owner);
        if (child == null) {
            if (player == null) return;
            try { start(job, player, false); }
            catch (IllegalArgumentException failure) { stop(job, player, failure.getMessage()); }
            return;
        }
        var receipt = Hk3ProbabilityOrderService.nexusReceipt(server, child);
        if (receipt == null) { stop(job, player, "找不到原概率订单回执"); return; }
        if (direct) {
            var delivered = receipt.delivered().min(job.requested);
            if (!delivered.equals(job.delivered)) { job.delivered = delivered; job.host.changed(); }
        }
        if (!receipt.settled()) return;
        var progress = new CompoundTag();
        progress.putLong("Pass", pass);
        progress.putInt("Index", index);
        progress.putByteArray("Budget", budget.subtract(receipt.attempts()).toByteArray());
        if (job.canceled) progress.putBoolean("Canceled", true);
        if (direct) progress.putByteArray("Delivered", job.delivered.toByteArray());
        else progress.put("DesiredStock", Hk3NexusLedger.write(desiredStock));
        if (!receipt.satisfied()) progress.putString("Reason", routes.get(index).key().getDisplayName().getString()
                + "：实得 " + receipt.actual() + "；" + receipt.note());
        if (Hk3ProbabilityOrderService.recordNexusProgress(server, child, progress)) apply(job, player, progress);
    }

    private boolean precedes(CompoundTag progress) {
        long recorded = progress.getLong("Pass");
        return pass < recorded || pass == recorded && index <= progress.getInt("Index");
    }

    private void apply(Hk3NexusJob job, ServerPlayer player, CompoundTag progress) {
        job.probabilityReceipt = true;
        pass = progress.getLong("Pass");
        index = progress.getInt("Index") + 1;
        budget = new BigInteger(progress.getByteArray("Budget"));
        child = null;
        if (direct) job.delivered = new BigInteger(progress.getByteArray("Delivered"));
        else {
            desiredStock.clear();
            desiredStock.putAll(Hk3NexusLedger.read(progress.getList("DesiredStock", Tag.TAG_COMPOUND)));
        }
        if (job.canceled || progress.getBoolean("Canceled")) {
            job.probability = null; job.canceled = true; job.state = "CANCELING"; job.link.cancel(); job.host.changed();
        }
        else if (progress.contains("Reason")) stop(job, player, progress.getString("Reason"));
        else if (index == routes.size()) finish(job);
        else job.host.changed();
    }

    static void restore(Hk3NexusJob job) {
        MinecraftServer server = job.host.level().getServer();
        var progress = Hk3ProbabilityOrderService.nexusProgress(server, job.id);
        var run = job.probability;
        if (progress != null) {
            if (run != null && run.precedes(progress)) run.apply(job, null, progress);
            else Hk3ProbabilityOrderService.forgetNexusProgress(server, job.id);
        }
        if (job.canceled && run != null && run.child != null
                && Hk3ProbabilityOrderService.hasNexusChild(server, job.id, run.child)) job.state = "CANCELING";
    }

    private void stop(Hk3NexusJob job, ServerPlayer player, String reason) {
        job.probability = null;
        job.dispatchNote = reason;
        job.state = "PROBABILITY_STOPPED";
        job.link.cancel();
        job.host.changed();
        if (player != null) player.sendSystemMessage(Component.literal("概率合成已停止：" + reason));
    }

    CompoundTag save() {
        var tag = new CompoundTag();
        var list = new ListTag();
        routes.forEach(route -> list.add(route.save()));
        tag.put("Routes", list);
        tag.putBoolean("Direct", direct);
        if (!direct) tag.put("DesiredStock", Hk3NexusLedger.write(desiredStock));
        tag.putLong("Pass", pass);
        tag.putInt("Index", index);
        tag.putByteArray("Budget", budget.toByteArray());
        if (child != null) tag.putUUID("Child", child);
        return tag;
    }

    static Hk3NexusProbabilityRun read(CompoundTag tag) {
        var routes = tag.getList("Routes", Tag.TAG_COMPOUND).stream().map(t -> NexusQuote.read((CompoundTag) t)).toList();
        var run = new Hk3NexusProbabilityRun(routes, new BigInteger(tag.getByteArray("Budget")), tag.getBoolean("Direct"),
                Hk3NexusLedger.read(tag.getList("StockAtQuote", Tag.TAG_COMPOUND)));
        if (tag.contains("DesiredStock")) {
            run.desiredStock.clear();
            run.desiredStock.putAll(Hk3NexusLedger.read(tag.getList("DesiredStock", Tag.TAG_COMPOUND)));
        }
        run.pass = tag.getLong("Pass");
        run.index = tag.getInt("Index");
        if (tag.hasUUID("Child")) run.child = tag.getUUID("Child");
        return run;
    }
}
