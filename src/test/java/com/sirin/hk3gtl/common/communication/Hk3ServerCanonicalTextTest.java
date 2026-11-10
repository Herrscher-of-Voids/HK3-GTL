package com.sirin.hk3gtl.common.communication;

import com.google.gson.JsonParser;
import com.sirin.hk3gtl.common.narrative.Hk3ApprovedProse;
import com.sirin.hk3gtl.common.narrative.Hk3ApprovedText;
import net.minecraft.locale.Language;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.FormattedText;
import net.minecraft.util.FormattedCharSequence;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.UUID;

/** 【变更记录 #1】2026-10-31 02:02:28（第1次备注 · 修订187）：新增专服无模组译表回归；执行真实服务正文入口，验证资源逐字一致和缺键拒绝，不代替联网客户端验收。 */
public final class Hk3ServerCanonicalTextTest {
    private static int checks;
    private static void check(boolean value,String label){if(!value)throw new AssertionError(label);checks++;}
    private static void reject(Runnable action,String label){
        try{action.run();}catch(IllegalArgumentException|IllegalStateException expected){checks++;return;}
        throw new AssertionError(label);
    }
    public static void main(String[] args) throws Exception {
        Language original=Language.getInstance();
        String firstKey="hk3gtl.approved.communication.A01.line.0";
        System.out.println("默认Language是否载入模组首信键："+original.has(firstKey));
        Language.inject(new Language(){
            @Override public String getOrDefault(String key,String fallback){return fallback;}
            @Override public boolean has(String key){return false;}
            @Override public boolean isDefaultRightToLeft(){return false;}
            @Override public FormattedCharSequence getVisualOrder(FormattedText text){return FormattedCharSequence.EMPTY;}
        });
        try(var stream=Hk3ServerCanonicalTextTest.class.getResourceAsStream("/assets/hk3gtl/lang/zh_cn.json")){
            check(Component.translatable(firstKey).getString().equals(firstKey),"重现专服缺译表时旧实现发送裸键");
            check(stream!=null,"批准中文资源存在");
            var lang=JsonParser.parseReader(new InputStreamReader(stream,StandardCharsets.UTF_8)).getAsJsonObject();
            var diplomacy=new Hk3DiplomacyData();UUID team=UUID.randomUUID();
            int communication=0;
            for(var entry:Hk3ApprovedProse.system("communication")){
                var expected=new StringBuilder();
                for(int i=0;i<entry.lineCount();i++){
                    if(i>0)expected.append("\n\n");
                    expected.append(lang.get(entry.key()+".line."+i).getAsString());
                }
                String id=entry.id().substring("communication.".length()),body=expected.toString();
                check(Hk3ApprovedText.body(entry).equals(body),"解析器逐字保留批准正文："+id);
                check(Hk3DiplomacyService.prose(id).equals(entry.speaker()+"\n\n"+body),"五方实际正文入口不依赖Language："+id);
                check(Hk3DiplomacyService.title(id).equals(entry.speaker()+"｜"+lang.get(entry.key()+".title").getAsString()),"标题保留批准原文："+id);
                String personal=Hk3PersonalCommunicationService.canonicalBody(diplomacy,team,id);
                check(personal.contains(body)&&!personal.contains("hk3gtl.approved."),"个人补谈实际入口没有裸键："+id);
                communication++;
            }
            check(communication==35,"覆盖全部35篇批准交流正文");
            for(int doc=0;doc<6;doc++){
                var entry=Hk3ApprovedProse.get("communication.A0"+(doc+1));
                String body=Hk3TeamContactService.canonicalBody(doc);
                check(body.equals(Hk3ApprovedText.body(entry))&&!body.contains("hk3gtl.approved."),"首信实际发包正文源："+doc);
            }
            check(Hk3TeamContactService.canonicalBody(0).startsWith("尊敬的异界先行者："),"实际首信含中文称呼而不是翻译键");
            for(var entry:Hk3FactionLetters.all())check(Hk3DiplomacyService.prose(entry.id()).equals(entry.speaker()+"\n\n"+String.join("\n\n",entry.lines())),"独立批准首信原文保留："+entry.id());
            reject(()->Hk3ApprovedText.text(firstKey+"_missing"),"缺键必须拒绝，不能回退裸键");
            reject(()->Hk3ApprovedText.body(null),"缺正文目录必须拒绝");
            reject(()->Hk3DiplomacyService.prose("missing_approved_document"),"未知正文不能回退空白");
            reject(()->Hk3DiplomacyService.title("missing_approved_document"),"未知标题不能回退ID");
            reject(()->Hk3TeamContactService.canonicalBody(6),"错误首信编号拒绝");
        }finally{Language.inject(original);}
        System.out.println("Hk3ServerCanonicalTextTest："+checks+"项通过；仅为专服缺译表正文回归，不代表客户端运行已验收。");
    }
}
