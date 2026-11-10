package com.sirin.hk3gtl.common.easter;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.network.NetworkEvent;
import java.util.function.Supplier;
/** 【变更记录 #1】2026-10-01 04:27:32（修订128）：删除无；新增白名单手机操作包；修改无；用途：只传App/拖动坐标/排列，无任意彩蛋ID，无API Key，无外部文件读取。 */
/** 【变更记录 #2】2026-10-01 05:04:18（修订128）：删除：旧固定上限或被替代的分支；新增/修改：原版背包与地图不要求安装手机；服务器校验真实当前物品，拒绝任意彩蛋ID；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #3】2026-10-01 05:33:27（修订128）：删除：旧固定上限或被替代的分支；新增/修改：终审行为回执不依赖手机安装，但必须匹配当前服务端正式终审会话；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #4】2026-10-01 12:13:33（修订128）：删除：无；新增/修改：增加已知阅读动作分派，处理器白名单验证，不开放通用彩蛋授予；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public record Hk3EggUiPacket(String action,String value){
    public static void encode(Hk3EggUiPacket p,FriendlyByteBuf b){b.writeUtf(p.action,24);b.writeUtf(p.value,512);}
    public static Hk3EggUiPacket decode(FriendlyByteBuf b){return new Hk3EggUiPacket(b.readUtf(24),b.readUtf(512));}
    public static void handle(Hk3EggUiPacket p,Supplier<NetworkEvent.Context> supplier){var c=supplier.get();c.enqueueWork(()->{var user=c.getSender();if(user!=null){if(p.action.equals("dialogue"))Hk3EggDialogueActions.input(user,p.value);else if(p.action.startsWith("egg_"))Hk3EggUiReceipts.input(user,p.action,p.value);else if(p.action.equals("inventory")||p.action.equals("map_view"))Hk3EggViews.input(user,p.action);else Hk3EggPhone.input(user,p.action,p.value);}});c.setPacketHandled(true);}
}
