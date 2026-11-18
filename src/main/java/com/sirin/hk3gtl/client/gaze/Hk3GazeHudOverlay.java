package com.sirin.hk3gtl.client.gaze;

import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.network.chat.Component;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import net.minecraftforge.client.gui.overlay.IGuiOverlay;

/**
 * 终焉注视度 HUD：屏幕左上角常驻，显示注视度数值、进度条与高注视变色预警。
 *
 * <h3>展示规则</h3>
 * <ul>
 *   <li>未同步（未进世界/未收到包）或注视度为 0 时不渲染，避免打扰前期玩家。</li>
 *   <li>进度条颜色按占比分级：低=青、中=黄、高=橙、临界=红闪，呼应“越强越被审视”的压迫感。</li>
 *   <li>缓冲单元激活时追加缓冲提示行。</li>
 * </ul>
 *
 * <p>纯读取 {@link Hk3ClientGazeState} 客户端缓存，不做任何计算，渲染线程安全。</p>
 */
@OnlyIn(Dist.CLIENT)
public final class Hk3GazeHudOverlay implements IGuiOverlay {

    public static final Hk3GazeHudOverlay INSTANCE = new Hk3GazeHudOverlay();

    private Hk3GazeHudOverlay() {}
    private static Component label(){return Component.translatable("hk3gtl.hud.gaze.label",Hk3ClientGazeState.getGaze(),Hk3ClientGazeState.getGazeMax());}
    private static Component team(){return Component.translatable("hk3gtl.hud.gaze.effective_team",Hk3ClientGazeState.getEffectiveGaze(),Hk3ClientGazeState.getTeamGaze());}
    private static int naturalWidth(){
        var font=Minecraft.getInstance().font;
        return Math.max(140,Math.max(font.width(label()),Math.max(font.width(team()),font.width(Component.translatable("hk3gtl.hud.gaze.buffer"))))+12);
    }
    public static com.sirin.hk3gtl.common.phone.Hk3GazeHudLayout.Box placement(int sw,int sh){
        return com.sirin.hk3gtl.common.phone.Hk3GazeHudLayout.place(sw,sh,naturalWidth(),55,
            com.sirin.hk3gtl.common.phone.Hk3PhoneConfig.GAZE_SCALE.get(),
            com.sirin.hk3gtl.common.phone.Hk3PhoneConfig.GAZE_X.get(),com.sirin.hk3gtl.common.phone.Hk3PhoneConfig.GAZE_Y.get());
    }
    public static void panel(GuiGraphics graphics){
        var font=Minecraft.getInstance().font;int w=naturalWidth();float ratio=Hk3ClientGazeState.getRatio();
        graphics.fill(0,0,w,55,0xD0121925);
        graphics.drawString(font,label(),6,6,colorForRatio(ratio),false);
        graphics.fill(6,18,w-6,24,0xFF293343);
        graphics.fill(6,18,6+Math.round((w-12)*ratio),24,colorForRatio(ratio));
        graphics.drawString(font,team(),6,28,0xFFCCCCCC,false);
        if(Hk3ClientGazeState.isBufferActive())graphics.drawString(font,Component.translatable("hk3gtl.hud.gaze.buffer"),6,40,0xFF55FFFF,false);
    }
    @Override public void render(net.minecraftforge.client.gui.overlay.ForgeGui gui,GuiGraphics graphics,float partialTick,int screenWidth,int screenHeight){
        var mc=Minecraft.getInstance();
        if(mc.screen!=null||mc.options.hideGui||mc.options.renderDebug||!Hk3ClientGazeState.isSynced()
                ||(Hk3ClientGazeState.getGaze()<=0&&Hk3ClientGazeState.getTeamGaze()<=0))return;
        var p=placement(screenWidth,screenHeight);
        graphics.pose().pushPose();graphics.pose().translate(p.x(),p.y(),0);graphics.pose().scale((float)p.scale(),(float)p.scale(),1);
        panel(graphics);graphics.pose().popPose();
    }

    /**
     * 注视度占比 → 进度条颜色（含 alpha）：
     * <0.3 青 / <0.6 黄 / <0.85 橙 / >=0.85 红闪（随游戏刻闪烁，强化临界预警）。
     */
    private static int colorForRatio(float ratio) {
        if (ratio < 0.3F) return 0xFF33CCFF;
        if (ratio < 0.6F) return 0xFFFFDD33;
        if (ratio < 0.85F) return 0xFFFF8800;
        // 临界：基于系统时间做简单闪烁，无需持久状态
        boolean blinkOn = (System.currentTimeMillis() / 400L) % 2L == 0L;
        return blinkOn ? 0xFFFF3333 : 0xFFAA0000;
    }
}
