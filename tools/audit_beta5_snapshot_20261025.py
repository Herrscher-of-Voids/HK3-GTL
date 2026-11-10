# -*- coding: utf-8 -*-
"""采集本轮全库审计的文件身份、资源语法与现行注册概况，不给完成率打分。

【变更记录 #1】2026-10-25 00:48:00（审计工具，不增加模组修订）
删除：无。新增：源码/测试/资源/规则/设计哈希清单及JSON语法检查。
修改：不修改产品代码、历史审计或游戏实例；所有结果单独写入本轮logs。
用途：使逐系统人工审计具有可复核的全库覆盖基准。
"""
from pathlib import Path
import collections
import datetime as dt
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'logs/beta5-audit-20261025'


def identity(path):
    raw = path.read_bytes()
    result = {'path':path.relative_to(ROOT).as_posix(), 'sha256':hashlib.sha256(raw).hexdigest(), 'bytes':len(raw)}
    try:
        text = raw.decode('utf-8-sig')
        result['lines'] = len(text.splitlines())
        if path.suffix == '.java':
            result['package'] = next(iter(re.findall(r'^package\s+([^;]+);',text,re.M)), '')
            result['declarations'] = re.findall(r'\b(?:class|interface|enum|record)\s+(\w+)', strip_comments(text))
    except UnicodeDecodeError:
        pass
    return result


def strip_comments(text):
    # 保留字符串中的URL和注释样式文本，避免误删真实业务表达式。
    token = re.compile(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|/\*[\s\S]*?\*/|//[^\n]*')
    return token.sub(lambda m: '' if m[0].startswith(('/',)) else m[0],text)


def main():
    OUT.mkdir(exist_ok=True)
    categories = {
        'main_java': list((ROOT/'src/main/java').rglob('*.java')),
        'test_java': list((ROOT/'src/test/java').rglob('*.java')),
        'main_resources': [p for p in (ROOT/'src/main/resources').rglob('*') if p.is_file()],
        'rules': [p for p in (ROOT/'rule').rglob('*') if p.is_file()],
        'beta5_design': [p for p in (ROOT/'doc/HK3GTL-内测5').rglob('*') if p.is_file() and not any(x in p.parts for x in ('完整对话归档','讨论记录','69座重设计_实体预览01','69座重设计_实体预览02'))],
        'discussions': list((ROOT/'doc/HK3GTL-内测5/讨论记录').glob('*.html')),
    }
    inventory = {key:[identity(p) for p in sorted(paths)] for key,paths in categories.items()}
    syntax = []; duplicates = []
    for p in sorted((ROOT/'src/main/resources').rglob('*.json')):
        repeated = []
        def pairs(items):
            result = {}
            for key,value in items:
                if key in result:repeated.append(key)
                result[key] = value
            return result
        try:
            json.loads(p.read_text(encoding='utf-8-sig'),object_pairs_hook=pairs)
        except Exception as exc:
            syntax.append({'path':p.relative_to(ROOT).as_posix(),'error':str(exc)})
        if repeated:duplicates.append({'path':p.relative_to(ROOT).as_posix(),'keys':repeated})
    report = {
        'created_at':dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat(),
        'scope':'主产品Java、测试Java、正式资源全量文件身份；JSON全量语法与重复键。哈希索引不等于语义审查通过。',
        'counts':{key:len(rows) for key,rows in inventory.items()},
        'java_package_counts':dict(collections.Counter(row['package'] for row in inventory['main_java'])),
        'json_files_checked':len(list((ROOT/'src/main/resources').rglob('*.json'))),
        'json_syntax_failures':syntax,'json_duplicate_keys':duplicates,'files':inventory,
    }
    (OUT/'repository-inventory.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ('files','java_package_counts')},ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
