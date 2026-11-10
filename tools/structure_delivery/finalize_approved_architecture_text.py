"""变更记录 #1：2026-10-15 01:15:46（内测5修订156）。
为21个正式结构补中英文名称和最新尺寸，追加修订说明；保留无关语言条目及历史修订。
输入为现有语言JSON及批准布局，输出为原文件；重复执行不重复增加修订，非法JSON直接失败。
"""
from pathlib import Path
import json
import re
from datetime import datetime

ROOT = Path(__file__).resolve().parents[2]
# 运行环境未必安装tzdata；Windows本机时区已由项目约定固定为UTC+08。
from datetime import timedelta, timezone
stamp = datetime.now(timezone(timedelta(hours=8)))

def update_lang(locale):
    path = ROOT / 'src/main/resources/assets/hk3gtl/lang' / f'{locale}.json'
    text = path.read_text(encoding='utf-8')
    old = json.loads(text)
    zh = locale == 'zh_cn'
    changes = {}
    for stage, machine in enumerate(['abyss_research_analysis_matrix', 's02_matter_reconstruction_institute',
            's03_quantum_domain_institute', 's04_world_maintenance_institute', 's05_civilization_cognition_dome'], 1):
        changes[f'block.hk3gtl.{machine}'] = old[f'hk3gtl.research.lab.grade.{stage}']
    changes['block.hk3gtl.i13_honkai_resistant_coating_array'] = '崩坏抗性包覆阵列' if zh else 'Honkai-Resistant Coating Array'
    changes['hk3gtl.machine.i13_honkai_resistant_coating_array.tooltip.0'] = ('对受控纳米群施加抗崩坏包覆，输出抗性纳米群与废包覆液。' if zh else 'Coats controlled nano swarms and outputs resistant swarms and spent coating fluid.')
    changes['hk3gtl.machine.i13_honkai_resistant_coating_array.tooltip.1'] = ('需要崩坏抗性包覆研究，使用绑定玩家的无线电网。' if zh else 'Requires Honkai resistance research and draws from the bound player\'s wireless grid.')
    changes['hk3gtl.machine.abyss_research_analysis_matrix.tooltip.0'] = ('§7崩坏现象研究与工程试验平台' if zh else '§7Research and engineering trials for Honkai phenomena')
    changes['hk3gtl.machine.abyss_research_analysis_matrix.tooltip.1'] = ('§7承载独立研究队列，完成工程研究后可在原址扩建' if zh else '§7Hosts independent research queues; expand on the same site after engineering research')
    changes['hk3gtl.machine.abyss_research_analysis_matrix.tooltip.2'] = ('§7结构：17×25×17（宽×长×高）' if zh else '§7Structure: 17×25×17 (width×depth×height)')
    changes['hk3gtl.research.lab.tooltip'] = ('开题支付研究点或背包材料，实验仍需完成；使用绑定玩家电网，并行槽位与注视规则随研究所阶级变化。' if zh else 'Pay research points or inventory materials at start; experiments remain required. Uses the bound player grid; topic slots and gaze rules depend on institute grade.')
    changes['_comment_approved_architecture_r156'] = f'变更记录 #1 · {stamp:%Y-%m-%d %H:%M:%S} Asia/Hong_Kong · 修订156；新增I13及S02–S05名称，更新S01尺寸和职责，五阶共有说明按实际阶级执行。名称沿用批准总表，无关条目保留。'
    appended = {}
    for key, value in changes.items():
        if key in old:
            pattern = r'("' + re.escape(key) + r'"\s*:\s*)"(?:\\.|[^"\\])*"'
            replacement = json.dumps(value, ensure_ascii=False)
            text, count = re.subn(pattern, lambda m: m[1] + replacement, text)
            if count != 1:
                raise ValueError(f'语言键异常：{key}，数量{count}')
        else:
            appended[key] = value
    if appended:
        index = text.rfind('}')
        prefix = text[:index].rstrip()
        tail = ',\n' + '\n'.join('  ' + json.dumps(k, ensure_ascii=False) + ': ' + json.dumps(v, ensure_ascii=False) + (',' if i < len(appended)-1 else '') for i, (k,v) in enumerate(appended.items()))
        text = prefix + tail + '\n}\n'
    json.loads(text)
    with path.open('w', encoding='utf-8', newline='\n') as output:
        output.write(text)

for locale in ('zh_cn', 'en_us'):
    update_lang(locale)
path = ROOT / 'src/main/resources/assets/hk3gtl/changelog.json'
data = json.loads(path.read_text(encoding='utf-8'))
entry = {
    'revision': 156, 'date': stamp.strftime('%Y-%m-%d'), 'time': stamp.strftime('%H:%M:%S'),
    'reason': '将负责人最终指定四个ZIP的18座机器、21种结构正式接入游戏',
    'changes': [
        'I01四阶V8覆盖V7旧采集塔；I02–I08 V7、I09–I13 V6、S01–S05 V1只替换正式主控，主体逐格保留。',
        '正式注册I13和S02–S05；工业接口按工艺能力要求成型，填充壳不计能力；研究沿用背包支付和玩家电网。',
        'I01高级阶段保留低级采集配方，I06–I13使用对应工艺执行身份与注册类型，不跳过研究权限或事实条件。',
        'I13沿用工业主控装配模板；S02–S05消耗上一阶主控并沿用S01既有装配材料、1200tick、MAX耗电，绑定正式阶级解锁课题。',
        'I09–I12控制器研究门槛改为既定SSP/NBS/NRA/NSP，避免错误RN-CCE反锁；同步中英文名称及最新尺寸。',
        '增加21项正式资源、必要接口可安置性、七次逐块继承及执行身份回归；游戏成型和大型S05扫描性能另行实测。'
    ]}
data['entries'] = [entry] + [e for e in data['entries'] if e.get('revision') != 156]
path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print('已更新中英文正式名称、尺寸和修订156记录')
