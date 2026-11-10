package com.sirin.hk3gtl.mixin.gtceu;

import com.lowdragmc.lowdraglib.client.scene.forge.WorldSceneRendererImpl;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.sirin.hk3gtl.client.preview.Hk3W01PreviewWorld;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.block.BlockRenderDispatcher;
import net.minecraft.core.BlockPos;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.BlockAndTintGetter;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.client.model.data.ModelData;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * 【文件职责】仅为W01稀疏预览启用MC原版相邻面遮挡，保留不完整和透明方块的原模型规则。
 * 【变更记录 #1】2026-10-29 23:12:35（第1次备注 · 本轮高度与预览修复）
 * 删除：无；新增：W01世界身份守卫；修改：该预览renderBatched的checkSides由false改true。
 * 用途：隐藏面不进入VBO，避免百万方块所有内面占用GPU；实体与材料统计不受影响。
 */
@Mixin(value = WorldSceneRendererImpl.class, remap = false)
public abstract class Hk3W01PreviewCullingMixin {
    @Inject(method = "renderBlocksForge", at = @At("HEAD"), cancellable = true)
    private static void hk3gtl$cullHiddenFaces(BlockRenderDispatcher dispatcher, BlockState state, BlockPos pos,
            BlockAndTintGetter world, PoseStack pose, VertexConsumer vertices, RandomSource random,
            RenderType layer, CallbackInfo callback) {
        if (!Hk3W01PreviewWorld.isW01Preview(world)) return;
        var entity = world.getBlockEntity(pos);
        ModelData modelData = dispatcher.getBlockModel(state).getModelData(world, pos, state,
                entity == null ? ModelData.EMPTY : entity.getModelData());
        dispatcher.renderBatched(state, pos, world, pose, vertices, true, random, modelData, layer);
        callback.cancel();
    }
}
