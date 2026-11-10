"""2026-09-28：只读扫描本机旧HK3GTL发布包/源码候选，报告写入项目日志。
不加载模组，不解压覆盖，不跟随链接，不进入Infinity Legacy II实例。
"""
import concurrent.futures
import datetime
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'logs' / 'historical-build-search-20260928'
OUT.mkdir(exist_ok=True)
name_pattern = re.compile(r'hk3|honkai|崩坏|崩壞|pre-beta[1-5]', re.I)
old_path_pattern = re.compile(r'内测[1-4一二三四]|內測[1-4一二三四]|beta[1-4]', re.I)


def scan(root):
    # 变更#2：同名实例带版本后缀时也跳过；原扫描只作文件名枚举，后续核验均排除此实例。
    args = ['rg','--files','--hidden','--no-ignore','-g','!**/Infinity Legacy II*/**']
    for pattern in ['*.jar','*.jar.disabled','*.jar.bak','*.zip','*.7z','*.rar','*.tar','*.tar.gz','gradle.properties']:
        args += ['-g',pattern]
    args.append(root)
    candidates = []
    count = 0
    with tempfile.TemporaryFile() as errors:
        proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=errors)
        for raw in proc.stdout:
            count += 1
            text = raw.decode('utf-8',errors='replace').strip()
            p = Path(text)
            named = bool(name_pattern.search(p.name))
            legacy_path = bool(old_path_pattern.search(text)) and p.suffix.lower() in {'.jar','.zip','.7z','.rar'}
            source = p.name == 'gradle.properties' and bool(name_pattern.search(str(p.parent)))
            if not (named or legacy_path or source):
                continue
            try:
                stat = p.stat()
                candidates.append({'path':text,'size':stat.st_size,'modified':datetime.datetime.fromtimestamp(stat.st_mtime).astimezone().isoformat(),'match':'filename' if named else 'source' if source else 'legacy_directory'})
            except OSError as exc:
                candidates.append({'path':text,'error':str(exc)})
        code = proc.wait()
        errors.seek(0)
        error_lines = errors.read().decode('utf-8',errors='replace').splitlines()
    return {'root':root,'listed_artifact_paths':count,'exit_code':code,'error_count':len(error_lines),'error_samples':error_lines[:8],'candidates':candidates}


if __name__ == '__main__':
    roots = [p + ':\\' for p in 'CDE' if Path(p + ':\\').exists()]
    report = {'time':datetime.datetime.now().astimezone().isoformat(),'excluded':'Infinity Legacy II；不跟随符号链接/目录联接','roots':[]}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        futures = {pool.submit(scan,r):r for r in roots}
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            report['roots'].append(result)
            print(json.dumps({k:v for k,v in result.items() if k!='candidates'},ensure_ascii=False),flush=True)
            print(json.dumps({'root':result['root'],'candidate_count':len(result['candidates'])},ensure_ascii=False),flush=True)
    destination = OUT / 'scan-results.json'
    destination.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'report':str(destination),'candidate_count':sum(len(r['candidates']) for r in report['roots'])},ensure_ascii=False),flush=True)
