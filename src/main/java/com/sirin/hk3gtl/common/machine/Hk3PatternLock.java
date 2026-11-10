package com.sirin.hk3gtl.common.machine;

import java.util.concurrent.locks.Lock;
import java.util.function.BooleanSupplier;
import java.util.function.Supplier;

/**
 * 【变更记录 #1】2026-10-15 02:59:25（第1次备注 · 香港时间 · 内测5修订159）
 * 删除：无。新增：HK3结构匹配和朝向更新的可测试锁调用边界。
 * 修改：阻塞调用与立即尝试调用都在finally释放所取得的锁，异常原样交给上层处理。
 * 用途：复用GT控制器自有锁，防止异常泄漏锁及尝试调用变成阻塞；不持有世界或结构缓存。
 */
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
