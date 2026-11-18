"""同步终端、接口及预览的离线交付；保留旧实机证据与全部系统分母。"""
from pathlib import Path
from datetime import datetime,timezone
import json,sys,shutil

ROOT=Path(__file__).resolve().parents[1]
LOG=ROOT/'logs/terminal-preview-r242-20261110'

def load(path):return json.loads(path.read_text('utf8'))
def save(path,data):path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf8')

def main():
    build=load(LOG/'build-r242-final/clean-build.json');assert build['status']=='passed' and build['source_inputs_unchanged']
    deployed=load(LOG/'deployment-r242.json') if (LOG/'deployment-r242.json').exists() else None
    processes=load(ROOT/'src/main/resources/data/hk3gtl/research/industrial_processes.json')['recipes']
    wonders=[p for p in processes if p.get('role','').startswith('W')];assert not wonders
    report=dict(revision=242,updated_at_utc=datetime.now(timezone.utc).isoformat(),
        status=('r242构建及离线回归通过，已部署增强版3.5；' if deployed else 'r242构建及离线回归通过，待停机部署；')
            +'并行批次、十次百分比进度、W02相邻接口与自家JEI预览已接代码，实机速度、界面及接口迁移未验收；W01与W03本轮完整验收仍未完成',
        build=build,deployment=deployed,game_verified=False,
        terminal=dict(parallel='1至3个后台线程、有界批次、世界与库存只在服务器线程提交',
            batch_size=2048,batches='工作线程数加一，另有当前提交批次',chunk_tickets_max=4,
            progress_messages=list(range(10,101,10)),measured_game_speedup=None,
            guards='原保护事件、材料预扣与回退、取消及区块票清理保留'),
        w02=load(LOG/'w02-export.json'),
        w02_migration=dict(explicit_button='校正八接口',creative_only=True,
            preserves_real_hatches=True,preserves_modified_blocks=True,game_verified=False),
        previews=dict(formal_sparse_sources=56,other_hk3_machines='小型正式形状转入同一自家场景',
            jei_entry_restored=['W02','W03','H01'],runtime_coordinates_per_axis=4096,
            lazy_decode=True,hidden_cache_release_seconds=2,game_verified=False),
        recipes=dict(industrial_plan_count=len(processes),wonder_plan_count=len(wonders),
            wonder_machine_production_enabled=False,scope='W01至W03仅创造巡检或场调试；W04候选预览；其余奇观正式生产链尚未接通'),
        mechanic_proposals=dict(approved=False,implemented=False,
            W02='解析完整度：以已研究蓝图及真实供料控制可重构品类和并行，不无限复制',
            W03='锚定稳定度：持续供能和空间校准控制可用范围，不依据客户端动画或帧率',
            W04='电磁相干度：线圈与冷却工况控制持续磁场及安全并行'),
        remaining=['真实客户端建造吞吐与卡顿对比','JEI实际打开、旋转缩放和逐层浏览',
            '旧W02测试船坞按钮迁移及保护回退实测','W01、W03完整实装测试收尾'])
    save(LOG/'results.json',report)
    current=ROOT/'logs/w01-w03-implementation-20261110/client-results.json'
    before=LOG/'before-client-results.json'
    if not before.exists():shutil.copy2(current,before)
    data=load(current);data['status']=report['status'];data['terminal_preview_r242']=report
    data['current_revision_game_verified']=False
    data['w02_current_geometry_note']='r242改为6072490实体及贴身八接口；r240/r241的6072498格实机通过只证明历史布局，不转记新接口已验收'
    save(current,data)
    sys.path.insert(0,str(ROOT/'tools/structure_delivery'))
    import publish_wonder_progress_20261110 as audit
    audit.main()
    print(json.dumps(dict(revision=242,installed=bool(deployed),game_verified=False)))

if __name__=='__main__':main()
