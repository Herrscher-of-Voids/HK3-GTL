package com.sirin.hk3gtl.common.easter;
import net.minecraft.server.level.ServerPlayer;
import java.util.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
/** 【变更记录 #1】2026-10-01 04:12:10（修订128）：删除无；新增成功保存笔记的有界摘要和内容事实；修改无；用途：不同正文计数不受重复保存刷取，内容不上传或读取外部文件。 */
/** 【变更记录 #2】2026-10-01 04:30:25（修订128）：删除：旧固定上限或被替代的分支；新增/修改：修正来源网址解析的空白字符转义，换行不被吃进网址；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #3】2026-10-01 04:41:04（修订128）：删除：旧固定上限或被替代的分支；新增/修改：备份日期使用纯函数有效日期校验，正文关键词不替代真正颜色标签；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #4】2026-10-01 04:47:12（修订128）：删除：旧固定上限或被替代的分支；新增/修改：按已审条件检测验收条目、重力文字方案及戴森球供能设想；参考来源允许明确署名而非硬性要求两个网址；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #5】2026-10-01 04:53:17（修订128）：删除：旧固定上限或被替代的分支；新增/修改：山地真实远距望远镜观察后保存3819风景笔记；未观察不触发；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #6】2026-10-01 05:02:11（修订128）：删除：旧固定上限或被替代的分支；新增/修改：3125须本人保存五项清单再重新打开；钓获后确已收竿再记录一条笔记；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #7】2026-10-01 05:28:18（修订128）：删除：旧固定上限或被替代的分支；新增/修改：已保存笔记关联真实修复花费及床设置回执；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #8】2026-10-01 05:41:36（修订128）：删除：旧固定上限或被替代的分支；新增/修改：记录1.618前须有本人实际完成16×10地板的几何回执；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #9】2026-10-01 06:05:54（修订128）：删除：无；新增/修改：探洞返回后的实际笔记打开采用服务器返回地面记录；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #10】2026-10-01 06:19:47（修订128）：删除：无；新增/修改：实际笔记保存和打开串联具名武器、锈蚀铜及盔甲展示回执；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #11】2026-10-01 06:23:20（修订128）：删除：无；新增/修改：猫旁实际放画之后保存半张照片标题才触发；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #12】2026-10-01 12:18:50（修订128）：删除：无；新增/修改：速通笔记保存建立实际主线/研究完成数基线，随后连续60秒无推进才授收藏；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public final class Hk3EggNotes {
    private Hk3EggNotes(){}
    public static String digest(String text){
        try{return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(text.getBytes(StandardCharsets.UTF_8)));}
        catch(java.security.NoSuchAlgorithmException impossible){throw new IllegalStateException(impossible);}
    }
    public static void saved(ServerPlayer p,String title,String body){
        var n=Hk3EggRuntime.state(p);var seen=n.getCompound("noteHashes");
        if(!body.isBlank()&&seen.size()<19)seen.putBoolean(digest(body),true);
        n.put("noteHashes",seen);
        var f=new LinkedHashMap<>(Hk3EggCalendar.facts(Hk3EggCalendar.now(),p.server.overworld().getDayTime()));
        f.putAll(Hk3EggNoteFacts.saved(title,body));
        f.put("different_saves",Integer.toString(seen.size()));
        f.put("green",Boolean.toString(body.contains("绿")));f.put("blue",Boolean.toString(body.contains("蓝")));
        f.put("thanks",Boolean.toString((title+body).contains("感谢")||(title+body).contains("谢谢")));
        f.put("recipe_note",Boolean.toString((title+body).contains("配方")&&!body.isBlank()));
        f.put("celebrate",Boolean.toString(body.contains("庆典")));f.put("constant",Boolean.toString(body.contains("永恒领域")));
        f.put("stars",Long.toString(body.codePoints().filter(c->c=='☆'||c=='★'||c=='*').count()));
        var urls=java.util.regex.Pattern.compile("https?://[^\\s]+",java.util.regex.Pattern.UNICODE_CHARACTER_CLASS).matcher(body);
        var sources=new HashSet<String>();while(urls.find())sources.add(urls.group());
        f.put("sources",Integer.toString(sources.size()));
        int modification=body.indexOf("改动");f.put("modification",Boolean.toString(modification>=0&&body.substring(modification+2).strip().codePointCount(0,body.substring(modification+2).strip().length())>=20));
        f.put("backup",Boolean.toString((title+body).contains("备份")));
        f.put("has_date",Boolean.toString(Hk3EggNoteFacts.hasValidDate(body)));
        f.put("acceptance",Boolean.toString((title+body).contains("验收")));
        f.put("gravity_plan",Boolean.toString(body.contains("如果重力倒过来")&&!body.replace("如果重力倒过来","").strip().isEmpty()));
        f.put("power_plan",Boolean.toString(body.contains("戴森球")&&body.replace("戴森球","").strip().codePointCount(0,body.replace("戴森球","").strip().length())>=20));
        f.put("reference",Boolean.toString(!sources.isEmpty()||java.util.regex.Pattern.compile("(?:来源|参考|作者)[：:]\\s*[^\\s：:]+",java.util.regex.Pattern.UNICODE_CHARACTER_CLASS).matcher(body).find()));
        f.put("steps",Long.toString(body.lines().map(String::strip).filter(s->s.matches("[1-9][.、)）].{3,}")).count()));
        n.putString("lastNoteBody",body);n.putString("lastNoteTitle",title);n.putLong("lastNoteTick",p.server.overworld().getGameTime());
        if(body.codePointCount(0,body.length())>=20)n.putBoolean("note20",true);
        if(title.equals("3125")&&body.lines().filter(line->line.strip().matches("[1-5][.、)）].{1,}")).count()==5)n.putString("saved3125",digest(body));
        if(n.getBoolean("fishedAndReeled")&&p.fishing==null&&!body.isBlank()){Hk3EggVanilla.caseEvent(p,456);n.remove("fishedAndReeled");}
        if(title.equals("3819")&&!body.isBlank()&&n.getBoolean("mountainSpied"))Hk3EggVanilla.caseEvent(p,402);
        if(n.getBoolean("floor1610")&&body.contains("1.618"))Hk3EggVanilla.caseEvent(p,330);
        Hk3EggExploration.note(p,title,body);
        Hk3EggLifeEvents.note(p,title,body);
        Hk3EggPersonalScenes.note(p,title,body);
        Hk3EggPaintingScenes.note(p,title);
        Hk3EggRuntime.observe(p,"note_saved",f);
    }
    public static void opened(ServerPlayer p,String title,String body){
        Hk3EggTravel.note(p,body);
        Hk3EggPersonalScenes.openedNote(p,body);
        if(title.equals("3125")&&Hk3EggRuntime.state(p).getString("saved3125").equals(digest(body)))Hk3EggVanilla.caseEvent(p,384);
        Hk3EggRuntime.observe(p,"note_open",Hk3EggRuntime.fields("title",title,"body",body));
    }
}
