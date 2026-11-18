# -*- coding: utf-8 -*-
"""只读核实无gameDir的Prism Java进程，不启动、关闭或写入任何进程。

输入为CIM采集的PID、创建时间和仅在内存解析的启动参数。通过64位
Windows查询句柄读取PEB中的实际cwd，并与完整natives路径、实例元数据
交叉核实。权限不足、架构不符、PID复用或证据矛盾时返回拒绝依据。
此处不接触环境变量块或完整启动参数输出；部署入口仍优先拒绝目标路径。

【变更记录 #1】2026-10-23 13:34:18（部署准备，不增加模组修订号）
- 删除：无。
- 新增：64位进程实际cwd、创建身份、Prism元数据与natives路径交叉核验。
- 修改：不因缺少显式gameDir就把已核实其他实例误判成目标实例。
- 用途：仅对证据完整且指向同一其他实例的Prism进程允许忽略；未知仍拒绝。
"""
from __future__ import annotations

import configparser
import ctypes
from ctypes import wintypes
from datetime import datetime, timezone
import hashlib
import json
import ntpath
import os
from pathlib import Path
import re


class _BasicInformation(ctypes.Structure):
    _fields_ = [('ExitStatus', wintypes.LONG), ('PebBaseAddress', ctypes.c_void_p),
                ('AffinityMask', ctypes.c_size_t), ('BasePriority', wintypes.LONG),
                ('UniqueProcessId', ctypes.c_size_t), ('ParentProcessId', ctypes.c_size_t)]


class _UnicodeString(ctypes.Structure):
    _fields_ = [('Length', wintypes.USHORT), ('MaximumLength', wintypes.USHORT),
                ('Buffer', ctypes.c_void_p)]


class _PebPrefix(ctypes.Structure):
    _fields_ = [('Reserved1', ctypes.c_ubyte * 2), ('BeingDebugged', ctypes.c_ubyte),
                ('Reserved2', ctypes.c_ubyte), ('Reserved3', ctypes.c_void_p * 2),
                ('Ldr', ctypes.c_void_p), ('ProcessParameters', ctypes.c_void_p)]


class _ParametersPrefix(ctypes.Structure):
    _fields_ = [('Reserved1', ctypes.c_ubyte * 16), ('Reserved2', ctypes.c_void_p * 5),
                ('CurrentDirectory', _UnicodeString)]


def native_process_cwd(pid: int) -> dict:
    """只申请查询和读内存权限；已退出、读取失败或非64位进程均抛出异常。"""
    if os.name != 'nt' or ctypes.sizeof(ctypes.c_void_p) != 8:
        raise OSError('当前读取器仅支持64位Windows和64位Python')
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    nt = ctypes.WinDLL('ntdll')
    kernel.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = (wintypes.HANDLE,)
    kernel.CloseHandle.restype = wintypes.BOOL
    kernel.ReadProcessMemory.argtypes = (wintypes.HANDLE, ctypes.c_void_p, ctypes.c_void_p,
                                         ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t))
    kernel.ReadProcessMemory.restype = wintypes.BOOL
    kernel.IsWow64Process.argtypes = (wintypes.HANDLE, ctypes.POINTER(wintypes.BOOL))
    kernel.IsWow64Process.restype = wintypes.BOOL
    kernel.GetProcessTimes.argtypes = (wintypes.HANDLE,) + (ctypes.POINTER(wintypes.FILETIME),) * 4
    kernel.GetProcessTimes.restype = wintypes.BOOL
    kernel.GetExitCodeProcess.argtypes = (wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD))
    kernel.GetExitCodeProcess.restype = wintypes.BOOL
    nt.NtQueryInformationProcess.argtypes = (wintypes.HANDLE, wintypes.ULONG, ctypes.c_void_p,
                                            wintypes.ULONG, ctypes.POINTER(wintypes.ULONG))
    nt.NtQueryInformationProcess.restype = wintypes.LONG
    handle = kernel.OpenProcess(0x0400 | 0x0010, False, pid)
    if not handle:
        raise OSError('无法只读打开进程')
    try:
        wow64 = wintypes.BOOL()
        if not kernel.IsWow64Process(handle, ctypes.byref(wow64)) or wow64.value:
            raise OSError('无法确认进程为原生64位')
        created, exited, kernel_time, user_time = (wintypes.FILETIME() for _ in range(4))
        if not kernel.GetProcessTimes(handle, ctypes.byref(created), ctypes.byref(exited),
                                       ctypes.byref(kernel_time), ctypes.byref(user_time)):
            raise OSError('无法核对进程创建时间')
        basic, returned = _BasicInformation(), wintypes.ULONG()
        if nt.NtQueryInformationProcess(handle, 0, ctypes.byref(basic), ctypes.sizeof(basic),
                                         ctypes.byref(returned)) != 0 or basic.UniqueProcessId != pid:
            raise OSError('进程基础身份读取失败')

        def read(address, count):
            if not address or not 0 < count <= 65536:
                raise OSError('只读地址或长度无效')
            buffer, received = ctypes.create_string_buffer(count), ctypes.c_size_t()
            if not kernel.ReadProcessMemory(handle, address, buffer, count, ctypes.byref(received)) or received.value != count:
                raise OSError('进程只读数据不完整')
            return buffer.raw

        peb = _PebPrefix.from_buffer_copy(read(basic.PebBaseAddress, ctypes.sizeof(_PebPrefix)))
        params = _ParametersPrefix.from_buffer_copy(read(peb.ProcessParameters, ctypes.sizeof(_ParametersPrefix)))
        current = params.CurrentDirectory
        if current.Length % 2 or not 0 < current.Length <= current.MaximumLength <= 65534:
            raise OSError('进程工作目录长度无效')
        cwd = read(current.Buffer, current.Length).decode('utf-16-le', errors='strict')
        repeated = _ParametersPrefix.from_buffer_copy(read(peb.ProcessParameters, ctypes.sizeof(_ParametersPrefix))).CurrentDirectory
        if (current.Buffer, current.Length) != (repeated.Buffer, repeated.Length):
            raise OSError('进程工作目录读取期间发生变化')
        exit_code = wintypes.DWORD()
        if not kernel.GetExitCodeProcess(handle, ctypes.byref(exit_code)) or exit_code.value != 259:
            raise OSError('查询期间进程已退出')
        ticks = (created.dwHighDateTime << 32) | created.dwLowDateTime
        return {'cwd': cwd, 'creation_time_unix': (ticks - 116444736000000000) / 10000000,
                'method': 'Windows只读查询句柄和PEB工作目录；未读取环境变量块'}
    finally:
        kernel.CloseHandle(handle)


def verified_other_prism(process: dict, arguments: list, target_instance: Path,
                         cwd_reader=native_process_cwd) -> dict:
    """只在cwd、natives和真实其他Prism实例一致时解除未知入口阻塞。"""
    evidence = {'verified': False, 'reason': '实际工作目录与实例证据尚未核实'}
    try:
        native = cwd_reader(process['ProcessId'])
        created = process.get('CreationTimeUtc')
        if not isinstance(created, str):
            raise ValueError('CIM缺少创建时间，不能排除PID复用')
        created = re.sub(r'(\.\d{6})\d+(?=Z|[+-])', r'\1', created).replace('Z', '+00:00')
        expected_time = datetime.fromisoformat(created).astimezone(timezone.utc).timestamp()
        if abs(expected_time - native['creation_time_unix']) > 0.002:
            raise ValueError('CIM与只读句柄的创建时间不一致')
        raw_cwd = native['cwd']
        drive, tail = ntpath.splitdrive(raw_cwd)
        if not drive or not tail.startswith(('\\', '/')) or any(c in raw_cwd for c in ('\x00', '\r', '\n')):
            raise ValueError('实际工作目录不是有效绝对路径')
        cwd = Path(raw_cwd).resolve(strict=True)
        target = target_instance.resolve(strict=True)
        evidence.update({'cwd': str(cwd), 'creation_time_utc': created, 'cwd_method': native['method']})
        if cwd == target or cwd == target / 'minecraft' or target in cwd.parents:
            evidence['reason'] = '实际工作目录属于目标实例'
            evidence['target_cwd'] = True
            return evidence
        instance = cwd.parent
        if cwd.name.casefold() != 'minecraft' or instance.parent != target.parent:
            raise ValueError('实际工作目录不在同一Prism实例根下的minecraft目录')
        natives = [value.split('=', 1)[1] for value in arguments if value.casefold().startswith('-djava.library.path=')]
        # natives可在载入后被启动器清理；核对的是进程实际参数中的完整路径。
        # 实际cwd、实例根、instance.cfg和mmc-pack仍必须真实存在。
        expected_natives = (instance / 'natives').resolve(strict=False)
        if len(natives) != 1 or ';' in natives[0] or Path(natives[0]).resolve(strict=False) != expected_natives:
            raise ValueError('启动参数的natives目录与实际工作目录实例不一致')
        game_dirs = []
        for index, value in enumerate(arguments):
            if value.casefold() in ('--gamedir', '--game-dir'):
                if index + 1 >= len(arguments):
                    raise ValueError('gameDir参数缺少值')
                game_dirs.append(arguments[index + 1])
            elif value.casefold().startswith(('--gamedir=', '--game-dir=')):
                game_dirs.append(value.split('=', 1)[1])
        for value in game_dirs:
            if (cwd / value).resolve(strict=True) != cwd:
                raise ValueError('gameDir与实际工作目录冲突')
        cfg_path, pack_path = instance / 'instance.cfg', instance / 'mmc-pack.json'
        cfg = configparser.ConfigParser(interpolation=None)
        cfg.read(cfg_path, encoding='utf-8-sig')
        if cfg.get('General', 'InstanceType', fallback='') != 'OneSix' or not cfg.get('General', 'name', fallback='').strip():
            raise ValueError('其他实例instance.cfg身份无效')
        pack = json.loads(pack_path.read_text(encoding='utf-8-sig'))
        minecraft = [c for c in pack['components'] if c.get('uid') == 'net.minecraft']
        if len(minecraft) != 1 or not minecraft[0].get('version'):
            raise ValueError('其他实例Minecraft组件身份无效')
        evidence.update({'verified': True, 'reason': '实际cwd、创建身份、natives与其他Prism实例元数据一致',
                         'instance': str(instance), 'instance_name': cfg.get('General', 'name'),
                         'minecraft_version': minecraft[0]['version'], 'natives': str(expected_natives),
                         'natives_exists_at_query': expected_natives.exists(),
                         'metadata_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (cfg_path, pack_path)}})
    except (OSError, ValueError, KeyError, TypeError, configparser.Error):
        # 不记录异常对象，避免未预期的参数或环境信息进入部署日志。
        evidence['reason'] = '实际cwd、创建身份、natives或Prism元数据未能一致核实；保持拒绝'
    return evidence
