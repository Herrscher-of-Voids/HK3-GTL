package com.sirin.hk3gtl.test.dialogue;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.level.GameType;
import org.objectweb.asm.ClassReader;
import org.objectweb.asm.ClassWriter;
import org.objectweb.asm.commons.ClassRemapper;
import org.objectweb.asm.commons.SimpleRemapper;

import java.io.InputStream;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.net.URL;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.util.HexFormat;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.UUID;

/** 用可控边界替身执行真实编译方法；不重写方法体、不启动服务器或 Forge 事件。 */
public final class FinaleReturnModeTest {
    private static final String KEY = "hk3gtl_finale_return_mode_v5";
    private static final String ORIGINAL = "com/sirin/hk3gtl/common/finale/Hk3FinalePlayerMode";
    private static final String RESOURCE = ORIGINAL + ".class";
    private static final String EXECUTABLE = "com/sirin/hk3gtl/test/dialogue/ExecutableFinalePlayerMode";
    private static int checks;

    private FinaleReturnModeTest() {}

    public static void main(String[] args) throws Exception {
        Executable code = load(args);
        if (code.source.legacy) {
            legacy(code);
            return;
        }
        memoryApi(code);
        normalRestores(code, true);
        graduationOverride(code);
        queryFailures(code);
        changeFailure(code);
        appliedChangeFailure(code);
        cancelledChange(code);
        redirectedChange(code);
        alreadyAtTarget(code);
        invalidSavedMode(code);
        missingModeAndIsolation(code);
        copiedDataRetry(code);
        System.out.println("终审返程模式：" + checks + "项检查通过；执行真实生产方法，未启动真实服务器或 Forge 事件。");
        System.out.println("执行来源：" + code.source.location + "；SHA256=" + code.source.sha256);
    }

    private static void memoryApi(Executable code) throws Exception {
        CompoundTag data = new CompoundTag();
        code.remember(data, GameType.SURVIVAL);
        code.remember(data, GameType.CREATIVE);
        check(data.getString(KEY).equals("SURVIVAL"), "重复入场保留首次模式");
        check(code.take(data) == GameType.SURVIVAL && !data.contains(KEY), "take 正常消费已保存模式");
        check(code.take(data) == null, "take 缺键不伪造模式");
        FakeServerPlayer player = player(GameType.SPECTATOR);
        code.enter(player);
        check(player.gameMode.current == GameType.ADVENTURE, "入场切换冒险模式");
        check(code.hasSavedMode(player) && player.data.getString(KEY).equals("SPECTATOR"), "入场保存本人原模式");
        code.enter(player);
        check(player.data.getString(KEY).equals("SPECTATOR"), "重复入场不覆盖首次旁观模式");
        code.leave(player);
        check(player.gameMode.current == GameType.SPECTATOR && !code.hasSavedMode(player), "入场返程闭环恢复并消费本人模式");
    }

    private static void normalRestores(Executable code, boolean requireNoRedundantChange) throws Exception {
        for (GameType original : GameType.values()) {
            FakeServerPlayer player = player(GameType.ADVENTURE);
            code.remember(player.data, original);
            code.leave(player);
            check(player.gameMode.current == original, "恢复原模式：" + original);
            check(!code.hasSavedMode(player), "成功恢复后清键：" + original);
            check(player.data.getString("foreign").equals("保留"), "保留其他个人数据：" + original);
            if (requireNoRedundantChange) {
                check(player.setCalls == (original == GameType.ADVENTURE ? 0 : 1), "仅在需要时修改模式：" + original);
            }
        }
    }

    private static void graduationOverride(Executable code) throws Exception {
        FakeServerPlayer player = player(GameType.ADVENTURE);
        code.remember(player.data, GameType.SPECTATOR);
        player.level.ledger.graduated = player.uuid;
        code.leave(player);
        check(player.gameMode.current == GameType.CREATIVE && !code.hasSavedMode(player), "真实毕业状态覆盖原旁观模式并消费键");
        FakeServerPlayer keyless = player(GameType.SURVIVAL);
        keyless.level.ledger.graduated = keyless.uuid;
        code.leave(keyless);
        check(keyless.gameMode.current == GameType.CREATIVE && !code.hasSavedMode(keyless), "毕业且缺原模式仍按既有规则授创造模式");
    }

    private static void queryFailures(Executable code) throws Exception {
        for (boolean duringGet : new boolean[] {true, false}) {
            FakeServerPlayer player = player(GameType.ADVENTURE);
            code.remember(player.data, GameType.SURVIVAL);
            CompoundTag before = player.data.copy();
            RuntimeException failure = new IllegalStateException(duringGet ? "读取账本失败" : "查询毕业状态失败");
            if (duringGet) player.level.getFailure = failure;
            else player.level.ledger.queryFailure = failure;
            expectSameFailure(() -> code.leave(player), failure, "毕业账本异常原样抛出");
            check(player.data.equals(before) && code.hasSavedMode(player), "毕业查询异常不消费模式或修改其他数据");
            check(player.gameMode.current == GameType.ADVENTURE && player.setCalls == 0, "毕业查询异常不触发模式修改");
            player.level.getFailure = null;
            player.level.ledger.queryFailure = null;
            code.leave(player);
            check(player.gameMode.current == GameType.SURVIVAL && !code.hasSavedMode(player), "毕业查询恢复后可重试返程");
        }
    }

    private static void changeFailure(Executable code) throws Exception {
        FakeServerPlayer player = player(GameType.ADVENTURE);
        code.remember(player.data, GameType.CREATIVE);
        CompoundTag before = player.data.copy();
        player.behavior = Change.THROW;
        expectSameFailure(() -> code.leave(player), player.changeFailure, "模式修改异常原样抛出");
        check(player.data.equals(before) && code.hasSavedMode(player), "修改异常保留原模式及个人数据");
        check(player.gameMode.current == GameType.ADVENTURE, "修改异常不伪造成功模式");
        player.behavior = Change.ACCEPT;
        code.leave(player);
        check(player.gameMode.current == GameType.CREATIVE && !code.hasSavedMode(player), "修改异常后可重试成功");
    }

    private static void cancelledChange(Executable code) throws Exception {
        FakeServerPlayer player = player(GameType.ADVENTURE);
        code.remember(player.data, GameType.SURVIVAL);
        player.behavior = Change.CANCEL;
        code.leave(player);
        check(player.gameMode.current == GameType.ADVENTURE && player.setCalls == 1, "取消返回 false 且实际模式未变");
        check(code.hasSavedMode(player) && player.data.getString(KEY).equals("SURVIVAL"), "取消模式修改保留返程键");
        player.behavior = Change.ACCEPT;
        code.leave(player);
        check(player.gameMode.current == GameType.SURVIVAL && !code.hasSavedMode(player), "取消后重试可恢复原模式");
    }

    private static void appliedChangeFailure(Executable code) throws Exception {
        FakeServerPlayer player = player(GameType.ADVENTURE);
        code.remember(player.data, GameType.SURVIVAL);
        CompoundTag before = player.data.copy();
        player.behavior = Change.APPLY_THEN_THROW;
        expectSameFailure(() -> code.leave(player), player.changeFailure, "实际修改模式后抛错仍传播原异常");
        check(player.gameMode.current == GameType.SURVIVAL && player.data.equals(before), "已修改后抛错仍保留返程键及原值");
        code.leave(player);
        check(player.setCalls == 1 && !code.hasSavedMode(player), "已生效异常后的重试跳过 setter 并清键");
    }

    private static void redirectedChange(Executable code) throws Exception {
        FakeServerPlayer player = player(GameType.ADVENTURE);
        code.remember(player.data, GameType.SURVIVAL);
        player.behavior = Change.REDIRECT;
        code.leave(player);
        check(player.gameMode.current == GameType.SPECTATOR && player.lastResult, "边界返回 true 但将目标改写为旁观模式");
        check(code.hasSavedMode(player) && player.data.getString(KEY).equals("SURVIVAL"), "实际模式不是目标时保留键，不信任布尔返回值");
        player.behavior = Change.ACCEPT;
        code.leave(player);
        check(player.gameMode.current == GameType.SURVIVAL && !code.hasSavedMode(player), "目标被改写后仍可重试本人原模式");
    }

    private static void alreadyAtTarget(Executable code) throws Exception {
        FakeServerPlayer player = player(GameType.SURVIVAL);
        code.remember(player.data, GameType.SURVIVAL);
        player.behavior = Change.THROW;
        code.leave(player);
        check(player.setCalls == 0 && player.gameMode.current == GameType.SURVIVAL, "已是原模式时跳过可能返回 false 的重复设置");
        check(!code.hasSavedMode(player), "已是原模式可直接完成消费");
        FakeServerPlayer graduate = player(GameType.CREATIVE);
        code.remember(graduate.data, GameType.SURVIVAL);
        graduate.level.ledger.graduated = graduate.uuid;
        graduate.behavior = Change.THROW;
        code.leave(graduate);
        check(graduate.setCalls == 0 && !code.hasSavedMode(graduate), "已毕业且已是创造模式也无需重复设置");
    }

    private static void missingModeAndIsolation(Executable code) throws Exception {
        FakeServerPlayer keyless = player(GameType.SPECTATOR);
        CompoundTag before = keyless.data.copy();
        code.leave(keyless);
        check(keyless.gameMode.current == GameType.SPECTATOR && keyless.setCalls == 0, "未毕业且无键不编造返程模式");
        check(keyless.data.equals(before) && !code.hasSavedMode(keyless), "无键返程保持个人数据");
        FakeServerPlayer first = player(GameType.ADVENTURE);
        FakeServerPlayer second = player(GameType.ADVENTURE);
        code.remember(first.data, GameType.SURVIVAL);
        code.remember(second.data, GameType.SPECTATOR);
        first.behavior = Change.CANCEL;
        code.leave(first);
        code.leave(second);
        check(code.hasSavedMode(first) && first.gameMode.current == GameType.ADVENTURE, "另一玩家成功不消费失败玩家的键");
        check(!code.hasSavedMode(second) && second.gameMode.current == GameType.SPECTATOR, "另一玩家按本人模式恢复");
        first.behavior = Change.ACCEPT;
        code.leave(first);
        check(!code.hasSavedMode(first) && first.gameMode.current == GameType.SURVIVAL, "失败玩家独立重试成功");
        check(second.gameMode.current == GameType.SPECTATOR && !code.hasSavedMode(second), "重试不影响已完成玩家");
    }

    private static void invalidSavedMode(Executable code) throws Exception {
        for (boolean wrongType : new boolean[] {false, true}) {
            for (boolean graduated : new boolean[] {false, true}) {
                FakeServerPlayer player = player(GameType.ADVENTURE);
                if (wrongType) player.data.putInt(KEY, 7);
                else player.data.putString(KEY, "不合法的游戏模式");
                if (graduated) player.level.ledger.graduated = player.uuid;
                CompoundTag before = player.data.copy();
                expectParseFailure(() -> code.leave(player), "拒绝非法或错型原模式，毕业状态也不能绕过解析");
                check(player.data.equals(before), "解析失败保留返程键原类型、原值及其他数据");
                check(player.gameMode.current == GameType.ADVENTURE && player.setCalls == 0
                        && player.level.getCalls == 0, "解析失败不修改模式或继续查询毕业账本");
            }
        }
    }

    private static void copiedDataRetry(Executable code) throws Exception {
        FakeServerPlayer source = player(GameType.ADVENTURE);
        code.remember(source.data, GameType.SURVIVAL);
        source.behavior = Change.CANCEL;
        code.leave(source);
        CompoundTag saved = source.data.copy();
        check(saved.getString(KEY).equals("SURVIVAL"), "取消后复制的持久NBT保留原模式");
        FakeServerPlayer restored = new FakeServerPlayer(GameType.ADVENTURE, saved.copy(), source.uuid, source.level);
        check(restored.data.equals(saved) && code.hasSavedMode(restored), "同UUID新玩家从复制的NBT恢复未消费模式");
        code.leave(restored);
        check(restored.gameMode.current == GameType.SURVIVAL && !code.hasSavedMode(restored), "复制NBT后的新玩家可重试返程");
        check(source.data.equals(saved) && code.hasSavedMode(source), "新玩家消费不反向修改旧玩家NBT副本");
        code.leave(restored);
        check(restored.gameMode.current == GameType.SURVIVAL && restored.setCalls == 1
                && !code.hasSavedMode(restored), "成功后重复返程保持模式且不额外调用 setter");
    }

    private static void legacy(Executable code) throws Exception {
        normalRestores(code, false);
        graduationOverride(code);
        FakeServerPlayer query = player(GameType.ADVENTURE);
        code.remember(query.data, GameType.SURVIVAL);
        query.level.ledger.queryFailure = new IllegalStateException("冻结旧类的查询失败复现");
        expectSameFailure(() -> code.leave(query), query.level.ledger.queryFailure, "旧类查询错误仍向外传播");
        check(!code.hasSavedMode(query) && query.gameMode.current == GameType.ADVENTURE, "观察旧类在毕业查询抛错前已丢失返程键");
        FakeServerPlayer cancelled = player(GameType.ADVENTURE);
        code.remember(cancelled.data, GameType.SURVIVAL);
        cancelled.behavior = Change.CANCEL;
        code.leave(cancelled);
        check(!code.hasSavedMode(cancelled) && cancelled.gameMode.current == GameType.ADVENTURE, "观察旧类取消设置后丢失返程键");
        Map<String, Object> observed = new LinkedHashMap<>();
        observed.put("mode", "legacy");
        observed.put("source_kind", code.source.legacy ? "file" : "resource");
        observed.put("source_location", code.source.location);
        observed.put("input_class_sha256", code.source.sha256);
        observed.put("class_source", code.source.location);
        observed.put("class_sha256", code.source.sha256);
        observed.put("valid_control", true);
        observed.put("graduation_failure_lost_key", !code.hasSavedMode(query)
                && query.gameMode.current == GameType.ADVENTURE);
        observed.put("setter_cancel_lost_key", !code.hasSavedMode(cancelled)
                && cancelled.gameMode.current == GameType.ADVENTURE);
        observed.put("execution", "ASM ClassRemapper 仅映射边界类名，真实方法体与控制流保持");
        observed.put("query_failure", Map.of("thrown", true, "saved_before", "SURVIVAL", "saved_after", false,
                "mode_before", "ADVENTURE", "mode_after", query.gameMode.current.name(), "key_lost", true));
        observed.put("cancelled_change", Map.of("set_result", cancelled.lastResult, "saved_before", "SURVIVAL",
                "saved_after", false, "mode_before", "ADVENTURE", "mode_after", cancelled.gameMode.current.name(), "key_lost", true));
        observed.put("normal_control", Map.of("four_game_modes_restored", true, "graduated_creative", true));
        observed.put("checks", checks);
        observed.put("real_server_started", false);
        observed.put("forge_events_executed", false);
        observed.put("limitation", "玩家、模式修改与毕业账本使用可控替身；不等于真实服务器或 Forge 取消事件实测");
        System.out.println("OBSERVED " + json(observed));
        System.out.println("冻结旧类：正常对照通过；两条返程键丢失路径已实际复现。");
    }

    private static Executable load(String[] args) throws Exception {
        boolean legacy = args.length == 2 && args[0].equals("--legacy-class");
        if (args.length != 0 && !legacy) throw new IllegalArgumentException("参数：无参数，或 --legacy-class <绝对.class路径>");
        byte[] bytes;
        String location;
        if (legacy) {
            Path path = Path.of(args[1]);
            if (!path.isAbsolute()) throw new IllegalArgumentException("冻结类必须使用绝对路径");
            path = path.normalize();
            bytes = Files.readAllBytes(path);
            location = path.toString();
        } else {
            URL resource = FinaleReturnModeTest.class.getClassLoader().getResource(RESOURCE);
            if (resource == null) throw new IllegalStateException("缺少真实生产编译类：" + RESOURCE);
            try (InputStream in = resource.openStream()) { bytes = in.readAllBytes(); }
            location = resource.toExternalForm();
        }
        ClassReader reader = new ClassReader(bytes);
        if (!reader.getClassName().equals(ORIGINAL)) throw new IllegalArgumentException("输入不是目标生产类");
        Map<String, String> names = Map.of(
                ORIGINAL, EXECUTABLE,
                "net/minecraft/server/level/ServerPlayer", internal(FakeServerPlayer.class),
                "net/minecraft/server/level/ServerPlayerGameMode", internal(FakePlayerGameMode.class),
                "net/minecraft/server/level/ServerLevel", internal(FakeServerLevel.class),
                "com/sirin/hk3gtl/common/dimension/Hk3GraduationData", internal(FakeGraduationData.class));
        ClassWriter writer = new ClassWriter(0);
        reader.accept(new ClassRemapper(writer, new SimpleRemapper(names)), 0);
        Class<?> mapped = new MappedLoader(FinaleReturnModeTest.class.getClassLoader()).define(writer.toByteArray());
        String sha = HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes));
        return new Executable(mapped, new Source(legacy, location, sha));
    }

    private static FakeServerPlayer player(GameType initial) { return new FakeServerPlayer(initial); }
    private static String internal(Class<?> type) { return type.getName().replace('.', '/'); }
    private static void check(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
        checks++;
    }
    private static void expectSameFailure(Operation operation, RuntimeException expected, String message) throws Exception {
        try { operation.run(); }
        catch (RuntimeException failure) { check(failure == expected, message); return; }
        throw new AssertionError(message + "：未抛出异常");
    }
    private static void expectParseFailure(Operation operation, String message) throws Exception {
        try { operation.run(); }
        catch (IllegalArgumentException expected) { check(true, message); return; }
        throw new AssertionError(message + "：未拒绝损坏模式");
    }
    @FunctionalInterface private interface Operation { void run() throws Exception; }
    private record Source(boolean legacy, String location, String sha256) {}

    private static final class MappedLoader extends ClassLoader {
        private MappedLoader(ClassLoader parent) { super(parent); }
        private Class<?> define(byte[] bytes) { return defineClass(EXECUTABLE.replace('/', '.'), bytes, 0, bytes.length); }
    }

    private static final class Executable {
        private final Source source;
        private final Method enter, leave, remember, take, hasSavedMode;
        private Executable(Class<?> type, Source source) throws Exception {
            this.source = source;
            enter = type.getMethod("enter", FakeServerPlayer.class);
            leave = type.getMethod("leave", FakeServerPlayer.class);
            remember = type.getMethod("remember", CompoundTag.class, GameType.class);
            take = type.getMethod("take", CompoundTag.class);
            hasSavedMode = type.getMethod("hasSavedMode", FakeServerPlayer.class);
        }
        private void enter(FakeServerPlayer player) throws Exception { invoke(enter, player); }
        private void leave(FakeServerPlayer player) throws Exception { invoke(leave, player); }
        private void remember(CompoundTag data, GameType mode) throws Exception { invoke(remember, data, mode); }
        private GameType take(CompoundTag data) throws Exception { return (GameType) invoke(take, data); }
        private boolean hasSavedMode(FakeServerPlayer player) throws Exception { return (Boolean) invoke(hasSavedMode, player); }
        private Object invoke(Method method, Object... args) throws Exception {
            try { return method.invoke(null, args); }
            catch (InvocationTargetException wrapped) {
                Throwable failure = wrapped.getCause();
                if (failure instanceof Exception exception) throw exception;
                if (failure instanceof Error error) throw error;
                throw new AssertionError("无法传播生产异常", failure);
            }
        }
    }

    public enum Change { ACCEPT, CANCEL, THROW, APPLY_THEN_THROW, REDIRECT }

    public static final class FakeServerPlayer {
        public final FakePlayerGameMode gameMode;
        public final CompoundTag data;
        public final FakeServerLevel level;
        public final UUID uuid;
        public Change behavior = Change.ACCEPT;
        public final RuntimeException changeFailure = new IllegalStateException("可控模式修改失败");
        public int setCalls;
        public boolean lastResult;
        public FakeServerPlayer(GameType initial) {
            this(initial, new CompoundTag(), UUID.randomUUID(), new FakeServerLevel());
            data.putString("foreign", "保留");
        }
        public FakeServerPlayer(GameType initial, CompoundTag data, UUID uuid, FakeServerLevel level) {
            gameMode = new FakePlayerGameMode(initial);
            this.data = data;
            this.uuid = uuid;
            this.level = level;
        }
        public CompoundTag getPersistentData() { return data; }
        public FakeServerLevel serverLevel() { return level; }
        public UUID getUUID() { return uuid; }
        public boolean setGameMode(GameType target) {
            setCalls++;
            if (behavior == Change.THROW) throw changeFailure;
            if (behavior == Change.APPLY_THEN_THROW) {
                gameMode.current = target;
                throw changeFailure;
            }
            if (behavior == Change.CANCEL) return lastResult = false;
            if (behavior == Change.REDIRECT) {
                gameMode.current = GameType.SPECTATOR;
                return lastResult = true;
            }
            boolean changed = gameMode.current != target;
            gameMode.current = target;
            return lastResult = changed;
        }
    }

    public static final class FakePlayerGameMode {
        public GameType current;
        public FakePlayerGameMode(GameType initial) { current = initial; }
        public GameType getGameModeForPlayer() { return current; }
    }

    public static final class FakeServerLevel {
        public final FakeGraduationData ledger = new FakeGraduationData();
        public RuntimeException getFailure;
        public int getCalls;
    }

    public static final class FakeGraduationData {
        public UUID graduated;
        public RuntimeException queryFailure;
        public static FakeGraduationData get(FakeServerLevel level) {
            level.getCalls++;
            if (level.getFailure != null) throw level.getFailure;
            return level.ledger;
        }
        public boolean isGraduated(UUID player) {
            if (queryFailure != null) throw queryFailure;
            return player.equals(graduated);
        }
    }

    private static String json(Object value) {
        if (value instanceof Map<?, ?> values) {
            StringBuilder result = new StringBuilder("{");
            for (Map.Entry<?, ?> entry : values.entrySet()) {
                if (result.length() > 1) result.append(',');
                result.append(json(entry.getKey().toString())).append(':').append(json(entry.getValue()));
            }
            return result.append('}').toString();
        }
        if (value instanceof Boolean || value instanceof Number) return value.toString();
        String text = value.toString().replace("\\", "\\\\").replace("\"", "\\\"")
                .replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t");
        return '"' + text + '"';
    }
}
