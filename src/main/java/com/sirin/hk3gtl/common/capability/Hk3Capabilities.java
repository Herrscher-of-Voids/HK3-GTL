package com.sirin.hk3gtl.common.capability;


/**
 * 【文件职责】
 * - 维护 Hk3Capabilities 的核心功能实现。
 * - 关键调用链：由上层系统入口调用 -> 本文件核心方法 -> 下游模块。
 *
 * 【变更记录】2026-05-19
 * - 删除：
 *   1) 初始归档备注：自 v0.3 基线梳理，无本次 diff。
 * - 新增：
 *   1) 新增统一变更备注块，便于后续维护与审计追踪。
 * - 修改：
 *   1) 未改动业务逻辑，仅补充文件级职责与维护注释模板。
 * - 用途：
 *   1) 帮助维护者快速理解文件职责、变更背景与风险点。
 *
 * 【段内说明】
 * - 复杂方法补充“干什么 / 边界 / 线程侧”精简中文注释。
 */
import net.minecraftforge.common.capabilities.Capability;
import net.minecraftforge.common.capabilities.CapabilityManager;
import net.minecraftforge.common.capabilities.CapabilityToken;
import net.minecraftforge.common.capabilities.RegisterCapabilitiesEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import com.sirin.hk3gtl.common.constants.Hk3Constants;

/**
 * 本模组自定义 Forge Capability 注册中心。
 *
 * <h3>职责</h3>
 * 集中定义并注册所有本模组引入的 Capability，当前只有 {@link #HONKAI_ENERGY}。
 * Capability 本身需要在 Forge 的 {@code RegisterCapabilitiesEvent} 中调用 {@code register} 登记，
 * 否则 {@link Capability#isRegistered()} 返回 false，{@link #HONKAI_ENERGY} 就无法被其他 mod 查询。
 *
 * <h3>注册时序</h3>
 * <ul>
 *   <li>{@link Mod.EventBusSubscriber} 的 MOD bus 在 {@code Hk3Gtl} 构造后自动触发</li>
 *   <li>{@link #onRegisterCapabilities} 收到事件后将 {@code IHonkaiEnergyContainer} 登记到 Forge</li>
 *   <li>注册完毕后其他代码可以 {@code stack.getCapability(Hk3Capabilities.HONKAI_ENERGY)} 获取</li>
 * </ul>
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>新增 Capability：仿照 {@link #HONKAI_ENERGY} 添加 {@code CapabilityToken} 字段 + 在
 *       {@link #onRegisterCapabilities} 中追加 {@code event.register(xxx.class)}</li>
 *   <li>不要在编译期引用具体实现类：仅通过接口 + {@code CapabilityToken} 锁 Capability 对象</li>
 *   <li>bus = MOD：Forge Capability 注册强制走 MOD bus，不是 FORGE bus</li>
 * </ul>
 */
@Mod.EventBusSubscriber(modid = Hk3Constants.MOD_ID, bus = Mod.EventBusSubscriber.Bus.MOD)
public final class Hk3Capabilities {

    private Hk3Capabilities() {}

    /**
     * 崩坏能 Capability。获取方式：
     * <pre>
     *   blockEntity.getCapability(Hk3Capabilities.HONKAI_ENERGY, direction)
     *       .ifPresent(storage -> storage.insert(100, false));
     * </pre>
     */
    public static final Capability<IHonkaiEnergyContainer> HONKAI_ENERGY =
            CapabilityManager.get(new CapabilityToken<>() {});

    @SubscribeEvent
    public static void onRegisterCapabilities(RegisterCapabilitiesEvent event) {
        event.register(IHonkaiEnergyContainer.class);
    }
}
