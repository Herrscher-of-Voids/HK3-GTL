package com.sirin.hk3gtl.common.multiblock.pattern;



import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.api.pattern.BlockPattern;
import com.sirin.hk3gtl.common.multiblock.hyperion.HyperionPatternData;

/**
 * 休伯利安号旗舰 GT 多方块结构 Pattern 提供器。
 *
 * <p>Pattern 数据由 {@link HyperionPatternData} 提供，后者由
 * {@code tools/hyperion_litematic_gen.js} 从单一 litematic 投影文件生成。</p>
 *
 * <h3>体素坐标（与 litematic 生成代码一致）</h3>
 * <p>投影/游戏内若用「船体局部体素」描述位置，与 Java 图案数组下标 (x,y,z) 的换算为：</p>
 * <pre>
 *   patternX = userX + 264;
 *   patternY = userY + 10;
 *   patternZ = userZ + 169;
 * </pre>
 * <p>例：控制器在玩家坐标 (3,32,29) → 代码 (267,42,198)；舱位 (1,2,4,5, 32, 29) → x=265..269 同行。</p>
 * <p>图案中舱位字符：Ω 物品输入、Ψ EU 输入、Φ 崩坏能输入、Σ 维护（UTF-8 希腊字母，见 HyperionLayerPart20）。</p>
 *
 * <h3>组建方式</h3>
 * 玩家按投影布局搭建飞船，在控制器标记位置放置 {@code hk3gtl:hyperion_flagship}
 * 方块后由 GTCEu Pattern 系统负责成型校验。
 */
public class HyperionPatternProviderImpl {

    HyperionPatternProviderImpl() {}

    public static BlockPattern createPattern(MultiblockMachineDefinition definition) {
        return HyperionPatternData.createPattern(definition);
    }
}
