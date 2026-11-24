package com.sirin.hk3gtl.common.integration.ae.exact;

import appeng.api.config.CpuSelectionMode;
import appeng.api.networking.IGrid;
import appeng.api.networking.IGridNode;
import appeng.api.networking.crafting.ICraftingSimulationRequester;
import appeng.api.networking.crafting.ICraftingCPU;
import appeng.api.networking.security.IActionHost;
import appeng.api.networking.security.IActionSource;
import appeng.api.stacks.AEKey;
import appeng.me.cluster.implementations.CraftingCPUCluster;
import appeng.menu.me.crafting.CraftAmountMenu;
import appeng.menu.me.crafting.CraftConfirmMenu;
import com.sirin.hk3gtl.common.integration.ae.nexus.crafting.Hk3NexusCrafting;
import com.sirin.hk3gtl.common.integration.ae.nexus.crafting.Hk3NexusPlanSummary;
import com.mojang.logging.LogUtils;
import com.sirin.hk3gtl.common.integration.ae.Hk3AePlanningService;
import com.sirin.hk3gtl.common.integration.ae.Hk3CraftingCycleFlag;
import com.sirin.hk3gtl.common.network.Hk3ExactOrderStatusPacket;
import com.sirin.hk3gtl.common.network.Hk3Network;
import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.ModList;
import net.minecraftforge.network.PacketDistributor;

import java.io.IOException;
import java.math.BigInteger;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.LinkedHashMap;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Future;
import java.util.concurrent.RejectedExecutionException;
import java.util.function.Function;

/** 大数父订单只调度真实AE小批作业；世界与存储访问全部留在服务器线程。 */
public final class Hk3ExactOrderService {
    private static final Hk3ExactPlanner.Limits LIMITS = new Hk3ExactPlanner.Limits(2048, 8192);
    private static final Map<MinecraftServer, RuntimeState> RUNTIMES = new ConcurrentHashMap<>();

    private record Binding(UUID owner, IActionHost host, IGridNode node, IGrid grid,
                           IActionSource source, ICraftingCPU preferredCpu) implements ICraftingSimulationRequester {
        @Override public IActionSource getActionSource() { return source; }
        @Override public IGridNode getGridNode() { return node; }
        Hk3NexusCrafting supplyHost() { return preferredCpu instanceof Hk3NexusCrafting.NexusCpu cpu ? cpu.host() : null; }
        boolean valid(MinecraftServer server) {
            return server.getPlayerList().getPlayer(owner) != null && host.getActionableNode() == node
                    && node.isActive() && node.getGrid() == grid
                    && source.player().map(player -> player == server.getPlayerList().getPlayer(owner)).orElse(false);
        }
    }

    private record Preview(BigInteger amount, AEKey target, Binding binding,
                           CraftAmountMenu menu, PlanWork<Estimate> future) {}
    private record Estimate(BigInteger bytes, int nodes, Map<AEKey, BigInteger> missing,
                            boolean hasCycles, Map<AEKey, BigInteger> seeds, boolean seedsAvailable) {}
    private static final class PlanWork<T> {
        private Hk3AeExactSnapshot.Capture capture;
        private Function<Hk3AeExactSnapshot.Capture, T> calculation;
        private Future<T> running;

        PlanWork(Binding binding, AEKey target, Function<Hk3AeExactSnapshot, T> calculation) {
            this(binding, target, true, null, collected -> calculation.apply(collected.finish()));
        }

        private PlanWork(Binding binding, AEKey target, boolean captureInventory, Hk3NexusCrafting supplyHost,
                         Function<Hk3AeExactSnapshot.Capture, T> calculation) {
            capture = new Hk3AeExactSnapshot.Capture(binding.node().getLevel(), binding.grid(), binding, target, LIMITS, captureInventory, supplyHost);
            this.calculation = calculation;
        }

        static PlanWork<Boolean> verify(Binding binding, Hk3AeExactSnapshot planned) {
            return new PlanWork<>(binding, planned.target(), false, null, collected -> collected.matches(planned));
        }

        void step(MinecraftServer server, long deadline) {
            if (capture == null || !capture.step(deadline)) return;
            var collected = capture;
            var work = calculation;
            running = Hk3AePlanningService.submit(server, () -> work.apply(collected));
            capture = null;
            calculation = null;
        }

        boolean isDone() { return running != null && running.isDone(); }
        T get() throws Exception { return running.get(); }
        void cancel(boolean interrupt) {
            capture = null;
            calculation = null;
            if (running != null) running.cancel(interrupt);
        }
    }
    private static final class BatchJob {
        private final Binding binding;
        private final PlanWork<Hk3ExactBatchPlanner.Selection> future;
        private Hk3ExactBatchPlanner.Batch batch;
        private PlanWork<Boolean> verification;

        BatchJob(Binding binding, PlanWork<Hk3ExactBatchPlanner.Selection> future) {
            this.binding = binding;
            this.future = future;
        }
        Binding binding() { return binding; }
        void cancel() {
            future.cancel(true);
            if (verification != null) verification.cancel(true);
        }
    }
    private static final class Watch {
        final CraftAmountMenu menu;
        final AEKey target;
        UUID orderId;
        Hk3ExactOrderStatusPacket last;
        Hk3ExactOrder.Snapshot lastState;
        String lastNote;

        Watch(CraftAmountMenu menu, AEKey target) {
            this.menu = menu;
            this.target = target;
        }
    }
    private static final class RuntimeState {
        final Map<UUID, Preview> previews = new HashMap<>();
        final Map<UUID, Watch> watches = new HashMap<>();
        final Map<UUID, Binding> bindings = new HashMap<>();
        final Map<UUID, BatchJob> jobs = new HashMap<>();
        final Set<UUID> resumeAfterReceipt = new HashSet<>();
        final Map<UUID, Long> actions = new HashMap<>();
        int cursor;
        boolean ledgerFault;

        int collecting() {
            int count = 0;
            for (var preview : previews.values()) if (preview.future().capture != null) count++;
            for (var job : jobs.values()) {
                if (job.future.capture != null) count++;
                if (job.verification != null && job.verification.capture != null) count++;
            }
            return count;
        }
    }

    private Hk3ExactOrderService() {}

    private record NativeEstimate(Hk3NexusPlanSummary summary, Estimate estimate) {}

    public static final class NativePreview {
        private final BigInteger amount;
        private final AEKey target;
        private final Binding binding;
        private final PlanWork<NativeEstimate> work;
        private NativeEstimate estimate;

        private NativePreview(CraftConfirmMenu menu, IActionHost host, AEKey target, BigInteger amount) {
            this.amount = amount;
            this.target = target;
            var node = host.getActionableNode();
            binding = new Binding(menu.getPlayer().getUUID(), host, node, node.getGrid(), menu.getActionSource(), null);
            work = new PlanWork<>(binding, target, snapshot -> {
                var detailed = snapshot.planDetailed(amount, () -> Thread.currentThread().isInterrupted());
                var result = detailed.result();
                BigInteger bytes = Hk3AeExactPlanAdapter.estimateBytes(snapshot, amount, result);
                Map<AEKey, BigInteger> crafting = new LinkedHashMap<>(), operations = new LinkedHashMap<>();
                result.batches().forEach((pattern, count) -> snapshot.recipe(pattern).outputs().forEach((key, output) -> {
                    crafting.merge(key, output.multiply(count), BigInteger::add);
                    operations.merge(key, count, BigInteger::add);
                }));
                crafting.putIfAbsent(target, amount);
                boolean unsupported = result.status() != Hk3ExactPlanner.Status.SUCCESS
                        && result.status() != Hk3ExactPlanner.Status.MISSING_INPUT;
                var summary = Hk3NexusPlanSummary.of(target, amount, bytes, unsupported, result.missing(),
                        result.stockUsed(), crafting, operations, result.batches()).batched();
                ((Hk3CraftingCycleFlag) (Object) summary).hk3gtl$setHasCycles(detailed.orderedExecutionRequired());
                var note = new Estimate(bytes, result.visitedNodes(), result.missing(), detailed.orderedExecutionRequired(),
                        detailed.seedRequired(), detailed.seedRequired().entrySet().stream().allMatch(seed ->
                                snapshot.inventory().getOrDefault(seed.getKey(), BigInteger.ZERO).compareTo(seed.getValue()) >= 0));
                return new NativeEstimate(summary, note);
            });
        }

        public AEKey target() { return target; }
        public BigInteger amount() { return amount; }
        public void tick() { work.step(binding.node().getLevel().getServer(), System.nanoTime() + 2_000_000L); }
        public boolean isDone() { return work.isDone(); }
        public Hk3NexusPlanSummary summary() throws Exception {
            estimate = work.get();
            return estimate.summary();
        }
        public void cancel() { work.cancel(true); }

        public void start(ICraftingCPU selectedCpu) throws IOException {
            var server = binding.node().getLevel().getServer();
            var runtime = RUNTIMES.computeIfAbsent(server, ignored -> new RuntimeState());
            var data = Hk3ExactOrderData.get(server);
            prune(data, binding.owner());
            var order = new Hk3ExactOrder(UUID.randomUUID(), binding.owner(), amount);
            var entry = new Hk3ExactOrderData.Entry(order, target, estimate.summary().exactBytes,
                    estimateNote(estimate.estimate()));
            data.entries.put(order.snapshot().orderId(), entry);
            var selected = new Binding(binding.owner(), binding.host(), binding.node(), binding.grid(), binding.source(), selectedCpu);
            Hk3ExactOrderService.start(server, runtime, data, entry, selected);
        }
    }

    public static NativePreview previewNative(CraftConfirmMenu menu, IActionHost host, AEKey target, BigInteger amount) {
        return new NativePreview(menu, host, target, amount);
    }

    public static void action(CraftAmountMenu menu, String action) {
        if (!(menu.getPlayer() instanceof ServerPlayer player) || player.containerMenu != menu
                || !menu.isValidMenu() || action == null || action.length() > 512) return;
        var server = player.getServer();
        var runtime = RUNTIMES.computeIfAbsent(server, ignored -> new RuntimeState());
        if (action.equals("leave") || action.equals("cancel_preview")) {
            if (com.sirin.hk3gtl.common.integration.ae.nexus.crafting.Hk3NexusTerminalOrders.action(menu, action)) return;
            Preview preview = runtime.previews.remove(player.getUUID());
            if (preview != null) preview.future().cancel(true);
            if (action.equals("leave")) runtime.watches.remove(player.getUUID());
            else send(player, menu.containerId, null, preview == null
                    ? "没有待取消的规划；已确认的订单保持原状态" : "规划已取消；已确认的订单保持原状态");
            return;
        }
        long now = server.getTickCount();
        Long previous = runtime.actions.put(player.getUUID(), now);
        if (previous != null && now - previous < 10) {
            send(player, menu.containerId, null, "操作过快，请稍候重试");
            return;
        }
        try {
            if (runtime.ledgerFault) throw new IllegalStateException("订单账本异常已冻结，请核对日志和原文件后重启");
            var source = menu.getActionSource();
            if (!(menu.getTarget() instanceof IActionHost host) || source == null)
                throw new IllegalArgumentException("当前终端没有可用AE操作来源");
            var node = host.getActionableNode();
            if (node == null) throw new IllegalArgumentException("当前AE终端未连接网络");
            var binding = new Binding(player.getUUID(), host, node, node.getGrid(), source, null);
            if (!binding.valid(server)) throw new IllegalArgumentException("AE网络离线或操作归属无效");
            var targetStack = menu.getWhatToCraft();
            if (targetStack == null) throw new IllegalArgumentException("没有选择合成目标");
            if (com.sirin.hk3gtl.common.integration.ae.nexus.crafting.Hk3NexusTerminalOrders.action(menu, action)) return;
            AEKey target = targetStack.what();
            Watch watch = runtime.watches.get(player.getUUID());
            if (watch == null || watch.menu != menu || !watch.target.equals(target))
                runtime.watches.put(player.getUUID(), new Watch(menu, target));
            var data = Hk3ExactOrderData.get(server);
            String[] parts = action.split(":", 2);
            String verb = parts[0];
            if (verb.equals("preview") && parts.length == 2) {
                BigInteger amount = Hk3ExactOrder.parsePositiveDecimal(parts[1]);
                Preview previousPreview = runtime.previews.remove(player.getUUID());
                if (previousPreview != null) previousPreview.future().cancel(true);
                if (!Hk3AePlanningService.hasCapacity(server, runtime.collecting()))
                    throw new IllegalArgumentException("AE规划队列已满，请稍后重试");
                prune(data, player.getUUID());
                if (data.entries.size() >= Hk3ExactOrderData.MAX_ORDERS
                        || data.entries.values().stream().filter(row -> row.order.snapshot().owner().equals(player.getUUID())).count() >= 16)
                    throw new IllegalArgumentException("订单容量已满，请先完成或取消既有订单");
                var future = new PlanWork<>(binding, target, snapshot -> {
                    var detailed = snapshot.planDetailed(amount, () -> Thread.currentThread().isInterrupted());
                    var result = detailed.result();
                    if (result.status() != Hk3ExactPlanner.Status.SUCCESS
                            && result.status() != Hk3ExactPlanner.Status.MISSING_INPUT)
                        throw new IllegalArgumentException(result.reason());
                    return new Estimate(Hk3AeExactPlanAdapter.estimateBytes(snapshot, amount, result),
                            result.visitedNodes(), result.missing(), detailed.orderedExecutionRequired(),
                            detailed.seedRequired(), detailed.seedRequired().entrySet().stream().allMatch(seed ->
                                    snapshot.inventory().getOrDefault(seed.getKey(), BigInteger.ZERO).compareTo(seed.getValue()) >= 0));
                });
                runtime.previews.put(player.getUUID(), new Preview(amount, target, binding, menu, future));
                return;
            }
            Hk3ExactOrderData.Entry entry = find(data, player.getUUID(), target, parts.length == 2 ? parts[1] : null);
            if (entry == null) { send(player, menu.containerId, null, "当前目标没有大数订单，请先规划"); return; }
            UUID id = entry.order.snapshot().orderId();
            switch (verb) {
                case "start", "resume" -> start(server, runtime, data, entry, binding);
                case "pause", "cancel" -> {
                    runtime.resumeAfterReceipt.remove(entry.order.snapshot().activeToken());
                    if (verb.equals("cancel")) entry.order.cancel(); else entry.order.pause();
                    BatchJob job = runtime.jobs.remove(id);
                    if (job != null) job.cancel();
                    runtime.bindings.remove(id);
                    entry.note = verb.equals("cancel")
                            ? "取消已记录；程序CPU停止新投料，等待本批实物全部回流后结算；普通CPU按原生逻辑取消"
                            : "已暂停后续批次；当前CPU批次允许完成";
                    data.checkpoint(server);
                }
                case "status" -> { }
                default -> throw new IllegalArgumentException("未知大数订单动作");
            }
            send(player, menu.containerId, id, describe(entry));
        } catch (Exception failure) {
            if (!(failure instanceof IllegalArgumentException)) LogUtils.getLogger().warn("HK3大数订单操作失败", failure);
            send(player, menu.containerId, null, "操作未完成：" + failure.getMessage());
        }
    }

    private static void start(MinecraftServer server, RuntimeState runtime, Hk3ExactOrderData data,
                              Hk3ExactOrderData.Entry entry, Binding binding) throws IOException {
        UUID id = entry.order.snapshot().orderId();
        var state = entry.order.snapshot();
        if (state.activeToken() != null) {
            if (state.state() != Hk3ExactOrder.State.PAUSED && state.state() != Hk3ExactOrder.State.RUNNING)
                throw new IllegalArgumentException("该订单当前无法恢复");
            long amount = state.activeAmount().longValueExact();
            long matches = binding.grid().getCraftingService().getCpus().stream()
                    .map(cpu -> cpu instanceof CraftingCPUCluster cluster ? cluster.craftingLogic : cpu)
                    .filter(cpu -> cpu instanceof Hk3ExactCpuTracker.BatchAccess batch
                            && batch.hk3gtl$matchesBatch(state.activeToken(), entry.target, amount)).count();
            if (matches != 1)
                throw new IllegalArgumentException("请将原CPU接回当前AE网络并恢复工作；当前批次保持暂停，不会重复投料");
            entry.note = "已核对同网原CPU；当前批次不重投，收到真实成功回执后继续后续批次";
            data.checkpoint(server);
            runtime.bindings.put(id, binding);
            runtime.resumeAfterReceipt.add(state.activeToken());
            return;
        }
        if (entry.order.snapshot().state() == Hk3ExactOrder.State.PAUSED) entry.order.resume();
        if (entry.order.snapshot().state() != Hk3ExactOrder.State.READY)
            throw new IllegalArgumentException("该订单当前不能开始");
        BatchJob stale = runtime.jobs.remove(id);
        if (stale != null) stale.cancel();
        entry.missingSupply = Map.of();
        runtime.bindings.remove(id);
        entry.note = "已确认，每批投料前核对样板和库存";
        try { data.checkpoint(server); }
        catch (IOException failure) { entry.order.pause(); data.setDirty(); throw failure; }
        runtime.bindings.put(id, binding);
    }

    static Hk3ExactOrderData.Entry createSupply(ServerPlayer player, UUID parent, AEKey target, long amount) throws IOException {
        var data = Hk3ExactOrderData.get(player.server);
        for (var entry : data.entries.values()) if (parent.equals(entry.parent)) return entry;
        prune(data, player.getUUID());
        if (data.entries.size() >= Hk3ExactOrderData.MAX_ORDERS
                || data.entries.values().stream().filter(row -> row.order.snapshot().owner().equals(player.getUUID())).count() >= 16)
            return null;
        var order = new Hk3ExactOrder(UUID.randomUUID(), player.getUUID(), BigInteger.valueOf(amount));
        var entry = new Hk3ExactOrderData.Entry(order, target, BigInteger.ZERO, "概率订单的确定性前置生产");
        entry.parent = parent;
        data.entries.put(order.snapshot().orderId(), entry);
        data.checkpoint(player.server);
        return entry;
    }

    static Hk3ExactOrderData.Entry supply(MinecraftServer server, UUID parent, UUID id) throws IOException {
        var entry = Hk3ExactOrderData.get(server).entries.get(id);
        if (entry == null || !parent.equals(entry.parent)) throw new IOException("前置订单记录缺失或归属不符；保留父引用，禁止重建重投");
        return entry;
    }

    static void resumeSupply(ServerPlayer player, IActionHost host, UUID parent, UUID id, ICraftingCPU cpu) throws IOException {
        var entry = supply(player.server, parent, id);
        var state = entry.order.snapshot();
        if (!state.owner().equals(player.getUUID())) throw new IllegalArgumentException("前置订单不属于本人");
        if (state.state() == Hk3ExactOrder.State.COMPLETE || state.state() == Hk3ExactOrder.State.CANCELLED) return;
        var node = host.getActionableNode();
        var binding = new Binding(player.getUUID(), host, node, node.getGrid(), IActionSource.ofPlayer(player), cpu);
        var runtime = RUNTIMES.computeIfAbsent(player.server, ignored -> new RuntimeState());
        if (runtime.ledgerFault) throw new IllegalStateException("确定性订单账本已冻结");
        start(player.server, runtime, Hk3ExactOrderData.get(player.server), entry, binding);
    }

    static void stopSupply(MinecraftServer server, UUID parent, UUID id, boolean cancel) throws IOException {
        var entry = supply(server, parent, id);
        if (cancel) entry.order.cancel(); else entry.order.pause();
        var runtime = RUNTIMES.get(server);
        if (runtime != null) {
            runtime.resumeAfterReceipt.remove(entry.order.snapshot().activeToken());
            var job = runtime.jobs.remove(id);
            if (job != null) job.cancel();
            runtime.bindings.remove(id);
        }
        entry.note = cancel ? "所属概率订单已停止；仅取消本前置订单" : "所属概率订单已暂停";
        Hk3ExactOrderData.get(server).checkpoint(server);
    }

    static void forgetSupply(MinecraftServer server, UUID parent, UUID id) throws IOException {
        var entry = supply(server, parent, id);
        if (entry.order.snapshot().activeToken() != null) throw new IllegalArgumentException("前置订单仍有在途批次");
        Hk3ExactOrderData.get(server).entries.remove(id);
        Hk3ExactOrderData.get(server).checkpoint(server);
    }

    @SubscribeEvent
    public static void tick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || !ModList.get().isLoaded("ae2")) return;
        var server = event.getServer();
        var runtime = RUNTIMES.get(server);
        if (runtime == null || runtime.ledgerFault) return;
        try {
            var data = Hk3ExactOrderData.get(server);
            long deadline = System.nanoTime() + 2_000_000L;
            completePreviews(server, runtime, data, deadline);
            completeBatches(server, runtime, data, deadline);
            if (server.getTickCount() % 20 != 0) return;
            syncWatches(server, runtime, data);
            if (runtime.bindings.isEmpty()) return;
            var ids = new ArrayList<>(runtime.bindings.keySet());
            UUID id = ids.get(Math.floorMod(runtime.cursor++, ids.size()));
            var entry = data.entries.get(id);
            if (entry == null || entry.order.snapshot().state() == Hk3ExactOrder.State.COMPLETE
                    || entry.order.snapshot().state() == Hk3ExactOrder.State.CANCELLED) {
                runtime.bindings.remove(id); return;
            }
            if (entry.order.snapshot().state() != Hk3ExactOrder.State.READY || runtime.jobs.containsKey(id)) return;
            Binding binding = runtime.bindings.get(id);
            if (!binding.valid(server)) {
                entry.order.pause(); entry.note = "玩家离线或AE连接改变；请在终端中明确恢复";
                runtime.bindings.remove(id); data.checkpoint(server); return;
            }
            BigInteger capacity = binding.grid().getCraftingService().getCpus().stream()
                    .filter(cpu -> binding.preferredCpu() == null || cpu == binding.preferredCpu())
                    .filter(cpu -> !cpu.isBusy() && cpu.getSelectionMode() != CpuSelectionMode.MACHINE_ONLY)
                    .map(Hk3ExactCpuCapacity::exactBytes).max(BigInteger::compareTo).orElse(BigInteger.ZERO);
            if (capacity.signum() <= 0) { entry.note = "等待可用的玩家合成CPU"; return; }
            if (!Hk3AePlanningService.hasCapacity(server, runtime.collecting())) { entry.note = "等待AE规划队列空位"; return; }
            BigInteger remaining = entry.order.remaining();
            var supplyHost = entry.parent == null ? null : binding.supplyHost();
            runtime.jobs.put(id, new BatchJob(binding, new PlanWork<>(binding, entry.target, true, supplyHost,
                    capture -> Hk3ExactBatchPlanner.plan(capture.finish(), remaining, capacity,
                            () -> Thread.currentThread().isInterrupted(), supplyHost != null))));
        } catch (Exception failure) {
            ledgerFault(server, new IllegalStateException("大数订单调度失败", failure));
        }
    }

    private static void completePreviews(MinecraftServer server, RuntimeState runtime, Hk3ExactOrderData data, long deadline) throws Exception {
        for (var item : new ArrayList<>(runtime.previews.entrySet())) {
            Preview preview = item.getValue();
            ServerPlayer player = server.getPlayerList().getPlayer(item.getKey());
            if (player == null || player.containerMenu != preview.menu() || !preview.menu().isValidMenu()) {
                runtime.previews.remove(item.getKey());
                preview.future().cancel(true);
                continue;
            }
            try {
                preview.future().step(server, deadline);
                if (!preview.future().isDone()) continue;
                runtime.previews.remove(item.getKey());
                Estimate estimate = preview.future().get();
                if (!preview.binding().valid(server)) throw new IllegalStateException("规划期间AE连接已改变");
                prune(data, item.getKey());
                if (data.entries.size() >= Hk3ExactOrderData.MAX_ORDERS
                        || data.entries.values().stream().filter(row -> row.order.snapshot().owner().equals(item.getKey())).count() >= 16)
                    throw new IllegalStateException("订单容量已满，请先完成或取消既有订单");
                var order = new Hk3ExactOrder(UUID.randomUUID(), item.getKey(), preview.amount());
                var entry = new Hk3ExactOrderData.Entry(order, preview.target(), estimate.bytes(), estimateNote(estimate));
                data.entries.put(order.snapshot().orderId(), entry);
                data.checkpoint(server);
                send(player, preview.menu().containerId, order.snapshot().orderId(), describe(entry));
            } catch (Exception failure) {
                runtime.previews.remove(item.getKey());
                preview.future().cancel(true);
                send(player, preview.menu().containerId, null, "规划未提交：" + failure.getMessage());
            }
        }
    }

    private static void completeBatches(MinecraftServer server, RuntimeState runtime, Hk3ExactOrderData data, long deadline) throws IOException {
        for (var item : new ArrayList<>(runtime.jobs.entrySet())) {
            BatchJob job = item.getValue();
            var entry = data.entries.get(item.getKey());
            if (entry == null || entry.order.snapshot().state() != Hk3ExactOrder.State.READY
                    || runtime.bindings.get(item.getKey()) != job.binding()) {
                runtime.jobs.remove(item.getKey());
                job.cancel();
                continue;
            }
            try {
                if (!job.binding().valid(server)) throw new IllegalStateException("批次规划期间AE连接已改变");
                job.future.step(server, deadline);
                if (!job.future.isDone()) continue;
                if (job.verification == null) {
                    var selected = job.future.get();
                    job.batch = selected.batch();
                    if (entry.parent != null) entry.missingSupply = selected.missing();
                    if (job.batch == null) {
                        runtime.jobs.remove(item.getKey());
                        entry.note = "等待材料或足够的CPU容量（最小批次尚不可执行）";
                        continue;
                    }
                    job.verification = PlanWork.verify(job.binding(), job.batch.snapshot());
                }
                job.verification.step(server, deadline);
                if (!job.verification.isDone()) continue;
                runtime.jobs.remove(item.getKey());
                var batch = job.batch;
                if (!job.verification.get())
                    throw new IllegalStateException("批次规划期间样板已改变，请重新规划");
                var plan = batch.nexusPlan() == null ? batch.plan() : job.binding().supplyHost()
                        .supplyPlan(job.binding().owner(), entry.target, batch.amount(), batch.nexusPlan());
                UUID token = entry.order.beginBatch(batch.amount());
                data.activeTokens.put(token, entry);
                BigInteger bytes = Hk3ExactCpuCapacity.requiredBytes(plan);
                entry.note = "合成 CPU 正在投料：" + batch.amount() + "；本批所需存储字节：" + bytes;
                // 先持久化意图。后续结果未知也保留令牌，绝不推测成未提交后重发。
                data.checkpoint(server);
                var submitted = Hk3ExactCpuTracker.submit(token, () -> job.binding().grid().getCraftingService()
                        .submitJob(plan, null, job.binding().preferredCpu(), true, job.binding().source()));
                if (!submitted.successful()) {
                    entry.order.finish(token, false, BigInteger.ZERO);
                    data.activeTokens.remove(token);
                    entry.note = "AE未能开始本批生产：" + submitted.errorCode() + "；已暂停，请补足条件后恢复";
                    data.checkpoint(server);
                } else {
                    entry.note = "当前批次生产数量：" + batch.amount() + "；本批所需存储字节："
                            + bytes + "；网络中最大单CPU容量："
                            + job.binding().grid().getCraftingService().getCpus().stream()
                                .map(Hk3ExactCpuCapacity::exactBytes).max(BigInteger::compareTo).orElse(BigInteger.ZERO)
                            + "；等待本批产物";
                }
            } catch (Exception failure) {
                runtime.jobs.remove(item.getKey());
                job.cancel();
                if (failure instanceof ExecutionException && failure.getCause() instanceof RejectedExecutionException) {
                    entry.note = "AE规划队列繁忙；等待下一轮调度，不重复投料";
                    continue;
                }
                entry.order.pause();
                entry.note = "本批结果尚未确认，订单已暂停；恢复前请检查原CPU：" + failure.getMessage();
                data.checkpoint(server);
                LogUtils.getLogger().warn("HK3大数订单批次暂停", failure);
            }
        }
    }

    private static void syncWatches(MinecraftServer server, RuntimeState runtime, Hk3ExactOrderData data) {
        var iterator = runtime.watches.entrySet().iterator();
        while (iterator.hasNext()) {
            var item = iterator.next();
            Watch watch = item.getValue();
            ServerPlayer player = server.getPlayerList().getPlayer(item.getKey());
            if (player == null || player.containerMenu != watch.menu || !watch.menu.isValidMenu()) {
                iterator.remove();
                continue;
            }
            if (runtime.previews.containsKey(item.getKey())) continue;
            var entry = watch.orderId == null ? find(data, item.getKey(), watch.target, null) : data.entries.get(watch.orderId);
            var state = entry == null ? null : entry.order.snapshot();
            String note = entry == null ? null : entry.note;
            if (watch.last != null && java.util.Objects.equals(state, watch.lastState)
                    && java.util.Objects.equals(note, watch.lastNote)) continue;
            watch.lastState = state;
            watch.lastNote = note;
            String text = entry == null ? "当前目标没有大数订单，请先规划" : describe(entry);
            var status = new Hk3ExactOrderStatusPacket(watch.menu.containerId,
                    entry == null ? null : state.orderId(), text.length() > 8000 ? text.substring(0, 8000) : text);
            if (!status.equals(watch.last)) send(player, status.menuId(), status.orderId(), status.text());
        }
    }

    public static void finished(ServerLevel level, UUID token, boolean success, long produced) {
        try { recordFinished(level, token, success, produced); }
        catch (RuntimeException failure) { ledgerFault(level.getServer(), failure); }
    }

    private static void recordFinished(ServerLevel level, UUID token, boolean success, long produced) {
        var server = level.getServer();
        var data = Hk3ExactOrderData.get(server);
        var entry = data.activeTokens.get(token);
        if (entry == null) return;
        var runtime = RUNTIMES.get(server);
        UUID id = entry.order.snapshot().orderId();
        boolean resume = runtime != null && runtime.resumeAfterReceipt.remove(token);
        if (produced < 0) {
            entry.order.pause();
            entry.note = "本批产量尚未确认，订单已暂停；请检查原CPU，避免重复投料";
        } else {
            entry.order.finish(token, success, BigInteger.valueOf(produced));
            data.activeTokens.remove(token);
            entry.note = success ? "已收到真实CPU生产成功回执；产物流向保持原生AE逻辑"
                    : "原生CPU取消或失败；已计入真实成品" + produced + "，剩余数量暂停";
            if (resume && success) {
                Binding binding = runtime.bindings.get(id);
                if (binding != null && binding.valid(server)) entry.order.resume();
            }
        }
        try { data.checkpoint(server); }
        catch (IOException failure) {
            entry.order.pause(); data.setDirty();
            LogUtils.getLogger().error("HK3大数订单回执落盘失败，禁止自动续批", failure);
        }
    }

    public static boolean cancelRequested(ServerLevel level, UUID token) {
        var entry = Hk3ExactOrderData.get(level.getServer()).activeTokens.get(token);
        return entry != null && entry.order.snapshot().state() == Hk3ExactOrder.State.CANCELLED;
    }

    public static boolean freezeRequested(ServerLevel level, UUID token) {
        var server = level.getServer();
        var runtime = RUNTIMES.get(server);
        if (runtime != null && runtime.ledgerFault) return true;
        try {
            // 跨文件保存无法确认的旧CPU只冻结，不自动退库或继续生产。
            return !Hk3ExactOrderData.get(server).activeTokens.containsKey(token);
        } catch (RuntimeException failure) {
            ledgerFault(server, failure);
            return true;
        }
    }

    private static void ledgerFault(MinecraftServer server, RuntimeException failure) {
        var runtime = RUNTIMES.computeIfAbsent(server, ignored -> new RuntimeState());
        if (!runtime.ledgerFault) LogUtils.getLogger().error("HK3大数订单账本异常，已冻结调度和所属CPU，拒绝重置账本", failure);
        runtime.ledgerFault = true;
        runtime.previews.values().forEach(job -> job.future().cancel(true));
        runtime.previews.clear();
        runtime.jobs.values().forEach(job -> job.cancel());
        runtime.jobs.clear();
        runtime.resumeAfterReceipt.clear();
        runtime.bindings.clear();
        runtime.watches.clear();
    }

    @SubscribeEvent
    public static void stopped(ServerStoppedEvent event) {
        var runtime = RUNTIMES.remove(event.getServer());
        if (runtime != null) {
            runtime.previews.values().forEach(job -> job.future().cancel(true));
            runtime.jobs.values().forEach(job -> job.cancel());
        }
    }

    public static void loggedOut(ServerPlayer player) {
        var server = player.getServer();
        var runtime = RUNTIMES.get(server);
        if (runtime == null) return;
        UUID owner = player.getUUID();
        runtime.actions.remove(owner);
        runtime.watches.remove(owner);
        Preview preview = runtime.previews.remove(owner);
        if (preview != null) preview.future().cancel(true);
        try {
            var data = Hk3ExactOrderData.get(server);
            boolean changed = false;
            for (var item : new ArrayList<>(runtime.bindings.entrySet())) {
                if (!item.getValue().owner().equals(owner)) continue;
                runtime.bindings.remove(item.getKey());
                BatchJob job = runtime.jobs.remove(item.getKey());
                if (job != null) job.cancel();
                var entry = data.entries.get(item.getKey());
                if (entry != null) {
                    runtime.resumeAfterReceipt.remove(entry.order.snapshot().activeToken());
                    changed |= entry.order.pause();
                    entry.note = "玩家已离线，后续批次暂停；在途CPU仍按真实回执结算";
                }
            }
            if (changed) data.checkpoint(server);
        } catch (Exception failure) {
            ledgerFault(server, new IllegalStateException("离线暂停订单失败", failure));
        }
    }

    private static Hk3ExactOrderData.Entry find(Hk3ExactOrderData data, UUID owner, AEKey target, String value) {
        if (value != null && !value.isBlank()) {
            var entry = data.entries.get(UUID.fromString(value));
            if (entry == null || entry.parent != null || !entry.order.snapshot().owner().equals(owner) || !entry.target.equals(target))
                throw new IllegalArgumentException("订单不属于本人或与当前合成目标不同");
            return entry;
        }
        Hk3ExactOrderData.Entry latest = null;
        for (var entry : data.entries.values())
            if (entry.parent == null && entry.order.snapshot().owner().equals(owner) && entry.target.equals(target)) latest = entry;
        return latest;
    }

    private static void prune(Hk3ExactOrderData data, UUID owner) {
        if (data.entries.values().removeIf(entry -> entry.parent == null && entry.order.snapshot().owner().equals(owner)
                && entry.order.snapshot().activeToken() == null
                && (entry.order.snapshot().state() == Hk3ExactOrder.State.CANCELLED
                    || entry.order.snapshot().state() == Hk3ExactOrder.State.COMPLETE))) data.setDirty();
    }

    private static String describe(Hk3ExactOrderData.Entry entry) {
        var state = entry.order.snapshot();
        return entry.target.getDisplayName().getString() + "\n状态：" + state.state()
                + "\n新增总量：" + state.total() + "\n生产完成：" + state.completed()
                + "\n剩余：" + entry.order.remaining() + "\n在途：" + state.activeAmount()
                + "\n全单规划估算字节：" + shortNumber(entry.plannedBytes)
                + "（非单个CPU容量；每批另算）\n" + entry.note;
    }

    private static String estimateNote(Estimate estimate) {
        StringBuilder note = new StringBuilder("全单需求已聚合；可达节点：").append(estimate.nodes());
        if (estimate.hasCycles()) {
            note.append("\n存在循环；启动种子：").append(estimate.seedsAvailable() ? "库存满足" : "库存不足");
            estimate.seeds().entrySet().stream().limit(6).forEach(entry -> note.append("\n")
                    .append(entry.getKey().getDisplayName().getString()).append(" × ").append(shortNumber(entry.getValue())));
            if (estimate.seeds().size() > 6) note.append("\n另需启动种子：").append(estimate.seeds().size() - 6).append("种");
        }
        if (!estimate.missing().isEmpty()) {
            note.append("\n全单缺料（允许按现有库存分批生产）：");
            estimate.missing().entrySet().stream().limit(6).forEach(entry -> note.append("\n")
                    .append(entry.getKey().getDisplayName().getString()).append(" × ").append(shortNumber(entry.getValue())));
            if (estimate.missing().size() > 6) note.append("\n另有材料缺口：").append(estimate.missing().size() - 6).append("种");
        }
        return note.toString();
    }

    private static String shortNumber(BigInteger number) {
        String text = number.toString();
        return text.length() <= 256 ? text : text.substring(0, 64) + "…（共" + text.length() + "位）";
    }

    private static void send(ServerPlayer player, int menuId, UUID order, String text) {
        if (text.length() > 8000) text = text.substring(0, 8000);
        var status = new Hk3ExactOrderStatusPacket(menuId, order, text);
        var watch = RUNTIMES.get(player.getServer()).watches.get(player.getUUID());
        if (watch != null && watch.menu.containerId == menuId) {
            watch.last = status;
            if (order != null) watch.orderId = order;
        }
        Hk3Network.CHANNEL.send(PacketDistributor.PLAYER.with(() -> player), status);
        if (player.containerMenu.containerId != menuId) player.sendSystemMessage(Component.literal(text));
    }
}
