package com.sirin.hk3gtl.mixin.client;

import com.mojang.blaze3d.vertex.*;
import net.minecraft.client.renderer.block.ModelBlockRenderer;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.resources.model.BakedModel;
import net.minecraft.core.BlockPos;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.BlockAndTintGetter;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.client.model.data.ModelData;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(ModelBlockRenderer.class)
public abstract class Hk3W03BlockRenderMixin {
    @Inject(method="tesselateBlock(Lnet/minecraft/world/level/BlockAndTintGetter;Lnet/minecraft/client/resources/model/BakedModel;Lnet/minecraft/world/level/block/state/BlockState;Lnet/minecraft/core/BlockPos;Lcom/mojang/blaze3d/vertex/PoseStack;Lcom/mojang/blaze3d/vertex/VertexConsumer;ZLnet/minecraft/util/RandomSource;JILnet/minecraftforge/client/model/data/ModelData;Lnet/minecraft/client/renderer/RenderType;)V",at=@At("HEAD"),cancellable=true,remap=false)
    private void hk3gtl$c9(BlockAndTintGetter world,BakedModel model,BlockState state,BlockPos pos,PoseStack pose,VertexConsumer vertices,boolean cull,RandomSource random,long seed,int overlay,ModelData data,RenderType layer,CallbackInfo ci){
        if(com.sirin.hk3gtl.client.wonder.Hk3W03FieldScenes.hidden(pos,state)
                ||com.sirin.hk3gtl.client.wonder.Hk3W08FieldScenes.hidden(pos,state)
                ||com.sirin.hk3gtl.client.wonder.Hk3W10FieldScenes.hidden(pos,state)
                ||com.sirin.hk3gtl.client.wonder.Hk3W12FieldScenes.hidden(pos,state)
                ||com.sirin.hk3gtl.client.wonder.Hk3W11FieldScenes.hidden(pos,state)
                ||com.sirin.hk3gtl.client.wonder.Hk3W13FieldScenes.hidden(pos,state)
                ||com.sirin.hk3gtl.client.wonder.Hk3WonderFxScenes.hidden(pos,state))ci.cancel();
    }
}
