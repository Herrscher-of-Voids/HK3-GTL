package com.sirin.hk3gtl.common.integration.ae.nexus.management;

import appeng.api.crafting.IPatternDetails;
import appeng.api.networking.IGrid;
import appeng.api.networking.crafting.ICraftingProvider;
import appeng.api.stacks.AEItemKey;
import appeng.api.stacks.AEKey;
import appeng.me.service.CraftingService;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.IdentityHashMap;
import java.util.Iterator;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

public final class Hk3NexusPatternCatalog {
    private record Visit(AEKey key, Iterator<AEKey> edges) {}

    private Set<IPatternDetails> previous = Set.of();
    private Set<AEItemKey> cyclic = Set.of();
    private int patternCount;
    private int busyProviders;
    private int offline;
    private int unpowered;
    private int nodes;

    public void refresh(IGrid grid, List<IPatternDetails> local) {
        var patterns = new LinkedHashSet<>(local);
        var service = (CraftingService) grid.getCraftingService();
        for (AEKey key : service.getCraftables(value -> true)) patterns.addAll(service.getCraftingFor(key));
        Set<ICraftingProvider> providers = Collections.newSetFromMap(new IdentityHashMap<>());
        nodes = offline = unpowered = 0;
        for (var node : grid.getNodes()) {
            nodes++;
            if (!node.isOnline()) offline++;
            if (!node.isPowered()) unpowered++;
            ICraftingProvider provider = node.getService(ICraftingProvider.class);
            if (provider == null) continue;
            patterns.addAll(provider.getAvailablePatterns());
            providers.add(provider);
        }
        if (!patterns.equals(previous)) {
            cyclic = cycles(patterns);
            previous = Set.copyOf(patterns);
        }
        patternCount = patterns.size();
        busyProviders = (int) providers.stream().filter(ICraftingProvider::isBusy).count();
    }

    public int size() { return patternCount; }
    public int nodes() { return nodes; }
    public int offline() { return offline; }
    public int unpowered() { return unpowered; }
    public int busyProviders() { return busyProviders; }
    public int cyclicPatterns() { return cyclic.size(); }

    private static Set<AEItemKey> cycles(Set<IPatternDetails> patterns) {
        Map<AEKey, Set<AEKey>> graph = new HashMap<>();
        Map<AEKey, Set<AEKey>> reverse = new HashMap<>();
        for (IPatternDetails pattern : patterns) {
            for (var output : pattern.getOutputs()) {
                AEKey key = output.what();
                graph.computeIfAbsent(key, ignored -> new HashSet<>());
                reverse.computeIfAbsent(key, ignored -> new HashSet<>());
                for (var input : pattern.getInputs()) for (var option : input.getPossibleInputs()) {
                    graph.computeIfAbsent(option.what(), ignored -> new HashSet<>());
                    reverse.computeIfAbsent(option.what(), ignored -> new HashSet<>()).add(key);
                    graph.get(key).add(option.what());
                }
            }
        }
        var visited = new HashSet<AEKey>();
        var order = new ArrayList<AEKey>();
        for (AEKey key : graph.keySet()) {
            if (!visited.add(key)) continue;
            var stack = new ArrayDeque<Visit>();
            stack.push(new Visit(key, graph.get(key).iterator()));
            while (!stack.isEmpty()) {
                Visit visit = stack.peek();
                if (!visit.edges().hasNext()) { order.add(visit.key()); stack.pop(); continue; }
                AEKey next = visit.edges().next();
                if (visited.add(next)) stack.push(new Visit(next, graph.get(next).iterator()));
            }
        }
        Collections.reverse(order);
        Map<AEKey, Integer> component = new HashMap<>();
        int id = 0;
        for (AEKey key : order) {
            if (component.containsKey(key)) continue;
            var stack = new ArrayDeque<AEKey>();
            stack.push(key);
            component.put(key, id);
            while (!stack.isEmpty()) for (AEKey next : reverse.get(stack.pop())) {
                if (component.putIfAbsent(next, id) == null) stack.push(next);
            }
            id++;
        }
        var result = new HashSet<AEItemKey>();
        for (IPatternDetails pattern : patterns) {
            for (var output : pattern.getOutputs()) for (var input : pattern.getInputs()) {
                for (var option : input.getPossibleInputs()) if (component.get(output.what()).equals(component.get(option.what()))) {
                    result.add(pattern.getDefinition());
                }
            }
        }
        return result;
    }
}
