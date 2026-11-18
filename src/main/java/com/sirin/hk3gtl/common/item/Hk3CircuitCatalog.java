package com.sirin.hk3gtl.common.item;

import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraft.world.item.Item;
import java.util.List;


























public final class Hk3CircuitCatalog {
    public record Entry(String id, int tier, String family, int form, boolean primary) {}
    public static final List<Entry> ENTRIES = List.of(
            new Entry("hbv_processor", 15, "soulium_lattice", 0, true),
            new Entry("hcv_assembly", 16, "soulium_lattice", 1, true),
            new Entry("hrv_computer", 17, "soulium_lattice", 2, true),
            new Entry("hdv_processor_mainframe", 18, "soulium_lattice", 3, true),
            new Entry("rhythmic_coupling_processor", 16, "rhythmic_coupling", 0, false),
            new Entry("rhythmic_coupling_assembly", 17, "rhythmic_coupling", 1, false),
            new Entry("rhythmic_coupling_computer", 18, "rhythmic_coupling", 2, false),
            new Entry("rhythmic_coupling_processor_mainframe", 19, "rhythmic_coupling", 3, false),
            new Entry("honkai_resonance_processor", 17, "honkai_resonance", 0, false),
            new Entry("honkai_resonance_assembly", 18, "honkai_resonance", 1, false),
            new Entry("honkai_resonance_computer", 19, "honkai_resonance", 2, false),
            new Entry("honkai_resonance_processor_mainframe", 20, "honkai_resonance", 3, false),
            new Entry("quantum_bridge_processor", 18, "quantum_bridge", 0, false),
            new Entry("quantum_bridge_assembly", 19, "quantum_bridge", 1, false),
            new Entry("quantum_bridge_computer", 20, "quantum_bridge", 2, false),
            new Entry("quantum_bridge_processor_mainframe", 21, "quantum_bridge", 3, false),
            new Entry("qsv_processor", 19, "quantum_coherence", 0, true),
            new Entry("qcv_assembly", 20, "quantum_coherence", 1, true),
            new Entry("qev_computer", 21, "quantum_coherence", 2, true),
            new Entry("qav_processor_mainframe", 22, "quantum_coherence", 3, true),
            new Entry("quantum_interference_processor", 20, "quantum_interference", 0, false),
            new Entry("quantum_interference_assembly", 21, "quantum_interference", 1, false),
            new Entry("quantum_interference_computer", 22, "quantum_interference", 2, false),
            new Entry("quantum_interference_processor_mainframe", 23, "quantum_interference", 3, false),
            new Entry("entanglement_anchor_processor", 21, "entanglement_anchor", 0, false),
            new Entry("entanglement_anchor_assembly", 22, "entanglement_anchor", 1, false),
            new Entry("entanglement_anchor_computer", 23, "entanglement_anchor", 2, false),
            new Entry("entanglement_anchor_processor_mainframe", 24, "entanglement_anchor", 3, false),
            new Entry("imaginary_anchoring_processor", 22, "imaginary_anchoring", 0, false),
            new Entry("imaginary_anchoring_assembly", 23, "imaginary_anchoring", 1, false),
            new Entry("imaginary_anchoring_computer", 24, "imaginary_anchoring", 2, false),
            new Entry("imaginary_anchoring_processor_mainframe", 25, "imaginary_anchoring", 3, false),
            new Entry("imv_processor", 23, "imaginary_reconstruction", 0, true),
            new Entry("icv_assembly", 24, "imaginary_reconstruction", 1, true),
            new Entry("irv_computer", 25, "imaginary_reconstruction", 2, true),
            new Entry("iwv_processor_mainframe", 26, "imaginary_reconstruction", 3, true),
            new Entry("causal_reconstruction_processor", 24, "causal_reconstruction", 0, false),
            new Entry("causal_reconstruction_assembly", 25, "causal_reconstruction", 1, false),
            new Entry("causal_reconstruction_computer", 26, "causal_reconstruction", 2, false),
            new Entry("causal_reconstruction_processor_mainframe", 27, "causal_reconstruction", 3, false),
            new Entry("world_weaving_processor", 25, "world_weaving", 0, false),
            new Entry("world_weaving_assembly", 26, "world_weaving", 1, false),
            new Entry("world_weaving_computer", 27, "world_weaving", 2, false),
            new Entry("world_weaving_processor_mainframe", 28, "world_weaving", 3, false),
            new Entry("terminal_computation_processor", 26, "terminal_computation", 0, false),
            new Entry("terminal_computation_assembly", 27, "terminal_computation", 1, false),
            new Entry("terminal_computation_computer", 28, "terminal_computation", 2, false),
            new Entry("terminal_computation_processor_mainframe", 29, "terminal_computation", 3, false),
            new Entry("wfv_processor", 27, "civilization_endurance", 0, true),
            new Entry("wsv_assembly", 28, "civilization_endurance", 1, true),
            new Entry("civ_computer", 29, "civilization_endurance", 2, true),
            new Entry("cev_processor_mainframe", 30, "civilization_endurance", 3, true)
    );
    private Hk3CircuitCatalog() {}
    public static TagKey<Item> tag(int tier) {
        return TagKey.create(Registries.ITEM, tagId(tier));
    }
    /** 路径计算不触发Forge注册引导，供数据审计与实际TagKey共同使用。 */
    public static ResourceLocation tagId(int tier) {
        return new ResourceLocation("forge", "circuits/" + Hk3Tiers.voltageKey(tier));
    }
    public static int tier(ResourceLocation id) {
        if (id == null || !id.getNamespace().equals("hk3gtl")) return -1;
        return ENTRIES.stream().filter(e -> e.id().equals(id.getPath())).mapToInt(Entry::tier).findFirst().orElse(-1);
    }
    public static List<String> paths() { return ENTRIES.stream().map(Entry::id).toList(); }
}
