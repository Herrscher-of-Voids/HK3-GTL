package com.sirin.hk3gtl.client.preview;

import com.mojang.blaze3d.pipeline.TextureTarget;
import com.mojang.blaze3d.platform.GlStateManager;
import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.*;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.renderer.GameRenderer;
import org.joml.Matrix4f;
import org.joml.Vector3f;
import org.lwjgl.opengl.GL11;
import org.lwjgl.opengl.GL13;
import org.lwjgl.opengl.GL14;
import org.lwjgl.opengl.GL15;
import org.lwjgl.opengl.GL20;
import org.lwjgl.opengl.GL30;

/** 静止预览复用原分辨率GPU帧，不回读像素或重新绘制方块模型。 */
public final class Hk3PreviewFrameCache implements AutoCloseable {
    private TextureTarget target,composite;
    private final Matrix4f sceneModelView=new Matrix4f(),sceneProjection=new Matrix4f();
    private VertexSorting sceneSorting;
    private boolean captured;
    private int windowWidth,windowHeight;
    private double guiScale;

    public boolean valid(){
        var window=Minecraft.getInstance().getWindow();
        return captured&&windowWidth==window.getWidth()&&windowHeight==window.getHeight()&&guiScale==window.getGuiScale();
    }

    public void invalidate(){captured=false;}

    public void capture(GuiGraphics graphics,int x,int y,int width,int height){
        graphics.flush();
        var mc=Minecraft.getInstance();var window=mc.getWindow();
        guiScale=window.getGuiScale();windowWidth=window.getWidth();windowHeight=window.getHeight();
        var matrix=graphics.pose().last().pose();
        var first=matrix.transformPosition(new Vector3f(x,y,0));
        var last=matrix.transformPosition(new Vector3f(x+width,y+height,0));
        int left=(int)(first.x*guiScale),top=(int)(first.y*guiScale);
        int right=(int)(last.x*guiScale),bottom=(int)(last.y*guiScale);
        captureRegion(left,mc.getMainRenderTarget().height-bottom,right-left,bottom-top,false);
    }

    /** 在LDLib清除场景深度前保存建筑；动画不写入底图。 */
    public void captureScene(){
        var window=Minecraft.getInstance().getWindow();
        guiScale=window.getGuiScale();windowWidth=window.getWidth();windowHeight=window.getHeight();
        sceneModelView.set(RenderSystem.getModelViewMatrix());sceneProjection.set(RenderSystem.getProjectionMatrix());
        sceneSorting=RenderSystem.getVertexSorting();
        int[] viewport=new int[4];GL11.glGetIntegerv(GL11.GL_VIEWPORT,viewport);
        captureRegion(viewport[0],viewport[1],viewport[2],viewport[3],true);
    }

    private void captureRegion(int x,int y,int width,int height,boolean includeDepth){
        int read=GL11.glGetInteger(GL30.GL_READ_FRAMEBUFFER_BINDING),draw=GL11.glGetInteger(GL30.GL_DRAW_FRAMEBUFFER_BINDING);
        int active=GlStateManager._getActiveTexture();
        GlStateManager._activeTexture(GL13.GL_TEXTURE0);
        int texture=GL11.glGetInteger(GL11.GL_TEXTURE_BINDING_2D);
        int[] viewport=new int[4],scissor=new int[4];float[] clear=new float[4];
        GL11.glGetIntegerv(GL11.GL_VIEWPORT,viewport);GL11.glGetIntegerv(GL11.GL_SCISSOR_BOX,scissor);
        GL11.glGetFloatv(GL11.GL_COLOR_CLEAR_VALUE,clear);
        double clearDepth=GL11.glGetDouble(GL11.GL_DEPTH_CLEAR_VALUE);
        boolean clipped=GL11.glIsEnabled(GL11.GL_SCISSOR_TEST),depth=GL11.glIsEnabled(GL11.GL_DEPTH_TEST);
        RenderSystem.disableScissor();
        target=resize(target,width,height);
        GL30.glBindFramebuffer(GL30.GL_READ_FRAMEBUFFER,draw);
        GL30.glBindFramebuffer(GL30.GL_DRAW_FRAMEBUFFER,target.frameBufferId);
        GL30.glBlitFramebuffer(x,y,x+width,y+height,0,0,target.width,target.height,
                GL11.GL_COLOR_BUFFER_BIT|(includeDepth?GL11.GL_DEPTH_BUFFER_BIT:0),GL11.GL_NEAREST);
        GL30.glBindFramebuffer(GL30.GL_READ_FRAMEBUFFER,read);GL30.glBindFramebuffer(GL30.GL_DRAW_FRAMEBUFFER,draw);
        GlStateManager._bindTexture(texture);GlStateManager._activeTexture(active);
        RenderSystem.viewport(viewport[0],viewport[1],viewport[2],viewport[3]);
        RenderSystem.clearColor(clear[0],clear[1],clear[2],clear[3]);
        RenderSystem.clearDepth(clearDepth);
        if(clipped)RenderSystem.enableScissor(scissor[0],scissor[1],scissor[2],scissor[3]);
        if(!depth)RenderSystem.disableDepthTest();
        captured=true;
    }

    private static TextureTarget resize(TextureTarget buffer,int width,int height){
        if(buffer==null)buffer=new TextureTarget(width,height,true,Minecraft.ON_OSX);
        if(buffer.width!=width||buffer.height!=height)buffer.resize(width,height,Minecraft.ON_OSX);
        if(Minecraft.getInstance().getMainRenderTarget().isStencilEnabled()&&!buffer.isStencilEnabled())buffer.enableStencil();
        return buffer;
    }

    public void draw(GuiGraphics graphics,int x,int y,int width,int height){
        draw(target,graphics,x,y,width,height);
    }

    /** 工作帧复用建筑颜色与深度，只重新投影树影；主GUI深度不受影响。 */
    public void drawScene(GuiGraphics graphics,int x,int y,int width,int height,Runnable effects){
        graphics.flush();
        int read=GL11.glGetInteger(GL30.GL_READ_FRAMEBUFFER_BINDING),draw=GL11.glGetInteger(GL30.GL_DRAW_FRAMEBUFFER_BINDING);
        int active=GlStateManager._getActiveTexture();GlStateManager._activeTexture(GL13.GL_TEXTURE0);
        int boundTexture=GL11.glGetInteger(GL11.GL_TEXTURE_BINDING_2D),shaderTexture=RenderSystem.getShaderTexture(0);
        int program=GL11.glGetInteger(GL20.GL_CURRENT_PROGRAM),vao=GL11.glGetInteger(GL30.GL_VERTEX_ARRAY_BINDING);
        int arrayBuffer=GL11.glGetInteger(GL15.GL_ARRAY_BUFFER_BINDING),depthFunc=GL11.glGetInteger(GL11.GL_DEPTH_FUNC);
        int srcRgb=GL11.glGetInteger(GL14.GL_BLEND_SRC_RGB),dstRgb=GL11.glGetInteger(GL14.GL_BLEND_DST_RGB);
        int srcAlpha=GL11.glGetInteger(GL14.GL_BLEND_SRC_ALPHA),dstAlpha=GL11.glGetInteger(GL14.GL_BLEND_DST_ALPHA);
        int equationRgb=GL11.glGetInteger(GL20.GL_BLEND_EQUATION_RGB),equationAlpha=GL11.glGetInteger(GL20.GL_BLEND_EQUATION_ALPHA);
        int[] viewport=new int[4],scissor=new int[4];float[] clear=new float[4];
        GL11.glGetIntegerv(GL11.GL_VIEWPORT,viewport);GL11.glGetIntegerv(GL11.GL_SCISSOR_BOX,scissor);
        GL11.glGetFloatv(GL11.GL_COLOR_CLEAR_VALUE,clear);
        double clearDepth=GL11.glGetDouble(GL11.GL_DEPTH_CLEAR_VALUE);
        boolean clipped=GL11.glIsEnabled(GL11.GL_SCISSOR_TEST),depth=GL11.glIsEnabled(GL11.GL_DEPTH_TEST);
        boolean stencil=GL11.glIsEnabled(GL11.GL_STENCIL_TEST);
        boolean blend=GL11.glIsEnabled(GL11.GL_BLEND),cull=GL11.glIsEnabled(GL11.GL_CULL_FACE);
        boolean depthMask=GL11.glGetBoolean(GL11.GL_DEPTH_WRITEMASK);
        var shader=RenderSystem.getShader();float[] color=RenderSystem.getShaderColor().clone();
        var projection=new Matrix4f(RenderSystem.getProjectionMatrix());var sorting=RenderSystem.getVertexSorting();
        var poses=RenderSystem.getModelViewStack();poses.pushPose();
        try{
            RenderSystem.disableScissor();
            GL11.glDisable(GL11.GL_STENCIL_TEST);
            composite=resize(composite,target.width,target.height);
            GL30.glBindFramebuffer(GL30.GL_READ_FRAMEBUFFER,target.frameBufferId);
            GL30.glBindFramebuffer(GL30.GL_DRAW_FRAMEBUFFER,composite.frameBufferId);
            GL30.glBlitFramebuffer(0,0,target.width,target.height,0,0,composite.width,composite.height,
                    GL11.GL_COLOR_BUFFER_BIT|GL11.GL_DEPTH_BUFFER_BIT,GL11.GL_NEAREST);
            RenderSystem.viewport(0,0,composite.width,composite.height);
            poses.last().pose().set(sceneModelView);RenderSystem.applyModelViewMatrix();
            RenderSystem.setProjectionMatrix(sceneProjection,sceneSorting);
            effects.run();
        }finally{
            poses.popPose();RenderSystem.applyModelViewMatrix();RenderSystem.setProjectionMatrix(projection,sorting);
            GL30.glBindFramebuffer(GL30.GL_READ_FRAMEBUFFER,read);GL30.glBindFramebuffer(GL30.GL_DRAW_FRAMEBUFFER,draw);
            RenderSystem.viewport(viewport[0],viewport[1],viewport[2],viewport[3]);
            RenderSystem.clearColor(clear[0],clear[1],clear[2],clear[3]);
            RenderSystem.clearDepth(clearDepth);
            if(stencil)GL11.glEnable(GL11.GL_STENCIL_TEST);
            if(clipped)RenderSystem.enableScissor(scissor[0],scissor[1],scissor[2],scissor[3]);else RenderSystem.disableScissor();
            RenderSystem.depthMask(depthMask);RenderSystem.depthFunc(depthFunc);
            if(depth)RenderSystem.enableDepthTest();else RenderSystem.disableDepthTest();
            if(blend)RenderSystem.enableBlend();else RenderSystem.disableBlend();
            if(cull)RenderSystem.enableCull();else RenderSystem.disableCull();
            GlStateManager._blendFuncSeparate(srcRgb,dstRgb,srcAlpha,dstAlpha);GL20.glBlendEquationSeparate(equationRgb,equationAlpha);
            RenderSystem.setShader(()->shader);RenderSystem.setShaderTexture(0,shaderTexture);
            RenderSystem.setShaderColor(color[0],color[1],color[2],color[3]);
            GlStateManager._activeTexture(GL13.GL_TEXTURE0);GlStateManager._bindTexture(boundTexture);GlStateManager._activeTexture(active);
            GlStateManager._glBindVertexArray(vao);GlStateManager._glBindBuffer(GL15.GL_ARRAY_BUFFER,arrayBuffer);GlStateManager._glUseProgram(program);
        }
        draw(composite,graphics,x,y,width,height);
    }

    private void draw(TextureTarget source,GuiGraphics graphics,int x,int y,int width,int height){
        graphics.flush();
        var shader=RenderSystem.getShader();int texture=RenderSystem.getShaderTexture(0);
        int active=GlStateManager._getActiveTexture();GlStateManager._activeTexture(GL13.GL_TEXTURE0);
        int boundTexture=GL11.glGetInteger(GL11.GL_TEXTURE_BINDING_2D);
        float[] color=RenderSystem.getShaderColor().clone();
        boolean blend=GL11.glIsEnabled(GL11.GL_BLEND),depth=GL11.glIsEnabled(GL11.GL_DEPTH_TEST),depthMask=GL11.glGetBoolean(GL11.GL_DEPTH_WRITEMASK);
        RenderSystem.disableBlend();RenderSystem.disableDepthTest();RenderSystem.depthMask(false);
        RenderSystem.setShader(GameRenderer::getPositionTexShader);RenderSystem.setShaderTexture(0,source.getColorTextureId());RenderSystem.setShaderColor(1,1,1,1);
        var matrix=graphics.pose().last().pose();var builder=Tesselator.getInstance().getBuilder();
        builder.begin(VertexFormat.Mode.QUADS,DefaultVertexFormat.POSITION_TEX);
        builder.vertex(matrix,x,y,0).uv(0,1).endVertex();
        builder.vertex(matrix,x,y+height,0).uv(0,0).endVertex();
        builder.vertex(matrix,x+width,y+height,0).uv(1,0).endVertex();
        builder.vertex(matrix,x+width,y,0).uv(1,1).endVertex();
        BufferUploader.drawWithShader(builder.end());
        RenderSystem.setShader(()->shader);RenderSystem.setShaderTexture(0,texture);RenderSystem.setShaderColor(color[0],color[1],color[2],color[3]);
        GlStateManager._activeTexture(GL13.GL_TEXTURE0);GlStateManager._bindTexture(boundTexture);GlStateManager._activeTexture(active);
        RenderSystem.depthMask(depthMask);if(depth)RenderSystem.enableDepthTest();if(blend)RenderSystem.enableBlend();
    }

    @Override public void close(){
        captured=false;
        int read=GL11.glGetInteger(GL30.GL_READ_FRAMEBUFFER_BINDING),draw=GL11.glGetInteger(GL30.GL_DRAW_FRAMEBUFFER_BINDING);
        int texture=GL11.glGetInteger(GL11.GL_TEXTURE_BINDING_2D);
        if(target!=null){target.destroyBuffers();target=null;}
        if(composite!=null){composite.destroyBuffers();composite=null;}
        GL30.glBindFramebuffer(GL30.GL_READ_FRAMEBUFFER,read);GL30.glBindFramebuffer(GL30.GL_DRAW_FRAMEBUFFER,draw);
        GlStateManager._bindTexture(texture);
    }
}
