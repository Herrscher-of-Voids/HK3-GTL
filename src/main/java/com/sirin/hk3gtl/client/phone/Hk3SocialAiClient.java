package com.sirin.hk3gtl.client.phone;

import com.google.gson.*;
import com.sirin.hk3gtl.common.phone.Hk3SocialCatalog;
import java.net.URI;
import java.net.http.*;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.io.ByteArrayOutputStream;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.Flow;

 
 
 





public final class Hk3SocialAiClient {
    public record Message(String role,String text){}
    public record Result(String text,String error){public boolean ok(){return error.isEmpty();}}
    private static final HttpClient HTTP=HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(10)).followRedirects(HttpClient.Redirect.NEVER).build();
    private static String endpoint="",model="",key="";
    private static CompletableFuture<?> pending;
    private static int epoch;
    private Hk3SocialAiClient(){}
    public static String endpoint(){return endpoint;}public static String model(){return model;}
    public static boolean configured(){return !endpoint.isEmpty()&&!model.isEmpty()&&!key.isEmpty();}
    public static boolean busy(){return pending!=null&&!pending.isDone();}
    public static int epoch(){return epoch;}
    public static void cancel(){epoch++;if(pending!=null)pending.cancel(true);pending=null;}
    public static void reset(){cancel();endpoint="";model="";key="";}
    public static String configure(String address,String modelName,String secret){
        try{
            URI uri=endpoint(address);
            if(modelName.isBlank()||modelName.length()>128||modelName.chars().anyMatch(Character::isISOControl))return "请填写有效模型名称。";
            // 留空只允许保留同一完整接口的凭据；换服务、端口或路径都必须重新填写。
            if(secret.isEmpty()&&!endpoint.isEmpty()&&!uri.equals(URI.create(endpoint)))
                return "接口地址已更改，请重新填写该接口的 API Key；原配置未改动。";
            String value=secret.isEmpty()?key:secret.strip();
            if(value.isEmpty()||value.length()>2048||value.chars().anyMatch(c->c<33||c>126))return "请填写有效 API Key；本地服务可填其要求的占位值。";
            cancel();endpoint=uri.toString();model=modelName.strip();key=value;return "";
        }catch(IllegalArgumentException ex){return "地址需为 HTTPS 完整接口，或本机 HTTP 接口；不能含账号、参数或片段。";}
    }
    public static URI endpoint(String raw){
        URI u=URI.create(raw.strip());String host=u.getHost();String scheme=u.getScheme();
        boolean local=host!=null&&(host.equalsIgnoreCase("localhost")||host.equals("127.0.0.1")||host.equals("[::1]")||host.equals("::1"));
        if(host==null||u.getPort()>65535||u.getPort()==0||u.getUserInfo()!=null||u.getRawQuery()!=null||u.getRawFragment()!=null||!("https".equalsIgnoreCase(scheme)||local&&"http".equalsIgnoreCase(scheme)))throw new IllegalArgumentException();
        String text=u.toString().replaceAll("/+$","");
        if(!text.endsWith("/chat/completions"))text+="/chat/completions";
        return URI.create(text);
    }
    public static String payload(String model,Hk3SocialCatalog.Contact contact,String input,List<Message> history){
        var root=new JsonObject();root.addProperty("model",model);root.addProperty("max_tokens",512);root.addProperty("stream",false);var messages=new JsonArray();
        add(messages,"system",Hk3SocialPersonas.prompt(contact));
        for(var m:history.subList(Math.max(0,history.size()-8),history.size())){
            if(!m.role.equals("user")&&!m.role.equals("assistant"))continue;
            if(m.role.equals("assistant")&&Hk3SocialPersonas.breaksCharacter(contact,m.text))continue;
            add(messages,m.role,m.text.substring(0,Math.min(1800,m.text.length())));
        }
        add(messages,"user",input);root.add("messages",messages);return root.toString();
    }
    private static void add(JsonArray array,String role,String text){var item=new JsonObject();item.addProperty("role",role);item.addProperty("content",text);array.add(item);}
    public static CompletableFuture<Result> send(Hk3SocialCatalog.Contact contact,String input,List<Message> history){
        if(!configured()||busy()||!Hk3SocialCatalog.validInput(input))return CompletableFuture.completedFuture(new Result("","请先配置，或等待当前请求结束。"));
        var request=request(endpoint(endpoint),key,payload(model,contact,input,history));pending=request;
        return request.thenApply(result->validateReply(contact,result));
    }
    /** 出戏内容不进入角色记录，不用付费重试掩盖问题，也不冒充模型生成本地兜底。 */
    public static Result validateReply(Hk3SocialCatalog.Contact contact,Result result){
        if(!result.ok())return result;
        if(Hk3SocialPersonas.breaksCharacter(contact,result.text))
            return new Result("","回复偏离角色，已拦截且未重试；本次仍可能计费。请核对服务设置。");
        return new Result(contact.finish(result.text),"");
    }
    /** 公共测试入口只接受显式凭据，永远不读取环境变量或配置文件。重定向不会携带认证继续发送。 */
    public static CompletableFuture<Result> request(URI uri,String secret,String json){
        HttpRequest req=HttpRequest.newBuilder(uri).timeout(Duration.ofSeconds(45)).header("Content-Type","application/json")
            .header("Authorization","Bearer "+secret).POST(HttpRequest.BodyPublishers.ofString(json,StandardCharsets.UTF_8)).build();
        var transport=HTTP.sendAsync(req,info->new LimitedBody());
        // 响应头返回后仍限制整个响应期限，并取消尚未结束的正文传输。
        var result=transport.thenApply(response->{
            if(response.statusCode()!=200)return new Result("","服务返回 HTTP "+response.statusCode()+"；未自动重试。请核对地址、模型、余额与服务权限。");
            try{
                var content=JsonParser.parseString(response.body()).getAsJsonObject().getAsJsonArray("choices").get(0).getAsJsonObject().getAsJsonObject("message").get("content");
                if(content==null||!content.isJsonPrimitive()||!content.getAsJsonPrimitive().isString()||content.getAsString().isBlank())throw new IllegalArgumentException();
                String text=content.getAsString().replaceAll("[\\p{Cc}&&[^\\n\\t]]","").replace("§","");
                return new Result(text.substring(0,Math.min(1800,text.length())),"");
            }catch(RuntimeException ex){return new Result("","返回内容不是兼容的文本回复；未自动重试。");}
        }).orTimeout(45,TimeUnit.SECONDS).exceptionally(ex->{
            transport.cancel(true);return new Result("","连接失败、超时或响应超过128KB；未自动重试。");
        });
        result.whenComplete((value,error)->{if(result.isCancelled())transport.cancel(true);});return result;
    }
    private static final class LimitedBody implements HttpResponse.BodySubscriber<String>{
        private final CompletableFuture<String> body=new CompletableFuture<>();private final ByteArrayOutputStream bytes=new ByteArrayOutputStream();private Flow.Subscription subscription;
        public CompletionStage<String> getBody(){return body;}
        public void onSubscribe(Flow.Subscription s){subscription=s;s.request(1);}
        public void onNext(List<ByteBuffer> chunks){
            for(var chunk:chunks){if(bytes.size()+chunk.remaining()>131072){subscription.cancel();body.completeExceptionally(new IllegalArgumentException("响应过大"));return;}
                byte[] value=new byte[chunk.remaining()];chunk.get(value);bytes.writeBytes(value);}
            subscription.request(1);
        }
        public void onError(Throwable error){body.completeExceptionally(error);}
        public void onComplete(){body.complete(bytes.toString(StandardCharsets.UTF_8));}
    }
}
