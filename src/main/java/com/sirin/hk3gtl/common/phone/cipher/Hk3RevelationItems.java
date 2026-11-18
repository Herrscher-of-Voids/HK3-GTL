package com.sirin.hk3gtl.common.phone.cipher;

import appeng.api.crafting.PatternDetailsHelper;
import appeng.blockentity.qnb.QuantumBridgeBlockEntity;
import appeng.items.tools.MemoryCardItem;
import com.gregtechceu.gtceu.common.item.IntCircuitBehaviour;
import java.util.List;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;

final class Hk3RevelationItems {
    private record Entry(String id, String verse, String evidence) {}
    private static final List<Entry> ITEMS = List.of(
            new Entry("hk3gtl:world_bubble_sample",
                    "我不是一片可供落脚的大陆，却让世界有了可被观察的一角。模型与石英岩，曾一同浸过稳定之液。",
                    "去看化学浸洗留下的产物：世界模型载体、石英岩粉与稳定液态崩坏能。别把石英岩误读成石英。"),
            new Entry("hk3gtl:data_precivilization_fragment",
                    "我不是遗迹里的石头，而是旧记录被光重新读出后，落在硅上的一角。四角尚未重聚，钨钢还没有替我合拢往昔。",
                    "遗产记录与硅板经过激光蚀刻分析。找它的产物，别拿重构之后的传承来回答。"),
            new Entry("hk3gtl:phase_transfer_mirror",
                    "我的镜面由纳米陶瓷筑成，感知与发射成对写进其中。你寻找的不是照见面容的那一面。",
                    "制造它的配方同时出现 MAX 传感器与 MAX 发射器。这里只要镜面本体，不需要让材料自行发光或传送。"),
            new Entry("hk3gtl:ancient_legacy",
                    "四角残文在此重聚，研究为它作证，钨钢为它留形。我已经越过碎片，仍未成为意志。",
                    "四份前文明资料片段与数据研究包、钨钢板重构所得的那一件；它还可继续参与远古意志的制造。"),
            new Entry("hk3gtl:prototype_honkai_detector",
                    "我在最早的液态采样中留下名字；无数液态空气经过，我仍留在原处，只让微量异质离开。",
                    "找液态采样配方中的不消耗条件，认准试作型号。无需用它手持扫描地形。"),
            new Entry("ae2:memory_card",
                    "不挪动机器，不搬走成品，我只将它曾经遵循的安排，带往另一台。空白者，尚没有可带走的记忆。",
                    "在 ME 设备上保存过设置的那张卡。它应当同时带着设备配置名和实际设置，清空的卡不会回应。"),
            new Entry("ae2:crafting_pattern",
                    "我没有原料，却记得原料相聚的方法。空白时无从开口，写入一种合成之后，工厂才读得懂我。",
                    "须为能够解码的合成配方，任何有效配方都可。空白样板和处理样板并非此页的答案。"),
            new Entry("ae2:singularity",
                    "众物挤进同一个微小的答案。我尚未因末影与爆裂分成一双，仍是那孤独的一点。",
                    "看 ME 物质聚合器的产物；不要拿已经带着量子关联的那一种来对照。"),
            new Entry("ae2:quantum_entangled_singularity",
                    "同一个奇点遇到末影，经一声爆裂留下两个名字；它们从诞生起便互相记得。带来仍记着同伴的其中一个。",
                    "由奇点和末影珍珠或珍珠粉，经原生爆炸转化而来；须保有原生关联记录，不要求把一对同时交出。"),
            new Entry("gtceu:programmed_circuit",
                    "没有换过身躯，只改一数，工厂便转向别处。此行认的是第 %d 道岔，别把零当作它的回答。",
                    "可配置的电路为配方选择数字。物件与当前配置必须一同符合本页的岔路数。"),
            new Entry("gtceu:data_stick",
                    "我装下数据，却还不到成球的规模。小容量是我的边界，别拿那更大的球体来回答。",
                    "在 GT 的数据载体中，说明标作小容量的那一件。本页不要求写入某项研究。"),
            new Entry("gtceu:data_orb",
                    "当小小的存储不够，数据便有了球形的居所。我要的是大容量的那一个，尚不必在其中藏一整个宇宙。",
                    "在 GT 的数据载体中，说明标作大容量的球形物件。本页不要求指定研究内容。")
    );

    private Hk3RevelationItems() {}

    static int size() { return ITEMS.size(); }
    static String namespace(int entry) { return ITEMS.get(entry).id().split(":")[0]; }
    static String verse(int entry, int circuit) { return ITEMS.get(entry).verse().formatted(circuit); }
    static String evidence(int entry) { return ITEMS.get(entry).evidence(); }

    static boolean accepts(ServerPlayer player, int entry, int circuit, ItemStack stack) {
        if (!BuiltInRegistries.ITEM.getKey(stack.getItem()).toString().equals(ITEMS.get(entry).id())) return false;
        return switch (entry) {
            case 5 -> stack.hasTag() && !stack.getTag().getString("Config").isEmpty()
                    && !((MemoryCardItem) stack.getItem()).getData(stack).isEmpty();
            case 6 -> PatternDetailsHelper.decodePattern(stack, player.level(), false) != null;
            case 8 -> QuantumBridgeBlockEntity.isValidEntangledSingularity(stack);
            case 9 -> IntCircuitBehaviour.getCircuitConfiguration(stack) == circuit;
            default -> true;
        };
    }
}
