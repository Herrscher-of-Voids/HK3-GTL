package com.sirin.hk3gtl.common.narrative;



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
public final class Hk3NarrativeLog {

    /** 解锁标记的键前缀。一旦上线绝对不可更改 */
    public static final String TAG_PREFIX = "hk3gtl_nar_";

    private Hk3NarrativeLog() {}

    /** 判断指定玩家是否已解锁某节点 */
    public static boolean isUnlocked(Player player, String nodeId) {
        return player.getPersistentData().getBoolean(TAG_PREFIX + nodeId);
    }

    /** 标记解锁。返回 true 表示"这次是新解锁"，false 表示"已解锁过" */
    public static boolean unlock(Player player, String nodeId) {
        if (isUnlocked(player, nodeId)) return false;
        player.getPersistentData().putBoolean(TAG_PREFIX + nodeId, true);
        return true;
    }

    /** 返回玩家当前已解锁的所有节点 ID 集合（LinkedHashSet 保证插入顺序） */
    public static Set<String> allUnlocked(Player player) {
        CompoundTag data = player.getPersistentData();
        Set<String> out = new LinkedHashSet<>();
        for (String key : data.getAllKeys()) {
            if (!key.startsWith(TAG_PREFIX)) continue;
            if (!data.getBoolean(key)) continue;
            out.add(key.substring(TAG_PREFIX.length()));
        }
        return out;
    }

    /** 计数器：已解锁多少节点（用于成就系统 / 毕业验证） */
    public static int unlockedCount(Player player) {
        int count = 0;
        for (String key : player.getPersistentData().getAllKeys()) {
            if (key.startsWith(TAG_PREFIX) && player.getPersistentData().getBoolean(key)) {
                count++;
            }
        }
        return count;
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
