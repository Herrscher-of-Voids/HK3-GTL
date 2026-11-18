package com.sirin.hk3gtl.common.research;

import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.sirin.hk3gtl.common.capability.Hk3EnergyTick;
import com.sirin.hk3gtl.common.capability.Hk3RefundJournal;
import com.sirin.hk3gtl.common.capability.HonkaiWirelessNetwork;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.machine.Hk3WorkableMultiblockMachine;
import com.sirin.hk3gtl.common.machine.research.Hk3ResearchInstituteMachine;
import com.sirin.hk3gtl.common.machine.wonder.Hk3WonderCatalog;
import com.sirin.hk3gtl.common.recipe.power.Hk3PortPayment;
import com.sirin.hk3gtl.common.recipe.power.Hk3PowerPorts;
import com.sirin.hk3gtl.common.review.Hk3ReviewData;
import com.sirin.hk3gtl.common.review.Hk3ReviewLedger;
import net.minecraft.server.MinecraftServer;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.IdentityHashMap;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.UUID;

/** 正式研究在同tick末统一选位；只有真实W13主控实现Source并登记后才能提供加速。 */
@Mod.EventBusSubscriber(modid = "hk3gtl", bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class Hk3W13ResearchService {
    public static final int CAPACITY = 16;
    public static final int RUNTIME_TIER = Hk3WonderCatalog.get("W13").runtimeTier();
    public static final long EU_PER_JOB = Hk3Values.VA_LONG[RUNTIME_TIER];
    public static final BigInteger HW_PER_JOB = BigInteger.valueOf(256);
    public interface Source {
        UUID researchServiceId();
        boolean researchServiceRunning();
    }
    @FunctionalInterface public interface Advance { void run(boolean wonder, Runnable advanced); }
    private record Request(Hk3ResearchInstituteMachine lab, Hk3ResearchWorkQueue.Snapshot job, Advance advance) {}
    private record Candidate(Request request, Hk3WorkableMultiblockMachine mother, Hk3W13ResearchData.Link link) {}
    private record Observation(long tick, String state) {}
    private static final class Runtime {
        final Map<UUID, Hk3WorkableMultiblockMachine> sources = new LinkedHashMap<>();
        final Map<UUID, Request> requests = new LinkedHashMap<>();
        final Map<UUID, Integer> served = new HashMap<>();
        final Map<UUID, Observation> observations = new HashMap<>();
        final Map<UUID, Hk3EnergyTick> refunds = new HashMap<>();
    }
    private static final Map<MinecraftServer, Runtime> RUNTIMES = new IdentityHashMap<>();
    private Hk3W13ResearchService() {}
    private static Runtime runtime(MinecraftServer server) { return RUNTIMES.computeIfAbsent(server, key -> new Runtime()); }

    public static void loaded(Hk3WorkableMultiblockMachine machine) {
        var source = (Source) machine;
        var state = runtime(machine.getLevel().getServer());
        if (state.sources.put(source.researchServiceId(), machine) != machine)
            state.refunds.remove(source.researchServiceId());
    }
    public static void unloaded(Hk3WorkableMultiblockMachine machine) {
        runtime(machine.getLevel().getServer()).sources.remove(((Source) machine).researchServiceId(), machine);
    }
    private static boolean live(Hk3WorkableMultiblockMachine machine) {
        return !machine.isInValid() && machine.getLevel().hasChunkAt(machine.getPos())
                && MetaMachine.getMachine(machine.getLevel(), machine.getPos()) == machine;
    }
    public static Hk3W13ResearchData.Endpoint mother(Hk3WorkableMultiblockMachine machine) {
        if (!(machine instanceof Source source) || !live(machine) || machine.getOwnerUUID() == null
                || runtime(machine.getLevel().getServer()).sources.get(source.researchServiceId()) != machine) return null;
        return endpoint(machine, source.researchServiceId());
    }
    public static Hk3W13ResearchData.Endpoint endpoint(Hk3WorkableMultiblockMachine machine, UUID id) {
        return new Hk3W13ResearchData.Endpoint(id, machine.getLevel().dimension().location().toString(),
                machine.getPos().asLong(), machine.getOwnerUUID(), machine.getResearchTeamUUID());
    }
    private static boolean available(MinecraftServer server, Hk3WorkableMultiblockMachine machine) {
        return live(machine) && machine.isFormed() && machine.getRecipeLogic().isWorkingEnabled()
                && ((Source) machine).researchServiceRunning()
                && Hk3ResearchData.get(server).completed(machine.getResearchTeamUUID(), "RN-ASR")
                && Hk3ReviewData.get(server).settled(machine.getResearchTeamUUID(), Hk3ReviewLedger.Kind.SECOND);
    }
    public static void submit(Hk3ResearchInstituteMachine lab, Hk3ResearchWorkQueue.Snapshot job, Advance advance) {
        var server = lab.getLevel().getServer();
        var state = runtime(server);
        boolean connected = Hk3W13ResearchData.get(server).forLab(lab.researchServiceId()).stream()
                .anyMatch(link -> link.authorized(server) && link.lab().equals(lab.researchEndpoint())
                        && state.sources.containsKey(link.mother().id()));
        if (Hk3LabExperimentRules.get(job.quote().topic()) != null || !connected) advance.run(false, () -> {});
        else state.requests.putIfAbsent(job.id(), new Request(lab, job, advance));
    }
    public static String status(Hk3ResearchInstituteMachine lab) {
        var server = lab.getLevel().getServer();
        var observation = runtime(server).observations.get(lab.researchServiceId());
        if (observation != null && observation.tick() >= server.overworld().getGameTime() - 1) return observation.state();
        var links = Hk3W13ResearchData.get(server).forLab(lab.researchServiceId());
        if (links.isEmpty()) return "unbound";
        return links.stream().anyMatch(link -> link.authorized(server)) ? "idle" : "pending";
    }
    public static int served(MinecraftServer server, UUID mother) { return runtime(server).served.getOrDefault(mother, 0); }

    public static boolean settleRefund(Hk3WorkableMultiblockMachine machine) {
        var state = runtime(machine.getLevel().getServer());
        UUID id = ((Source) machine).researchServiceId();
        var payment = state.refunds.get(id);
        if (payment == null) {
            payment = Hk3RefundJournal.resume(machine);
            if (payment == null) return true;
            state.refunds.put(id, payment);
        }
        if (!payment.finish(false)) return false;
        state.refunds.remove(id);
        return true;
    }

    public static void finishPayment(Hk3WorkableMultiblockMachine machine, Hk3EnergyTick payment, boolean committed) {
        if (!payment.finish(committed))
            runtime(machine.getLevel().getServer()).refunds.put(((Source) machine).researchServiceId(), payment);
    }

    @SubscribeEvent public static void tick(TickEvent.ServerTickEvent event) {
        if (event.phase == TickEvent.Phase.END) flush(event.getServer());
    }
    @SubscribeEvent public static void stopped(ServerStoppedEvent event) { RUNTIMES.remove(event.getServer()); }

    private static void flush(MinecraftServer server) {
        var state = runtime(server);
        state.served.clear();
        state.sources.values().removeIf(machine -> !live(machine));
        state.sources.forEach((id, machine) -> {
            if (!state.refunds.containsKey(id)) {
                var refund = Hk3RefundJournal.resume(machine);
                if (refund != null) state.refunds.put(id, refund);
            }
        });
        state.refunds.entrySet().removeIf(entry -> entry.getValue().finish(false));
        if (state.requests.isEmpty()) return;
        var requests = new ArrayList<>(state.requests.values());
        state.requests.clear();
        var data = Hk3W13ResearchData.get(server);
        var candidates = new ArrayList<Candidate>();
        for (var request : requests) {
            for (var link : data.forLab(request.lab().researchServiceId())) {
                var mother = state.sources.get(link.mother().id());
                if (mother != null && link.authorized(server) && link.lab().equals(request.lab().researchEndpoint())
                        && link.mother().equals(mother(mother)) && available(server, mother))
                    candidates.add(new Candidate(request, mother, link));
            }
        }
        candidates.sort(Comparator.<Candidate>comparingInt(c -> c.link().priority()).reversed()
                .thenComparingLong(c -> c.request().job().order())
                .thenComparing(c -> c.request().job().id()).thenComparing(c -> c.link().mother().id()));
        var advanced = new HashSet<UUID>();
        for (var candidate : candidates) {
            var request = candidate.request();
            UUID source = candidate.link().mother().id();
            if (advanced.contains(request.job().id())) continue;
            if (state.served.getOrDefault(source, 0) >= CAPACITY) {
                observe(server, request.lab(), "capacity");
                continue;
            }
            var current = data.link(source, request.lab().researchServiceId());
            if (current.version() != candidate.link().version() || !current.authorized(server)
                    || !live(request.lab()) || !current.lab().equals(request.lab().researchEndpoint())
                    || !current.mother().equals(mother(candidate.mother())) || !available(server, candidate.mother())) continue;
            if (state.refunds.containsKey(source) || !payAndAdvance(candidate, state)) {
                observe(server, request.lab(), "power");
                continue;
            }
            advanced.add(request.job().id());
            state.served.merge(source, 1, Integer::sum);
            observe(server, request.lab(), "active");
        }
        for (var request : requests) if (!advanced.contains(request.job().id())) {
            observe(server, request.lab(), "unavailable");
            if (live(request.lab())) request.advance().run(false, () -> {});
        }
    }
    private static void observe(MinecraftServer server, Hk3ResearchInstituteMachine lab, String value) {
        var observations = runtime(server).observations;
        var old = observations.get(lab.researchServiceId());
        long tick = server.overworld().getGameTime();
        if (old == null || old.tick() != tick || old.state().equals("unavailable") || value.equals("active"))
            observations.put(lab.researchServiceId(), new Observation(tick, value));
    }
    private static boolean payAndAdvance(Candidate candidate, Runtime state) {
        var machine = candidate.mother();
        var ports = Hk3PowerPorts.of(machine.getRecipeLogic());
        BigInteger cost = BigInteger.valueOf(EU_PER_JOB);
        BigInteger demand = cost.multiply(BigInteger.valueOf(
                state.served.getOrDefault(candidate.link().mother().id(), 0) + 1L));
        if (Hk3PortPayment.power(ports).compareTo(demand) < 0) return false;
        var payment = Hk3RefundJournal.open(machine);
        boolean[] advanced = {false};
        try {
            if (!Hk3PortPayment.pay(ports, cost, payment)
                    || !HonkaiWirelessNetwork.reserve(machine.getOwnerUUID(), HW_PER_JOB, payment)) return false;
            candidate.request().advance().run(true, () -> advanced[0] = true);
            return advanced[0];
        } finally {
            if (!payment.finish(advanced[0])) state.refunds.put(candidate.link().mother().id(), payment);
        }
    }
}
