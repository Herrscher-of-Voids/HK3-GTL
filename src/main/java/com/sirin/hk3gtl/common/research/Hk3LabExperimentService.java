package com.sirin.hk3gtl.common.research;



/**
 * 【文件职责／本轮边界】按获批样件与工装实际扣入托管，ALE使用MAX、ERM使用QSV，只有成功实验才记证据。
 * 【变更记录 #1】2026-09-29 21:06:40（第 1 次编号备注 · 内测5修订100）
 * 删除：取消已被批准规则替代的研究个人独占、旧数值或在线限定分支；历史备注与其他系统保留。
 * 新增／修改：按获批样件与工装实际扣入托管，ALE使用MAX、ERM使用QSV，只有成功实验才记证据。
 * 用途：接通实际证据→付款→研究完成与权限检查；不授予缺真实证据的课题。
 * 边界：编译和账本测试不代表游戏验收；S02至S05正式结构及未接线课题仍未完成。
 * 追溯：logs/research-mainline-r100；R100_FINAL_RECORD。
 */

import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.core.registries.Registries;
import net.minecraft.tags.TagKey;
import net.minecraft.resources.ResourceLocation;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.registration.Hk3IndustrialContent;
import java.util.*;
import static com.sirin.hk3gtl.common.research.Hk3ResearchMaterialPayment.Requirement;

/** 修订100 · 2026-09-29：仅注册审核过的固定实验；不把样件持有当成功证据。 */
/**
 * 【变更记录 #2】2026-09-29 23:37:35（内测5修订101）
 * 删除：本轮被替代的单前置或旧提示分支；其余历史保留。
 * 新增／修改：OPR耗用三张纸并托管三类回收凭据，成功仅记实验证据，取消沿用原付款人退款。
 * 用途：补足研究接线并如实保留未接物理执行器及结构审批边界。
 * 追溯：logs/research-mainline-r101；R101_FINAL_RECORD。
 */
/**
 * 【变更记录 #3】2026-11-04 01:23:43（第3次备注 · 内测5修订194）
 * - 删除：实验托管仅内存扣料的提交路径。
 * - 新增：Hk3ResearchPayment持久事务；修改：真实材料、工装和凭据快照随工单一起落盘。
 * - 用途：实验开题硬崩恢复；失败不记成功，成功和取消仍沿原工具退还规则。
 */
public final class Hk3LabExperimentService {
    private Hk3LabExperimentService() {}
    private static Requirement tag(String id,int count) {
        var tag=TagKey.create(Registries.ITEM,new ResourceLocation(id));
        return new Requirement(s -> s.is(tag),count,false);
    }
    public static Hk3ResearchStartService.Result start(ServerPlayer player,UUID scope,String facility,int lab,boolean available,String research) {
        var data=Hk3ResearchData.get(player);
        if(!available || !data.isMember(player.getUUID(),scope))return Hk3ResearchStartService.Result.UNAVAILABLE;
        String id=Hk3LabExperimentRules.next(research,data.hasLabBaseline(scope));
        var spec=Hk3LabExperimentRules.get(id);var topic=Hk3ResearchCatalog.bundled().get(research);
        if(spec==null || topic==null || lab<spec.lab() || !topic.prerequisites().stream().allMatch(p -> data.completed(scope,p)))return Hk3ResearchStartService.Result.LOCKED;
        if(data.completed(scope,research) || data.hasExperiment(scope,research))return Hk3ResearchStartService.Result.COMPLETED;
        if(data.displayJob(scope,research)!=null)return Hk3ResearchStartService.Result.RUNNING;
        List<Requirement> needs=new ArrayList<>();
        if (research.equals("RN-OPR") && !data.recoveryAuditReady(scope)) return Hk3ResearchStartService.Result.LOCKED;
        long eut=Hk3Values.VA_LONG[com.gregtechceu.gtceu.api.GTValues.MAX];
        if(research.equals("RN-ALE")) {
            needs.add(tag("forge:plates/soulium",4));needs.add(tag("forge:fine_wires/soulium",4));
            needs.add(new Requirement(s -> s.is(Hk3IndustrialContent.items().get("etched_circuit_layer").get()),2,false));
            needs.add(new Requirement(s -> s.is(Items.PAPER),4,false));
            needs.add(new Requirement(s -> s.is(org.gtlcore.gtlcore.common.data.GTLItems.SENSOR_MAX.asItem()),1,true));
        } else if (research.equals("RN-OPR")) {
            needs.add(new Requirement(s -> s.is(Items.PAPER),3,false));
        } else {
            needs.add(tag("gtceu:circuits/max",2));needs.add(new Requirement(s -> s.is(Items.PAPER),4,false));
            if(!spec.baseline())needs.add(new Requirement(s -> s.is(Hk3IndustrialContent.items().get("imitation_corruption_core").get()),1,true));
            // 新16档中QSV为第19档，沿用正式电压数组，不使用废弃四档名称。
            eut=Hk3Values.VA_LONG[19];
        }
        var payment=Hk3ResearchMaterialPayment.prepareExperiment(player.getInventory(),needs);
        if(payment==null)return Hk3ResearchStartService.Result.INSUFFICIENT;
        var receipt=payment.receipt();
        if(research.equals("RN-OPR"))receipt.put("RecoveryProofs",data.recoveryProofs(scope));
        var quote=Hk3ResearchData.withPayer(new Hk3ResearchWorkQueue.Quote(id,facility,lab,spec.ticks(),eut,"materials",receipt),player.getUUID());
        boolean started=Hk3ResearchPayment.commit(player,data,() -> data.startResearch(scope,quote,true,payment::commit));
        if(started)player.inventoryMenu.broadcastChanges();
        return started?Hk3ResearchStartService.Result.STARTED:Hk3ResearchStartService.Result.CAPACITY;
    }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
