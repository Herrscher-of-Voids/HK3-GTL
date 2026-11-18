package com.sirin.hk3gtl.common.campus;

import com.google.gson.JsonParser;
import com.gtl.enhancedcore.common.world.plot.PlotPresetShare;
import com.gtl.enhancedcore.common.world.plot.PlotSettings;
import com.mojang.datafixers.util.Pair;
import com.mojang.serialization.Codec;
import com.mojang.serialization.DataResult;
import com.mojang.serialization.DynamicOps;

public interface Hk3CampusLayoutVersion {
    int CURRENT = 7;
    String FIELD = "hk3gtl_layout_version";

    int hk3gtl$layoutVersion();
    void hk3gtl$layoutVersion(int version);

    static int get(PlotSettings settings) {
        return ((Hk3CampusLayoutVersion) (Object) settings).hk3gtl$layoutVersion();
    }

    static void set(PlotSettings settings, int version) {
        ((Hk3CampusLayoutVersion) (Object) settings).hk3gtl$layoutVersion(version);
    }

    static Key key(PlotSettings settings) {
        return new Key(settings, get(settings));
    }

    static Codec<PlotSettings> codec(Codec<PlotSettings> original) {
        return new Codec<>() {
            @Override
            public <T> DataResult<T> encode(PlotSettings settings, DynamicOps<T> ops, T prefix) {
                return original.encode(settings, ops, prefix).flatMap(encoded ->
                        ops.mergeToMap(encoded, ops.createString(FIELD), ops.createInt(get(settings))));
            }

            @Override
            public <T> DataResult<Pair<PlotSettings, T>> decode(DynamicOps<T> ops, T input) {
                int version = ops.get(input, FIELD).flatMap(ops::getNumberValue)
                        .result().map(Number::intValue).orElse(1);
                return original.decode(ops, input).map(decoded -> {
                    set(decoded.getFirst(), version);
                    return decoded;
                });
            }
        };
    }

    static String encodeShare(PlotSettings settings) {
        var json = JsonParser.parseString(PlotPresetShare.encode(settings)).getAsJsonObject();
        json.addProperty(FIELD, get(settings));
        return json.toString();
    }

    static PlotSettings decodeShare(String source) {
        return decodeShare(source, false);
    }

    static PlotSettings decodeStoredShare(String source) {
        return decodeShare(source, true);
    }

    private static PlotSettings decodeShare(String source, boolean stored) {
        var json = JsonParser.parseString(source).getAsJsonObject();
        int version = json.has(FIELD) ? json.remove(FIELD).getAsInt() : 1;
        var settings = stored ? PlotPresetShare.decodeStored(json.toString()) : PlotPresetShare.decode(json.toString());
        set(settings, version);
        return settings;
    }

    record Key(PlotSettings settings, int version) {}
}
