package com.sirin.hk3gtl.common.worldbubble;

import com.sirin.hk3gtl.common.recipe.Hk3ResearchProcessPlans;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;
import net.minecraft.resources.ResourceLocation;

import java.util.Set;
import java.util.stream.Collectors;

/** 由批准工艺和实际泡投入产出确定W14生命周期。 */
public final class Hk3W14WorldProcesses {
    public enum Stage { NONE, CREATE, CREATE_STABLE, STABILIZE, TERMINATE, STABILIZE_TERMINATE, DISCARD }
    public record Process(Stage stage, long bubbles) {
        public boolean creates() { return stage == Stage.CREATE || stage == Stage.CREATE_STABLE; }
        public Hk3WorldBubbleLedger.SimulationState inputState() {
            return switch (stage) {
                case STABILIZE, STABILIZE_TERMINATE, DISCARD -> Hk3WorldBubbleLedger.SimulationState.CREATED;
                case TERMINATE -> Hk3WorldBubbleLedger.SimulationState.STABLE;
                default -> null;
            };
        }
        public boolean supports(String step) {
            return switch (stage) {
                case CREATE -> step.equals("CREATE");
                case CREATE_STABLE -> step.equals("CREATE") || step.equals("STABILIZE");
                case STABILIZE -> step.equals("STABILIZE");
                case TERMINATE -> step.equals("TERMINATE");
                case STABILIZE_TERMINATE -> step.equals("STABILIZE") || step.equals("TERMINATE");
                case DISCARD -> step.equals("DISCARD");
                case NONE -> false;
            };
        }
    }
    private static final Set<String> APPROVED = Hk3ResearchProcessPlans.all().stream()
            .filter(plan -> plan.role().equals("W14") && !plan.provisional())
            .map(Hk3ResearchProcessPlans.Plan::id).collect(Collectors.toUnmodifiableSet());
    private static final Process NONE = new Process(Stage.NONE, 0);

    private Hk3W14WorldProcesses() {}

    public static Process of(CompoundTag receipt) {
        var recipe = new ResourceLocation(receipt.getString("Recipe"));
        String path = recipe.getPath();
        String id = path.substring(path.lastIndexOf('/') + 1);
        if (id.equals("wonder_w14_unstable_world_disassembly")) id = "wonder_w14_unstable_world_salvage";
        if (!recipe.getNamespace().equals("hk3gtl") || !APPROVED.contains(id)) return NONE;
        long unstableIn = count(receipt.getCompound("Inputs"), "hk3gtl:unstable_simulated_world_bubble");
        long stableIn = count(receipt.getCompound("Inputs"), "hk3gtl:stable_simulated_world_bubble");
        long unstableOut = count(receipt.getCompound("Outputs"), "hk3gtl:unstable_simulated_world_bubble");
        long stableOut = count(receipt.getCompound("Outputs"), "hk3gtl:stable_simulated_world_bubble");
        if (unstableOut > 0) return new Process(Stage.CREATE, unstableOut);
        if (stableOut > 0) return new Process(unstableIn > 0 ? Stage.STABILIZE : Stage.CREATE_STABLE, stableOut);
        if (stableIn > 0) return new Process(Stage.TERMINATE, stableIn);
        if (unstableIn > 0) return new Process(id.equals("wonder_w14_unstable_world_salvage")
                ? Stage.DISCARD : Stage.STABILIZE_TERMINATE, unstableIn);
        return NONE;
    }

    private static long count(CompoundTag contents, String id) {
        long count = 0;
        for (var raw : contents.getList("Items", Tag.TAG_COMPOUND)) {
            var line = (CompoundTag) raw;
            count += line.getList("Alternatives", Tag.TAG_COMPOUND).stream().map(CompoundTag.class::cast)
                    .filter(stack -> id.equals(stack.getString("id"))).mapToLong(stack -> stack.getLong("ActualCount"))
                    .max().orElse(0);
        }
        return count;
    }
}
