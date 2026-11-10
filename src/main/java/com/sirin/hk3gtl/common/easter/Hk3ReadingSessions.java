package com.sirin.hk3gtl.common.easter;

/** 【变更记录 #1】2026-10-31 00:46:39（第1次备注 · 修订187）：删除无；新增每人当前正文会话、完整阅读与动作单次消费；修改由原阅读服务调用；用途：服务端主线程内验证正文，关闭、断线与过期清理。 */

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/** 每人只保留当前正文会话；完整阅读凭据绑定原预览动作，关闭、换页会话和断线均失效。 */
public final class Hk3ReadingSessions {
    public record Session(UUID token, String id, String action, boolean letter, Hk3EggReadingCursor cursor, long expires) {}
    private static final long LIFETIME = 36000;
    private final Map<UUID, Session> active = new HashMap<>();

    public Session open(UUID actor, String id, String body, String action, boolean letter, long now) {
        var session = new Session(UUID.randomUUID(), id, action, letter, new Hk3EggReadingCursor(body), now + LIFETIME);
        active.put(actor, session);
        return session;
    }

    /** 仅首次连续读完返回会话，重传不会重复产生阅读副作用。 */
    public Session accept(UUID actor, UUID token, int start, String piece, long now) {
        var session = current(actor, now);
        if (session == null || !session.token.equals(token) || session.cursor.done()
                || !session.cursor.accept(start, piece) || !session.cursor.done()) return null;
        return session;
    }

    public boolean consumeAction(UUID actor, String action, long now) {
        var session = current(actor, now);
        if (session == null || action.isEmpty() || !session.action.equals(action) || !session.cursor.done()) return false;
        active.remove(actor);
        return true;
    }

    private Session current(UUID actor, long now) {
        var session = active.get(actor);
        if (session != null && (now >= session.expires || now < session.expires - LIFETIME)) {
            active.remove(actor);
            return null;
        }
        return session;
    }

    public void close(UUID actor, UUID token) {
        var session = active.get(actor);
        if (session != null && session.token.equals(token)) active.remove(actor);
    }

    public void clear(UUID actor) { active.remove(actor); }
    public void clear() { active.clear(); }
}
