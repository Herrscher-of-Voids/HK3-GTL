"""修订108：按批准电压配色换色，保留原像素位置/透明度/动画；固定备份确保可重复生成。"""
import json, hashlib, colorsys, shutil
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
RES=ROOT/'src/main/resources'
ASSET=RES/'assets/hk3gtl'
OUT=ROOT/'logs/palette-r108'
BACK=OUT/'texture-baseline'
PALETTE=json.loads((RES/'data/hk3gtl/catalog/voltage_palette.json').read_text(encoding='utf-8'))['palettes']
CIRCUITS=json.loads((RES/'data/hk3gtl/catalog/circuit_series.json').read_text(encoding='utf-8'))['entries']
TYPES='electric_motor electric_pump electric_piston conveyor_module robot_arm sensor emitter field_generator'.split()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rgb(s): return tuple(bytes.fromhex(s.lstrip('#')))
def blend(a,b,t): return tuple(round(x*(1-t)+y*t) for x,y in zip(a,b))
def texture(id):
    m=json.loads((ASSET/'models/item'/f'{id}.json').read_text(encoding='utf-8'))
    ns,path=m['textures']['layer0'].split(':')
    assert ns=='hk3gtl'
    return ASSET/'textures'/(path+'.png')
def tasks():
    for p in PALETTE:
        for typ in TYPES: yield typ+'_'+p['key'].lower(),p['tier'],'component'
    formal={e['id'] for e in CIRCUITS}
    for e in CIRCUITS: yield e['id'],e['tier'],'formal_circuit'
    for p in PALETTE:
        for form in ['processor','assembly','computer','processor_mainframe']:
            id=p['key'].lower()+'_'+form
            if id not in formal: yield id,p['tier'],'archived_circuit'
    for platform,tier in zip(['honkai_lattice','quantum_coherence','imaginary_topology','civilization_endurance'],[15,19,23,27]):
        yield platform+'_printed_circuit_board',tier,'platform_pcb'
def main():
    OUT.mkdir(parents=True,exist_ok=True); entries=[]
    for id,tier,kind in tasks():
        p=PALETTE[tier-15]; dest=texture(id); rel=dest.relative_to(RES); old=BACK/rel
        old.parent.mkdir(parents=True,exist_ok=True)
        if not old.exists(): shutil.copy2(dest,old)
        meta=Path(str(dest)+'.mcmeta'); meta_hash=sha(meta) if meta.exists() else None
        im=Image.open(old).convert('RGBA'); px=list(im.getdata()); mainc,accent,glow=[rgb(p[k]) for k in ['main','accent','glow']]
        # Components retain neutral metal pixels. Circuit art had a whole-image tint;
        # low-saturation pads use accent, colored traces use main, existing highlights use glow.
        selected=[x for x in px if x[3] and (kind!='component' or max(x[:3])-min(x[:3])>35)]
        assert selected,id
        values=sorted(max(x[:3]) for x in selected); peak=values[int((len(values)-1)*.95)]
        out=[]; changed=0; neutral=0
        for pixel in px:
            r,g,b,a=pixel; v=max(r,g,b); chroma=v-min(r,g,b)
            if not a or (kind=='component' and chroma<=35):
                out.append(pixel); neutral+=int(bool(a)); continue
            base=accent if kind!='component' and chroma/max(v,1)<.42 else mainc
            strength=v/max(peak,1)
            # Monotonic shading retains dark edges and existing light/dark detail.
            if strength<=1: color=tuple(round(c*strength) for c in base)
            else: color=blend(base,glow,min(1,(strength-1)*3))
            result=(*color,a); out.append(result); changed+=result!=pixel
        assert changed>0,id
        result=Image.new('RGBA',im.size); result.putdata(out); result.save(dest)
        assert result.getchannel('A').tobytes()==im.getchannel('A').tobytes()
        assert (sha(meta) if meta.exists() else None)==meta_hash
        entries.append(dict(id=id,tier=tier,kind=kind,palette=p['key'],destination=rel.as_posix(),baseline_sha256=sha(old),sha256=sha(dest),size=list(im.size),alpha_sha256=hashlib.sha256(im.getchannel('A').tobytes()).hexdigest(),mcmeta_sha256=meta_hash,changed_pixels=changed,preserved_neutral_pixels=neutral))
    ledger=dict(revision=108,generated_at=datetime.now().astimezone().isoformat(),method='Existing pixel recolor only; neutral component metal unchanged; source alpha, frames and mcmeta preserved',platform_pcb_convention='Shared PCB uses platform entry tier HBV/QSV/IMV/WFV; no new recipe or circuit tier',entries=entries)
    (RES/'data/hk3gtl/catalog/voltage_art108.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+chr(10),encoding='utf-8')
    (OUT/'texture-manifest.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+chr(10),encoding='utf-8')
    font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',17)
    sheet=Image.new('RGB',(1280,16*106+65),'#171D28'); d=ImageDraw.Draw(sheet)
    headers=['电压','马达','泵','活塞','传送带','机械臂','传感器','发射器','力场','主电路']
    for i,h in enumerate(headers):d.text((i*126+8,12),h,font=font,fill='white')
    for row,p in enumerate(PALETTE):
        y=60+row*106; d.text((8,y+12),p['key'],font=font,fill=p['main']);d.rectangle((8,y+45,92,y+62),fill=p['main'])
        primary=next(e['id'] for e in CIRCUITS if e['tier']==p['tier'] and e['primary'])
        for col,id in enumerate([t+'_'+p['key'].lower() for t in TYPES]+[primary],1):
            im=Image.open(texture(id)).convert('RGBA'); frame=im.crop((0,0,im.width,im.width)).resize((80,80),Image.Resampling.NEAREST);sheet.paste(frame,(col*126+8,y),frame)
    sheet.save(OUT/'approved-palette-production.png')
    print(json.dumps({'textures':len(entries),'counts':{k:sum(e['kind']==k for e in entries) for k in sorted(set(e['kind'] for e in entries))},'alpha_and_animation_preserved':True},ensure_ascii=False))
if __name__=='__main__': main()
