"""Build lossless HK3P v2 runtime resources; reviewed sources remain untouched."""
from __future__ import annotations
import gzip
import hashlib
import importlib.util
import json
import mmap
import re
from pathlib import Path
import struct
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / 'src/main/resources/data/hk3gtl'
OUT = ROOT / 'build/generated/compactResources/data/hk3gtl'
LOG = ROOT / 'logs/native-distance-package-r219-20261108'
ROW = np.dtype([('pos', '>i4'), ('state', '>u2'), ('bytes', '>i4')])
RUN = struct.Struct('>iiiHi')
CELL = re.compile(rb'\{\s*"pos"\s*:\s*\[\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\]\s*,\s*"state"\s*:\s*"([^"\\]+)"\s*\}')
spec = importlib.util.spec_from_file_location('nbt_source', Path(__file__).with_name('build_late_approved_resources_20261026.py'))
nbt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nbt)


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''): h.update(b)
    return h.hexdigest()


def ports(path):
    with path.open('rb') as f, mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as m:
        at = m.find(b'"ports"')
        assert at >= 0, path
        at = m.find(b':', at) + 1
        return json.JSONDecoder().raw_decode(m[at:at + 2_000_000].decode('utf-8').lstrip())[0]


def read_source(key, meta):
    path = RES / 'structures/approved_preview' / (key + '.bin.gz')
    if path.exists():
        raw = gzip.decompress(path.read_bytes())
        header = struct.unpack_from('>9iH', raw)
        assert header[:2] == (0x484b3350, 1)
        at = 38; palette = []
        for _ in range(header[-1]):
            n = struct.unpack_from('>H', raw, at)[0]; at += 2
            palette.append(raw[at:at+n].decode('ascii')); at += n

        def chunks():
            nonlocal at
            remaining = header[-2]
            while remaining:
                count = min(65536, remaining, (len(raw)-at)//10)
                rows = np.frombuffer(raw, ROW, count=count, offset=at)
                entities = np.flatnonzero(rows['bytes'])
                plain = int(entities[0]) if len(entities) else count
                if plain:
                    yield rows['pos'][:plain], rows['state'][:plain], b''
                    at += plain*10; remaining -= plain
                else:
                    pos, state, length = struct.unpack_from('>iHi', raw, at); at += 10
                    assert 0 < length <= 1_048_576
                    tag = raw[at:at+length]; assert len(tag) == length; at += length
                    yield np.array([pos], dtype='>i4'), np.array([state], dtype='>u2'), tag
                    remaining -= 1
            assert at == len(raw)
        return header[2:5], header[5:8], palette, header[-2], chunks()

    source = RES / 'structures/approved' / (key + '.nbt')
    assert digest(source) == meta['template_sha256']
    raw = gzip.decompress(source.read_bytes()); fields = nbt.top(raw)
    palette = nbt.palette(raw, fields['palette'])
    count = struct.unpack_from('>i', raw, fields['blocks'][0]+1)[0]
    assert meta.get('blocks',count)==count
    meta['blocks']=count

    def chunks():
        at = fields['blocks'][0]+5; positions = []; states = []
        for _ in range(count):
            _, at, pos, state, _, entity = nbt.block(raw, at)
            linear = (pos[0]*meta['size_xyz'][1]+pos[1])*meta['size_xyz'][2]+pos[2]
            if entity is not None:
                if positions:
                    yield np.array(positions, dtype='>i4'), np.array(states, dtype='>u2'), b''
                    positions.clear(); states.clear()
                tag = b'\x0a\x00\x00'+raw[entity:nbt.skip(raw, entity, 10)]
                yield np.array([linear], dtype='>i4'), np.array([state], dtype='>u2'), tag
            else:
                positions.append(linear); states.append(state)
        if positions: yield np.array(positions, dtype='>i4'), np.array(states, dtype='>u2'), b''
        assert at == fields['blocks'][1]
    return meta['size_xyz'], meta['controller'], palette, count, chunks()


def build(key):
    metadata_path = RES / 'structures/approved' / (key+'.json')
    meta = json.loads(metadata_path.read_text(encoding='utf-8'))
    meta['size_xyz']=meta.get('size_xyz',meta.get('size'))
    size, controller, palette, count, chunks = read_source(key, meta)
    assert list(size) == meta['size_xyz'] and list(controller) == meta['controller'] and count == meta['blocks']
    destination = OUT / 'structures/compact' / (key+'.bin.gz')
    destination.parent.mkdir(parents=True, exist_ok=True)
    canonical = hashlib.sha256(); runs = entities = seen = 0
    occupied = np.zeros((int(np.prod(size))+7)//8, dtype=np.uint8)
    with destination.open('wb') as f, gzip.GzipFile(fileobj=f, mode='wb', compresslevel=9, mtime=0) as g:
        g.write(struct.pack('>9iH', 0x484b3350, 2, *size, *controller, count, len(palette)))
        for state in palette:
            b=state.encode('ascii'); g.write(struct.pack('>H', len(b))+b)
        for positions, states, tag in chunks:
            positions = positions.astype(np.int64); states = states.astype(np.int64)
            assert len(positions) and np.all(positions >= 0) and np.all(positions < np.prod(size))
            assert np.all(states >= 0) and np.all(states < len(palette))
            # Byte-index scatter cannot detect duplicates within one vector; unique does.
            assert len(np.unique(positions)) == len(positions)
            byte, bit = positions >> 3, (1 << (positions & 7)).astype(np.uint8)
            assert not np.any(occupied[byte] & bit), key
            np.bitwise_or.at(occupied, byte, bit)
            rows = np.zeros(len(positions), dtype=ROW); rows['pos']=positions; rows['state']=states
            rows['bytes']=len(tag)
            canonical.update(rows.tobytes()); canonical.update(tag)
            if tag:
                g.write(RUN.pack(int(positions[0]), 0, 1, int(states[0]), len(tag))+tag)
                entities += 1; runs += 1
            else:
                # Preserve source order: encode maximal equal-state arithmetic progressions.
                d = np.diff(positions)
                changes = np.flatnonzero((states[1:] != states[:-1]) | np.r_[False, d[1:] != d[:-1]])+1
                starts = np.r_[0, changes]; ends = np.r_[changes, len(positions)]
                for start, end in zip(starts, ends):
                    length = int(end-start); step = int(positions[start+1]-positions[start]) if length>1 else 0
                    g.write(RUN.pack(int(positions[start]), step, length, int(states[start]), 0)); runs += 1
            seen += len(positions)
    assert seen == count
    # Independent expansion, including complete entity payload, must reproduce every original record.
    actual = hashlib.sha256(); decoded = 0
    with gzip.open(destination,'rb') as g:
        assert struct.unpack('>9iH',g.read(38)) == (0x484b3350,2,*size,*controller,count,len(palette))
        for state in palette: assert g.read(struct.unpack('>H',g.read(2))[0]).decode('ascii') == state
        while decoded < count:
            start, step, length, state, nb = RUN.unpack(g.read(RUN.size))
            assert 0<length<=count-decoded and (not nb or length==1)
            rows=np.zeros(length, dtype=ROW);rows['pos']=start+np.arange(length,dtype=np.int64)*step
            rows['state']=state;rows['bytes']=nb
            actual.update(rows.tobytes());actual.update(g.read(nb));decoded += length
        assert g.read(1)==b'' and actual.digest()==canonical.digest()
    # Pattern JSON deliberately uses generic port markers and sometimes omits default facing.
    # Keep those exact strings separately; real construction/preview NBT remains unchanged.
    overrides={}; layout_digest=hashlib.sha256(); layout_count=0
    with (RES/'approved_architecture'/(key+'.json')).open('rb') as source, mmap.mmap(source.fileno(),0,access=mmap.ACCESS_READ) as mapped, gzip.open(destination,'rb') as g:
        matches=iter(CELL.finditer(mapped));g.read(38)
        for state in palette:g.read(2+len(state.encode('ascii')))
        done=0
        while done<count:
            start,step,length,state,nb=RUN.unpack(g.read(RUN.size));g.read(nb)
            for i in range(length):
                match=next(matches,None);assert match is not None, (key,'missing architecture cell',done)
                x,y,z=(int(match[j]) for j in (1,2,3));linear=(x*size[1]+y)*size[2]+z
                assert linear==start+i*step,(key,'architecture order/coordinate mismatch',done)
                text=match[4].decode('ascii')
                layout_digest.update(struct.pack('>i',linear)+text.encode()+b'\x00')
                if text!=palette[state]:overrides[str(linear)]=text
                layout_count+=1
            done+=length
        assert next(matches,None) is None and layout_count==count
    small = {**meta, 'size':list(size), 'ports':ports(RES/'approved_architecture'/(key+'.json')),
             'layout_state_overrides':overrides,'layout_records_sha256':layout_digest.hexdigest(),
             'compact_records_sha256':canonical.hexdigest(), 'compact_sha256':digest(destination),
             'source_architecture_sha256':digest(RES/'approved_architecture'/(key+'.json')),
             'runtime_format':'HK3P/2; original-order arithmetic runs; full entity NBT'}
    target=OUT/'compact_architecture'/(key+'.json');target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(small,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    result={'key':key,'blocks':count,'runs':runs,'entities':entities,'bytes':destination.stat().st_size,
            'records_sha256':canonical.hexdigest(),'layout_records_sha256':layout_digest.hexdigest(),
            'layout_state_overrides':len(overrides),'all_records_and_entities_equal':True}
    print(json.dumps(result),flush=True);return result


if __name__=='__main__':
    keys=sys.argv[1:] or sorted(p.stem for p in (RES/'approved_architecture').glob('*.json'))
    records=[build(k) for k in keys]
    LOG.mkdir(parents=True,exist_ok=True)
    (LOG/'compact-resource-verification.json').write_text(json.dumps({'structures':records,
        'total_blocks':sum(r['blocks'] for r in records),'total_bytes':sum(r['bytes'] for r in records)},indent=2)+'\n')
