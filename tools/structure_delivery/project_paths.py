"""读取历史清单时迁移已知项目根；不改写原清单或映射外部实例路径。"""
from pathlib import Path, PureWindowsPath


ROOT = Path(__file__).resolve().parents[2]
LEGACY_ROOTS = tuple(PureWindowsPath(value) for value in (
    'C:/Users/OWNER/Desktop/progrem/complate progrem/HK3GTL',
    'C:/Users/OWNER/Desktop/progrem/complate progrem/hk3gtm',
    'C:/Users/OWNER/Desktop/complate progrem/hk3gtl',
    'C:/Users/OWNER/Desktop/hk3gtl',
    'C:/Users/OWNER/Desktop/hk3gtm',
))


def project_path(value):
    """仅把已知旧根替换为本文件所在仓库；相对路径以仓库为基准。"""
    windows = PureWindowsPath(value)
    for old in LEGACY_ROOTS:
        try:
            relative = windows.relative_to(old)
        except ValueError:
            continue
        if '..' in relative.parts:
            raise ValueError('旧项目路径不能越出仓库：' + str(value))
        return ROOT.joinpath(*relative.parts)
    path = Path(value)
    return path if path.is_absolute() else ROOT / path
