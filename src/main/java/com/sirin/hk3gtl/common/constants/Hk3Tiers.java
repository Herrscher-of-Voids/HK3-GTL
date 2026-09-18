package com.sirin.hk3gtl.common.constants;



/**
 * 扩展电压等级常量的公开入口类。
 *
 * <p>职责：继承 {@link Hk3TiersImpl}，外部统一通过本类引用所有 tier 索引常量和查询方法。</p>
 *
 * <p>实现类：{@link Hk3TiersImpl}（包含全部常量定义和方法实现）</p>
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>新增 tier 常量或方法请在 {@link Hk3TiersImpl} 中添加，本类自动继承</li>
 *   <li>tier 索引范围：原版 0~14 (ULV~MAX)，扩展 15~30 (海渊~终焉)</li>
 *   <li>GTValues.ALL_TIERS / TIER_COUNT 保持原版 0~14 / 15，扩展等级通过 Hk3Tiers/Hk3Values 单独访问</li>
 * </ul>
 *
 * @see Hk3TiersImpl 常量与方法的实际定义
 * @see Hk3Values 电压数值查询
 */
public class Hk3Tiers extends Hk3TiersImpl {
}
