package com.sirin.hk3gtl.common.machine;

/**
 * 跨配方并行计算的能量/输入分配策略。
 *
 * <ul>
 *   <li><b>GREEDY（贪心）</b>：按配方遍历顺序，每个配方尽可能多地分配并行量，
 *       耗光当前库存/能量后再处理下一个。适合玩家对产出顺序无要求的场景，
 *       吞吐量最高。</li>
 *   <li><b>FAIR（公平）</b>：在所有匹配的配方之间等比例分配可用并行量，
 *       保证每种配方都能得到执行机会。适合希望均衡产出的场景。</li>
 * </ul>
 */
public enum AllocationAlgorithm {
    GREEDY,
    FAIR
}
