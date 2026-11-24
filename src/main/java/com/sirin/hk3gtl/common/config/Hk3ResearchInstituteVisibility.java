package com.sirin.hk3gtl.common.config;

import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.Item;

import java.util.Set;
import java.util.stream.Collectors;

public final class Hk3ResearchInstituteVisibility {
    private static final Set<String> IDS = Set.of(
            "abyss_research_analysis_matrix",
            "s02_matter_reconstruction_institute",
            "s03_quantum_domain_institute",
            "s04_world_maintenance_institute",
            "s05_civilization_cognition_dome");

    private Hk3ResearchInstituteVisibility() {}

    public static boolean isInstitute(Item item) {
        ResourceLocation id = BuiltInRegistries.ITEM.getKey(item);
        return id.getNamespace().equals("hk3gtl") && IDS.contains(id.getPath());
    }

    public static Set<ResourceLocation> ids() {
        return IDS.stream().map(path -> new ResourceLocation("hk3gtl", path)).collect(Collectors.toUnmodifiableSet());
    }
}
