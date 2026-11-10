package com.sirin.hk3gtl;

/**
 * 【文件职责／本轮边界】初始化可选FTB研究团队桥接，保留其他系统注册。
 * 【变更记录 #4】2026-09-29 21:06:40（第 4 次编号备注 · 内测5修订100）
 * 删除：取消已被批准规则替代的研究个人独占、旧数值或在线限定分支；历史备注与其他系统保留。
 * 新增／修改：初始化可选FTB研究团队桥接，保留其他系统注册。
 * 用途：接通实际证据→付款→研究完成与权限检查；不授予缺真实证据的课题。
 * 边界：编译和账本测试不代表游戏验收；S02至S05正式结构及未接线课题仍未完成。
 * 追溯：logs/research-mainline-r100；R100_FINAL_RECORD。
 */


/**
 * 【文件职责】
 * - 维护 Hk3Gtl 的核心功能实现。
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
/**
 * 【变更记录 #1】2026-09-29 17:51:46（内测5修订93）
 * - 删除：旧正文活动引用被审核原文替代；保留历史资源和存档。
 * - 新增／修改：新增审核原文对白注册，先注册共同人物与段落，再注册正式终审。
 * - 用途：接通审核正文；其他系统触发及归属不据此宣称完成。
 */
/**
 * 【变更记录 #2】2026-09-29 18:22:20（内测5修订94）
 * - 删除：无；保留历史代码与数据入口。
 * - 新增：五方贸易服务端结算支持及失败校验。
 * - 修改：在审核正文注册后追加实际贸易往来对白定义，保留管理员只读预览。
 * - 用途：执行一次性交齐与交付前无损取消；报价未审核不开放，不授予研究完成。
 */
/** 【变更记录 #3】2026-09-29 19:50:20（内测5修订99）：删除：贸易对白注册；新增：无；修改：按负责人决定撤下五方贸易；用途：保留其他系统独立运行。 */
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
/**
 * 【变更记录 #5】2026-09-30 16:19:31（内测5修订110）
 * 删除：被新版通知读取流程替代的旧分支，历史备注保留。
 * 新增／修改：注册客户端通知配置，位置/声音等选项本地保存，不进入服务器业务权限。
 * 用途：通知与业务结果分离，服务端授权和个人持久化；不改结构、贴图和贸易。
 */
/** 【变更记录 #6】2026-10-01 04:12:10（修订128）：删除：旧固定上限或被替代的分支；新增/修改：注册存档级彩蛋日历时区，默认Asia/Hong_Kong并校验有效时区；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #7】2026-10-01 19:03:37（修订141）：删除：无；新增／修改：注册二审实体基础属性，避免生成时缺少属性；用途：琪亚娜二审形象和终审统一称谓，保留其他会话行为。 */
/** 【变更记录 #8】2026-10-17 21:25:49（第8次备注 · 修订166）：删除无；新增独立高度COMMON配置注册；修改在世界创建前提供服务器合同选择，不使用客户端配置改世界；用途为新世界全维度高度提供同一配置入口，已有世界不自动启用。 */
public class Hk3Gtl {

    private static final Logger LOGGER = LogUtils.getLogger();

    /** GT 注册器实例，由 {@link #onMaterialRegistry} 创建。供 Hk3Machines 等类访问 */
    public static GTRegistrate REGISTRATE;

    /** 模组构造函数 — 注册 DeferredRegister 和初始化网络 */
    public Hk3Gtl() {
        LOGGER.info("[HK3GTL] 崩坏三-GTL 模组初始化开始...");
        Hk3Network.init();
        com.sirin.hk3gtl.common.dimension.height.Hk3HeightConfig.register();
        net.minecraftforge.fml.ModLoadingContext.get().registerConfig(net.minecraftforge.fml.config.ModConfig.Type.CLIENT,
                com.sirin.hk3gtl.common.farview.Hk3FarViewConfig.SPEC,"hk3gtl-farview-client.toml");
        // 修订100 · 2026-09-29：注册团队研究归属变更监听。
        com.sirin.hk3gtl.common.research.Hk3ResearchTeams.init();

        // ── 对话系统初始化 ──
        DialogueRegistry.registerBuiltinSpeakers();
        com.sirin.hk3gtl.common.dialogue.definition.Hk3ApprovedDialogues.register();
        SirinDialogueDefinitions.register();
        com.sirin.hk3gtl.common.dialogue.definition.Hk3IfArchiveDialogue.register();
        UnluckyEggDialogueDefinition.register();

        net.minecraftforge.fml.ModLoadingContext.get().registerConfig(net.minecraftforge.fml.config.ModConfig.Type.CLIENT,
                com.sirin.hk3gtl.common.phone.Hk3PhoneConfig.SPEC, "hk3gtl-notifications-client.toml");
        net.minecraftforge.fml.ModLoadingContext.get().registerConfig(net.minecraftforge.fml.config.ModConfig.Type.SERVER,
                com.sirin.hk3gtl.common.easter.Hk3EggCalendar.SPEC,"hk3gtl-easter-server.toml");
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
        event.put(Hk3Entities.KIANA_REVIEW.get(), net.minecraft.world.entity.LivingEntity.createLivingAttributes().build());
        event.put(Hk3Entities.VOID_QUEEN_SIRIN.get(), VoidQueenSirinEntity.createAttributes().build());
    }
}
