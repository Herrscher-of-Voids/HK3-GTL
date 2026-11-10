package com.sirin.hk3gtl.test.circuit;

import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import com.sirin.hk3gtl.common.item.Hk3CircuitCatalog;
import java.util.Arrays;
import java.util.Locale;

/**
 * 【变更记录 #1】2026-09-30 02:21:00（内测5修订107）
 * 删除：无。新增：16档索引、唯一注册键、旧标签撤除和128件模型资源检查。
 * 修改：无运行时业务；用途：防止只改显示、错位映射、遗留别名或资源失联。
 */
public final class VoltageRegistryKeyTest {
    private static int checks;
    private static final String[] KEYS = "hbv hcv hrv hdv qsv qcv qev qav imv icv irv iwv wfv wsv civ cev".split(" ");
    public static void main(String[] args) throws Exception {
        check(Arrays.equals(KEYS,Hk3Tiers.VOLTAGE_KEYS),"16档唯一注册键");
        int[] constants = {Hk3Tiers.HBV,Hk3Tiers.HCV,Hk3Tiers.HRV,Hk3Tiers.HDV,
                Hk3Tiers.QSV,Hk3Tiers.QCV,Hk3Tiers.QEV,Hk3Tiers.QAV,
                Hk3Tiers.IMV,Hk3Tiers.ICV,Hk3Tiers.IRV,Hk3Tiers.IWV,
                Hk3Tiers.WFV,Hk3Tiers.WSV,Hk3Tiers.CIV,Hk3Tiers.CEV};
        String[] legacyGroups={"abyss","imaginary","quantum","finality"};
        String[] legacyShort={"ab","im","qt","fn"};
        String[] roman={"i","ii","iii","iv"};
        String[] components={"electric_motor","electric_pump","electric_piston","conveyor_module",
                "robot_arm","sensor","emitter","field_generator"};
        for(int i=0;i<16;i++) {
            int tier=15+i; String key=KEYS[i]; String legacy=legacyGroups[i/4]+"_"+(i%4+1);
            check(constants[i]==tier && Hk3Tiers.ALL_NEW_TIERS[i]==tier,"tier索引不变");
            check(Hk3Tiers.voltageKey(tier).equals(key),"查询正式键");
            check(Hk3Tiers.VOLTAGE_SYMBOLS[i].equals(key.toUpperCase(Locale.ROOT)),"注册键对应显示缩写");
            check(Hk3CircuitCatalog.tagId(tier).toString().equals("forge:circuits/"+key),"实际标签入口");
            for(String ns:new String[]{"forge","gtceu"}) {
                check(resource("data/"+ns+"/tags/items/circuits/"+key+".json"),"正式标签存在");
                check(!resource("data/"+ns+"/tags/items/circuits/"+legacy+".json"),"旧长键删除");
                check(!resource("data/"+ns+"/tags/items/circuits/"+legacyShort[i/4]+"-"+roman[i%4]+".json"),"旧罗马别名删除");
            }
            for(String c:components) {
                check(resource("assets/hk3gtl/models/item/"+c+"_"+key+".json"),"部件新模型存在");
                check(!resource("assets/hk3gtl/models/item/"+c+"_"+legacy+".json"),"部件旧模型删除");
            }
        }
        for(var entry:Hk3CircuitCatalog.ENTRIES) {
            check(resource("assets/hk3gtl/models/item/"+entry.id()+".json"),"52电路模型存在");
            if(entry.primary())check(entry.id().startsWith(KEYS[entry.tier()-15]+"_"),"16个主电路逐tier映射");
        }
        for(var field:Hk3Tiers.class.getFields())check(!field.getName().matches("(ABYSS|IMAGINARY|QUANTUM|FINALITY)_[1-4]"),"删除旧公开常量");
        System.out.println("正式电压键迁移检查通过："+checks+"项；16档、52电路、128部件；不代表游戏存档验收。");
    }
    private static boolean resource(String path) { return VoltageRegistryKeyTest.class.getClassLoader().getResource(path)!=null; }
    private static void check(boolean ok,String message) { checks++;if(!ok)throw new AssertionError(message); }
}
