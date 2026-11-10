package com.sirin.hk3gtl.common.research;

import java.util.List;
import java.util.function.*;

/** 中文说明：该处说明已按当前代码行为整理。*/
public final class Hk3InventoryDebit<T> {
    private final List<T> before, after;
    private final IntFunction<T> read;
    private final BiConsumer<Integer,T> write;
    private final BiPredicate<T,T> equal;
    private final UnaryOperator<T> copy;
    private final Runnable changed;
    private boolean attempted;

    /** 中文说明：该处说明已按当前代码行为整理。*/
    public Hk3InventoryDebit(List<T> before,List<T> after,IntFunction<T> read,BiConsumer<Integer,T> write,
                            BiPredicate<T,T> equal,UnaryOperator<T> copy,Runnable changed) {
        if (before.size()!=after.size()) throw new IllegalArgumentException("Snapshot length mismatch");
        this.before=before.stream().map(copy).toList(); this.after=after.stream().map(copy).toList();
        this.read=read; this.write=write; this.equal=equal; this.copy=copy; this.changed=changed;
    }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    public boolean commit() {
        if (attempted) return false;
        attempted=true;
        for (int i=0;i<before.size();i++) if (!equal.test(before.get(i),read.apply(i))) return false;
        try {
            for (int i=0;i<before.size();i++) if (!equal.test(before.get(i),after.get(i))) write.accept(i,copy.apply(after.get(i)));
            changed.run(); return true;
        } catch (RuntimeException failure) {
            for (int i=0;i<before.size();i++) if (!equal.test(before.get(i),after.get(i))) {
                try { write.accept(i,copy.apply(before.get(i))); }
                catch (RuntimeException rollback) { failure.addSuppressed(rollback); }
            }
            try { changed.run(); } catch (RuntimeException notification) { failure.addSuppressed(notification); }
            throw failure;
        }
    }
}
