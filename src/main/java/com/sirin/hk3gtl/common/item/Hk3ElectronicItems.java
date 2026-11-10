package com.sirin.hk3gtl.common.item;

import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.registries.RegistryObject;

/**
 * 【变更记录 #1】2026-09-25 04:28:00（第 1 次备注 · 内测5修订72）
 * 删除：无。新增：四个平台各十种电子部件及统一查询入口。
 * 修改：电路完整物品与基板、贴片元件、存储和CPU分开注册。
 * 用途：由Hk3Items初始化，为电子制造和系列电路配方提供明确物品引用。
 * 注册期按顺序写入，运行期只读；未知部件立即报错，避免生成空气配方。
 */
/**
 * 【变更记录 #2】2026-09-26 01:58:37（第 2 次备注 · 内测5修订74）
 * 删除：无注册键。新增：每平台介电膜、互连网、外延晶圆、逻辑晶圆、裸片及贴片阵列，共24个半成品。
 * 修改：原40件保持不变；总计64件，均通过现有注册与创造栏入口展示。
 * 用途：把层压、光刻、切割和封装分开，避免普通纳米CPU直接改名成为高阶CPU。
 */
public final class Hk3ElectronicItems {
    public static final List<String> PLATFORMS = List.of(
            "honkai_lattice", "quantum_coherence", "imaginary_topology", "civilization_endurance");
    public static final List<String> PARTS = List.of(
            "circuit_substrate", "printed_circuit_board", "smd_capacitor", "smd_diode",
            "smd_resistor", "smd_transistor", "smd_inductor", "ram_wafer", "ram_chip", "cpu",
            "dielectric_film", "interconnect_mesh", "epitaxial_wafer", "logic_wafer", "logic_die", "smd_array");
    private static final Map<String, RegistryObject<Item>> ITEMS = new LinkedHashMap<>();

    private Hk3ElectronicItems() {}

    public static void register() {
        for (String platform : PLATFORMS) {
            for (String part : PARTS) {
                String id = platform + "_" + part;
                if (ITEMS.containsKey(id)) throw new IllegalStateException("重复电子部件：" + id);
                ITEMS.put(id, Hk3Items.ITEMS.register(id, () -> new Item(new Item.Properties())));
            }
        }
    }

    public static ItemStack stack(String platform, String part, int count) {
        String id = platform + "_" + part;
        RegistryObject<Item> item = ITEMS.get(id);
        if (item == null) throw new IllegalArgumentException("未知电子部件：" + id);
        return new ItemStack(item.get(), count);
    }

    public static Map<String, RegistryObject<Item>> items() {
        return Collections.unmodifiableMap(ITEMS);
    }
}
