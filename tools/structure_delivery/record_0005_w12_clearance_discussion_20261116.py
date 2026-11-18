from datetime import datetime
import json
from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[2]
LOG = ROOT / 'logs/0005-w12-clearance-discussion-20261116'
REPORT = ROOT / 'logs/beta5-completion-audit-20261030'
now = datetime.now().astimezone().isoformat()
discussion = dict(updated_at=now, candidate='W12 A1', stage='穿模定位完成，修订方案讨论中',
    source_preview='deliveries/0005_W12_作者蓝图原案_A1_20261116/index.html',
    geometry_modified=False, appearance_approval_added=False,
    confirmed=dict(rings='三环同半径正交，已解析证明两两全时间实碰；各环对三十字和12矛亦全时间实碰',
        cavity='名义球腔半径35，现有完整环最大球半径41.509；分层后须按新最外环扩大空腔',
        corridors=dict(west_inside_sphere_blocks=534, east_inside_sphere_blocks=428,
            shared_blocks=66732, shared_projection_x=[463, 599], magnetic_ring_gaps=[13, 17]),
        chains=dict(sphere_overlap_at_reference={'06': 14, '12': 564, '27': 200},
            chain21_collision_idle_seconds=33.06939635357677,
            chains_intersecting_corridors=22, midspan_intersecting_chain_pairs=14),
        crown=dict(intersecting_tower_ids=[2, 3, 6, 7], overlap_blocks_each=1263,
            filaments_inside_walls_windows_towers_union_blocks=3320)),
    preserved_connections=['塔墙固定连接', '锁链端部与对应固定锚座', '光丝顶端挂接', '三重十字固定机械连接'],
    proposed_order=['先确定三环与白洞的运动方式并扩大独立核心空间',
        '中央双长廊改为共用汇合段，将侵入核心的磁环重新绕核布置',
        '优先分流链06/12/21/27，随后处理其余中段相交与穿廊',
        '冠环与四内塔错层，光丝避开墙塔实体'],
    pending_preference='三环保留转动并分层，或合为固定拘束架；已向负责人提出选项',
    evidence={name: str((LOG / name).relative_to(ROOT)).replace('\\', '/')
              for name in ('core-motion.json', 'chains.json', 'frame.json')}, scores_changed=False)
(LOG / 'discussion.json').write_text(json.dumps(discussion, ensure_ascii=False, indent=2) + '\n', 'utf8')
backup = REPORT / ('history/before-0005-w12-clearance-discussion-' + datetime.now().strftime('%Y%m%d-%H%M%S'))
backup.mkdir(parents=True)
for name in ('index.html', 'current-summary.json'):
    shutil.copy2(REPORT / name, backup / name)
summary = json.loads((REPORT / 'current-summary.json').read_text('utf8'))
system = next(s for s in summary['systems'] if s['id'] == 'multiblocks')
system['w12_clearance_discussion_0005'] = discussion
system['w12_current_design_stage'] = discussion['stage']
system['updated_at'] = now
summary['w12_clearance_discussion_0005_receipt'] = 'logs/0005-w12-clearance-discussion-20261116/discussion.json'
summary['report_updated_at'] = now
summary['systems'].sort(key=lambda s: s['percent'])
(REPORT / 'current-summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', 'utf8')
html = (REPORT / 'index.html').read_text('utf8')
start = html.index('</summary>', html.index('<details id="system-multiblocks"')) + len('</summary>')
notice = '<section class="notice"><h3>W12穿模讨论</h3><p>三环同径正交全时间互穿；长廊侵入白洞，3条链参考姿态穿芯、另1条转动后刮入；22条链穿廊，14对链中段相交。修订方案讨论中，A1原案保留。</p><p><a href="../../logs/0005-w12-clearance-discussion-20261116/discussion.json">定位与修订顺序</a>；原验收4/6、研发4/5及全库分数保持。</p></section>'
html = html[:start] + notice + html[start:]
marker = '<script type="application/json" id="audit-data">'
start = html.index(marker) + len(marker)
end = html.index('</script>', start)
html = html[:start] + '\n' + json.dumps(summary, ensure_ascii=False, indent=2) + '\n' + html[end:]
(REPORT / 'index.html').write_text(html, 'utf8')
memory = f'''\n\n## 2026-11-16 对话0005：W12进入穿模讨论

- 负责人要求讨论穿模。本轮完成原案几何定位，修订方式待定，A1原文件与外观待审状态保留。
- 三同径正交核心环两两、各环对三十字及12矛已解析证明全时间实碰；半径35球腔不足容纳最大球半径41.509的现有环。双廊分别侵入白洞534/428格，中央137格投影区实占重叠66732格。
- 链06/12/27参考姿态穿芯14/564/200格，链21在白球转动后刮入；22条链穿廊、14对链中段相交。冠环与第2/3/6/7塔各重叠1263格，垂丝穿墙塔并集3320格。正常固定锚接、塔墙及挂接单列保留。
- 已提出核心三环保留转动分层并扩腔、或固定拘束架的选择。修改顺序为核心运动空间、中央长廊汇合与绕核、锁链分流错层、冠环及光丝净空；坐标尚未修改。证据入口`logs/0005-w12-clearance-discussion-20261116/discussion.json`，记录时间`{now}`；原分数和批准数保持。
'''
for name in ('AGENTS.md', 'rule/当前多方块设计规则.md'):
    with (ROOT / name).open('a', encoding='utf8') as handle:
        handle.write(memory)
print(json.dumps(dict(discussion=str(LOG / 'discussion.json'), overall_percent=summary['overall_percent'],
    acceptance=[system['earned'], system['possible']], geometry_modified=False)))
