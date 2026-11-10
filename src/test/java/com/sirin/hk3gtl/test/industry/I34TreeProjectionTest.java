package com.sirin.hk3gtl.test.industry;

import com.sirin.hk3gtl.client.tree.Hk3TreeProjectionModel;
import java.io.ByteArrayInputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import com.google.gson.JsonParser;

/** 确认版完整树影、根冠范围及截断资源拒绝，不依赖客户端伪造成型。 */
public final class I34TreeProjectionTest {
    public static void main(String[] args)throws Exception{
        var bytes=Files.readAllBytes(Path.of("src/main/resources/assets/hk3gtl/effects/i34_tree.bin.gz"));
        var model=Hk3TreeProjectionModel.read(new ByteArrayInputStream(bytes));
        check(model.positions().length==71948*3&&model.colors().length==71948*3,"完整曲线顶点");
        check(model.points().length==15567*6&&model.flows().length==720,"完整节点与光流");
        float minY=Float.POSITIVE_INFINITY,maxY=Float.NEGATIVE_INFINITY;
        for(int i=1;i<model.positions().length;i+=3){minY=Math.min(minY,model.positions()[i]);maxY=Math.max(maxY,model.positions()[i]);}
        check(minY<-28&&maxY>158,"根系与树冠未裁切");
        for(var flow:model.flows())check(flow.offset()>=0&&flow.offset()<1&&flow.speed()>0&&flow.size()>0&&flow.samples().length==195,"光流采样有效");
        for(String name:new String[]{"i34_tree","i34_tree_lines"}){
            var shader=JsonParser.parseString(Files.readString(Path.of("src/main/resources/assets/hk3gtl/shaders/core/"+name+".json"))).getAsJsonObject();
            var blend=shader.getAsJsonObject("blend");
            check(blend!=null&&blend.get("srcrgb").getAsString().equals("srcalpha")&&blend.get("dstrgb").getAsString().equals("one"),"柔光必须使用透明叠加，禁止退回不透明橙块");
        }
        try{Hk3TreeProjectionModel.read(new ByteArrayInputStream(Arrays.copyOf(bytes,bytes.length/2)));throw new AssertionError("错误接受截断树影");}catch(java.io.IOException expected){}
        System.out.println("PASS: I34确认版71948顶点、15567光点、720光流，根冠完整，截断资源拒绝。");
    }
    private static void check(boolean value,String reason){if(!value)throw new AssertionError(reason);}
}
