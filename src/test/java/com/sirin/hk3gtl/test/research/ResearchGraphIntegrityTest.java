package com.sirin.hk3gtl.test.research;

import com.sirin.hk3gtl.common.research.Hk3ResearchNode;
import com.sirin.hk3gtl.common.research.Hk3ResearchNodes;

import java.util.ArrayDeque;
import java.util.Deque;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

/**
 * 研究系统图完整性回归测试（纯逻辑，不依赖 Minecraft 运行时）。
 *
 * <p>背景：历史上多次出现"某研究前置事件=机器建成，而该机器配方门槛又指向该研究/其后继"
 * 造成的确定性死锁（反应堆、虚数入口、量子入口、R-QT-005/009 自锁）。本测试把
 * <b>可纯静态验证的部分</b>固化为回归用例，防止前置图回退。</p>
 *
 * <h3>覆盖</h3>
 * <ul>
 *   <li>R-101：前置依赖图无环（DFS 检测循环依赖）</li>
 *   <li>R-102：所有 prerequisites 引用的节点均已注册</li>
 *   <li>R-103：节点不得把自己列为前置</li>
 *   <li>R-104：R-QT-005 自锁修复固化（requiredEvent 不再是自身机器事件 E-FB-037）</li>
 *   <li>R-105：R-QT-009 自锁修复固化（requiredEvent 不再是自身机器事件 E-FB-043）</li>
 * </ul>
 *
 * <p>运行方式：通过 IDE 直接运行 main()，或纳入 test sourceset。</p>
 */
public class ResearchGraphIntegrityTest {

    /** R-101: 前置依赖图必须无环，否则任何环上节点都永远无法解锁 */
    public static boolean testR101_noPrereqCycle() {
        try {
            Map<String, List<String>> graph = Hk3ResearchNodes.allNodes().stream()
                    .collect(Collectors.toMap(Hk3ResearchNode::id, Hk3ResearchNode::prerequisites));

            Set<String> visited = new HashSet<>();
            for (String start : graph.keySet()) {
                if (visited.contains(start)) continue;
                Set<String> inStack = new HashSet<>();
                Deque<String> stack = new ArrayDeque<>();
                stack.push(start);
                // 迭代式 DFS，路径回溯用 inStack 判环
                Deque<java.util.Iterator<String>> iters = new ArrayDeque<>();
                Deque<String> path = new ArrayDeque<>();
                iters.push(graph.getOrDefault(start, List.of()).iterator());
                path.push(start);
                inStack.add(start);
                while (!path.isEmpty()) {
                    java.util.Iterator<String> it = iters.peek();
                    if (it.hasNext()) {
                        String next = it.next();
                        if (inStack.contains(next)) {
                            System.err.println("[R-101 FAIL] 发现前置循环: " + next + " 已在路径 " + path);
                            return false;
                        }
                        if (!graph.containsKey(next)) continue; // 存在性由 R-102 负责
                        inStack.add(next);
                        path.push(next);
                        iters.push(graph.get(next).iterator());
                    } else {
                        iters.pop();
                        inStack.remove(path.pop());
                        visited.add(start);
                    }
                }
            }
            return true;
        } catch (Throwable t) {
            System.err.println("[R-101 FAIL] " + t.getClass().getSimpleName() + ": " + t.getMessage());
            t.printStackTrace(System.err);
            return false;
        }
    }

    /** R-102: 所有前置引用的节点 ID 必须已注册，否则该前置永远无法满足 */
    public static boolean testR102_allPrereqsExist() {
        try {
            Set<String> ids = Hk3ResearchNodes.allNodes().stream()
                    .map(Hk3ResearchNode::id).collect(Collectors.toSet());
            for (Hk3ResearchNode node : Hk3ResearchNodes.allNodes()) {
                for (String prereq : node.prerequisites()) {
                    if (!ids.contains(prereq)) {
                        System.err.println("[R-102 FAIL] " + node.id() + " 的前置 " + prereq + " 未注册");
                        return false;
                    }
                }
            }
            return true;
        } catch (Throwable t) {
            System.err.println("[R-102 FAIL] " + t.getMessage());
            return false;
        }
    }

    /** R-103: 节点不得把自身列为前置（自环特例） */
    public static boolean testR103_noSelfPrereq() {
        try {
            for (Hk3ResearchNode node : Hk3ResearchNodes.allNodes()) {
                if (node.prerequisites().contains(node.id())) {
                    System.err.println("[R-103 FAIL] " + node.id() + " 把自己列为前置");
                    return false;
                }
            }
            return true;
        } catch (Throwable t) {
            System.err.println("[R-103 FAIL] " + t.getMessage());
            return false;
        }
    }

    /** R-104: R-QT-005 自锁修复固化——不得再以自身机器事件 E-FB-037 作为前置事件 */
    public static boolean testR104_qt005NotSelfLocked() {
        return assertRequiredEventNot("R-QT-005", "E-FB-037");
    }

    /** R-105: R-QT-009 自锁修复固化——不得再以自身机器事件 E-FB-043 作为前置事件 */
    public static boolean testR105_qt009NotSelfLocked() {
        return assertRequiredEventNot("R-QT-009", "E-FB-043");
    }

    private static boolean assertRequiredEventNot(String nodeId, String forbiddenEvent) {
        try {
            Hk3ResearchNode node = Hk3ResearchNodes.get(nodeId);
            if (node == null) {
                System.err.println("[FAIL] 节点不存在: " + nodeId);
                return false;
            }
            if (forbiddenEvent.equals(node.requiredEventId())) {
                System.err.println("[FAIL] " + nodeId + " 仍以 " + forbiddenEvent + " 为前置事件（自锁未修复）");
                return false;
            }
            return true;
        } catch (Throwable t) {
            System.err.println("[FAIL] " + t.getMessage());
            return false;
        }
    }

    // ── 运行器 ────────────────────────────────────────────────────────────

    public static void main(String[] args) {
        int passed = 0, failed = 0;
        int[] r;
        r = tally(run("R-101", ResearchGraphIntegrityTest::testR101_noPrereqCycle));   passed += r[0]; failed += r[1];
        r = tally(run("R-102", ResearchGraphIntegrityTest::testR102_allPrereqsExist)); passed += r[0]; failed += r[1];
        r = tally(run("R-103", ResearchGraphIntegrityTest::testR103_noSelfPrereq));    passed += r[0]; failed += r[1];
        r = tally(run("R-104", ResearchGraphIntegrityTest::testR104_qt005NotSelfLocked)); passed += r[0]; failed += r[1];
        r = tally(run("R-105", ResearchGraphIntegrityTest::testR105_qt009NotSelfLocked)); passed += r[0]; failed += r[1];

        System.out.println("\n=============================================");
        System.out.println("  HK3GTL Research Graph Integrity Test Results");
        System.out.println("=============================================");
        System.out.println("  Passed: " + passed + " / " + (passed + failed));
        System.out.println("  Failed: " + failed);
        System.out.println("=============================================");
        System.exit(failed > 0 ? 1 : 0);
    }

    private static int[] tally(boolean ok) {
        return ok ? new int[]{1, 0} : new int[]{0, 1};
    }

    @FunctionalInterface
    interface TestCase { boolean run() throws Throwable; }

    private static boolean run(String id, TestCase test) {
        try {
            boolean ok = test.run();
            System.out.println((ok ? "[PASS] " : "[FAIL] ") + id);
            return ok;
        } catch (Throwable t) {
            System.out.println("[FAIL] " + id + " -> " + t.getMessage());
            return false;
        }
    }
}
