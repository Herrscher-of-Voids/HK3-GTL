package com.sirin.hk3gtl.common.recipe;

public final class Hk3ResearchProcessPorts {
    private Hk3ResearchProcessPorts() {}
    public record Ports(int itemsIn,int itemsOut,int fluidsIn,int fluidsOut) {}
    public static Ports get(String role){
        return switch(role){
            case "GT_ASSEMBLER" -> new Ports(16,2,5,2);
            case "GT_MIXER" -> new Ports(6,2,4,2);
            case "GT_CHEMICAL" -> new Ports(2,2,3,2);
            case "GT_LARGE_CHEMICAL" -> new Ports(4,2,4,2);
            case "GT_CHEMICAL_BATH" -> new Ports(8,2,4,3);
            case "GT_LASER_ENGRAVER", "GT_CUTTER" -> new Ports(2,2,1,1);
            case "GT_FORMING_PRESS" -> new Ports(6,2,1,1);
            case "GT_CANNER" -> new Ports(2,2,1,1);
            case "GT_FLUID_SOLIDIFIER" -> new Ports(1,1,1,0);
            case "GT_PACKER", "GT_VACUUM", "GT_COMPRESSOR", "GT_CENTRIFUGE", "GT_BENDER" -> new Ports(2,2,1,1);
            case "GT_BLAST" -> new Ports(2,2,1,1);
            case "GTL_SUPRACHRONAL_ASSEMBLY_LINE" -> new Ports(24,4,5,4);
            case "GTL_PRECISION_ASSEMBLER" -> new Ports(16,4,4,4);
            case "GTL_CIRCUIT_ASSEMBLY_LINE" -> new Ports(12,2,3,1);
            case "GTL_SPS" -> new Ports(6,2,3,1);
            case "NETWORK_INJECTION" -> new Ports(8,4,4,2);
            case "I01-1" -> new Ports(6,4,2,3);
            case "I02" -> new Ports(7,4,3,2);
            case "I04" -> new Ports(13,6,4,4);
            case "I05", "I06" -> new Ports(8,6,5,4);
            case "I07" -> new Ports(8,4,0,0);
            case "I09" -> new Ports(12,6,4,4);
            case "I10", "I15", "I28", "I30", "I31", "I39", "I41" -> new Ports(11,6,4,4);
            case "I11" -> new Ports(20,6,4,2);
            case "I12" -> new Ports(12,4,3,2);
            case "I14", "I45" -> new Ports(10,6,4,4);
            case "I16" -> new Ports(28,8,5,4);
            case "I17" -> new Ports(8,6,8,4);
            case "I25", "I26", "I27", "I29" -> new Ports(15,6,4,4);
            case "I33" -> new Ports(16,4,4,2);
            case "I37" -> new Ports(16,6,4,4);
            case "I40" -> new Ports(9,6,4,4);
            case "I42" -> new Ports(18,6,5,4);
            default -> {
                if(!role.matches("I(0[3-9]|[1-3][0-9]|4[0-5])|I01-[234]|W(0[1-9]|1[0-5])|H01"))
                    throw new IllegalArgumentException("Unknown recipe role "+role);
                yield new Ports(role.startsWith("W")?24:8,role.startsWith("W")?8:6,role.startsWith("W")?5:4,4);
            }
        };
    }
    public static void validate(Hk3ResearchProcessPlans.Plan p){
        var limit=get(p.role());
        if(p.inputs().size()+p.catalysts().size()+(p.circuit()>0?1:0)>limit.itemsIn()||p.outputs().size()+p.chancedOutputs().size()>limit.itemsOut()
                ||p.fluidInputs().size()>limit.fluidsIn()||p.fluidOutputs().size()>limit.fluidsOut())
            throw new IllegalArgumentException("Recipe exceeds registered ports "+p.id());
    }
}
