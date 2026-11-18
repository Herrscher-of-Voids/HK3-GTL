package com.sirin.hk3gtl.common.narrative.story;

import com.google.gson.Gson;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.List;

public final class Hk3StoryCatalog {
    public record Memory(String fact, String reply) {}
    public record Choice(String id, String label, String reply, boolean defer, List<Memory> memories) {}
    public record Node(String id, String title, String speaker, List<String> requires,
                       String route, String body, List<Choice> choices, String source,
                       String window, List<String> onDelivery, List<String> onComplete) {}
    private record Catalog(List<Node> nodes) {}
    public static final List<Node> NODES = load();

    private Hk3StoryCatalog() {}

    private static List<Node> load() {
        try (var stream = Hk3StoryCatalog.class.getResourceAsStream("/assets/hk3gtl/narrative/story.json")) {
            return List.copyOf(new Gson().fromJson(new InputStreamReader(stream, StandardCharsets.UTF_8), Catalog.class).nodes());
        } catch (IOException exception) {
            throw new IllegalStateException("无法读取文明剧情", exception);
        }
    }

    public static Node node(String id) {
        return NODES.stream().filter(node -> node.id().equals(id)).findFirst().orElse(null);
    }
}
