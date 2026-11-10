package com.sirin.hk3gtl.common.dialogue.definition;

/**
 * 【变更记录 #1】2026-09-29 17:51:46（内测5修订93）
 * - 删除：旧正文活动引用被审核原文替代；保留历史资源和存档。
 * - 新增／修改：免费IF指令共用26条审核原文，每条十句，不扣正式终审五选名额。
 * - 用途：接通审核正文；其他系统触发及归属不据此宣称完成。
 */
import com.sirin.hk3gtl.common.dialogue.DialogueChoice;
import com.sirin.hk3gtl.common.dialogue.DialogueDefinition;
import com.sirin.hk3gtl.common.dialogue.DialogueLine;
import com.sirin.hk3gtl.common.dialogue.DialogueRegistry;
import com.sirin.hk3gtl.common.dialogue.Hk3FinaleIfData;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/** 指令用只读IF档案，与正式终审会话和五次名额完全分离。 */
public final class Hk3IfArchiveDialogue {
    public static final String ID = "hk3_if_archive";
    private static final int PAGE_SIZE = 5;

    private Hk3IfArchiveDialogue() {}

    public static void register() {
        Map<String, List<DialogueLine>> segments = new LinkedHashMap<>();
        int pages = (Hk3FinaleIfData.BRANCH_COUNT + PAGE_SIZE - 1) / PAGE_SIZE;
        for (int page = 0; page < pages; page++) {
            List<DialogueChoice> choices = new ArrayList<>();
            for (int index = page * PAGE_SIZE;
                 index < Math.min((page + 1) * PAGE_SIZE, Hk3FinaleIfData.BRANCH_COUNT); index++) {
                choices.add(new DialogueChoice("hk3gtl.dialogue.if_archive.choice." + index, "if_" + index));
            }
            if (page > 0) choices.add(new DialogueChoice("hk3gtl.dialogue.if_archive.previous", "page_" + (page - 1)));
            if (page + 1 < pages) choices.add(new DialogueChoice("hk3gtl.dialogue.if_archive.next", "page_" + (page + 1)));
            segments.put("page_" + page, List.of(new DialogueLine("sirin", "hk3gtl.dialogue.if_archive.prompt", null, choices)));
        }
        for (int index = 0; index < Hk3FinaleIfData.BRANCH_COUNT; index++) {
            var entry=com.sirin.hk3gtl.common.narrative.Hk3ApprovedProse.get(String.format(java.util.Locale.ROOT,"IF-%02d",index+1));
            List<DialogueLine> lines = new ArrayList<>(Hk3ApprovedDialogues.lines(entry,List.of()));
            lines.add(new DialogueLine("sirin", "hk3gtl.dialogue.if_archive.finished", null,
                    List.of(new DialogueChoice("hk3gtl.dialogue.if_archive.back", "page_" + (index / PAGE_SIZE)))));
            segments.put("if_" + index, lines);
        }
        DialogueRegistry.registerDialogue(new DialogueDefinition(ID, segments, "page_0", true, null));
    }
}
