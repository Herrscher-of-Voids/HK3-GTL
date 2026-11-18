package com.sirin.hk3gtl.common.machine.wonder;

import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import java.util.List;

public final class Hk3WonderCatalog {
    public record Entry(String role, String controller, String title, String research, String product, int runtimeTier) {}
    public static final List<Entry> ALL = List.of(
            new Entry("W01", "w01_origin_stellar_concert_court", "始源·群星协奏庭", "RN-HCCO", "civilization_cooperation_archive", Hk3Tiers.WSV),
            new Entry("W02", "omnia_autonomous_industrial_matrix", "理之律者·万象·自律工业矩阵", "RN-AIM", "autonomous_fabrication_matrix", Hk3Tiers.WSV),
            new Entry("W03", "void_anchor_ring", "空之律者·穹界·虚数锚定环", "RN-IAR", "imaginary_anchor_matrix", Hk3Tiers.WSV),
            new Entry("W04", "w04_thunder_superconducting_axis", "雷之律者·鸣霆·超导电磁天枢", "RN-SEM", "superconducting_polarization_matrix", Hk3Tiers.WSV),
            new Entry("W05", "w05_ideal_fluid_circulation_array", "风之律者·长风·理想流体环流阵", "RN-IFF", "ideal_flow_exchange_matrix", Hk3Tiers.WSV),
            new Entry("W06", "w06_cryogenic_condensed_factory", "冰之律者·永霜·极低温凝态工厂", "RN-CCF", "cryogenic_condensation_matrix", Hk3Tiers.WSV),
            new Entry("W07", "w07_matter_regeneration_ark", "死之律者·生息·物质再生方舟", "RN-MRA", "matter_regeneration_matrix", Hk3Tiers.CIV),
            new Entry("W08", "w08_stellar_casting_furnace", "炎之律者·劫焰·恒星熔铸炉", "RN-SFF", "stellar_forging_matrix", Hk3Tiers.CIV),
            new Entry("W09", "w09_civilization_consensus_matrix", "识之律者·万象·文明共识矩阵", "RN-CKV", "civilization_consensus_archive", Hk3Tiers.CEV),
            new Entry("W10", "w10_gravitational_singularity_forge", "岩之律者·坠星·引力奇点铸造井", "RN-GSF", "gravitational_singularity_matrix", Hk3Tiers.CIV),
            new Entry("W11", "w11_distributed_industrial_command", "支配之律者·千律·分布式工业统御阵", "RN-DIO", "distributed_industrial_contract", Hk3Tiers.CEV),
            new Entry("W12", "w12_global_energy_constraint_wall", "约束之律者·戒律·全域能量约束壁", "RN-ECB", "global_energy_constraint_matrix", Hk3Tiers.CIV),
            new Entry("W13", "w13_self_computing_research_mother", "侵蚀之律者·蚀界·自演算研究母机", "RN-ASR", "bounded_research_model", Hk3Tiers.CEV),
            new Entry("W14", "w14_world_bubble_recurrence_engine", "终焉之律者·终序·世界泡轮回引擎", "RN-WCE", "civilization_cycle_model", Hk3Tiers.CEV),
            new Entry("W15", "w15_tree_sea_audience_throne", "■■■·凌霄·树海朝觐圣座", "RN-TAA", "tree_sea_audience_credential", Hk3Tiers.CEV));
    private Hk3WonderCatalog() {}
    public static Entry get(String role) { return ALL.get(Integer.parseInt(role.substring(1)) - 1); }
    public static boolean hasBlueprint(String role) { return Integer.parseInt(role.substring(1)) <= 15; }
}
