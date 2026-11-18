package com.sirin.hk3gtl.common.research;



/**
 * 【文件职责／本轮边界】按获批样件与工装实际扣入托管，ALE使用MAX、ERM使用QSV，只有成功实验才记证据。
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

public final class Hk3LabExperimentService {
    private Hk3LabExperimentService() {}
    private static Requirement tag(String id,int count) { return tag(id,count,false); }
    private static Requirement tag(String id,int count,boolean tool) {
        var tag=TagKey.create(Registries.ITEM,new ResourceLocation(id));
        return new Requirement(s -> s.is(tag),count,tool);
    }
    public static Hk3ResearchStartService.Result start(ServerPlayer player,UUID scope,String facility,int lab,boolean available,String research) {
        var data=Hk3ResearchData.get(player);
        if(!available || !data.isMember(player.getUUID(),scope))return Hk3ResearchStartService.Result.UNAVAILABLE;
        String id=Hk3LabExperimentRules.next(research,data.hasLabBaseline(scope));
        var spec=Hk3LabExperimentRules.get(id);var topic=Hk3ResearchCatalog.bundled().get(research);
        if(spec==null || topic==null || lab<spec.lab() || !topic.prerequisites().stream().allMatch(p -> data.completed(scope,p)))return Hk3ResearchStartService.Result.LOCKED;
        if(data.completed(scope,research) || data.hasExperiment(scope,research))return Hk3ResearchStartService.Result.COMPLETED;
        boolean awaitingAid=research.equals("RN-ERM") && data.awaitingLabAid(scope);
        if(data.displayJob(scope,research)!=null && !awaitingAid)return Hk3ResearchStartService.Result.RUNNING;
        var baseline=data.researchJob(scope,"LAB-ERM-BASE");
        if(awaitingAid && !baseline.quote().facility().equals(facility))return Hk3ResearchStartService.Result.UNAVAILABLE;
        List<Requirement> needs=new ArrayList<>();
        if (research.equals("RN-OPR") && !data.recoveryAuditReady(scope)) return Hk3ResearchStartService.Result.LOCKED;
        long eut=Hk3Values.VA_LONG[com.gregtechceu.gtceu.api.GTValues.MAX];
        if(research.equals("RN-ALE")) {
            needs.add(tag("forge:plates/soulium",64,true));
            needs.add(tag("forge:fine_wires/soulium",64,true));
            needs.add(new Requirement(s -> s.is(Hk3IndustrialContent.items().get("etched_circuit_layer").get()),16,true));
            needs.add(new Requirement(s -> s.is(net.minecraft.core.registries.BuiltInRegistries.ITEM.get(
                    new ResourceLocation("hk3gtl","sensor_hrv"))),2,true));
            needs.add(new Requirement(s -> s.is(Items.PAPER),16,false));
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
        if(awaitingAid)receipt.putUUID("BaselineJob",baseline.id());
        if(research.equals("RN-OPR"))receipt.put("RecoveryProofs",data.recoveryProofs(scope));
        var quote=Hk3ResearchData.withPayer(new Hk3ResearchWorkQueue.Quote(id,facility,lab,spec.ticks(),eut,"materials",receipt),player.getUUID());
        boolean started=Hk3ResearchPayment.commit(player,data,() -> data.startResearch(scope,quote,true,payment::commit));
        if(started)player.inventoryMenu.broadcastChanges();
        return started?Hk3ResearchStartService.Result.STARTED:Hk3ResearchStartService.Result.CAPACITY;
    }
}

