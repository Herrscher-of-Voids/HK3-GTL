package com.sirin.hk3gtl.test.bootstrap;

import com.google.gson.*;
import com.sirin.hk3gtl.common.bootstrap.Hk3WelcomePending;
import com.sirin.hk3gtl.common.bootstrap.Hk3WelcomeState;
import com.sirin.hk3gtl.common.event.Hk3PlayerDataCloneHandler;
import com.sirin.hk3gtl.common.network.ModWelcomeS2CPacket;
import com.sirin.hk3gtl.common.narrative.Hk3ApprovedProse;
import io.netty.buffer.Unpooled;
import net.minecraft.nbt.*;
import net.minecraft.network.FriendlyByteBuf;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

/**
 * 【变更记录 #1】2026-10-01 16:14:20（修订133）
 * 删除：无；新增：真实NBT重载/重生复制、版本确认、玩家隔离、弹窗等待/会话切换与包边界验证。
 * 修改：无；用途：验证整个说明系统的数据生命周期；绘制、手机返回及实机启动仍需游戏验收。
 * 【变更记录 #2】2026-10-31 15:36:22（第2次备注 · 修订188）：删除无；新增旧网络连接延迟包在新连接上不展示的回归；修改交付测试覆盖切服后队列身份；用途：锁定断线旧队列隔离。
 */
public final class WelcomeSystemTest {
    private static int checks;
    private static void check(boolean pass, String label) { checks++; if (!pass) throw new AssertionError(label); }
    private static void reject(Runnable action, String label) {
        try { action.run(); } catch (IllegalArgumentException expected) { checks++; return; }
        throw new AssertionError(label);
    }
    public static void main(String[] args) throws Exception {
        state(); delivery(); packet(); content();
        System.out.println("更新详情系统：" + checks + "项回归通过；实际GUI与登录时序待游戏验收。");
    }
    private static void state() throws Exception {
        var data = new CompoundTag(); var other = new CompoundTag();
        String version = "0.5.0", id = Hk3WelcomeState.contentId(version);
        check(Hk3WelcomeState.first(data) && Hk3WelcomeState.unread(data, version), "新玩家未读");
        var before = data.copy();
        check(!Hk3WelcomeState.acknowledge(data, version, id, null), "未发送不能确认");
        check(data.equals(before), "拒绝确认不改数据");
        data.putString(Hk3WelcomeState.SEEN_TAG, version + "/approved-prose-93");
        check(!Hk3WelcomeState.first(data) && Hk3WelcomeState.unread(data, version), "同版真实补充仍需阅读");
        check(!Hk3WelcomeState.acknowledge(data, version, "0.4.0/old", id), "旧页不能确认新说明");
        data.putInt("hk3gtl_unrelated_progress", 17); data.putString("other_mod", "原值");
        check(Hk3WelcomeState.acknowledge(data, version, id, id), "已发送当前正文可以确认");
        check(!Hk3WelcomeState.unread(data, version), "重登同一说明不再弹出");
        check(Hk3WelcomeState.unread(data, "0.5.1"), "模组版本变化需要重新阅读");
        check(Hk3WelcomeState.unread(other, version), "另一玩家不受影响");
        check(data.getInt("hk3gtl_unrelated_progress") == 17 && data.getString("other_mod").equals("原值"), "阅读不修改其他成果");
        var bytes = new ByteArrayOutputStream(); NbtIo.writeCompressed(data, bytes);
        var restored = NbtIo.readCompressed(new ByteArrayInputStream(bytes.toByteArray()));
        check(!Hk3WelcomeState.unread(restored, version), "真实NBT存取保持已读");
        var respawn = new CompoundTag(); Hk3PlayerDataCloneHandler.copyPersistentState(restored, respawn);
        check(!Hk3WelcomeState.unread(respawn, version), "复用死亡与末地实体重建迁移");
        respawn.putString(Hk3WelcomeState.SEEN_TAG, "其他值");
        check(!Hk3WelcomeState.unread(restored, version), "复制无共享写入");
        check(!respawn.contains("other_mod"), "仅复制本模组状态");
    }
    private static void delivery() {
        var queue = new Hk3WelcomePending<String>(); Object a = new Object(), b = new Object();
        queue.offer(a, "登录说明", false);
        check(queue.take(a, false, false) == null, "玩家尚未加载时等待");
        check(queue.take(a, true, true) == null, "正在阅读或加载界面时不抢屏");
        check("登录说明".equals(queue.take(a, true, false)), "进入空闲界面后显示");
        check(queue.take(a, true, false) == null, "同一排队请求只展示一次");
        queue.offer(a, "手动重读", true); queue.offer(a, "迟到的登录包", false);
        check("手动重读".equals(queue.take(a, true, true)), "显式重读优先且可从手机打开");
        queue.offer(a, "旧服", false);
        check(queue.take(b, true, false) == null, "换服不能展示旧服内容");
        check(queue.take(a, true, false) == null, "旧连接内容已被切服取出并清理");
        queue.offer(b, b, "新服", false);
        queue.offer(b, a, "断线后迟到的旧包", true);
        check("新服".equals(queue.take(b, true, false)), "迟到旧包不能覆盖新服队列");
        queue.offer(b, a, "断线后迟到的旧包", false);
        check(queue.take(b, true, false) == null, "迟到旧包不能绑定新连接");
        queue.offer(a, "旧档", false); queue.clear();
        check(queue.take(a, true, false) == null, "断线清空");
        queue.offer(null, "无连接", true);
        check(queue.take(null, true, false) == null, "无连接不入队");
    }
    private static void packet() {
        var lines = new ArrayList<>(List.of("items:ok:123", "welcome:first", "content:" + Hk3WelcomeState.contentId("0.5.0")));
        var source = new ModWelcomeS2CPacket("0.5.0", lines); lines.clear();
        check(source.statusLines().size() == 3, "发送快照不可受调用者修改");
        var buffer = new FriendlyByteBuf(Unpooled.buffer());
        try { ModWelcomeS2CPacket.encode(source, buffer); check(source.equals(ModWelcomeS2CPacket.decode(buffer)), "真实包编码解码一致"); }
        finally { buffer.release(); }
        reject(() -> new ModWelcomeS2CPacket("x".repeat(129), List.of()), "拒绝过长版本");
        reject(() -> new ModWelcomeS2CPacket("0.5.0", Collections.nCopies(65, "x")), "拒绝过多状态行");
        reject(() -> new ModWelcomeS2CPacket("0.5.0", List.of("x".repeat(1025))), "拒绝过长状态行");
        for (int size : new int[]{-1, 65, Integer.MAX_VALUE}) {
            var invalid = new FriendlyByteBuf(Unpooled.buffer());
            try { invalid.writeUtf("0.5.0"); invalid.writeVarInt(size); reject(() -> ModWelcomeS2CPacket.decode(invalid), "无效条数在分配前拒绝"); }
            finally { invalid.release(); }
        }
    }
    private static void content() throws Exception {
        for (String locale : List.of("zh_cn", "en_us")) {
            try (var stream = WelcomeSystemTest.class.getResourceAsStream("/assets/hk3gtl/lang/" + locale + ".json")) {
                check(stream != null, "语言资源存在");
                var lang = JsonParser.parseReader(new InputStreamReader(stream, StandardCharsets.UTF_8)).getAsJsonObject();
                var ids = new ArrayList<>(Hk3WelcomeState.CURRENT_PROSE); ids.addAll(Hk3WelcomeState.COMPATIBILITY_PROSE);
                ids.addAll(List.of("U02", "U03", "U29", "U37"));
                for (String id : ids) {
                    var entry = Hk3ApprovedProse.get("update." + id);
                    for (int i = 0; i < entry.lineCount(); i++) check(lang.has(entry.key() + ".line." + i), "实际分类正文完整：" + id);
                }
                for (String version : Hk3WelcomeState.HISTORY) {
                    String prefix = "hk3gtl.welcome.release." + version.replace('.', '_');
                    check(lang.has(prefix + ".title") && lang.has(prefix + ".1"), "历史入口必须有对应实际正文");
                }
                for (int i = 1; i <= 6; i++) check(lang.has("hk3gtl.welcome.release.0_5_0." + i), "本版正文完整");
                String feedback = lang.get("hk3gtl.welcome.feedback_template").getAsString();
                check(feedback.contains("758974004") && feedback.contains("3929461640"), "两个批准的反馈入口保留");
                check(!ids.contains("U17"), "不宣传已取消的家园NPC实体");
                for (String key : List.of("tab.current", "tab.compatibility", "tab.health", "tab.history", "tab.feedback", "health_scope", "health_warning", "current_limits", "status.industrial_machines", "ack_stale"))
                    check(lang.has("hk3gtl.welcome." + key), "控件语言键存在：" + key);
            }
        }
    }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
