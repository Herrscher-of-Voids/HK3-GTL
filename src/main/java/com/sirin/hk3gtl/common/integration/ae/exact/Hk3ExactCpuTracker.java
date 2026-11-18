package com.sirin.hk3gtl.common.integration.ae.exact;

import appeng.api.stacks.AEKey;
import net.minecraft.server.level.ServerLevel;

import java.util.UUID;
import java.util.function.Supplier;

/** 将父订单的单批身份传入原生 CPU，实际投料和执行仍由 AE 负责。 */
public final class Hk3ExactCpuTracker {
    private static final ThreadLocal<UUID> SUBMISSION = new ThreadLocal<>();

    public interface BatchAccess {
        boolean hk3gtl$matchesBatch(UUID token, AEKey target, long amount);
    }

    public interface ProgramAccess {
        boolean hk3gtl$recoverableProgram();
    }

    private Hk3ExactCpuTracker() {}

    public static <T> T submit(UUID token, Supplier<T> action) {
        UUID previous = SUBMISSION.get();
        SUBMISSION.set(token);
        try {
            return action.get();
        } finally {
            if (previous == null) SUBMISSION.remove();
            else SUBMISSION.set(previous);
        }
    }

    public static UUID currentSubmission() {
        return SUBMISSION.get();
    }

    public static long produced(long original, long remaining) {
        return original > 0 && remaining >= 0 && remaining <= original ? original - remaining : -1;
    }

    public static long produced(long original, long remaining, boolean success, long inFlight) {
        return inFlight < 0 || !success && inFlight > 0 ? -1 : produced(original, remaining);
    }

    public static void finished(ServerLevel level, UUID token, boolean success, long produced) {
        Hk3ExactOrderService.finished(level, token, success, produced);
    }

    public static boolean cancelRequested(ServerLevel level, UUID token) {
        return Hk3ExactOrderService.cancelRequested(level, token);
    }

    public static boolean freezeRequested(ServerLevel level, UUID token) {
        return Hk3ExactOrderService.freezeRequested(level, token);
    }
}
