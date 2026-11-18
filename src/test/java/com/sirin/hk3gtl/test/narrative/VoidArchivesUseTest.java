package com.sirin.hk3gtl.test.narrative;

import com.sirin.hk3gtl.common.easter.Hk3EggRules;
import com.sirin.hk3gtl.common.easter.Hk3EggVoidArchivesFacts;
import com.sirin.hk3gtl.common.item.abyss.AbyssFunctionalItems;
import com.sirin.hk3gtl.common.item.abyss.Hk3VoidArchivesItem;
import net.minecraft.world.phys.HitResult;
import org.objectweb.asm.ClassReader;
import org.objectweb.asm.tree.ClassNode;
import org.objectweb.asm.tree.MethodInsnNode;
import org.objectweb.asm.tree.MethodNode;
import org.objectweb.asm.tree.FieldInsnNode;
import org.objectweb.asm.tree.TypeInsnNode;
import org.objectweb.asm.tree.LdcInsnNode;

import java.io.IOException;
import java.util.Map;

/** 079使用守卫及真实物品入口字节码检查；不冒充游戏右键或收藏投递验收。 */
public final class VoidArchivesUseTest {
    private static int checks;
    private static void check(boolean passed, String reason) {
        checks++;
        if (!passed) throw new AssertionError(reason);
    }

    public static void main(String[] args) {
        for (boolean identity : new boolean[]{false, true})
            for (int count : new int[]{-1, 0, 1, 64})
                for (HitResult.Type target : HitResult.Type.values())
                    check(Hk3EggVoidArchivesFacts.accepts(identity, count, target)
                            == (identity && count > 0 && target == HitResult.Type.MISS),
                            "仅正确所持遗物、正数量和空气目标成功");
        check(!Hk3EggVoidArchivesFacts.accepts(true, 1, null), "缺目标失败关闭");
        var rule = Hk3EggRules.all().stream().filter(r -> r.id().equals("E-EG-079")).findFirst().orElseThrow();
        check(rule.matches("vanilla_case", Map.of("case", "79")), "079成功回执匹配");
        check(!rule.matches("vanilla_case", Map.of("case", "78")), "其他成功事件不能代替");
        check(!rule.matches("vanilla_case", Map.of()), "仅持有不触发");
        check(!rule.matches("item_held", Map.of("case", "79")), "库存事实不能代替成功使用");
        try (var stream = AbyssFunctionalItems.class.getResourceAsStream("AbyssFunctionalItems.class")) {
            if (stream == null) throw new AssertionError("缺实际注册入口");
            var type = new ClassNode();
            new ClassReader(stream).accept(type, ClassReader.SKIP_DEBUG | ClassReader.SKIP_FRAMES);
            boolean registeredId = false, registeredType = false;
            for (var method : type.methods) for (var instruction : method.instructions) {
                if (instruction instanceof LdcInsnNode constant)
                    registeredId |= "artifact_void_archives".equals(constant.cst);
                if (instruction instanceof MethodInsnNode call)
                    registeredType |= call.owner.equals("com/sirin/hk3gtl/common/item/abyss/Hk3VoidArchivesItem")
                            && call.name.equals("<init>");
            }
            check(registeredId && registeredType, "既有注册ID使用真实功能物品类");
        } catch (IOException failure) { throw new AssertionError("注册入口读取失败", failure); }
        try (var stream = Hk3VoidArchivesItem.class.getResourceAsStream("Hk3VoidArchivesItem.class")) {
            if (stream == null) throw new AssertionError("缺实际物品入口");
            var type = new ClassNode();
            new ClassReader(stream).accept(type, ClassReader.SKIP_DEBUG | ClassReader.SKIP_FRAMES);
            var use = type.methods.stream().filter(m -> m.name.equals("use")).findFirst().orElseThrow();
            check(calls(use, "getItemInHand"), "实际入口按传入主副手取物品");
            check(calls(use, "getPlayerPOVHitResult") && calls(use, "accepts"), "实际入口使用视线目标和同一身份守卫");
            check(calls(use, "getEntityHitResult"), "实体目标不能借用方块射线的MISS");
            check(calls(use, "pass") && calls(use, "sidedSuccess"), "拒绝和成功沿原生交互结果返回");
            check(calls(use, "caseEvent"), "实际成功入口连接收藏事件");
            check(!calls(use, "shrink") && !calls(use, "setCount") && !calls(use, "hurtAndBreak"), "使用不消耗物品或耐久");
            boolean serverGuard = false, clientGuard = false, hardcodedHand = false;
            for (var instruction : use.instructions) {
                if (instruction instanceof TypeInsnNode typeCheck
                        && typeCheck.desc.equals("net/minecraft/server/level/ServerPlayer")) serverGuard = true;
                if (instruction instanceof FieldInsnNode field) {
                    clientGuard |= field.name.equals("isClientSide");
                    hardcodedHand |= field.owner.equals("net/minecraft/world/InteractionHand");
                }
            }
            check(serverGuard && clientGuard, "收藏派发保留服务端玩家与逻辑端守卫");
            check(!hardcodedHand, "没有硬编码主手而忽略副手");
        } catch (IOException failure) { throw new AssertionError("物品入口读取失败", failure); }
        System.out.println("虚空万藏使用：" + checks + "项检查通过；未运行客户端右键及真实收藏投递。");
    }

    private static boolean calls(MethodNode method, String name) {
        for (var instruction : method.instructions)
            if (instruction instanceof MethodInsnNode call && call.name.equals(name)) return true;
        return false;
    }
}
