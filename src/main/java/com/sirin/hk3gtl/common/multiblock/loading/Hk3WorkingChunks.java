package com.sirin.hk3gtl.common.multiblock.loading;

import com.gregtechceu.gtceu.api.machine.multiblock.MultiblockControllerMachine;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import org.gtlcore.gtlcore.api.machine.multiblock.IModularMachineHost;
import org.gtlcore.gtlcore.api.machine.multiblock.IModularMachineModule;
import org.gtlcore.gtlcore.common.data.machines.AdvancedMultiBlockMachineA;
import org.gtlcore.gtlcore.common.machine.multiblock.electric.BlockConversionRoomMachine;
import org.gtlcore.gtlcore.common.machine.multiblock.electric.GreenhouseMachine;
import org.gtlcore.gtlcore.common.machine.multiblock.electric.SlaughterhouseMachine;
import org.gtlcore.gtlcore.common.machine.multiblock.electric.SpaceProbeSurfaceReceptionMachine;
import org.gtlcore.gtlcore.common.machine.multiblock.generator.ChemicalEnergyDevourerMachine;
import org.gtlcore.gtlcore.common.machine.multiblock.generator.DysonSphereMachine;
import org.gtlcore.gtlcore.common.machine.multiblock.generator.GTLLargeCombustionEngineMachine;
import java.util.function.Consumer;

/** 只保留原机器运行期真实访问的工作点，不保留静态外壳。 */
final class Hk3WorkingChunks {
    private Hk3WorkingChunks(){}

    static void collect(MultiblockControllerMachine controller,Consumer<BlockPos> retain){
        var pos=controller.getPos();
        if(controller instanceof BlockConversionRoomMachine){
            int radius=controller.getDefinition()==AdvancedMultiBlockMachineA.LARGE_BLOCK_CONVERSION_ROOM?4:2;
            for(int x=-radius;x<=radius;x++)for(int z=-radius;z<=radius;z++)retain.accept(pos.offset(x,0,z));
        }
        if(controller instanceof GreenhouseMachine)
            for(int x=-3;x<=3;x++)for(int z=-3;z<=3;z++)
                if((x!=0||z!=0)&&(Math.abs(x)<=1||Math.abs(z)<=1))retain.accept(pos.offset(x,3,z));
        if(controller instanceof ChemicalEnergyDevourerMachine||controller instanceof GTLLargeCombustionEngineMachine){
            int radius=controller instanceof ChemicalEnergyDevourerMachine?3:1;
            var front=pos.relative(controller.getFrontFacing());
            for(int i=-radius;i<=radius;i++)
                retain.accept(controller.getFrontFacing().getAxis()==Direction.Axis.Z?front.offset(i,0,0):front.offset(0,0,i));
        }
        if(controller instanceof SpaceProbeSurfaceReceptionMachine){
            retain.accept(pos.offset(4,9,0));retain.accept(pos.offset(-4,9,0));
            retain.accept(pos.offset(0,9,4));retain.accept(pos.offset(0,9,-4));
        }
        if(controller instanceof DysonSphereMachine sphere){
            var points=sphere.getCachedCheckPositions();
            if(points!=null)points.forEach(retain);
        }
        if(controller instanceof SlaughterhouseMachine)
            for(var direction:Direction.Plane.HORIZONTAL){
                retain.accept(pos.relative(direction));retain.accept(pos.relative(direction,3).above());
            }
        if(controller instanceof IModularMachineHost<?> host)
            for(var point:host.getModuleScanPositions())retain.accept(point);
        if(controller instanceof IModularMachineModule<?,?> module)
            for(var point:module.getHostScanPositions())retain.accept(point);
    }
}
