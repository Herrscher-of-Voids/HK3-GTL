package com.sirin.hk3gtl.common.item;



import org.slf4j.Logger;
import com.mojang.logging.LogUtils;

/**
 * 彩蛋类物品注册槽位。
 *
 * <h3>当前状态</h3>
 * Phase 1 占位，仅定义 {@link #register()} 入口。具体物品（非酋证书、空之律者签名照等）
 * 在 Phase 3（研究系统重写）阶段统一实装。
 *
 * <h3>设计</h3>
 * 彩蛋物品由特殊事件触发授予（如累计研究失败 10 次的"非酋证书"），
 * 不参与正式工业链，无配方，无创造标签页。仅作为玩家成就纪念。
 *
 * @see Hk3ResearchFailureTracker 非酋彩蛋的触发逻辑
 */
public final class EasterEggItems {

    private static final Logger LOGGER = LogUtils.getLogger();

    private EasterEggItems() {}

    public static void register() {
        // Phase 3 将在此注册：
        //   - feihq_certificate（非酋证书，10 次失败时授予）
        //   - sirin_autograph（空之律者签名照，触发终局对话后授予）
        LOGGER.debug("[HK3GTL] 彩蛋物品注册槽位已就位（待 Phase 3 实装）。");
    }
}
