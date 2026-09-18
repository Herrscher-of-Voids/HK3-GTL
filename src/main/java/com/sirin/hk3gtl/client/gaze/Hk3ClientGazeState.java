package com.sirin.hk3gtl.client.gaze;

import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

/**
 * 客户端注视度缓存：仅保存服务端下发的注视快照，供 HUD 渲染读取。
 *
 * <p>纯客户端状态，不参与任何业务计算；所有权威数据以服务端 {@code Hk3GazeManager} 为准。
 * 字段用 volatile 保证网络线程写入、渲染线程读取的可见性。</p>
 */
@OnlyIn(Dist.CLIENT)
public final class Hk3ClientGazeState {

    /** 当前原始注视度（0~GAZE_MAX） */
    private static volatile int gaze = 0;
    /** 注视度上限，随包同步以便 HUD 计算进度比例 */
    private static volatile int gazeMax = 1000;
    /** 缓冲单元是否激活（HUD 显示缓冲提示） */
    private static volatile boolean bufferActive = false;
    /** 是否已收到过至少一次同步（未同步前不渲染 HUD） */
    private static volatile boolean synced = false;

    private Hk3ClientGazeState() {}

    public static void update(int newGaze, int newMax, boolean newBufferActive) {
        gaze = newGaze;
        gazeMax = Math.max(1, newMax);
        bufferActive = newBufferActive;
        synced = true;
    }

    /** 玩家断开连接时复位，避免残留数据串档。 */
    public static void reset() {
        gaze = 0;
        gazeMax = 1000;
        bufferActive = false;
        synced = false;
    }

    public static int getGaze() {
        return gaze;
    }

    public static int getGazeMax() {
        return gazeMax;
    }

    public static boolean isBufferActive() {
        return bufferActive;
    }

    public static boolean isSynced() {
        return synced;
    }

    /** 注视度占比 0.0~1.0，供进度条与变色阈值使用。 */
    public static float getRatio() {
        return Math.min(1.0F, (float) gaze / (float) Math.max(1, gazeMax));
    }
}
