package com.sirin.hk3gtl.client.review;

import com.mojang.blaze3d.platform.GlStateManager;
import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.DefaultVertexFormat;
import com.mojang.blaze3d.vertex.VertexFormat;
import net.minecraft.client.renderer.RenderStateShard;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.ShaderInstance;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RegisterShadersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid="hk3gtl",value=Dist.CLIENT,bus=Mod.EventBusSubscriber.Bus.MOD)
public final class Hk3CocoonRenderTypes extends RenderStateShard {
    private static ShaderInstance shader;
    private static boolean additive;
    public static final RenderType LIGHT=light("hk3_cocoon_light",false);
    public static final RenderType GLOW=light("hk3_cocoon_glow",true);
    public static final RenderType SOFT=RenderType.entityTranslucentEmissive(new ResourceLocation("hk3gtl","textures/effect/cocoon_soft.png"));
    public static final RenderType PIXEL=RenderType.entityTranslucentEmissive(new ResourceLocation("hk3gtl","textures/effect/cocoon_white.png"));
    private Hk3CocoonRenderTypes(){super("hk3_cocoon",()->{},()->{});}
    private static RenderType light(String name,boolean glow){
        return RenderType.create(name,DefaultVertexFormat.NEW_ENTITY,VertexFormat.Mode.QUADS,262144,false,false,
                RenderType.CompositeState.builder()
                        .setShaderState(new ShaderStateShard(()->{additive=glow;return shader;}))
                        .setTransparencyState(glow?LIGHTNING_TRANSPARENCY:NO_TRANSPARENCY)
                        .setCullState(NO_CULL)
                        .setWriteMaskState(glow?COLOR_WRITE:COLOR_DEPTH_WRITE)
                        .createCompositeState(false));
    }
    public static void time(float seconds){shader.safeGetUniform("SceneTime").set(seconds);}
    @SubscribeEvent public static void register(RegisterShadersEvent event)throws java.io.IOException {
        event.registerShader(new ShaderInstance(event.getResourceProvider(),new ResourceLocation("hk3gtl","cocoon_light"),DefaultVertexFormat.NEW_ENTITY){
            @Override public void apply(){
                super.apply();
                // 同一着色器共用两种混合，避免JSON混合状态覆盖当前批次。
                if(additive){
                    RenderSystem.enableBlend();
                    RenderSystem.blendFunc(GlStateManager.SourceFactor.SRC_ALPHA,GlStateManager.DestFactor.ONE);
                }else RenderSystem.disableBlend();
            }
        },value->shader=value);
    }
}
