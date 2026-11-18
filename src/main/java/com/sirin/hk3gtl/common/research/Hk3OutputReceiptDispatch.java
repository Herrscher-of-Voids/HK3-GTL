package com.sirin.hk3gtl.common.research;

import java.util.function.BooleanSupplier;
import java.util.function.Consumer;

/** 真实输出后的旁注失败不阻断生产收尾；必要资格与结算仍原样外抛。 */
public final class Hk3OutputReceiptDispatch {
    private Hk3OutputReceiptDispatch() {}

    public static void dispatch(boolean committed, BooleanSupplier eligible, Runnable required,
                                Runnable observer, Consumer<RuntimeException> failed) {
        if (!committed || !eligible.getAsBoolean()) return;
        required.run();
        try { observer.run(); }
        catch (RuntimeException failure) {
            try { failed.accept(failure); } catch (RuntimeException ignored) {}
        }
    }

    public static void dispatch(boolean committed, Runnable observer, Consumer<RuntimeException> failed) {
        dispatch(committed, () -> true, () -> {}, observer, failed);
    }
}
