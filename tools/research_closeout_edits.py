"""Record and integrate production research payment/UI and sampling corrections.
Change #1: backup files once, append historical Java comments, no saved-world mutation.
"""
from pathlib import Path
from datetime import datetime
import shutil,re
root=Path(__file__).resolve().parents[1]; java=root/'src/main/java/com/sirin/hk3gtl'
stamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
def edit(rel,transform,why):
    p=java/rel; s=p.read_text(encoding='utf-8'); backup=root/'archive/beta5-research-system-before'/rel
    if not backup.exists(): backup.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(p,backup)
    s=transform(s); n=max([int(x) for x in re.findall(r'变更记录\s*#(\d+)',s)]+[0])+1
    at=s.index('public '+('final class' if 'public final class' in s else 'class'))
    s=s[:at]+f'''/**
 * 【变更记录 #{n}】{stamp}（内测5第8次代码更新）
 * 删除：无旧代码删除，历史实现已归档。新增/修改：{why}。
 * 用途：研究系统实际服务端执行与验证，不以编译通过替代游戏验收。
 * Preserve archived implementation; integrate authoritative research execution and runtime verification.
 */
'''+s[at:]; p.write_text(s,encoding='utf-8')
def institute(s):
    a=s.index('            var data=Hk3ResearchData.get(server); var plan=Hk3ResearchPlans.get(selected);',s.index('private void action'))
    b=s.index('\n        }\n    }',a)
    s=s[:a]+'''            var result = requestResearch(server, selected, "points".equals(action));
            feedback = Component.translatable("hk3gtl.research.start." + result.name().toLowerCase(java.util.Locale.ROOT));'''+s[b:]
    pos=s.index('    /** 开题时锁定')
    s=s[:pos]+'''    /** 原生UI唯一付费入口；每次重新检查距离、世界、控制器、所有者和成型。
     * Single production payment entry, rechecking distance/world/controller/owner and formation on every request.
     */
    public Hk3ResearchStartService.Result requestResearch(ServerPlayer player, String topic, boolean points) {
        return Hk3ResearchStartService.start(player, facility(), lab, authorized(player) && isFormed(),
                topic, points, Math.max(0, Hk3GazeManager.getEffectiveGaze(player)));
    }

'''+s[pos:]
    s=s.replace('return plan.materials().stream().map(m -> new Hk3ResearchPlans.Material(m.tag(),Hk3ResearchMath.materialCount(m.count(),lab,gaze,0))).toList();','return Hk3ResearchStartService.materials(plan, lab, gaze);')
    s=s.replace('            out.add(Component.literal(plan.evidence()));','''            out.add(Component.literal(plan.evidence()));
            var selectedJob = data.researchJob(server.getUUID(), selected);
            if (selectedJob != null) {
                out.add(Component.translatable("hk3gtl.research.lab.progress", (int)(100 * selectedJob.progress() / selectedJob.quote().ticks()),
                        (long)Math.ceil((selectedJob.quote().ticks() - selectedJob.progress()) / 20.0), selectedJob.quote().eut()));
                if (!getRecipeLogic().isWorkingEnabled()) out.add(Component.translatable("hk3gtl.research.lab.paused"));
                else if (getEnergyContainer().getEnergyStored() < selectedJob.quote().eut())
                    out.add(Component.translatable("hk3gtl.research.lab.no_energy"));
            }
            out.add(ComponentPanelWidget.withButton(Component.translatable("hk3gtl.research.lab.toggle"), "toggle"));''')
    s=s.replace('            if ("next".equals(action))', '''            if ("toggle".equals(action)) { getRecipeLogic().setWorkingEnabled(!getRecipeLogic().isWorkingEnabled()); return; }
            if ("next".equals(action))''')
    return s
edit('common/machine/research/Hk3ResearchInstituteMachine.java',institute,'共用开题服务、精确失败提示、进度与停机原因及研究暂停开关')
for rel,why in [('common/machine/Hk3MachinesImpl.java','采集塔绑定指定配方成功输出记录器，原Pattern保留'),('common/recipe/Hk3RecipeTypesImpl.java','采集配方类型容纳2物入与1液出'),('common/recipe/honkai/HonkaiRecipes.java','新增非消耗零阶探测器液态采样配方，旧粒子配方保留')]: edit(rel,lambda s:s,why)
import json
translations={
 'hk3gtl.research.start.started':('研究已开题，费用已支付。','Research started; payment received.'),
 'hk3gtl.research.start.unavailable':('研究所未成型或无操作权限。','Institute unformed or access denied.'),
 'hk3gtl.research.start.locked':('研究所等级、知识或实验前置未满足。','Lab level, knowledge or experiment prerequisites are missing.'),
 'hk3gtl.research.start.completed':('此课题已完成，无需重复支付。','Topic already completed; no further payment needed.'),
 'hk3gtl.research.start.running':('此课题已有在研任务，未重复扣费。','Topic already in progress; no duplicate charge.'),
 'hk3gtl.research.start.insufficient':('研究点或材料不足，未扣费。','Insufficient points or materials; nothing charged.'),
 'hk3gtl.research.start.capacity':('研究槽位已满或设施归属不一致，未扣费。','No available slots or facility binding mismatch; nothing charged.'),
 'hk3gtl.research.lab.progress':('进度 %s%% · 剩余基础时间 %s 秒 · 每槽 %s EU/t','Progress %s%% · %s base seconds remaining · %s EU/t per slot'),
 'hk3gtl.research.lab.paused':('研究所已暂停；保留费用与进度。','Institute paused; payment and progress retained.'),
 'hk3gtl.research.lab.no_energy':('玩家电网供电不足；进度暂停。','Insufficient player-grid power; progress paused.'),
 'hk3gtl.research.lab.toggle':('暂停 / 恢复研究所','Pause / resume institute'),
}
for i,loc in enumerate(['zh_cn','en_us']):
    p=root/f'src/main/resources/assets/hk3gtl/lang/{loc}.json'; backup=root/'archive/beta5-research-system-before'/p.relative_to(root)
    if not backup.exists(): backup.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(p,backup)
    d=json.loads(p.read_text(encoding='utf8')); d.update({k:v[i] for k,v in translations.items()});p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
