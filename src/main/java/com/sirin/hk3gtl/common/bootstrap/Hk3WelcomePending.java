package com.sirin.hk3gtl.common.bootstrap;









public final class Hk3WelcomePending<T> {
    private Object session;
    private T value;
    private boolean manual;

    public void offer(Object current, Object source, T next, boolean requested) {
        if (current != source) return;
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
