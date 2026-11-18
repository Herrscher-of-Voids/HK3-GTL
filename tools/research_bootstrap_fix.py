"""Archive and correct the rejected inventory-based experiment shortcut.
Change #1: preserve prior source and append bilingual change notes; no world edits.
"""
from pathlib import Path
from datetime import datetime
import shutil
root=Path(__file__).resolve().parents[1]
base=root/'src/main/java/com/sirin/hk3gtl'
stamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
def write(rel,change):
    p=base/rel; s=p.read_text(encoding='utf-8'); dest=root/'archive/beta5-research-system-before'/rel
    if not dest.exists(): dest.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(p,dest)
    p.write_text(change(s),encoding='utf-8')
def institute(s):
    a=s.index('    /**\n     * 以真实背包样本'); b=s.index('    @Override public boolean shouldOpenUI',a)
    s=s[:a]+s[b:]
    s=s.replace('            // First observation is a physical detector + sample handoff, not a free client-side unlock.\n            if ("RN-HED".equals(selected)) bootstrapDetectionExperiment(server, data);\n','')
    pos=s.index('public final class')
    return s[:pos]+f'''/**
 * 【变更记录 #3】{stamp}（内测5研究系统修正）
 * 删除：撤回未经设计确认的背包晶体交样捷径，源代码已归档。
 * 新增：无。修改：恢复只读实验凭据校验，点击开题不再提前消耗样本。
 * 用途：RN-HED仅由采集塔的真实液态采样结算授予；并非持有样品即完成实验。
 * Remove the unapproved inventory-sample shortcut; keep archived source and require actual liquid sampling.
 */
'''+s[pos:]
write('common/machine/research/Hk3ResearchInstituteMachine.java',institute)

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
