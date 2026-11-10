package com.sirin.hk3gtl.client.review;

import com.sirin.hk3gtl.common.review.Hk3CocoonView;
import net.minecraft.client.CameraType;
import net.minecraft.client.Minecraft;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.ClientPlayerNetworkEvent;
import net.minecraftforge.client.event.MovementInputUpdateEvent;
import net.minecraftforge.client.event.ViewportEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/**
 * 【文件职责】一审空间固定第一人称观礼镜头，输入和渲染阶段共同约束。
 * 【变更记录 #1】2026-10-01 20:19:52（内测5修订147）
 * - 删除：无；新增：移动输入屏蔽、每帧朝向锁定、临时第一人称及离场恢复。
 * - 修改：只在cocoon_review维度启用，不拦截对话鼠标或退出键；用途：防止走到茧背面或转开镜头。
 * - 边界：返回其他维度、世界卸载、断线均还原进入前的相机模式，不改存盘选项或玩家飞行权限。
 */
@Mod.EventBusSubscriber(modid="hk3gtl", value=Dist.CLIENT)
public final class Hk3CocoonViewLock {
    private static final ResourceLocation DIMENSION=new ResourceLocation("hk3gtl","cocoon_review");
    private static CameraType previousCamera;
    private Hk3CocoonViewLock(){}
    private static boolean locked(){
        var mc=Minecraft.getInstance();return mc.player!=null&&mc.level!=null&&mc.player.isAlive()&&mc.level.dimension().location().equals(DIMENSION);
    }
    private static void release(){
        if(previousCamera!=null){Minecraft.getInstance().options.setCameraType(previousCamera);previousCamera=null;}
    }
    private static void apply(){
        if(!locked()){release();return;}
        var mc=Minecraft.getInstance();var p=mc.player;
        if(previousCamera==null)previousCamera=mc.options.getCameraType();
        mc.options.setCameraType(CameraType.FIRST_PERSON);
        float yaw=Hk3CocoonView.yaw(p.getX(),p.getZ()),pitch=Hk3CocoonView.pitch(p.getX(),p.getEyeY(),p.getZ());
        p.setYRot(yaw);p.yRotO=yaw;p.setXRot(pitch);p.xRotO=pitch;
        p.setYHeadRot(yaw);p.setYBodyRot(yaw);p.setDeltaMovement(Vec3.ZERO);p.setSprinting(false);
    }
    @SubscribeEvent(priority=EventPriority.LOWEST) public static void input(MovementInputUpdateEvent e){
        if(!locked()||e.getEntity()!=Minecraft.getInstance().player)return;
        var input=e.getInput();input.forwardImpulse=0;input.leftImpulse=0;
        input.up=false;input.down=false;input.left=false;input.right=false;input.jumping=false;input.shiftKeyDown=false;
        e.getEntity().setDeltaMovement(Vec3.ZERO);e.getEntity().setSprinting(false);
    }
    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent e){if(e.phase==TickEvent.Phase.END)apply();}
    @SubscribeEvent public static void render(TickEvent.RenderTickEvent e){if(e.phase==TickEvent.Phase.START)apply();}
    /** 覆盖鼠标在逻辑帧之间产生的朝向，避免相机仍短暂转开一帧。 */
    @SubscribeEvent(priority=EventPriority.LOWEST) public static void camera(ViewportEvent.ComputeCameraAngles e){
        if(!locked())return;var p=Minecraft.getInstance().player;
        e.setYaw(Hk3CocoonView.yaw(p.getX(),p.getZ()));e.setPitch(Hk3CocoonView.pitch(p.getX(),p.getEyeY(),p.getZ()));e.setRoll(0);
    }
    @SubscribeEvent public static void logout(ClientPlayerNetworkEvent.LoggingOut e){release();}
}
