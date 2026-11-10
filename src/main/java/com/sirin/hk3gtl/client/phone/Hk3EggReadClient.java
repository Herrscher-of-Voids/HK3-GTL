package com.sirin.hk3gtl.client.phone;

/** 【变更记录 #4】2026-10-31 01:06:22（第4次备注 · 修订187）：删除发送即完成的本地条件；新增当前阅读令牌的服务端确认状态；修改关闭时清理；用途：过期或被拒绝的回执不能启用按钮。 */

/** 【变更记录 #3】2026-10-31 00:46:39（第3次备注 · 修订187）：删除无；新增当前阅读令牌与规范正文长度的完成判定；修改无；用途：只控制按钮，业务仍由服务端核验。 */
import com.sirin.hk3gtl.common.easter.*;
import com.sirin.hk3gtl.common.network.Hk3Network;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.util.FormattedCharSequence;
import java.util.*;
/** 【变更记录 #1】2026-10-01 04:19:02（修订128）：删除无；新增显示一秒后的逐页片段回报；修改无；用途：阅读沿用原翻页布局，重绘不重复，直接跳末页不能代替读完。 */
/** 【变更记录 #2】2026-10-01 04:21:47（修订128）：删除：旧固定上限或被替代的分支；新增/修改：跳页不发送无效片段，回头补读后可以正常继续；重传不重复计页；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public final class Hk3EggReadClient {
    private UUID token;private int observed=-1,dwell,nextOffset;private boolean confirmed;private final Set<Integer> sent=new HashSet<>();
    public void tick(CompoundTag view,List<FormattedCharSequence> lines,int page,int size){
        if(!view.hasUUID("ReadToken")){close();return;}
        UUID next=view.getUUID("ReadToken");if(!next.equals(token)){close();token=next;}
        if(observed!=page){observed=page;dwell=0;}if(++dwell<20||sent.contains(page))return;
        var before=new StringBuilder();var current=new StringBuilder();
        for(int i=0;i<Math.min(lines.size(),(page+1)*size);i++){
            var output=i<page*size?before:current;lines.get(i).accept((index,style,cp)->{output.appendCodePoint(cp);return true;});
        }
        String piece=Hk3EggReadingCursor.normalize(current.toString());if(piece.isEmpty()||piece.length()>4096)return;
        int start=Hk3EggReadingCursor.normalize(before.toString()).length();if(start!=nextOffset)return;
        Hk3Network.CHANNEL.sendToServer(new Hk3EggReadPacket(token,start,piece));sent.add(page);nextOffset+=piece.length();
    }
    public void confirm(UUID readToken){if(readToken.equals(token))confirmed=true;}
    public boolean complete(CompoundTag view){return confirmed&&token!=null&&view.hasUUID("ReadToken")&&token.equals(view.getUUID("ReadToken"))
        &&nextOffset==Hk3EggReadingCursor.normalize(view.getString("Body")).length();}
    public void close(){if(token!=null)Hk3Network.CHANNEL.sendToServer(new Hk3EggReadPacket(token,-1,""));token=null;observed=-1;dwell=0;nextOffset=0;confirmed=false;sent.clear();}
}
