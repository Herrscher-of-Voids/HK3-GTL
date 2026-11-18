# -*- coding: utf-8 -*-
"""停机安装I34树影测试包，保留回滚和原第三方JAR。"""
from pathlib import Path
from datetime import datetime,timezone
import sys,json,hashlib,shutil,zipfile
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from deploy_industrial_build import target_process_guard

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    p=ROOT/'logs/i34-native-fx-r234-20261109'
    base=Path('C:/Users/OWNER/AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版/minecraft')
    guard=target_process_guard();assert guard['target_replace_allowed']
    assert 'BUILD SUCCESSFUL' in (p/'build.log').read_text(errors='replace')
    old=json.loads((ROOT/'logs/w03-c9-controller-r231-20261109/deployment.json').read_text(encoding='utf8'))
    target=base/'mods/HK3GTL-内测5.jar';assert sha(target)==old['sha256']
    backup=p/'r233-before-r234.jar';assert not backup.exists();shutil.copy2(target,backup)
    others={f.name:sha(f) for f in (base/'mods').glob('*.jar') if f.name!=target.name};assert others==old['third_party_hashes']
    source=ROOT/'build/libs/hk3gtl-0.5.0.jar'
    with zipfile.ZipFile(source) as z:
        assert z.testzip() is None
        assert json.loads(z.read('assets/hk3gtl/changelog.json'))['entries'][0]['revision']==234
    shutil.copy2(source,target);shutil.copy2(source,ROOT/'build/libs/HK3GTL-内测5.jar')
    (p/'options-before.txt').write_bytes((base/'options.txt').read_bytes())
    r=dict(revision=234,installed=True,sha256=sha(target),bytes=target.stat().st_size,installed_at=datetime.now(timezone.utc).isoformat(),backup=str(backup),guard=guard,third_party_hashes=others,third_party_unchanged=True,game_verified=False,test_world='HK3GTL_Farview_r226_ClientTest')
    (p/'deployment.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    r=dict(revision=234,status='已确认树影V1接入真实I34主控；构建、完整几何回归通过，r234已安装，客户端待测',controller=[0,361,-450],facing='south',dimension='minecraft:overworld',source_projection=[240,92,167],scale=.9,gt_formation_verified=False,fx_idle_verified=False,fx_motion_verified=False,fx_off_verified=False,fx_break_verified=False,production_verified=False,implementation_test_passed=False,w03_far_render_present=True,w03_previous_observed_distance=750,remaining='加载既有I34，核验完整GT成型、金白树影、工况切换及破坏停效；补核W03远距。')
    (p/'client-results.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('已停机安装r234，JAR',sha(target),'原92个第三方JAR未变。')
if __name__=='__main__':main()
