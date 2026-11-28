package com.sirin.hk3gtl.common.research;

import net.minecraft.nbt.CompoundTag;

import java.util.List;
import java.util.UUID;

/** 真实生产回执经独立耗材工况复核后，才形成高阶研究事实。 */
public final class Hk3ResearchEvidenceAnalysis {
    private static final String DOMAINS = "industrial_three_domain_analysis";
    private static final String DIFFERENCE = "industrial_three_domain_difference";
    private static final String COMPUTE = "industrial_bounded_computation";
    private static final String VERIFY = "industrial_bounded_result_verification";
    private static final String LAB_FOUR = "industrial_lab_four_interface_analysis";
    private static final String CROSS_ORDER = "industrial_cross_machine_order_verification";
    private static final List<String> DOMAIN_SOURCES = List.of(
            "liquid_collection", "simulation_created", "imaginary_observation");
    private static final int STEPS = 4096;

    private Hk3ResearchEvidenceAnalysis() {}

    public static boolean ready(Hk3ResearchData data, UUID team, String plan) {
        return switch (plan) {
            case DOMAINS, DIFFERENCE -> DOMAIN_SOURCES.stream().allMatch(fact -> data.hasProcessFact(team, fact))
                    && DOMAIN_SOURCES.stream().map(fact -> data.processFactReceipt(team, fact).getUUID("Batch"))
                    .distinct().count() == DOMAIN_SOURCES.size();
            case COMPUTE -> data.hasProcessFact(team, "liquid_collection");
            case VERIFY -> data.hasProcessFact(team, "bounded_computation_result");
            case LAB_FOUR -> (!com.sirin.hk3gtl.common.config.Hk3ResearchSettings.enabled()
                    || data.hasProcessFact(team, "lab_four_operation")) && data.hasProcessFact(team, "three_domains");
            case CROSS_ORDER -> data.hasProcessFact(team, "cross_machine_handoff") && data.hasProcessFact(team, "manual_dispatch");
            default -> Hk3ContradictionRetest.ready(data, team, plan);
        };
    }

    public static void settled(Hk3ResearchData data, UUID team, String plan, CompoundTag receipt) {
        switch (plan) {
            case DOMAINS, DIFFERENCE -> {
                var sources = new CompoundTag();
                for (String fact : DOMAIN_SOURCES) sources.put(fact, data.processFactReceipt(team, fact));
                receipt.put("Sources", sources);
                if (plan.equals(DIFFERENCE)) {
                    var differences = new CompoundTag();
                    for (int i = 0; i < DOMAIN_SOURCES.size(); i++) {
                        String left = DOMAIN_SOURCES.get(i), right = DOMAIN_SOURCES.get((i + 1) % DOMAIN_SOURCES.size());
                        var a = sources.getCompound(left); var b = sources.getCompound(right);
                        var pair = new CompoundTag();
                        pair.putBoolean("SameFacility", a.getString("Facility").equals(b.getString("Facility")));
                        pair.putBoolean("SameRecipe", a.getString("Recipe").equals(b.getString("Recipe")));
                        pair.putBoolean("SameInputs", a.getCompound("Inputs").equals(b.getCompound("Inputs")));
                        pair.putBoolean("SameOutputs", a.getCompound("Outputs").equals(b.getCompound("Outputs")));
                        differences.put(left + "/" + right, pair);
                    }
                    receipt.put("Differences", differences);
                    data.recordProcessFact(team, "three_domain_difference", receipt);
                } else data.recordProcessFact(team, "three_domains", receipt);
            }
            case COMPUTE -> {
                var source = data.processFactReceipt(team, "liquid_collection");
                int seed = (int) (source.getUUID("Batch").getLeastSignificantBits() & 0xffff);
                long result = 0;
                int step = 0;
                while (step < STEPS) {
                    step++;
                    result += seed + (long) step * step;
                }
                receipt.put("Source", source);
                receipt.putInt("Seed", seed);
                receipt.putInt("Steps", step);
                receipt.putLong("Result", result);
                receipt.putBoolean("Stopped", step == STEPS);
                data.recordProcessFact(team, "bounded_computation_result", receipt);
            }
            case VERIFY -> {
                var computation = data.processFactReceipt(team, "bounded_computation_result");
                int seed = computation.getInt("Seed");
                long expected = (long) seed * STEPS + (long) STEPS * (STEPS + 1) * (2 * STEPS + 1) / 6;
                if (computation.getInt("Steps") != STEPS || !computation.getBoolean("Stopped")
                        || computation.getLong("Result") != expected) return;
                receipt.put("Computation", computation);
                receipt.putLong("Expected", expected);
                receipt.putBoolean("Verified", true);
                data.recordProcessFact(team, "bounded_computation", receipt);
            }
            case LAB_FOUR -> {
                receipt.put("ResearchOperation", data.processFactReceipt(team, "lab_four_operation"));
                receipt.put("Domains", data.processFactReceipt(team, "three_domains"));
                data.recordProcessFact(team, "lab_four_interface", receipt);
            }
            case CROSS_ORDER -> Hk3CrossMachineOrders.verified(data, team, receipt);
            default -> Hk3ContradictionRetest.settled(data, team, plan, receipt);
        }
    }

    public static void researchCompleted(Hk3ResearchData data, UUID team, int lab,
                                         Hk3ResearchWorkQueue.Snapshot job, long tick) {
        if (lab != 4 || Hk3LabExperimentRules.get(job.quote().topic()) != null) return;
        var receipt = new CompoundTag();
        receipt.putUUID("Batch", job.id());
        receipt.putUUID("Team", team);
        receipt.putString("Facility", job.quote().facility());
        receipt.putString("Recipe", "hk3gtl:research_completion/" + job.quote().topic().toLowerCase(java.util.Locale.ROOT));
        receipt.putLong("Tick", tick);
        receipt.putInt("Lab", lab);
        receipt.putLong("Ticks", job.quote().ticks());
        receipt.putLong("EUt", job.quote().eut());
        receipt.put("Inputs", job.quote().paid());
        var output = new CompoundTag(); output.putString("Research", job.quote().topic());
        receipt.put("Outputs", output);
        data.recordProcessFact(team, "lab_four_operation", receipt);
    }
}
