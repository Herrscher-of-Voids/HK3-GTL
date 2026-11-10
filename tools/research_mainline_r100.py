"""2026-09-29：落实已批准研究数值与离线产点；保留改前副本。"""
from pathlib import Path
from datetime import datetime
import json,shutil
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'logs/research-mainline-r100';OUT.mkdir(parents=True,exist_ok=True)
STAMP=datetime.now().astimezone().isoformat()
def write(rel,text):
 p=ROOT/rel;backup=OUT/'before'/rel
 if p.exists() and not backup.exists():backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,backup)
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8')
def edit(rel,changes):
 text=(ROOT/rel).read_text(encoding='utf-8-sig')
 for old,new in changes:
  assert old in text,(rel,old[:120]);text=text.replace(old,new)
 marker='/** 【变更记录 · 内测5修订100】2026-09-29：落实已批准研究费用、三公式及离线账户规则。 */\n'
 pos=text.index('\n',text.index('package '))+1;text=text[:pos]+'\n'+marker+text[pos:];write(rel,text)
approved=json.loads((ROOT/'logs/research-r03-r06-review/confirmed-decisions-20260928-222343.json').read_text(encoding='utf-8'))
path='src/main/resources/data/hk3gtl/research/research_costs.json'
data=json.loads((ROOT/path).read_text(encoding='utf-8'));prior=sum(t['points'] for t in data['topics'])
plan={t['id']:t for t in approved['approved_proposal']['topics']}
for t in data['topics']:
 p=plan[t['id']];t['points']=p['candidate_points'];t['ticks']=p['ticks'];t['eut']=p['candidate_eut']
 t['materials']=[{k:m[k] for k in ('tag','count','sensitivity')} for m in p['candidate_materials']]
data['_comment_revision100']='2026-09-29：按2026-09-28 22:23:43批准快照落地；开题锁定实付，存量任务不重算。'
assert sum(t['points'] for t in data['topics'])==255750
write(path,json.dumps(data,ensure_ascii=False,indent=2)+'\n')
base='src/main/java/com/sirin/hk3gtl/common/'
edit(base+'research/Hk3ResearchPlans.java',[
 ('record Material(String tag, long count)', 'record Material(String tag, long count, double sensitivity)'),
 ('public Material {','public Material(String tag, long count) { this(tag, count, 1.0); }\n        public Material {\n            if (!Double.isFinite(sensitivity) || sensitivity < 0 || sensitivity > 1) throw new IllegalArgumentException("Invalid sensitivity");'),
 ('String result, List<Material> materials)', 'String result, List<Material> materials, long eut)'),
 ('if (points < 1 || ticks < 1 || materials.isEmpty())','if (points < 1 || ticks < 1 || eut < 1 || materials.isEmpty())'),
 ('material.get("count").getAsLong()))','material.get("count").getAsLong(), material.get("sensitivity").getAsDouble()))'),
 ('object.get("result").getAsString(), materials);','object.get("result").getAsString(), materials, object.get("eut").getAsLong());')])
edit(base+'research/Hk3ResearchMath.java',[
 ('private static double pressure(', 'public static double pressure('),
 ('return lab == 1 ? 0 : (gaze / (gaze + 100.0)) * (1 - suppression);','return lab == 1 ? 0 : (0.65 * (gaze / (gaze + 100.0)) + 0.35 * (gaze / (gaze + 300.0))) * Math.pow(1 - suppression, 1.25);'),
 ('return (1 + (erosion ? 0.25 : 0) + (wonder ? 0.75 : 0)) / (1 + 3 * pressure(lab, gaze, suppression));','double q = pressure(lab, gaze, suppression), q2 = q * q;\n        return Math.min(3, 1 + (erosion ? 0.5 : 0) + (wonder ? 1.5 : 0)) / (1 + 1.2 * q + 1.2 * q2 + 0.6 * q2 * q2);'),
 ('        if (base < 1) throw new IllegalArgumentException("Invalid material base");\n        double multiplier = 1 + pressure(lab, gaze, suppression);\n        return java.math.BigDecimal.valueOf(base).multiply(java.math.BigDecimal.valueOf(multiplier))\n                .setScale(0, java.math.RoundingMode.CEILING).longValueExact();',
  '        return materialCount(base, lab, gaze, suppression, 1.0);\n    }\n\n    /** 仅额外消耗逐项向上取整；基础数保留整数精度，关键材料可明确免压。 */\n    public static long materialCount(long base, int lab, double gaze, double suppression, double sensitivity) {\n        if (base < 1 || !Double.isFinite(sensitivity) || sensitivity < 0 || sensitivity > 1) throw new IllegalArgumentException("Invalid material sensitivity");\n        double q = pressure(lab, gaze, suppression);\n        if (q == 0 || sensitivity == 0) return base;\n        var extra = java.math.BigDecimal.valueOf(base).multiply(java.math.BigDecimal.valueOf(sensitivity))\n                .multiply(java.math.BigDecimal.valueOf(0.4 * q + 0.6 * q * q))\n                .setScale(0, java.math.RoundingMode.CEILING).longValueExact();\n        return Math.addExact(base, extra);')])
edit(base+'research/Hk3ResearchWorkQueue.java',[('speed > 2','speed > 3')])
edit(base+'research/Hk3ResearchStartService.java',[
 ('Hk3Values.VA_LONG[GTValues.MAX + definition.tier()]','plan.eut()'),
 ('Hk3ResearchMath.materialCount(m.count(), lab, Math.max(0, gaze), 0)','Hk3ResearchMath.materialCount(m.count(), lab, Math.max(0, gaze), 0, m.sensitivity())')])
edit(base+'machine/research/Hk3ResearchInstituteMachine.java',[
 ('Hk3Values.VA_LONG[GTValues.MAX + topic.tier()]','plan.eut()')])
edit(base+'machine/research/Hk3ResearchComputerMachine.java',[
 ('ServerPlayer player = ownerPlayer();\n        if (player == null) return;','if (owner == null || getLevel() == null || getLevel().getServer() == null) return;\n        var server = getLevel().getServer();'),
 ('Hk3ResearchData.get(player).tickComputer(owner, facility(), player.server.overworld().getGameTime(), level, true,','Hk3ResearchData.get(server).tickComputer(owner, facility(), server.overworld().getGameTime(), level, true,')])
for lang in ('zh_cn','en_us'):
 p=f'src/main/resources/assets/hk3gtl/lang/{lang}.json';d=json.loads((ROOT/p).read_text(encoding='utf-8'))
 names=list(approved['names'].values()) if lang=='zh_cn' else ['Honkai Phenomena Research Institute','Matter Reconstruction Research Institute','Quantum Domain Research Institute','World Maintenance Research Institute','Civilization Cognition Dome']
 for i,name in enumerate(names,1):d[f'hk3gtl.research.lab.grade.{i}']=name
 write(p,json.dumps(d,ensure_ascii=False,indent=2)+'\n')
(OUT/'balance-applied.json').write_text(json.dumps({'time':STAMP,'old_points':prior,'new_points':255750,'topics':100,'source':'confirmed-decisions-20260928-222343.json','runtime_verified':False},ensure_ascii=False,indent=2),encoding='utf-8')
print('Applied approved costs, pressure formulas, offline production; game not yet verified.')

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
