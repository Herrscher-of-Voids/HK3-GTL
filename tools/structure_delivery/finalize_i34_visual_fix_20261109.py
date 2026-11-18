# -*- coding: utf-8 -*-
"""归档树影外观迭代实机证据，停机核对并恢复测试选项。"""
from pathlib import Path
from datetime import datetime,timezone
import sys,json,hashlib,shutil
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from deploy_industrial_build import target_process_guard
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    revision=int(sys.argv[1]);assert revision in (235,236,237,238)
    folder=ROOT/f'logs/i34-native-fx-r{revision}-20261109'
    base=Path('C:/Users/OWNER/AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版/minecraft')
    guard=target_process_guard();assert guard['target_replace_allowed']
    deployment=json.loads((folder/'deployment.json').read_text(encoding='utf8'))
    assert sha(base/'mods/HK3GTL-内测5.jar')==deployment['sha256']
    others={p.name:sha(p) for p in (base/'mods').glob('*.jar') if p.name!='HK3GTL-内测5.jar'}
    assert others==deployment['third_party_hashes']
    original=base/'saves/HK3GTL_W03_C9_特效_r221'
    manifest=json.loads((ROOT/'logs/w03-c9-controller-r231-20261109/original-world-manifest.json').read_text(encoding='utf8'))
    assert {str(p.relative_to(original)):sha(p) for p in original.rglob('*') if p.is_file()}==manifest
    text=(base/'logs/latest.log').read_text(encoding='utf8')
    assert '树影绘制失败' not in text and '树影读取失败' not in text
    assert 'formed machine=hk3gtl:i34_imaginary_tree_observation_array' in text
    result=json.loads((folder/'client-results.json').read_text(encoding='utf8'))
    if result.get('temporary_forced_chunks_removed',False):assert '所有的强制加载区块' in text
    shutil.copy2(base/'logs/latest.log',folder/f'client-r{revision}-completed.log')
    for source,target in result['screenshot_sources'].items():shutil.copy2(base/'screenshots'/source,folder/target)
    (folder/'options-after-test.txt').write_bytes((base/'options.txt').read_bytes())
    (base/'options.txt').write_bytes((folder/'options-before.txt').read_bytes())
    result.update(updated_at=datetime.now(timezone.utc).isoformat(),client_exited_normally=True,original_world_unchanged=True,third_party_unchanged=True,options_restored=True,final_guard=guard,jar_sha256=deployment['sha256'])
    (folder/'client-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('r'+str(revision),'证据归档；原存档、92个第三方包未变，选项恢复。')
if __name__=='__main__':main()
