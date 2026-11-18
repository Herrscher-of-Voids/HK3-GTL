"""Read-only beta5 registry discovery; UTF-8 document and GT API inspection."""
from pathlib import Path
import re, zipfile
root = Path(__file__).resolve().parents[1]
for p in (root/'doc/HK3GTL-内测5/04_研究系统').glob('*目录*.html'):
    print(p.name)
    for title in re.findall(r'"title":\s*"([^"]+)"',p.read_text(encoding='utf-8')):
        if '核心' in title or '神之键' in title: print(title)
for p in (root/'src/main/java/com/sirin/hk3gtl/common/item').rglob('*.java'):
    ids = re.findall(r'(?:register|registerItem)\("([a-z0-9_]+)"',p.read_text(encoding='utf-8'))
    if ids: print(p.name, ', '.join(ids))
z=zipfile.ZipFile(next((root/'.gradle').rglob('*gtceu*sources.jar')))
s=z.read('com/gregtechceu/gtceu/api/data/chemical/material/Material.java').decode()
for m in re.finditer(r'public Builder (?:fluid|gas)\(',s): print(s[m.start():m.start()+480])

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
