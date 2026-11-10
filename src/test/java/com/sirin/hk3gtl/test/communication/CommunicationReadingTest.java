package com.sirin.hk3gtl.test.communication;

/** 【变更记录 #1】2026-10-31 00:46:39（第1次备注 · 修订187）：删除无；新增生产阅读会话22项边界校验；修改无；用途：拒绝未读推进、旧页重用、冒名和动作重放，不代替客户端验收。 */

import com.sirin.hk3gtl.common.easter.Hk3ReadingSessions;
import java.util.UUID;

/** 执行生产阅读会话，拒绝未读、跳页、旧页面、冒名、过期和动作重放。 */
public final class CommunicationReadingTest {
    private static int checks;
    private static void check(boolean ok, String message) {
        if (!ok) throw new AssertionError(message);
        checks++;
    }

    public static void main(String[] args) {
        var sessions = new Hk3ReadingSessions();
        UUID actor = UUID.randomUUID(), other = UUID.randomUUID();
        String action = UUID.randomUUID().toString();
        var s = sessions.open(actor, "contact_test", "首段\n末段", action, true, 100);
        check(!sessions.consumeAction(actor, action, 101), "打开页面不能确认");
        check(sessions.accept(other, s.token(), 0, "首段末段", 101) == null, "他人回执拒绝");
        check(sessions.accept(actor, UUID.randomUUID(), 0, "首段末段", 101) == null, "错误阅读令牌拒绝");
        check(sessions.accept(actor, s.token(), 2, "末段", 102) == null, "直接末页拒绝");
        check(sessions.accept(actor, s.token(), 0, "篡改", 102) == null, "非服务端正文拒绝");
        check(sessions.accept(actor, s.token(), 0, "首段", 103) == null, "首段未完成");
        check(!sessions.consumeAction(actor, action, 103), "部分阅读不能推进");
        check(sessions.accept(actor, s.token(), 0, "首段", 104) == null, "重传不推进游标");
        check(sessions.accept(actor, s.token(), 2, "末段", 105) != null, "完整阅读产生一次凭据");
        check(sessions.accept(actor, s.token(), 2, "末段", 106) == null, "重复完整回执不结算彩蛋");
        check(!sessions.consumeAction(other, action, 106), "他人不能消费");
        check(!sessions.consumeAction(actor, UUID.randomUUID().toString(), 106), "其他预览动作不能借用阅读");
        check(sessions.consumeAction(actor, action, 107), "当前动作可确认一次");
        check(!sessions.consumeAction(actor, action, 108), "动作重放拒绝");

        s = sessions.open(actor, "doc", "正文", action, true, 200);
        var old = s;
        s = sessions.open(actor, "doc", "新正文", action, true, 201);
        check(sessions.accept(actor, old.token(), 0, "正文", 202) == null, "重新打开使旧页面失效");
        sessions.accept(actor, s.token(), 0, "新正文", 202);
        sessions.close(actor, old.token());
        check(sessions.consumeAction(actor, action, 203), "延迟关闭旧页不清新页");

        s = sessions.open(actor, "doc", "正文", action, true, 300);
        sessions.accept(actor, s.token(), 0, "正文", 301);
        sessions.close(actor, s.token());
        check(!sessions.consumeAction(actor, action, 302), "关闭后即使读完也不得提交");
        s = sessions.open(actor, "doc", "正文", action, true, 400);
        sessions.accept(actor, s.token(), 0, "正文", 401);
        sessions.clear(actor);
        check(!sessions.consumeAction(actor, action, 402), "断线清除阅读凭据");
        s = sessions.open(actor, "doc", "正文", action, true, 500);
        sessions.accept(actor, s.token(), 0, "正文", 501);
        check(!sessions.consumeAction(actor, action, 36500), "到期边界拒绝");
        s = sessions.open(actor, "doc", "正文", action, true, 600);
        sessions.accept(actor, s.token(), 0, "正文", 601);
        check(!sessions.consumeAction(actor, action, 599), "时钟回退拒绝");

        s = sessions.open(actor, "history", "历史", "", true, 700);
        sessions.accept(actor, s.token(), 0, "历史", 701);
        check(!sessions.consumeAction(actor, "", 702), "只读历史没有动作资格");
        s = sessions.open(actor, "doc", "", action, true, 800);
        check(!sessions.consumeAction(actor, action, 801), "空正文不能算全读");
        sessions.clear();
        System.out.println("CommunicationReadingTest: " + checks + " checks passed");
    }
}
