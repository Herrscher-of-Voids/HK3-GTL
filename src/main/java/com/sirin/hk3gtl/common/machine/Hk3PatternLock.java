package com.sirin.hk3gtl.common.machine;

import java.util.concurrent.locks.Lock;
import java.util.function.BooleanSupplier;
import java.util.function.Supplier;

 





final class Hk3PatternLock {
    private Hk3PatternLock() {}

    /** 调用方提供既有可重入锁；本层只释放自己取得的一次持有权。 */
    static <T> T withLock(Lock lock, Supplier<T> operation) {
        lock.lock();
        try {
            return operation.get();
        } finally {
            lock.unlock();
        }
    }

    /** 取锁失败不能调用正文；成功后无论返回值或异常都释放本层持有权。 */
    static boolean tryCheck(Lock lock, BooleanSupplier operation) {
        if (!lock.tryLock()) return false;
        try {
            return operation.getAsBoolean();
        } finally {
            lock.unlock();
        }
    }
}
