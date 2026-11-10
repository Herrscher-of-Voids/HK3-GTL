package com.sirin.hk3gtl.test.circuit;

import com.google.gson.*;
import com.sirin.hk3gtl.common.constants.Hk3VoltagePalette;
import com.sirin.hk3gtl.common.item.Hk3CircuitCatalog;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;
import javax.imageio.ImageIO;

/**
 * 【变更记录 #1】2026-09-30 03:25:21（内测5修订108）
 * 删除：无。新增：16档批准色、232张贴图、52电路实际tier和动画资源回归。
 * 修改：纳入check。用途：拦截错色、漏图、透明度破坏和旧生成器覆盖，不代替游戏验收。
 */
public final class VoltagePaletteTest {
    private static int checks;
    private static final String BASE="data/hk3gtl/catalog/";
    private static final int[] APPROVED={0x428DFF,0xF4AE40,0xC93F63,0x48C9A3,0x91DCEB,0x5969C8,0xE56A38,0xB8524A,0x9B75CA,0xB68A4F,0xCECDA2,0xCE54A8,0xF3A9CF,0xBDA9F3,0x52BBD6,0xDCC17B};
    public static void main(String[] args) throws Exception {
        var palette=json(BASE+"voltage_palette.json").getAsJsonArray("palettes");
        check(palette.size()==16,"16档色卡");
        for(int i=0;i<16;i++) {
            var p=palette.get(i).getAsJsonObject();int tier=15+i;
            check(p.get("tier").getAsInt()==tier,"tier顺序");
            check(Integer.parseInt(p.get("main").getAsString().substring(1),16)==APPROVED[i],"批准主色");
            check(Hk3VoltagePalette.main(tier)==APPROVED[i],"Java与色卡一致");
            check(Hk3VoltagePalette.text(tier)==Integer.parseInt(p.get("textDark").getAsString().substring(1),16),"文字色一致");
            check(Hk3VoltagePalette.legacy(tier).matches("§[0-9a-f]§l"),"传统格式兼容");
        }
        check(palette.get(14).getAsJsonObject().get("role").getAsString().contains("贝拉"),"CIV贝拉");
        check(palette.get(15).getAsJsonObject().get("role").getAsString().contains("女王"),"CEV女王");
        boolean invalid=false;try{Hk3VoltagePalette.main(14);}catch(IllegalArgumentException expected){invalid=true;}check(invalid,"不改MAX及以下");
        var art=json(BASE+"voltage_art108.json").getAsJsonArray("entries");
        check(art.size()==232,"232张现有贴图");
        var byId=new HashMap<String,JsonObject>();var counts=new HashMap<String,Integer>();
        for(var raw:art) {
            var e=raw.getAsJsonObject();String id=e.get("id").getAsString();
            check(byId.put(id,e)==null,"唯一物品");counts.merge(e.get("kind").getAsString(),1,Integer::sum);
            String path=e.get("destination").getAsString();byte[] png=bytes(path);
            check(hash(png).equals(e.get("sha256").getAsString()),"贴图未被覆盖:"+id);
            check(!hash(png).equals(e.get("baseline_sha256").getAsString()),"贴图实际已换色:"+id);
            var image=ImageIO.read(new ByteArrayInputStream(png));var size=e.getAsJsonArray("size");
            check(image.getWidth()==size.get(0).getAsInt() && image.getHeight()==size.get(1).getAsInt(),"尺寸及帧数保持");
            byte[] alpha=new byte[image.getWidth()*image.getHeight()];int offset=0;
            for(int y=0;y<image.getHeight();y++)for(int x=0;x<image.getWidth();x++)alpha[offset++]=(byte)(image.getRGB(x,y)>>>24);
            check(hash(alpha).equals(e.get("alpha_sha256").getAsString()),"透明轮廓保持");
            var meta=e.get("mcmeta_sha256");
            if(meta.isJsonNull())check(VoltagePaletteTest.class.getClassLoader().getResource(path+".mcmeta")==null,"未新增动画");
            else check(hash(bytes(path+".mcmeta")).equals(meta.getAsString()),"动画节奏保持");
            var model=json("assets/hk3gtl/models/item/"+id+".json");
            check(path.equals("assets/hk3gtl/textures/"+model.getAsJsonObject("textures").get("layer0").getAsString().split(":")[1]+".png"),"实际模型接线");
        }
        check(counts.equals(Map.of("component",128,"formal_circuit",52,"archived_circuit",48,"platform_pcb",4)),"各类数量");
        for(var entry:Hk3CircuitCatalog.ENTRIES)check(byId.get(entry.id()).get("tier").getAsInt()==entry.tier(),"电路实际tier着色");
        String[] platforms={"honkai_lattice","quantum_coherence","imaginary_topology","civilization_endurance"};
        for(int i=0;i<4;i++)check(byId.get(platforms[i]+"_printed_circuit_board").get("tier").getAsInt()==15+i*4,"共用PCB平台首档");
        System.out.println("Voltage palette: "+checks+" checks passed; game rendering acceptance pending.");
    }
    private static byte[] bytes(String name) throws IOException {
        try(var in=VoltagePaletteTest.class.getClassLoader().getResourceAsStream(name)) {if(in==null)throw new IOException("Missing "+name);return in.readAllBytes();}
    }
    private static JsonObject json(String name) throws IOException { return JsonParser.parseString(new String(bytes(name),StandardCharsets.UTF_8)).getAsJsonObject(); }
    private static String hash(byte[] data) throws Exception {return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(data));}
    private static void check(boolean ok,String message) {checks++;if(!ok)throw new AssertionError(message);}
}
