"""AE Mixin 静态审计：读取实例 JAR 与嵌套 JAR，解析注解并保留可复核证据。
变更记录 #1：2026-09-28，新增只读扫描器；不修改实例，不把声明当成运行时生效。
"""
import io, json, struct, zipfile, hashlib, re
from pathlib import Path
from collections import Counter
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'logs/ae-mixin-audit-20260928'
BASE = Path.home() / 'AppData/Roaming/PrismLauncher/instances'
PACKS = {'original': BASE/'GregTech-Leisure-1.4.5.2/minecraft', 'enhanced': BASE/'GregTech Leisure-增强版「巨构时代」 2.1/minecraft'}

class Reader:
    def __init__(self,b): self.b=b; self.i=0
    def take(self,n): b=self.b[self.i:self.i+n]; self.i+=n; return b
    def u1(self): return self.take(1)[0]
    def u2(self): return struct.unpack('>H',self.take(2))[0]
    def u4(self): return struct.unpack('>I',self.take(4))[0]

def parse(b):
    r=Reader(b); r.take(8); cp=[None]*r.u2(); i=1
    while i<len(cp):
        t=r.u1()
        if t==1: cp[i]=r.take(r.u2()).decode('utf-8','replace')
        elif t in (3,4): cp[i]=struct.unpack('>i' if t==3 else '>f',r.take(4))[0]
        elif t in (5,6): cp[i]=struct.unpack('>q' if t==5 else '>d',r.take(8))[0]; i+=1
        elif t in (7,8,16,19,20): cp[i]=('ref',r.u2())
        elif t in (9,10,11,12,17,18): cp[i]=(t,r.u2(),r.u2())
        elif t==15: cp[i]=(t,r.u1(),r.u2())
        else: raise ValueError(t)
        i+=1
    def val(q):
        tag=chr(q.u1())
        if tag in 'BCDFIJSZsc': return cp[q.u2()]
        if tag=='e': return [cp[q.u2()],cp[q.u2()]]
        if tag=='@': return ann(q)
        if tag=='[': return [val(q) for _ in range(q.u2())]
        raise ValueError(tag)
    def ann(q):
        typ=cp[q.u2()]; values={}
        for _ in range(q.u2()): key=cp[q.u2()]; values[key]=val(q)
        return {'type':typ,'values':values}
    def attrs():
        result=[]
        for _ in range(r.u2()):
            name=cp[r.u2()]; q=Reader(r.take(r.u4()))
            if name in ('RuntimeVisibleAnnotations','RuntimeInvisibleAnnotations'):
                result += [ann(q) for _ in range(q.u2())]
        return result
    r.u2(); name=cp[cp[r.u2()][1]]; r.u2(); r.take(r.u2()*2)
    fields=[]; methods=[]
    for bucket in (fields,methods):
        for _ in range(r.u2()):
            flags=r.u2(); n=cp[r.u2()]; desc=cp[r.u2()]; a=attrs()
            bucket.append({'name':n,'descriptor':desc,'annotations':a})
    annotations=attrs()
    return {'class':name.replace('/','.'),'annotations':annotations,'methods':methods,'fields':fields}

def scan(pack,path):
    records=[]; configs=[]; inventory=[]; errors=[]; all_mixins=[]; classes=set()
    def archive(data,label,depth=0):
        z=zipfile.ZipFile(io.BytesIO(data)); names=z.namelist(); declarations={}
        for n in names:
            if not n.endswith('.json') or 'refmap' in n: continue
            try: d=json.loads(re.sub(r',\s*([\]}])',r'\1',z.read(n).decode('utf-8-sig')))
            except Exception: continue
            if not isinstance(d,dict) or 'package' not in d or not any(k in d for k in ('mixins','client','server')): continue
            cfg={'jar':label,'name':n,'config':d}; configs.append(cfg)
            prefix=d.get('package','')
            for side in ('mixins','client','server'):
                for c in d.get(side,[]):
                    if not isinstance(c,str): continue
                    declarations.setdefault((prefix+'.'+c).strip('.'),[]).append({'config':n,'side':side,'plugin':d.get('plugin'),'required':d.get('required'),'priority':d.get('priority',1000)})
        for n in names:
            if n.endswith('.class'):
                classes.add(n[:-6].replace('/','.'))
                b=z.read(n)
                if b'Lorg/spongepowered/asm/mixin/Mixin;' not in b: continue
                try: d=parse(b)
                except Exception as e: errors.append([label,n,str(e)]); continue
                a=next((a for a in d['annotations'] if a['type']=='Lorg/spongepowered/asm/mixin/Mixin;'),None)
                if not a: continue
                targets=a['values'].get('value',[])+a['values'].get('targets',[])
                targets=[t[1:-1].replace('/','.') if t.startswith('L') and t.endswith(';') else t.replace('/','.') for t in targets]
                d.update(jar=label,targets=targets,declared=declarations.get(d['class'],[]),sha256=hashlib.sha256(b).hexdigest(),references_ae=b'appeng/' in b)
                all_mixins.append(d)
            elif n.endswith('.jar') and depth<3:
                try: archive(z.read(n),label+'!/'+n,depth+1)
                except Exception as e: errors.append([label,n,str(e)])
        inventory.append({'jar':label,'sha256':hashlib.sha256(data).hexdigest(),'classes':sum(n.endswith('.class') for n in names),'manifest':z.read('META-INF/MANIFEST.MF').decode('utf-8','replace') if 'META-INF/MANIFEST.MF' in names else ''})
    for p in sorted((path/'mods').glob('*.jar')):
        try: archive(p.read_bytes(),p.name)
        except Exception as e: errors.append([p.name,str(e)])
    # 按真实目标包识别 AE2、附属及 GTL 内置 AE 机器，不依赖 Mixin 文件名猜测。
    prefixes=('appeng.','com.glodblock.github.','net.pedroksl.advanced_ae.','net.pedroksl.ae2','com.ae2','org.appliedenergistics.','com.glodblock.','com.github.glodblock.','net.p3pp3rf1y.functionalstorage.compat.ae2')
    for d in all_mixins:
        d['missing_targets']=[t for t in d['targets'] if t not in classes]
        target=' '.join(d['targets']).lower()
        if any(t.startswith(prefixes) for t in d['targets']) or any(s in target for s in ('extendedae','expattern','molecularmanip','mae2','ae2','craftingcpu')):
            records.append(d)
    indirect=[d for d in all_mixins if d not in records and d['references_ae']]
    result={'pack':pack,'path':str(path),'inventory':inventory,'configs':configs,'all_mixins':all_mixins,'ae_mixins':records,'indirect_ae_mixins':indirect,'errors':errors}
    (OUT/(pack+'.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(pack,'jars',len(inventory),'all mixins',len(all_mixins),'AE candidates',len(records),'errors',errors)
    print(json.dumps(Counter(d['jar'] for d in records),ensure_ascii=False,indent=2))

if __name__=='__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    for key,path in PACKS.items(): scan(key,path)
