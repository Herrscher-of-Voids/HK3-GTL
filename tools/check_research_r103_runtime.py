"""修订103：读取实例只读导出；核对完整性与最终研究配方，不认可生存资源白名单。
变更记录 #1 2026-09-30 01:00:17。删除：无；新增：哈希/计数/实例状态检查；修改：无；用途：进入游戏后复用真实产物验收。
"""
from pathlib import Path
import argparse, hashlib, json, sys

def verify(directory):
    directory=Path(directory)
    report=json.loads((directory/'report.json').read_text(encoding='utf-8'))
    failures=[]
    if report.get('schema')!=1 or report.get('revision') not in (103,104,106,107,108): failures.append('unsupported_report')
    for field in ('export_complete','recipe_snapshot_unchanged','process_recipe_audit_pass','registered_recipe_export_complete'):
        if report.get(field) is not True: failures.append(field)
    for filename in ('manifest.json','registries.json','recipes.jsonl'):
        target=directory/filename
        expected=report.get('sha256',{}).get(filename)
        if not expected or not target.is_file(): failures.append('missing:'+filename); continue
        digest=hashlib.sha256()
        with target.open('rb') as source:
            for chunk in iter(lambda:source.read(1024*1024),b''): digest.update(chunk)
        if digest.hexdigest()!=expected: failures.append('sha256:'+filename)
    manifest=json.loads((directory/'manifest.json').read_text(encoding='utf-8'))
    if manifest.get('revision')!=report.get('revision'): failures.append('manifest_revision')
    expected_ids=manifest.get('expected_process_plan_ids',[])
    if report.get('revision')==103:
        expected_count=250 # 旧实测报告兼容，原报告没有清单；不把此常量用于新版本。
    else:
        expected_count=len(expected_ids)
        if not expected_count or len(set(expected_ids))!=expected_count: failures.append('invalid_expected_plan_ids')
        if not manifest.get('process_table_sha256') or manifest['process_table_sha256']!=report.get('process_table_sha256'):
            failures.append('process_table_sha256')
    if report.get('expected_process_recipes')!=expected_count or report.get('passed_process_recipes')!=expected_count:
        failures.append('expected_process_recipe_count')
    checks=report.get('checks',[])
    if len(checks)!=expected_count or len({c.get('plan') for c in checks})!=expected_count: failures.append('unique_plan_coverage')
    if expected_ids and {c.get('plan') for c in checks}!=set(expected_ids): failures.append('plan_identity_coverage')
    for check in checks:
        if check.get('failures') or check.get('audit_error'): failures.append(check.get('plan','unknown'))
    return dict(report=str(directory/'report.json'),registration_verified=not failures,failures=failures,
        gameplay_verified=False,survival_catalog_verified=False,
        boundary='配方注册核验不等于100课题可玩；资源池和物理任务仍需独立接线与验收。')

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--instance',type=Path,required=True,help='实例的minecraft目录')
    args=ap.parse_args()
    base=args.instance/'logs/hk3gtl-research-audit'
    directories=sorted((p for p in base.iterdir() if p.is_dir()),key=lambda p:p.name,reverse=True) if base.is_dir() else []
    if not directories:
        print(json.dumps(dict(instance=str(args.instance),status='WAITING_FOR_GAME',registration_verified=False),ensure_ascii=False,indent=2));return 2
    newest=directories[0]
    if not (newest/'report.json').is_file():
        print(json.dumps(dict(instance=str(args.instance),directory=str(newest),status='INCOMPLETE_EXPORT',registration_verified=False),ensure_ascii=False,indent=2));return 2
    try: result=verify(newest)
    except (OSError,ValueError,KeyError,TypeError) as exc:
        result=dict(registration_verified=False,status='INVALID_EXPORT',error=str(exc))
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if result['registration_verified'] else 1
if __name__=='__main__':sys.exit(main())

# 变更记录 #2 · 2026-09-30 01:18:22 · 修订104。删除：新版本固定250条限制；新增：清单身份及源表哈希核对；用途：扩展配方仍准确验收，兼容旧103报告。

# 变更记录 #3 · 2026-09-30 01:42:00 · 修订106。删除：无；新增：106报告支持；修改：版本白名单；用途：继续核验全部哈希和配方，不改写旧报告。

# 变更记录 #107 · 2026-09-30 02:20:26 · 修订107：删除旧电压输出键；修改为16档正式键；用途：防止工具重新生成过期引用。
