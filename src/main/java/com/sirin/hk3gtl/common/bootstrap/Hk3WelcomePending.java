package com.sirin.hk3gtl.common.bootstrap;

/**
 * 客户端主线程使用的单槽待显示说明；会话按连接对象身份隔离。
 * 【变更记录 #1】2026-10-01 16:11:00（修订133）
 * 删除：无；新增：可等待玩家加载和空闲屏幕、优先保留手动打开、取出后去重。
 * 修改：无；用途：防登录说明吞掉正在阅读的信件/剧情或串到下一服务器。
 * 【变更记录 #2】2026-10-31 15:42:00（第2次备注 · 修订188）
 * 删除：无；新增：按当前连接校验来源连接的入队入口；修改：旧包不清空新会话的待显示内容；用途：隔离切服后的延迟网络工作。
 */
public final class Hk3WelcomePending<T> {
    private Object session;
    private T value;
    private boolean manual;

    public void offer(Object current, Object source, T next, boolean requested) {
        if (source == null || current != source) return;
        offer(source, next, requested);
    }

    public void offer(Object connection, T next, boolean requested) {
        if (connection == null) return;
        if (session != connection) clear();
        if (value != null && manual && !requested) return;
        session = connection;
        value = next;
        manual = requested;
    }

    public T take(Object connection, boolean ready, boolean busy) {
        if (session != connection) { clear(); return null; }
        if (!ready || value == null || (busy && !manual)) return null;
        T next = value;
        clear();
        return next;
    }

    public void clear() { session = null; value = null; manual = false; }
}
