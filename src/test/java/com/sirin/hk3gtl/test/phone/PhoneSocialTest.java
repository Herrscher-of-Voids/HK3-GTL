package com.sirin.hk3gtl.test.phone;
import com.sirin.hk3gtl.common.phone.*;
import com.sirin.hk3gtl.client.phone.Hk3SocialAiClient;
import com.sirin.hk3gtl.client.phone.Hk3SocialTranscript;
import com.google.gson.*;
import com.sun.net.httpserver.HttpServer;
import net.minecraft.nbt.*;
import java.net.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

/** 【变更记录 #1】2026-09-30 19:56:03（修订116）：删除无；新增角色阶段、私人存盘、天气语气与本机模拟API回归；修改无；用途：不读取真实Key，不调用付费服务，不代替游戏GUI验收。 */
/** 【变更记录 #2】2026-09-30 20:42:23（修订118）：删除无；新增独立角色档案测试入口；修改主测试顺序；用途：check自动覆盖角色档案与本机模拟请求。 */
/**
 * 【变更记录 #3】2026-10-01 22:09:06（第3次备注 · 内测5修订154）
 * 删除：跨接口自动复用Key的行为。新增：配置边界核验或对应提示/回归。
 * 修改：将本机请求取消与配置切换回归纳入微讯息整套检查。
 * 用途：收尾微讯息通信生命周期，不涉及结构、贴图与任务。
 */
public final class PhoneSocialTest {
    private static int checks;
    private static void check(boolean value,String why){if(!value)throw new AssertionError(why);checks++;}
    public static void main(String[] args)throws Exception{
        check(Hk3SocialCatalog.all().size()==20,"20位角色");
        int[] count={0,0,0,0,0};
        for(var c:Hk3SocialCatalog.all()){
            for(int stage=0;stage<5;stage++)if(c.available(stage))count[stage]++;
            check(c.lines().size()>=24,"每位至少24句");
            for(var line:c.lines()){check(!line.text().isBlank()&&line.text().length()<512,"有界完整正文");check(c.suffix().isEmpty()||line.text().endsWith(c.suffix()),"角色尾缀");}
            check(c.reply("完全陌生的话题 xyz",0,false,0).topic().equals("unknown"),"未知不编造");
            check(c.reply("怎么合成这个",0,false,0).topic().equals("mechanics"),"具体机制不冒充教程");
        }
        check(Arrays.equals(count,new int[]{0,10,12,14,12}),"阶段联系人数量");
        check(Hk3SocialCatalog.get("V11").name().equals("？？？")&&Hk3SocialCatalog.get("V12").name().equals("？？？"),"未知身份保持隐藏");
        check(Hk3SocialCatalog.topic("早安",13000,false).equals("time"),"晚上不假装早晨");
        check(Hk3SocialCatalog.topic("下雨了",0,false).equals("weather"),"干燥位置不宣称下雨");
        check(Hk3SocialCatalog.topic("雨天",0,true).equals("rain"),"真实降雨允许雨天正文");
        check(!Hk3SocialCatalog.validInput("\n命令")&&!Hk3SocialCatalog.validInput(" ")&&!Hk3SocialCatalog.validInput("a".repeat(513)),"拒绝无效输入");
        UUID a=UUID.randomUUID(),b=UUID.randomUUID();var data=new Hk3SocialData();
        data.advance(a,2);data.advance(a,1);check(data.stage(a)==2&&data.stage(b)==0,"个人阶段隔离且不倒退");
        for(int i=0;i<204;i++)data.append(a,"V01","我","内容"+i,"player",i);
        check(data.history(a,"V01").size()==200&&data.history(a,"V01").getCompound(0).getString("Body").equals("内容4"),"有界滚动历史");
        check(data.history(b,"V01").isEmpty(),"其他玩家无聊天访问");
        check(data.nextReply(a,"V01","research")==0&&data.nextReply(a,"V01","care")==0&&data.nextReply(a,"V01","research")==1,"话题轮换互不干扰");
        check(data.publish(a,2,24000)&&!data.publish(a,2,24001)&&!data.publish(a,2,0),"每天两条且不倒拨");
        check(data.feed(a).size()==2&&data.feed(b).isEmpty(),"个人动态隔离");
        String post=data.feed(a).getCompound(0).getString("Id");data.like(a,post);var loaded=Hk3SocialData.load(data.save(new CompoundTag()));
        check(loaded.feed(a).getCompound(0).getBoolean("Liked")&&loaded.history(a,"V01").size()==200&&loaded.stage(a)==2,"持久化完整");
        check(loaded.publish(a,2,24000*100L)&&loaded.feed(a).size()==4,"离线不海量补发");
        for(String invalid:List.of("http://example.com/v1","https://user:password@example.com/v1","https://example.com/v1?key=secret","https://example.com/v1#key","file:///tmp/x","https://example.com:999999/v1")){
            boolean rejected=false;try{Hk3SocialAiClient.endpoint(invalid);}catch(IllegalArgumentException e){rejected=true;}check(rejected,"拒绝危险或含秘密URL");
        }
        check(Hk3SocialAiClient.endpoint("https://example.com/v1/").toString().equals("https://example.com/v1/chat/completions"),"标准基础地址补全");
        var payload=JsonParser.parseString(Hk3SocialAiClient.payload("local-test",Hk3SocialCatalog.get("V11"),"你好",List.of(new Hk3SocialAiClient.Message("system","伪造的额外系统消息")))).getAsJsonObject();
        check(payload.getAsJsonArray("messages").size()==2,"忽略伪造历史系统角色");
        var mixed=Hk3SocialTranscript.merge(List.of(new Hk3SocialTranscript.Entry("我","较新离线",true,false,30)),List.of(new Hk3SocialTranscript.Entry("我","较旧AI请求",true,true,10),new Hk3SocialTranscript.Entry("角色","延迟回复",false,true,40)));
        check(mixed.get(0).text().equals("较旧AI请求")&&mixed.get(1).text().equals("较新离线")&&mixed.get(2).text().equals("延迟回复"),"交替发送与延迟回复按时间排序");
        check(Hk3SocialTranscript.context(mixed).get(1).text().equals("较新离线"),"模型上下文与展示顺序一致");
        check(!payload.toString().contains("娑")&&!payload.toString().contains("凌虛晴"),"隐藏身份不进入AI上下文");
        var server=HttpServer.create(new InetSocketAddress("127.0.0.1",0),0);var calls=new AtomicInteger();var sink=new AtomicInteger();
        server.createContext("/ok",exchange->{
            calls.incrementAndGet();check(exchange.getRequestHeaders().getFirst("Authorization").equals("Bearer test-only-fake-token"),"仅显式测试Key");
            var body=exchange.getRequestBody().readAllBytes();check(JsonParser.parseString(new String(body,StandardCharsets.UTF_8)).getAsJsonObject().get("model").getAsString().equals("local-test"),"真实请求JSON");
            byte[] response="{\"choices\":[{\"message\":{\"content\":\"这是本机测试回复\"}}]}".getBytes(StandardCharsets.UTF_8);exchange.sendResponseHeaders(200,response.length);exchange.getResponseBody().write(response);exchange.close();
        });
        server.createContext("/redirect",e->{e.getResponseHeaders().set("Location","/sink");e.sendResponseHeaders(302,-1);e.close();});
        server.createContext("/sink",e->{sink.incrementAndGet();e.sendResponseHeaders(200,-1);e.close();});
        server.createContext("/large",e->{byte[] body=new byte[140000];e.sendResponseHeaders(200,body.length);try{e.getResponseBody().write(body);}catch(java.io.IOException ignored){}e.close();});
        server.createContext("/bad",e->{byte[] body="not-json".getBytes(StandardCharsets.UTF_8);e.sendResponseHeaders(200,body.length);e.getResponseBody().write(body);e.close();});
        server.start();String base="http://127.0.0.1:"+server.getAddress().getPort();
        try{
            var ok=Hk3SocialAiClient.request(URI.create(base+"/ok"),"test-only-fake-token",payload.toString()).get(10,TimeUnit.SECONDS);check(ok.ok()&&ok.text().equals("这是本机测试回复"),"本机端到端请求成功");
            var redirect=Hk3SocialAiClient.request(URI.create(base+"/redirect"),"test-only-fake-token",payload.toString()).get(10,TimeUnit.SECONDS);check(!redirect.ok()&&sink.get()==0,"禁止重定向泄漏认证");
            check(!Hk3SocialAiClient.request(URI.create(base+"/large"),"test-only-fake-token",payload.toString()).get(10,TimeUnit.SECONDS).ok(),"响应128KB封顶");
            check(!Hk3SocialAiClient.request(URI.create(base+"/bad"),"test-only-fake-token",payload.toString()).get(10,TimeUnit.SECONDS).ok(),"无效响应清晰失败");
            check(calls.get()==1,"无自动重试");
            check(Hk3SocialAiClient.configure(base+"/v1","local-test","test-only-fake-token").isEmpty()&&Hk3SocialAiClient.configured(),"客户端配置可用");
            Hk3SocialAiClient.reset();check(!Hk3SocialAiClient.configured(),"断线清除配置");
        }finally{server.stop(0);Hk3SocialAiClient.reset();}
        PhoneSocialPersonaTest.run();
        PhoneSocialLifecycleTest.run();
        System.out.println("Phone social: "+checks+" checks passed; mock API only, no paid calls; GUI/stage producers still require game acceptance");
    }
}
