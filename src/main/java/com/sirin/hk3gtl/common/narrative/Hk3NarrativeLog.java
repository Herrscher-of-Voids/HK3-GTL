package com.sirin.hk3gtl.common.narrative;


/**
 * 【文件职责】
 * - 管理 Hk3NarrativeLog 叙事节点与档案显示数据。
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
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.entity.player.Player;

import java.util.Collection;
import java.util.LinkedHashSet;
import java.util.Set;

/**
 * 玩家叙事节点解锁日志（读写玩家 {@code persistentData}）。
 *
 * <h3>存储布局</h3>
 * 所有已解锁节点的 ID 写入玩家 {@code persistentData} 的键 {@link #TAG_PREFIX}{@code id} = true。
 * <br>示例：{@code hk3gtl_nar_HQ-001 = true} 表示玩家已解锁 HQ-001。
 *
 * <h3>为什么用 persistentData 前缀而不是子 tag</h3>
 * 与 {@link com.sirin.hk3gtl.common.research.Hk3ResearchManager#TAG_PREFIX} 的方案一致：
 * 扁平 key + 前缀过滤足够用，不引入嵌套 tag 的读写复杂度。
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>更换前缀前必须写存档迁移：否则老玩家全部进度丢失</li>
 *   <li>如需改为 WorldSavedData（全服共享）：留意多人服的"章节是否因人而异"的设计分歧</li>
 *   <li>所有公开方法必须在服务端主线程调用，persistentData 非线程安全</li>
 * </ul>
 */
/** 【变更记录 #1】2026-10-01 01:54:14（修订127）：删除：被替代的旧分支；新增/修改：抽出同源NBT读写并拒绝未知节点，保留原键与调试重置语义；用途：个人收藏与正式资格分离，保留历史记录。 */
/** 【变更记录 #2】2026-10-01 01:56:49（修订127）：删除：被替代的旧分支；新增/修改：汇总仅计已注册节点，未知旧标记不抬高收藏进度；用途：个人收藏与正式资格分离，保留历史记录。 */
public final class Hk3NarrativeLog {

    /** 解锁标记的键前缀。一旦上线绝对不可更改 */
    public static final String TAG_PREFIX = "hk3gtl_nar_";

    private Hk3NarrativeLog() {}

    /** 判断指定玩家是否已解锁某节点 */
    public static boolean isUnlocked(Player player, String nodeId) {
        return isUnlocked(player.getPersistentData(), nodeId);
    }

    /** 标记解锁。返回 true 表示"这次是新解锁"，false 表示"已解锁过" */
    public static boolean unlock(Player player, String nodeId) {
        return unlock(player.getPersistentData(), nodeId);
    }

    public static boolean isUnlocked(CompoundTag data,String nodeId) {
        return Hk3NarrativeNodes.byId(nodeId)!=null&&data.getBoolean(TAG_PREFIX+nodeId);
    }
    public static boolean unlock(CompoundTag data,String nodeId) {
        if(Hk3NarrativeNodes.byId(nodeId)==null||isUnlocked(data,nodeId))return false;
        data.putBoolean(TAG_PREFIX+nodeId,true);return true;
    }

    /** 返回玩家当前已解锁的所有节点 ID 集合（LinkedHashSet 保证插入顺序） */
    public static Set<String> allUnlocked(Player player) {
        CompoundTag data = player.getPersistentData();
        Set<String> out = new LinkedHashSet<>();
        for (String key : data.getAllKeys()) {
            if (!key.startsWith(TAG_PREFIX)) continue;
            if (!data.getBoolean(key)) continue;
            String id=key.substring(TAG_PREFIX.length());
            if(Hk3NarrativeNodes.byId(id)!=null)out.add(id);
        }
        return out;
    }

    /** 计数器：已解锁多少有效展示节点（不用于毕业资格） */
    public static int unlockedCount(Player player) {
        return allUnlocked(player).size();
    }

    /** 批量解锁（用于调试命令 / 作弊模式）。返回本次新增数量 */
    public static int unlockAll(Player player, Collection<String> nodeIds) {
        int added = 0;
        for (String id : nodeIds) {
            if (unlock(player, id)) added++;
        }
        return added;
    }
}
