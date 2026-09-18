package com.sirin.hk3gtl;



import com.gregtechceu.gtceu.api.GTCEuAPI;
import com.gregtechceu.gtceu.api.data.chemical.material.event.MaterialEvent;
import com.gregtechceu.gtceu.api.data.chemical.material.event.MaterialRegistryEvent;
import com.gregtechceu.gtceu.api.registry.registrate.GTRegistrate;
import com.sirin.hk3gtl.common.constants.Hk3Constants;
import com.sirin.hk3gtl.common.dialogue.DialogueRegistry;
import com.sirin.hk3gtl.common.dialogue.definition.SirinDialogueDefinitions;
import com.sirin.hk3gtl.common.dialogue.definition.UnluckyEggDialogueDefinition;
import com.sirin.hk3gtl.common.entity.Hk3Entities;
import com.sirin.hk3gtl.common.entity.VoidQueenSirinEntity;
import com.sirin.hk3gtl.common.network.Hk3Network;
import com.sirin.hk3gtl.common.registration.Hk3CreativeTabs;
import com.sirin.hk3gtl.common.item.Hk3Items;
import com.sirin.hk3gtl.common.block.Hk3Blocks;
import com.sirin.hk3gtl.common.material.Hk3Materials;

import net.minecraftforge.event.entity.EntityAttributeCreationEvent;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;

import org.slf4j.Logger;
import com.mojang.logging.LogUtils;

/**
 * 崩坏三-GTL 模组主类 — Forge 模组入口点。
 *
 * <h3>职责</h3>
 * <ul>
 *   <li>构造函数中注册 DeferredRegister（物品/方块/流体/创造页签/实体）</li>
 *   <li>响应 GT 材料事件创建 GTRegistrate 和注册自定义材料</li>
 *   <li>初始化网络通信层</li>
 * </ul>
 *
 * <h3>初始化顺序（严格遵循）</h3>
 * <ol>
 *   <li>构造函数 → DeferredRegister 注册物品/方块/流体/创造页签</li>
 *   <li>{@link #onMaterialRegistry} → 创建 GTRegistrate 和材料注册表</li>
 *   <li>{@link #onMaterialRegister} → 注册 GT 材料（魂钢等）</li>
 *   <li>Mixin 注入 → GTRecipeTypesMixin → Hk3RecipeTypes.init()，GTMachinesMixin → Hk3Machines.init()</li>
 *   <li>{@link Hk3GtAddon#addRecipes} → 注册所有 GT 配方</li>
 *   <li>{@link Hk3GtAddon#removeRecipes} → 移除魂钢自动配方</li>
 * </ol>
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>新增物品/方块 → 在 {@link com.sirin.hk3gtl.common.item.Hk3Items} / {@link com.sirin.hk3gtl.common.block.Hk3Blocks} 中添加</li>
 *   <li>新增材料 → 在 {@link com.sirin.hk3gtl.common.material.Hk3Materials} 中添加</li>
 *   <li>新增实体 → 在 {@link com.sirin.hk3gtl.common.entity.Hk3Entities} 中添加</li>
 * </ul>
 */
@Mod(Hk3Constants.MOD_ID)
public class Hk3Gtl {

    private static final Logger LOGGER = LogUtils.getLogger();

    /** GT 注册器实例，由 {@link #onMaterialRegistry} 创建。供 Hk3Machines 等类访问 */
    public static GTRegistrate REGISTRATE;

    /** 模组构造函数 — 注册 DeferredRegister 和初始化网络 */
    public Hk3Gtl() {
        LOGGER.info("[HK3GTL] 崩坏三-GTL 模组初始化开始...");
        Hk3Network.init();

        // ── 对话系统初始化 ──
        DialogueRegistry.registerBuiltinSpeakers();
        SirinDialogueDefinitions.register();
        UnluckyEggDialogueDefinition.register();

        IEventBus modEventBus = FMLJavaModLoadingContext.get().getModEventBus();
        modEventBus.register(this);

        // ── 普通物品/方块/流体注册（DeferredRegister，顺序无严格要求）──
        Hk3Items.register();
        Hk3Items.ITEMS.register(modEventBus);

        Hk3Blocks.register();
        Hk3Blocks.BLOCKS.register(modEventBus);
        Hk3Blocks.BLOCK_ITEMS.register(modEventBus);
        // 崩坏能仓的 BlockEntity 类型（需求 13 Phase A）。必须挂在 MOD bus 上才会真正注册。
        com.sirin.hk3gtl.common.block.Hk3BlockEntities.BE_TYPES.register(modEventBus);

        Hk3CreativeTabs.register(modEventBus);

        // ── 实体注册 ──
        Hk3Entities.ENTITY_TYPES.register(modEventBus);

        // FTB Quests 集成已恢复：FtbQuestsIntegration（EventBusSubscriber 自动注册）
        // 在服务端启动时同步 assets/hk3gtl/ftbquests/ 下的 6 章任务线 SNBT。

        // ── 双能源配方引擎（审计项 D-01）：登记全部双能源机器的崩坏能消耗档位 ──
        com.sirin.hk3gtl.common.capability.Hk3DualEnergyCosts.init();

        LOGGER.info("[HK3GTL] 崩坏三-GTL 模组初始化完成（等待后续事件）。");
    }

    /**
     * MaterialRegistryEvent — GT 最早的事件回调。
     * 此时必须完成 GTRegistrate 的创建，否则后续 Mixin 中无法注册机器/配方类型。
     */
    @SubscribeEvent
    public void onMaterialRegistry(MaterialRegistryEvent event) {
        LOGGER.info("[HK3GTL] 创建材料注册表...");
        REGISTRATE = GTRegistrate.create(Hk3Constants.MOD_ID);
        GTCEuAPI.materialManager.createRegistry(Hk3Constants.MOD_ID);
        LOGGER.info("[HK3GTL] 材料注册表创建完成。");
    }

    /** MaterialEvent — 注册 GT 自定义材料（魂钢等），在 Mixin 注入之前完成 */
    @SubscribeEvent
    public void onMaterialRegister(MaterialEvent event) {
        LOGGER.info("[HK3GTL] 注册GT材料...");
        Hk3Materials.register();
        LOGGER.info("[HK3GTL] GT材料注册完成。");
    }

    /** 实体属性注册 — 为自定义实体绑定属性（如 Boss 生命值/攻击力） */
    @SubscribeEvent
    public void onEntityAttributeCreation(EntityAttributeCreationEvent event) {
        event.put(Hk3Entities.VOID_QUEEN_SIRIN.get(), VoidQueenSirinEntity.createAttributes().build());
    }
}