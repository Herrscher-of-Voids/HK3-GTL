"""修订107：将当前源码和打包资源的旧电压键迁移到16档正式缩写；历史记录不改写。
先备份并检查所有目标冲突，再统一修改；纹理只改路径，像素与结构几何不变。
"""
from pathlib import Path
from datetime import datetime
import re, json, hashlib, zipfile

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'logs/voltage-keys-r107'
SYMBOLS='hbv hcv hrv hdv qsv qcv qev qav imv icv irv iwv wfv wsv civ cev'.split()
OLD=[f'{s}_{n}' for s in ('abyss','imaginary','quantum','finality') for n in range(1,5)]
MAP=dict(zip(OLD,SYMBOLS))
MAP.update({f'{s}-{n}':SYMBOLS[g*4+i] for g,s in enumerate(('ab','im','qt','fn')) for i,n in enumerate(('i','ii','iii','iv'))})
RX=re.compile(r'(?<![a-zA-Z0-9])(?:'+ '|'.join(sorted(map(re.escape,MAP),key=len,reverse=True))+r')(?![a-zA-Z0-9])',re.I)
LEX=re.compile(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|//[^\n]*|/\*[\s\S]*?\*/')

def convert(text):
    return RX.sub(lambda m:MAP[m[0].lower()].upper() if m[0].isupper() else MAP[m[0].lower()],text)

def java_code(text):
    out=[];pos=0
    for m in LEX.finditer(text):
        out.append(convert(text[pos:m.start()]))
        out.append(m[0] if m[0].startswith(('//','/*')) else convert(m[0]));pos=m.end()
    return ''.join(out)+convert(text[pos:])

def json_data(v):
    if isinstance(v,str):return convert(v)
    if isinstance(v,list):return [json_data(x) for x in v]
    if isinstance(v,dict):
        result={}
        for k,x in v.items():
            nk=convert(k)
            nx=x if k.startswith(('_comment','_history')) else json_data(x)
            if nk in result and result[nk]!=nx:raise ValueError('JSON键冲突 '+nk)
            result[nk]=nx
        return result
    return v

def java_note(text,stamp):
    n=max([int(x) for x in re.findall(r'变更记录\s*#(\d+)',text)],default=0)+1
    note=f'/**\n * 【变更记录 #{n}】{stamp}（第{n}次备注 · 内测5修订107）\n * 删除：本文件可执行代码中的旧电压键及常量引用，不保留旧键注册别名。\n * 新增：16档正式缩写作为唯一电压标识；逐文件映射见logs/voltage-keys-r107。\n * 修改：注册、配方、查询或标签引用按原tier序号一一迁移；数值、层级与资源内容保持原义。\n * 用途：避免显示名与实际注册键不一致；历史备注保留，旧存档不自动改写。\n */\n'
    match=re.search(r'(?m)^(?:public |final |abstract )*(?:class|interface|enum|record)\s',text)
    if not match:raise ValueError('找不到Java类型声明')
    return text[:match.start()]+note+text[match.start():]

def main():
    OUT.mkdir(exist_ok=True,parents=True)
    if (OUT/'migration.json').exists():raise SystemExit('已迁移，请使用验证器检查，禁止重复变更')
    stamp=datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S')
    files=[p for p in (ROOT/'src').rglob('*') if p.is_file()]
    plan=[]
    for p in files:
        rel=p.relative_to(ROOT).as_posix();dest=ROOT/convert(rel);before=p.read_bytes();after=before
        if p.name!='changelog.json':
            if p.suffix=='.java':
                text=before.decode('utf-8-sig');new=java_code(text)
                if new!=text:after=java_note(new,stamp).encode('utf-8')
            elif p.suffix in ('.json','.mcmeta'):
                text=before.decode('utf-8-sig');data=json.loads(text);new=json_data(data)
                if new!=data:after=(json.dumps(new,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
            elif p.suffix in ('.snbt','.txt','.js','.toml','.properties'):
                text=before.decode('utf-8-sig');after=convert(text).encode('utf-8')
        if before!=after or p!=dest:plan.append((p,dest,before,after))
    by_dest={}
    for p,q,b,a in plan:
        if q in by_dest and a!=by_dest[q][3]:raise ValueError('目标冲突 '+str(q))
        by_dest[q]=(p,q,b,a)
    planned={p for p,_,_,_ in plan}
    for p,q,b,a in plan:
        if q.exists() and q not in planned and q!=p:
            qb=q.read_bytes()
            if q.suffix=='.json':
                same=json_data(json.loads(qb.decode('utf-8-sig')))==json.loads(a.decode('utf-8-sig'))
            else:same=qb==a
            if not same:raise ValueError('已有目标不等价 '+str(q))
    backups={p for p,_,_,_ in plan}|{q for _,q,_,_ in plan if q.exists()}
    with zipfile.ZipFile(OUT/'before.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(backups):z.write(p,p.relative_to(ROOT).as_posix())
    records=[]
    for p,q,b,a in plan:
        q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(a)
        records.append({'old':p.relative_to(ROOT).as_posix(),'new':q.relative_to(ROOT).as_posix(),'before_sha256':hashlib.sha256(b).hexdigest(),'after_sha256':hashlib.sha256(a).hexdigest(),'pixels_unchanged':b==a if p.suffix=='.png' else None})
    for p,q,_,_ in plan:
        if p!=q and p not in by_dest:p.unlink()
    manifest={'at':stamp,'revision':107,'mapping':MAP,'changes':records,'scope':'当前源码、资源、测试；不更改历史文档、存档或纹理像素。非Java改动统一在本清单逐文件留存SHA与映射。'}
    (OUT/'migration.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'modified':len(records),'renamed':sum(p!=q for p,q,_,_ in plan),'png_preserved':sum(p.suffix=='.png' and b==a for p,q,b,a in plan),'manifest':str(OUT/'migration.json')},ensure_ascii=False))

if __name__=='__main__':main()
