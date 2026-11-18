from pathlib import Path
import json
import re

root = Path(__file__).resolve().parents[1]
machine_names = json.loads((root / 'src/main/resources/data/hk3gtl/guide/tutorial_names.json').read_text(encoding='utf-8'))['machines']
aliases = {key: [name] for key, name in machine_names.items()}
aliases.update({'I01': [machine_names['I01'], '采集塔'],
                'I02': [machine_names['I02'], '样本光谱分析阵列', '光谱阵列'],
                'I03': [machine_names['I03'], '分馏中心', '分离中心'],
                'I04': [machine_names['I04'], '稳定塔'],
                'I06': [machine_names['I06'], '崩坏燃料调配厂'],
                'I09': [machine_names['I09'], '魂钢前驱体混合釜']})
machine_pattern = re.compile(r'(?<![A-Za-z0-9:-])(?:I\d\d(?:-[1-4])?|S0[1-5]|W\d\d|H01)(?![A-Za-z0-9:-])')
material_names = {'steel': '钢板', 'tungsten_steel': '钨钢板', 'titanium': '钛板', 'stainless_steel': '不锈钢板',
                  'naquadah_alloy': '硅岩合金板', 'neutronium': '中子素板', 'tritanium': '三钛板'}

def normalize(text):
    text = re.sub(r'记录本队执行生产计划approved_[a-z0-9_]+并完整结算产物的事实；持有产物不代替该工艺事件。',
                  '由本队完成这道工艺的一整批生产，并领取全部产物。', text)
    text = machine_pattern.sub(lambda match: machine_names[match[0]], text)
    for key, names in aliases.items():
        name = machine_names[key]
        for alias in sorted(names, key=len, reverse=True):
            text = re.sub(re.escape(name) + r'\s*' + re.escape(alias), lambda _: name, text)
    text = re.sub(r'forge:plates/([a-z_]+)', lambda match: material_names[match[1]], text)
    text = re.sub(r'(?:forge|gtceu):circuits/([a-zA-Z]+)', lambda match: match[1].upper() + '级电路', text)
    return text

def clean_player_fields(value):
    if isinstance(value, dict):
        value.pop('_comment', None)
        for key, field in value.items():
            if key in ('title', 'title_en', 'subtitle', 'description', 'label', 'detail'):
                if isinstance(field, str):
                    value[key] = normalize(field)
                elif isinstance(field, list):
                    value[key] = [normalize(text) for text in field]
            else:
                clean_player_fields(field)
    elif isinstance(value, list):
        for field in value:
            clean_player_fields(field)
    return value
