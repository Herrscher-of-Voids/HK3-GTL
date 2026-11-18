package com.sirin.hk3gtl.common.multiblock.build;

import com.gregtechceu.gtceu.api.machine.multiblock.MultiblockControllerMachine;
import com.gregtechceu.gtceu.api.machine.IMachineBlockEntity;
import com.gregtechceu.gtceu.api.machine.feature.multiblock.IMultiPart;
import com.gregtechceu.gtceu.api.pattern.MultiblockState;
import com.gregtechceu.gtceu.api.pattern.TraceabilityPredicate;
import com.gregtechceu.gtceu.api.pattern.error.PatternStringError;
import com.sirin.hk3gtl.mixin.gtceu.Hk3MultiblockStateAccess;
import it.unimi.dsi.fastutil.longs.Long2ObjectOpenHashMap;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Set;

/** 分批实读与具体机器的成型状态分离，不以建造计数授予成型。 */
public interface Hk3IntegrityHost {
    MultiblockControllerMachine integrityController();
    void integrityFailed(String reason);
    void integrityPassed(Direction facing);
    default void acceptVerifiedPlan(Hk3BuildPlan plan) {}
    void acceptVerifiedInterfaces(Set<BlockPos> positions);
    void acceptInterfaceChunks(Hk3InterfaceChunks chunks);
    Set<BlockPos> verifiedInterfaces();
    default boolean matchVerifiedInterfaces(MultiblockState state, TraceabilityPredicate predicate, boolean savePredicate) {
        var access=(Hk3MultiblockStateAccess)(Object)state;
        for(var limit:predicate.limited)state.getGlobalCount().put(limit,0);
        for(var pos:verifiedInterfaces()) {
            if(!access.hk3gtl$update(pos,predicate)||!predicate.test(state))return false;
            if(state.getTileEntity() instanceof IMachineBlockEntity entity&&entity.getMetaMachine() instanceof IMultiPart part) {
                if(part.isFormed()&&!part.canShared()&&!part.hasController(state.controllerPos)) {
                    state.setError(new PatternStringError("接口仓已被其他控制器占用"));return false;
                }
                state.getMatchContext().getOrCreate("parts",HashSet::new).add(part);
            }
            state.addPosCache(pos);
            state.getMatchContext().getOrCreate("ioMap",Long2ObjectOpenHashMap::new).put(pos.asLong(),state.io);
            if(savePredicate)state.getMatchContext().getOrCreate("predicates",HashMap::new).put(pos,predicate);
        }
        for(var limit:predicate.limited) {
            int count=state.getGlobalCount().getOrDefault(limit,0);
            if(count<limit.minCount||limit.maxCount>=0&&count>limit.maxCount) {
                state.setError(new PatternStringError("通用接口数量不符合机器要求"));return false;
            }
        }
        return true;
    }
    default boolean captureFarView() { return true; }
}
