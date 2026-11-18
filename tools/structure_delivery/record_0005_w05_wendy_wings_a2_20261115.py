from datetime import datetime
from pathlib import Path
import json


root = Path(__file__).resolve().parents[2]
delivery = 'deliveries/0005_W05_温蒂风翼渴望之心_A2_20261115'
log_path = 'logs/0005-w05-wendy-wings-a2-20261115'
out, log = root/delivery, root/log_path
m = json.loads((out/'manifest.json').read_text('utf8'))
capture = json.loads((log/'preview-capture.json').read_text('utf8'))
clearance = m['geometry_clearance']
receipt = dict(conversation='0005', conversation_id=m['conversation_id'],
    created_at=datetime.now().astimezone().isoformat(timespec='seconds'),
    candidate=m['title'], preview=delivery+'/三维评审.html', size_wdh=m['size_wdh'],
    block_count=m['block_count'], components=len(m['parts']),
    geometry_clearance=clearance, screenshots=10,
    visual_review=dict(reviewed=['整体预览.png', '正面预览.png', '侧面预览.png', '俯视预览.png', '核心近景.png', '评审界面.png'],
                       result='完整取景与前后分层可见；正交投影遮挡不作为实体交叠。风车四片叶片已独立纳入整机查重。'),
    browser_errors=capture['errors'], failed_requests=capture['failed'],
    appearance_approved=False, runtime_blueprint_modified=False, jar_built=False,
    installed=False, desktop_used=False, game_verified=False, acceptance_score_changed=False)
(log/'completion.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+'\n', 'utf8')
w, d, h = m['size_wdh']
entry = f'''

## 2026-11-15 对话0005：W05温蒂风翼与渴望之心A2候选

- 仅适用于对话0005（ID `01a1d6b8-bd81-79d3-a6f4-4f590806cc8e`）。负责人授权中央宝石、双翼、风车纹章预览，并反复要求构件不得穿模；旧W05双层回流A1及现行运行蓝图保留。
- 本对话当前候选预览：`{delivery}/三维评审.html`。实际宽{w}×深{d}×高{h}格、{m['block_count']:,}方块、{len(m['parts'])}独立构件、10种现有材料；中央悬浮晶体、左右各7片分离风翼、前庭风车、双侧低位回流槽与4座换热泵。羽片数量、四叶纹章及晶体几何均为建筑转译，不宣称官方实体精确复刻。
- 全部构件合并前按实际整数体素查重，{clearance['checked_component_pairs']}对构件交叠0；风车四片叶片单独纳入检查，不以覆盖、删除或裁切消解。关键体素表面间隔下界：相邻羽片至少11格，翼骨与羽片至少9格，宝石与约束轨38格、与导流带11格。数值仅描述对应两件的间隔，不冒充整机空闲通道证明；承台与落地构件按面相接。证据：同目录`净空记录.json`。
- 完整NBT/Schematic、统一三维预览及10幅headless截图已生成，页面脚本报错和请求失败均0。W05已有真实GT主控，本稿红石仅标记主控位置；外观待评审、未替换运行蓝图、未打包安装或启动游戏，不增加分数或批准数。回执：`{log_path}/completion.json`。
'''
for path in (root/'AGENTS.md', root/'rule/当前多方块设计规则.md'):
    with path.open('a', encoding='utf8', newline='') as handle:
        handle.write(entry)
print(json.dumps(dict(receipt=str(log/'completion.json'), memory_entries=2), ensure_ascii=False))
