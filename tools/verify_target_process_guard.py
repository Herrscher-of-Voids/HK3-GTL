# -*- coding: utf-8 -*-
"""只读核对部署守卫的目标路径、未知入口与实际cwd反例，不写游戏实例。

【变更记录 #1】2026-10-23 13:43:12（部署守卫验证，不增加模组修订号）
- 删除：无。
- 新增：目标JAR/实例、未知Java、未知Prism、错误cwd/创建身份及natives反例。
- 修改：自进程cwd和当前实际其他Prism进程均以只读句柄交叉核验。
- 用途：证明修正解除已核实其他实例误拒，同时保留目标与证据不足时的拒绝。

【变更记录 #2】2026-10-23 13:49:50（反例夹具来源纠正）
- 删除：从当前预检中强取已经自然退出的进程身份。
- 新增：读取独立历史观察补记的显式测试桩，不冒充当前实际进程。
- 修改：无游戏进程时仍能运行创建时间、cwd、natives冲突等拒绝检查。
- 用途：修复只读验证入口的空列表失败，不改变部署守卫或游戏文件。
"""
import copy
from datetime import datetime, timezone, timedelta
import hashlib
import json
import os
from pathlib import Path
import subprocess
from unittest.mock import patch

import deploy_industrial_build as deploy
import prism_process_identity as identity


def main():
    checks = []

    def check(name, passed):
        if not passed:
            raise RuntimeError('守卫验证失败：' + name)
        checks.append({'name': name, 'passed': True})

    own = identity.native_process_cwd(os.getpid())
    check('实际读取本进程cwd与os.getcwd一致', Path(own['cwd']).resolve() == Path.cwd().resolve())
    target = str(deploy.INSTANCE / 'minecraft')
    examples = [
        ('目标gameDir必须阻止', f'java.exe org.prismlauncher.EntryPoint --gameDir "{target}"', True),
        ('目标JAR路径必须阻止', f'java.exe -cp "{deploy.TARGET}" org.prismlauncher.EntryPoint', True),
        ('构建主JAR被Java引用必须阻止', f'java.exe -cp "{deploy.SOURCE}" sample.Main', True),
        ('明确其他绝对gameDir沿用原合同', 'java.exe org.prismlauncher.EntryPoint --gameDir C:/guard-fixture-other', False),
        ('无法定位的Prism入口必须阻止', 'java.exe org.prismlauncher.EntryPoint', True),
        ('无法定位的Forge入口必须阻止', 'java.exe cpw.mods.modlauncher.Launcher forgeclient', True),
        ('无命令行Java必须阻止', '', True),
        ('普通不引用目标的Java任务不阻止', 'java.exe example.tool.Main', False),
    ]
    for name, command, expected in examples:
        result = deploy.classify_java_process({'ProcessId': 0, 'CommandLine': command})
        check(name, result['blocks_target_replace'] is expected)
    command = ("[Console]::OutputEncoding=New-Object System.Text.UTF8Encoding($false); "
               "@(Get-CimInstance Win32_Process -Filter \"Name='java.exe' OR Name='javaw.exe'\" -ErrorAction Stop | "
               "Select-Object ProcessId,CommandLine,@{Name='CreationTimeUtc';Expression={$_.CreationDate.ToUniversalTime().ToString('o')}}) "
               "| ConvertTo-Json -Compress")
    raw = subprocess.check_output(['powershell.exe', '-NoProfile', '-Command', command], encoding='utf-8')
    processes = json.loads(raw.lstrip('\ufeff').strip() or '[]')
    if isinstance(processes, dict):
        processes = [processes]
    others = [p for p in processes if deploy.classify_java_process(p)['classification'] == 'verified_other_prism_actual_cwd']
    exercised_other, fixture_basis = None, None
    if others:
        source = others[0]
        args = deploy.windows_arguments(source['CommandLine'])
        native = identity.native_process_cwd(source['ProcessId'])
        exercised_other = deploy.classify_java_process(source)
        check('当前实际其他Prism经完整证据后允许忽略', not exercised_other['blocks_target_replace'])
        fixture_basis = '当前实际其他Prism进程的只读证据；反例使用显式测试桩'
    else:
        # 没有游戏运行时仍执行反例；复用此前已验证路径，仅作为合成测试数据。
        observation = json.loads((deploy.ROOT / 'logs/controller-centering-install-20261023/prism-cwd-observation.json').read_text(encoding='utf-8'))
        evidence = observation['identity_evidence']
        args = ['java.exe', '-Djava.library.path=' + evidence['natives'], 'org.prismlauncher.EntryPoint']
        source = {'ProcessId': 0, 'CreationTimeUtc': evidence['creation_time_utc'], 'CommandLine': 'java.exe org.prismlauncher.EntryPoint'}
        native = {'cwd': evidence['cwd'], 'creation_time_unix': datetime.fromisoformat(evidence['creation_time_utc']).timestamp(),
                  'method': '显式测试桩；不表示对应进程当前仍运行'}
        fixture_basis = '此前实际只读观察补记中的其他实例路径加显式创建/cwd测试桩；不冒充当前活进程'
    fixture_reader = lambda _: native
    check('一致cwd/创建身份/natives/真实元数据的测试桩可识别', identity.verified_other_prism(source, args, deploy.INSTANCE, cwd_reader=fixture_reader)['verified'])
    invalid = copy.deepcopy(source)
    invalid['CreationTimeUtc'] = '2000-01-01T00:00:00Z'
    check('创建时间不一致拒绝，避免PID复用', not identity.verified_other_prism(invalid, args, deploy.INSTANCE, cwd_reader=fixture_reader)['verified'])
    missing = copy.deepcopy(source)
    missing.pop('CreationTimeUtc')
    check('缺少创建身份拒绝', not identity.verified_other_prism(missing, args, deploy.INSTANCE, cwd_reader=fixture_reader)['verified'])
    wrong_args = [a for a in args if not a.casefold().startswith('-djava.library.path=')]
    wrong_args.append('-Djava.library.path=C:/guard-fixture-other/natives')
    check('natives与实际cwd冲突拒绝', not identity.verified_other_prism(source, wrong_args, deploy.INSTANCE, cwd_reader=fixture_reader)['verified'])
    wrong_cwd = dict(native, cwd=str(deploy.INSTANCE / 'minecraft'))
    target_proof = identity.verified_other_prism(source, args, deploy.INSTANCE, cwd_reader=lambda _: wrong_cwd)
    check('实际cwd属于目标时标识为目标', target_proof.get('target_cwd') is True and not target_proof['verified'])
    with patch.object(deploy, 'verified_other_prism', return_value=target_proof):
        check('即使其他natives参数，目标实际cwd仍阻止', deploy.classify_java_process(source)['blocks_target_replace'])

    def denied(_):
        raise OSError('模拟读取拒绝')

    check('无权限读取cwd保持拒绝', not identity.verified_other_prism(source, args, deploy.INSTANCE, cwd_reader=denied)['verified'])
    foreign = dict(native, cwd=str(Path.cwd()))
    check('cwd不在真实Prism实例目录拒绝', not identity.verified_other_prism(source, args, deploy.INSTANCE, cwd_reader=lambda _: foreign)['verified'])
    guard = deploy.target_process_guard()
    now = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')
    result = {'recorded_at': now, 'status': 'passed', 'checks': checks,
              'actual_other_instance_exercised': exercised_other, 'fixture_basis': fixture_basis, 'final_real_process_guard': guard,
              'raw_command_lines_recorded': False, 'game_started_or_stopped': False, 'instance_written': False,
              'tool_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in
                              [Path(__file__), Path(deploy.__file__), Path(identity.__file__)]},
              '_change_records': [{'number': 1, 'time': now, 'delete': '无', 'add': '守卫正反例检查',
                                   'modify': '仅项目日志记录', 'purpose': '验证未知或目标进程仍阻止替换'}]}
    output = deploy.ROOT / 'logs/controller-centering-install-20261023/guard-verification.json'
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': result['status'], 'checks': len(checks), 'actual_other_exercised': bool(others),
                      'target_replace_allowed': guard['target_replace_allowed']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
