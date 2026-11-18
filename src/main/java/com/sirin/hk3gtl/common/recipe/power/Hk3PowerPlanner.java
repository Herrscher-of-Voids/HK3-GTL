package com.sirin.hk3gtl.common.recipe.power;

/**
 * 只读核验规划入口的继承身份，防止未知批次规划器绕过固定工况分流。
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
