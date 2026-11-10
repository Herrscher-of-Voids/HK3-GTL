"""专用世界的原版验收函数，只调用真实主控、建造器和检查按钮。"""
import json
from pathlib import Path
import deploy_industrial_build as base

base.target_process_guard()
world=base.INSTANCE/'minecraft/saves/HK3GTL_W01_W02_W03_r239_Test'
pack=world/'datapacks/hk3_wonder_test'
folder=pack/'data/hk3test/functions';folder.mkdir(parents=True,exist_ok=True)
(pack/'pack.mcmeta').write_text(json.dumps({'pack':{'pack_format':15,'description':'W01–W03创造验收，正式生产另定'}},ensure_ascii=False),'utf8')
functions={
    'w01_setup':['tp @s 12284 209 0.5 -90 20','setblock 12288 209 0 hk3gtl:w01_origin_stellar_concert_court[facing=west]','hk3wonder 12288 209 0 build'],
    'w02_setup':['tp @s 16384.5 203 4 180 20','setblock 16384 203 0 hk3gtl:omnia_autonomous_industrial_matrix[facing=south]','hk3wonder 16384 203 0 build'],
    'w03_check':['tp @s 8192.5 167 -4 0 20','hk3wonder 8192 167 0 check'],
    'w01_status':['hk3wonder 12288 209 0 status'],
    'w02_status':['hk3wonder 16384 203 0 status'],
    'w03_status':['hk3wonder 8192 167 0 status'],
    'w01_toggle':['hk3wonder 12288 209 0 toggle','hk3wonder 12288 209 0 status'],
    'w02_toggle':['hk3wonder 16384 203 0 toggle','hk3wonder 16384 203 0 status'],
    'w03_toggle':['hk3wonder 8192 167 0 toggle','hk3wonder 8192 167 0 status'],
    'w01_front':['tp @s 11900 440 0 -90 12'],
    'w02_front':['tp @s 16384 435 550 180 8'],
    'w03_front':['tp @s 8192 495 -750 0 8'],
    'w01_control':['tp @s 12284 209 0.5 -90 20'],
    'w02_control':['tp @s 16384.5 203 4 180 20'],
    'w03_control':['tp @s 8192.5 167 -4 0 20']
}
for name,commands in functions.items():(folder/(name+'.mcfunction')).write_text('\n'.join(commands)+'\n','utf8')
print('专用测试函数已保存；仅放置真实控制器，不注入结构或成型结果。')
