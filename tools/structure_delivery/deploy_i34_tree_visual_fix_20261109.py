# -*- coding: utf-8 -*-
"""树影外观修复包停机替换，保留r234及第三方文件证据。"""
from pathlib import Path
from datetime import datetime,timezone
import sys,json,hashlib,shutil,zipfile
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from deploy_industrial_build import target_process_guard
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    revision=int(sys.argv[1]);assert revision in (235,236,237,238)
    previous=revision-1
    log=ROOT/f'logs/i34-native-fx-r{revision}-20261109'
    base=Path('C:/Users/OWNER/AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版/minecraft')
    guard=target_process_guard();assert guard['target_replace_allowed']
    assert 'BUILD SUCCESSFUL' in (log/'build.log').read_text(errors='replace')
    old=json.loads((ROOT/f'logs/i34-native-fx-r{previous}-20261109/deployment.json').read_text(encoding='utf8'))
    target=base/'mods/HK3GTL-内测5.jar';assert sha(target)==old['sha256']
    others={p.name:sha(p) for p in (base/'mods').glob('*.jar') if p!=target};assert others==old['third_party_hashes']
    backup=log/f'r{previous}-before-r{revision}.jar';assert not backup.exists();shutil.copy2(target,backup)
    source=ROOT/'build/libs/hk3gtl-0.5.0.jar'
    with zipfile.ZipFile(source) as z:
        assert z.testzip() is None
        assert json.loads(z.read('assets/hk3gtl/changelog.json'))['entries'][0]['revision']==revision
    shutil.copy2(source,target);shutil.copy2(source,ROOT/'build/libs/HK3GTL-内测5.jar')
    (log/'options-before.txt').write_bytes((base/'options.txt').read_bytes())
    r=dict(revision=revision,sha256=sha(target),bytes=target.stat().st_size,installed_at=datetime.now(timezone.utc).isoformat(),backup=str(backup),guard=guard,third_party_hashes=others,third_party_unchanged=True,game_verified=False,test_world='HK3GTL_Farview_r226_ClientTest')
    (log/'deployment.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('r'+str(revision),r['sha256'],r['bytes'])
if __name__=='__main__':main()
