package com.sirin.hk3gtl.common.campus;

import com.google.gson.JsonParser;
import com.gregtechceu.gtceu.api.machine.MachineDefinition;
import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.api.registry.GTRegistries;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import com.sirin.hk3gtl.common.machine.ae.Hk3NexusStructure;
import com.sirin.hk3gtl.common.machine.wonder.Hk3WonderCatalog;
import com.sirin.hk3gtl.common.multiblock.build.Hk3W11BuildPlan;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3ApprovedArchitecture;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3LiquidLineLayout;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3SparsePreviewData;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3StructureStream;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;
import net.minecraft.resources.ResourceLocation;

import java.io.DataInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Set;
import com.sirin.hk3gtl.common.util.Hk3PackedResources;

/** 园区只读取正式结构头与身份，不为预留用地展开百万格蓝图。 */
public final class Hk3CampusCatalog {
    public record Entry(ResourceLocation machineId, String key, int tier,
                        int sizeX, int sizeY, int sizeZ, int controllerX, int controllerY, int controllerZ,
                        Direction front, MachineDefinition definition) {}
    private static List<Entry> entries, legacyEntries;
    private static final Set<String> ADDED_IN_V6 = Set.of("ae_nexus_a1", "w09_candidate", "w11_candidate", "w12_candidate");

    private Hk3CampusCatalog() {}

    public static synchronized List<Entry> entries() {
        if (entries != null) return entries;
        return entries = legacyEntries().stream()
                .filter(entry -> entry.definition() instanceof MultiblockMachineDefinition).toList();
    }

    public static List<Entry> entries(int version) {
        var catalog = version == 1 ? legacyEntries() : entries();
        return version >= 6 ? catalog : catalog.stream().filter(entry -> !ADDED_IN_V6.contains(entry.key())).toList();
    }

    public static synchronized List<Entry> legacyEntries() {
        if (legacyEntries != null) return legacyEntries;
        var result = new ArrayList<Entry>();
        var approved = new HashMap<ResourceLocation, Entry>();
        try {
            for (String key : Hk3ApprovedArchitecture.IDS) {
                try (var stream = Hk3CampusCatalog.class.getResourceAsStream("/data/hk3gtl/compact_architecture/" + key + ".json")) {
                    var json = JsonParser.parseReader(new InputStreamReader(stream, StandardCharsets.UTF_8)).getAsJsonObject();
                    var id = new ResourceLocation(json.get("machine").getAsString());
                    var definition = GTRegistries.MACHINES.get(id);
                    var size = json.getAsJsonArray("size");
                    var control = json.getAsJsonArray("controller");
                    int tier = definition.getTier();
                    if (json.has("target_voltage")) {
                        String voltage = json.get("target_voltage").getAsString();
                        for (int i = 0; i <= 30; i++) if (Hk3Values.getVN(i).equals(voltage)) tier = i;
                    }
                    approved.put(id, new Entry(id, key, tier, size.get(0).getAsInt(), size.get(1).getAsInt(),
                            size.get(2).getAsInt(), control.get(0).getAsInt(), control.get(1).getAsInt(),
                            control.get(2).getAsInt(), Direction.NORTH, definition));
                }
            }
            for (var definition : GTRegistries.MACHINES.values()) {
                var id = definition.getId();
                if (!id.getNamespace().equals("hk3gtl")) continue;
                if (Hk3WonderCatalog.ALL.stream().anyMatch(entry -> entry.controller().equals(id.getPath())
                        && !Hk3WonderCatalog.hasBlueprint(entry.role()))) continue;
                if (approved.containsKey(id)) result.add(approved.get(id));
                else if (id.getPath().equals("research_point_computer"))
                    result.add(new Entry(id, "research_computer", definition.getTier(), 1, 1, 1, 0, 0, 0, Direction.NORTH, definition));
                else if (definition instanceof MultiblockMachineDefinition) result.add(special(definition));
            }
        } catch (IOException failure) {
            throw new IllegalStateException("读取园区正式机器目录失败", failure);
        }
        result.sort(Comparator.comparingInt(Entry::tier).thenComparing(Entry::key));
        return legacyEntries = List.copyOf(result);
    }

    private static Entry special(MachineDefinition definition) throws IOException {
        var id = definition.getId();
        if (id.getPath().equals("ae_nexus")) {
            var template = Hk3NexusStructure.template();
            var size = template.getList("size", Tag.TAG_INT);
            var palette = template.getList("palette", Tag.TAG_COMPOUND);
            for (var raw : template.getList("blocks", Tag.TAG_COMPOUND)) {
                var block = (CompoundTag) raw;
                var state = palette.getCompound(block.getInt("state"));
                if (!state.getString("Name").equals(id.toString())) continue;
                var pos = block.getList("pos", Tag.TAG_INT);
                return new Entry(id, "ae_nexus_a1", definition.getTier(), size.getInt(0), size.getInt(1), size.getInt(2),
                        pos.getInt(0), pos.getInt(1), pos.getInt(2), Direction.byName(state.getCompound("Properties").getString("facing")), definition);
            }
        }
        if (id.getPath().equals("honkai_network_injector")) {
            var kind = Hk3LiquidLineLayout.Kind.INJECTION;
            var layout = Hk3LiquidLineLayout.create(kind);
            for (int x = 0; x < kind.width; x++) for (int y = 0; y < kind.height; y++) for (int z = 0; z < kind.depth; z++)
                if (layout.at(x, y, z) == 'S') return new Entry(id, "network_injector_v2", definition.getTier(),
                        kind.width, kind.height, kind.depth, x, y, z, Direction.NORTH, definition);
        }
        if (id.getPath().equals("w01_origin_stellar_concert_court")) {
            try (var input = new DataInputStream(Hk3PackedResources.open(Hk3CampusCatalog.class.getResourceAsStream("/data/hk3gtl/structures/w01_hall.bin.gz")))) {
                input.readInt(); input.readInt();
                return new Entry(id, "w01", definition.getTier(), input.readInt(), input.readInt(), input.readInt(),
                        input.readInt(), input.readInt(), input.readInt(), Direction.WEST, definition);
            }
        }
        var source = Hk3SparsePreviewData.source(id.toString());
        String key = source.key();
        if (key.equals("w11_candidate")) {
            var h = Hk3W11BuildPlan.header();
            return new Entry(id, key, definition.getTier(), h.width(), h.height(), h.depth(), h.cx(), h.cy(), h.cz(), source.front(), definition);
        }
        try (var input = new Hk3StructureStream(Hk3PackedResources.resource(Hk3CampusCatalog.class, "/data/hk3gtl/structures/" + key + ".bin.gz"))) {
            var h = input.header();
            int tier = key.equals("w03_c9") ? Hk3Tiers.WSV : definition.getTier();
            return new Entry(id, key, tier, h.width(), h.height(), h.depth(), h.cx(), h.cy(), h.cz(), source.front(), definition);
        }
    }
}
