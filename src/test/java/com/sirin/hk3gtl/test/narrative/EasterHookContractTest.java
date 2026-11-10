package com.sirin.hk3gtl.test.narrative;
import com.google.gson.*;
import org.objectweb.asm.*;
import org.objectweb.asm.tree.*;
import java.util.*;
import java.io.*;
/** 【变更记录 #1】2026-10-01 05:30:00（修订128）：删除无；新增直接读取当前依赖class的Mixin契约检查；修改无；用途：无需启动注册表即可发现目标签名漂移，不代替真实Mixin启动验收。 */
/** 【变更记录 #2】2026-10-01 06:36:54（修订128）：删除：无；新增/修改：新增Inject回调参数、返回回调类型、静态性和Accessor实际字段契约，提前发现启动时注入失败；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #3】2026-10-01 13:40:41（修订128）：删除：无；新增/修改：同时核验client数组，并检查Redirect目标调用的接收者、形参、返回值及ordinal，避免只查调用点存在；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #4】2026-10-01 14:26:58（修订130）：删除无；新增GTLCore改写后调用点与实际Mixin优先级规则检查；修改从只查原类扩展至覆盖后的方法；用途：复现并防止同优先级启动崩溃，不替代实机注入验收。 */
public final class EasterHookContractTest {
    private static int checks;
    private static final Map<String,ClassNode> CACHE=new HashMap<>();
    private static ClassNode node(String name){return CACHE.computeIfAbsent(name,key->{try(var in=EasterHookContractTest.class.getClassLoader().getResourceAsStream(key+".class")){if(in==null)throw new AssertionError("缺少目标class："+key);var n=new ClassNode();new ClassReader(in).accept(n,ClassReader.SKIP_DEBUG|ClassReader.SKIP_FRAMES);return n;}catch(IOException e){throw new UncheckedIOException(e);}});}
    private static Object value(AnnotationNode a,String key){if(a.values!=null)for(int i=0;i<a.values.size();i+=2)if(a.values.get(i).equals(key))return a.values.get(i+1);return null;}
    private static List<AnnotationNode> annotations(List<AnnotationNode> visible,List<AnnotationNode> invisible){var all=new ArrayList<AnnotationNode>();if(visible!=null)all.addAll(visible);if(invisible!=null)all.addAll(invisible);return all;}
    private static boolean method(String selector,MethodNode m){int i=selector.indexOf('(');return i<0?m.name.equals(selector):m.name.equals(selector.substring(0,i))&&m.desc.equals(selector.substring(i));}
    private static void check(boolean ok,String message){checks++;if(!ok)throw new AssertionError(message);}
    private static boolean field(ClassNode type,String name,String desc){if(type.fields.stream().anyMatch(f->f.name.equals(name)&&f.desc.equals(desc)))return true;return type.superName!=null&&!type.superName.equals("java/lang/Object")&&field(node(type.superName),name,desc);}
    private static List<AnnotationNode> at(Object raw){if(raw instanceof AnnotationNode a)return List.of(a);if(raw instanceof List<?> list)return list.stream().filter(AnnotationNode.class::isInstance).map(AnnotationNode.class::cast).toList();return List.of();}
    private static boolean invocation(MethodNode m,String target){int semi=target.indexOf(';'),paren=target.indexOf('(');if(semi<0||paren<0)return false;String owner=target.substring(1,semi),name=target.substring(semi+1,paren),desc=target.substring(paren);for(var insn:m.instructions)if(insn instanceof MethodInsnNode call&&call.owner.equals(owner)&&call.name.equals(name)&&call.desc.equals(desc))return true;return false;}
    private static boolean handlerMatches(MethodNode handler,MethodNode target){
        Type[] actual=Type.getArgumentTypes(handler.desc),expected=Type.getArgumentTypes(target.desc);
        if(actual.length==0||!Type.getReturnType(handler.desc).equals(Type.VOID_TYPE))return false;
        String callback=Type.getReturnType(target.desc).equals(Type.VOID_TYPE)?"org/spongepowered/asm/mixin/injection/callback/CallbackInfo":"org/spongepowered/asm/mixin/injection/callback/CallbackInfoReturnable";
        if(!actual[actual.length-1].getInternalName().equals(callback))return false;
        if((handler.access&Opcodes.ACC_STATIC)!=(target.access&Opcodes.ACC_STATIC))return false;
        if(actual.length==1)return true;
        return actual.length==expected.length+1&&java.util.Arrays.equals(java.util.Arrays.copyOf(actual,actual.length-1),expected);
    }
    private static boolean redirectMatches(MethodNode handler,MethodNode enclosing,String selector,int ordinal){
        int semi=selector.indexOf(';'),paren=selector.indexOf('(');if(semi<0||paren<0)return false;
        String owner=selector.substring(1,semi),name=selector.substring(semi+1,paren),desc=selector.substring(paren);
        int seen=0;boolean found=false;
        for(var insn:enclosing.instructions)if(insn instanceof MethodInsnNode call&&call.owner.equals(owner)&&call.name.equals(name)&&call.desc.equals(desc)){
            if(ordinal>=0&&seen++!=ordinal)continue;found=true;
            var expected=new ArrayList<Type>();if(call.getOpcode()!=Opcodes.INVOKESTATIC)expected.add(Type.getObjectType(owner));expected.addAll(Arrays.asList(Type.getArgumentTypes(desc)));
            var actual=Arrays.asList(Type.getArgumentTypes(handler.desc));boolean plain=actual.equals(expected);expected.addAll(Arrays.asList(Type.getArgumentTypes(enclosing.desc)));
            if(!plain&&!actual.equals(expected))return false;
            if(!Type.getReturnType(handler.desc).equals(Type.getReturnType(desc)))return false;
            if((enclosing.access&Opcodes.ACC_STATIC)!=0&&(handler.access&Opcodes.ACC_STATIC)==0)return false;
        }return found;
    }
    private record Replacement(String owner,String name,String desc,MethodNode body,int priority) {}
    private static AnnotationNode mixinAnnotation(ClassNode n){return annotations(n.visibleAnnotations,n.invisibleAnnotations).stream().filter(a->a.desc.equals("Lorg/spongepowered/asm/mixin/Mixin;")).findFirst().orElseThrow();}
    private static int priority(AnnotationNode a,int fallback){return value(a,"priority") instanceof Integer n?n:fallback;}
    /** 比较实际GTLCore配置里的Overwrite，不能只检查未经改写的GTMThings原类。 */
    private static void overwrittenContracts(JsonArray configured)throws IOException{
        var replacements=new ArrayList<Replacement>();
        try(var in=EasterHookContractTest.class.getClassLoader().getResourceAsStream("gtlcore.mixin.json")){
            if(in==null)throw new AssertionError("缺少实际GTLCore Mixin配置");
            var cfg=JsonParser.parseReader(new InputStreamReader(in,java.nio.charset.StandardCharsets.UTF_8)).getAsJsonObject();
            int fallback=cfg.has("priority")?cfg.get("priority").getAsInt():1000;
            var all=new JsonArray();all.addAll(cfg.getAsJsonArray("mixins"));if(cfg.has("client"))all.addAll(cfg.getAsJsonArray("client"));
            for(var raw:all){
                var foreign=node(cfg.get("package").getAsString().replace('.','/')+'/'+raw.getAsString().replace('.','/'));
                var a=mixinAnnotation(foreign);var owners=new ArrayList<String>();
                if(value(a,"value") instanceof List<?> values)for(var v:values)owners.add(((Type)v).getInternalName());
                if(value(a,"targets") instanceof List<?> values)for(var v:values)owners.add(v.toString().replace('.','/'));
                for(var m:foreign.methods)if(annotations(m.visibleAnnotations,m.invisibleAnnotations).stream().anyMatch(an->an.desc.equals("Lorg/spongepowered/asm/mixin/Overwrite;")))
                    for(var owner:owners)replacements.add(new Replacement(owner,m.name,m.desc,m,priority(a,fallback)));
            }
        }
        var policy=new org.spongepowered.asm.mixin.injection.InjectionPoint(){
            @Override public boolean find(String desc,InsnList insns,Collection<AbstractInsnNode> nodes){return false;}
        };
        check(!policy.checkPriority(1000,1000),"复现报告中同优先级被实际Mixin拒绝");
        int matched=0;
        for(var raw:configured){
            String name=raw.getAsString();if(!name.contains("Hk3Egg"))continue;
            var own=node("com/sirin/hk3gtl/mixin/"+name.replace('.','/'));var a=mixinAnnotation(own);
            for(var t:(List<?>)value(a,"value"))for(var rep:replacements){
                if(!((Type)t).getInternalName().equals(rep.owner()))continue;
                for(var handler:own.methods)for(var inject:annotations(handler.visibleAnnotations,handler.invisibleAnnotations)){
                    if(!inject.desc.equals("Lorg/spongepowered/asm/mixin/injection/Redirect;")&&!inject.desc.equals("Lorg/spongepowered/asm/mixin/injection/Inject;"))continue;
                    for(var selector:(List<?>)value(inject,"method"))if(method(selector.toString(),rep.body()))for(var point:at(value(inject,"at"))){
                        if(!"INVOKE".equals(value(point,"value")))continue;matched++;
                        check(policy.checkPriority(rep.priority(),priority(a,1000)),"覆盖后注入优先级冲突："+name+" -> "+rep.name());
                        String call=(String)value(point,"target");check(invocation(rep.body(),call),"GTLCore覆盖后调用点缺失："+call);
                        if(inject.desc.endsWith("Redirect;"))check(redirectMatches(handler,rep.body(),call,value(point,"ordinal") instanceof Integer n?n:-1),"覆盖后Redirect签名不匹配："+name);
                    }
                }
            }
        }
        check(matched>=2,"必须覆盖无线能源覆盖板的两条实际接收路径");
        System.out.println("GTLCore overwrite compatibility: "+matched+" INVOKE hooks checked against replacement bodies and Mixin priority policy.");
    }
    public static void main(String[] args){
        try(var in=EasterHookContractTest.class.getClassLoader().getResourceAsStream("hk3gtl.mixins.json")){
            if(in==null)throw new AssertionError("缺少Mixin配置");var config=JsonParser.parseReader(new InputStreamReader(in,java.nio.charset.StandardCharsets.UTF_8)).getAsJsonObject();
            var configured=new JsonArray();configured.addAll(config.getAsJsonArray("mixins"));configured.addAll(config.getAsJsonArray("client"));
            for(var item:configured){
                String name=item.getAsString();if(!name.contains("Hk3Egg"))continue;
                var mixin=node("com/sirin/hk3gtl/mixin/"+name.replace('.','/'));
                var annotation=annotations(mixin.visibleAnnotations,mixin.invisibleAnnotations).stream().filter(a->a.desc.equals("Lorg/spongepowered/asm/mixin/Mixin;")).findFirst().orElseThrow();
                var targets=(List<?>)value(annotation,"value");check(targets!=null&&!targets.isEmpty(),"未声明目标："+name);
                for(var t:targets){var target=node(((Type)t).getInternalName());
                    for(var f:mixin.fields)for(var a:annotations(f.visibleAnnotations,f.invisibleAnnotations))if(a.desc.equals("Lorg/spongepowered/asm/mixin/Shadow;"))check(field(target,f.name,f.desc),"影子字段不存在："+name+" / "+f.name+f.desc);
                    for(var handler:mixin.methods)for(var a:annotations(handler.visibleAnnotations,handler.invisibleAnnotations)){
                        if(a.desc.equals("Lorg/spongepowered/asm/mixin/gen/Accessor;")){var key=value(a,"value");check(key instanceof String&&field(target,(String)key,Type.getReturnType(handler.desc).getDescriptor()),"访问器目标字段不匹配："+name+" / "+key);}
                        if(!a.desc.equals("Lorg/spongepowered/asm/mixin/injection/Inject;")&&!a.desc.equals("Lorg/spongepowered/asm/mixin/injection/Redirect;"))continue;
                        Object selectors=value(a,"method");check(selectors instanceof List<?>,"注入选择器缺失："+name);
                        for(var selector:(List<?>)selectors){var methods=target.methods.stream().filter(m->method((String)selector,m)).toList();check(!methods.isEmpty(),"目标方法不存在："+name+" -> "+selector);
                            if(a.desc.equals("Lorg/spongepowered/asm/mixin/injection/Inject;"))check(methods.stream().allMatch(m->handlerMatches(handler,m)),"回调参数或静态性不匹配："+name+" -> "+selector+" / "+handler.desc);
                            for(var point:at(value(a,"at"))){Object call=value(point,"target");if(call instanceof String s&&!s.isEmpty()&&s.contains("(")){
                                check(methods.stream().anyMatch(m->invocation(m,s)),"字节码调用点不存在："+name+" -> "+selector+" / "+s);
                                if(a.desc.equals("Lorg/spongepowered/asm/mixin/injection/Redirect;")){int ordinal=value(point,"ordinal") instanceof Integer n?n:-1;check(methods.stream().anyMatch(m->redirectMatches(handler,m,s,ordinal)),"Redirect参数/返回值/调用序号不匹配："+name+" -> "+selector+" / "+handler.desc);}
                            }}
                        }
                    }
                }
            }
            overwrittenContracts(configured);
            System.out.println("Easter hook contracts: "+checks+" checks passed against current dependency bytecode; runtime mixin application still needs game startup.");
        }catch(IOException e){throw new UncheckedIOException(e);}
    }
}
