"""修订74写入辅助：保留原文件、历史备注与UTF-8；所有写入纳入变更清单。"""
from pathlib import Path
from datetime import datetime
import re
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
JAVA = ROOT / 'src/main/java/com/sirin/hk3gtl'
RES = ROOT / 'src/main/resources'
LOG = ROOT / 'logs/revision74'


def write(path, text):
    if path.exists():
        if path.read_text('utf-8') == text:
            return
        backup = LOG / 'backup' / path.relative_to(ROOT)
        if not backup.exists():
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, backup)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')


def note(text, description):
    now = datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S')
    nums = [int(x) for x in re.findall(r'变更记录\s*#(\d+)', text)]
    num = max(nums, default=0) + 1
    block = f'/**\n * 【变更记录 #{num}】{now}（第 {num} 次备注 · 内测5修订74）\n * {description}\n */\n'
    return re.sub(r'(?m)^public (?:final )?class ', lambda m: block + m[0], text, count=1)


def patch_java(rel, transform, description):
    path = JAVA / rel
    text = path.read_text('utf-8')
    updated = transform(text)
    if updated != text:
        write(path, note(updated, description))


def new_java(rel, source, description):
    write(JAVA / rel, note(source, description))


def save_json(path, obj):
    write(path, json.dumps(obj, ensure_ascii=False, indent=2) + '\n')
