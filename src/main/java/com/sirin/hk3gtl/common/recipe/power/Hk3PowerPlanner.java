package com.sirin.hk3gtl.common.recipe.power;

/**
 * 【文件职责】只读核验规划入口的继承身份，防止未知批次规划器绕过固定工况分流。
 * 【变更记录 #1】2026-10-17 17:58:50（第1次备注 · 修订165）
 * 删除：无；新增：标准入口继承与另建getGTRecipe规划入口的反射判定。
 * 修改：未知子类必须继续使用已接线的选方及完工入口，否则拒绝显式HK高阶工况。
 * 用途：关闭GTLAdd自建规划器聚合后丢失费用data的缺口，不修改原第三方工况。
 */
public final class Hk3PowerPlanner {
    private Hk3PowerPlanner() {}

    public static boolean inherits(Class<?> type, Class<?> owner, String... entries) {
        if (type == null || owner == null || !owner.isAssignableFrom(type)) return false;
        try {
            for (String entry : entries)
                if (type.getMethod(entry).getDeclaringClass() != owner) return false;
            for (Class<?> current = type; current != owner; current = current.getSuperclass())
                for (var method : current.getDeclaredMethods())
                    if (method.getName().equals("getGTRecipe")) return false;
            return true;
        } catch (ReflectiveOperationException | SecurityException unsupported) {
            return false;
        }
    }
}
