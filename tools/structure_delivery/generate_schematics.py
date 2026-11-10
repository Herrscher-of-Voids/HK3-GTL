# -*- coding: utf-8 -*-
"""生成内测5十六级多方块建筑的 Sponge Schematic v2。

本脚本只负责建筑结构文件与交付清单，不修改 Java、KubeJS、配方、控制器或玩家存档。
所有材料均来自指定 Prism 实例中已经核对过的 GTCEu/GTLCore 方块资源；结构中的
钻石方块和普通钻石矿分别表示核心与接口占位，不能被当作可运行的机器方块。
"""

# 变更记录 #1 2026-09-25 04:49:51（内测5修订72）
# 删除：六种动态建材省略状态的歧义。新增：active=false 静态建筑状态。
# 修改：仅明确材料状态，不改变几何；用途：让结构文件与材质预览选择相同模型。
from __future__ import annotations

import argparse
import collections
import gzip
import hashlib
import html
import json
import shutil
from pathlib import Path
from typing import Callable, Iterable

import nbtlib as nbt


PROJECT = Path(__file__).resolve().parents[2]
INSTANCE = Path(r"C:\Users\OWNER\AppData\Roaming\PrismLauncher\instances\GregTech-Leisure-1.4.5.2\minecraft")
SCHEMATIC_DIR = INSTANCE / "config" / "worldedit" / "schematics"


AIR = "minecraft:air"
CORE = "minecraft:diamond_block"
INTERFACE = "minecraft:diamond_ore"
FORBIDDEN_PREFIXES = ("hk3gtl:",)


def find_industrial_structure_dir() -> Path:
    """按 ASCII 前缀定位内测5文档目录，避免命令行编码影响中文路径。"""

    candidates = [
        path
        for path in (PROJECT / "doc").iterdir()
        if path.is_dir() and path.name.startswith("HK3GTL-") and len(path.name) < 12
    ]
    if not candidates:
        raise FileNotFoundError("找不到内测5文档目录")
    return next(path for path in candidates if any(child.name.startswith("03_") for child in path.iterdir()))


DELIVERY_ROOT = find_industrial_structure_dir() / "03_机器结构" / "结构文件交付_v1"
ARCHIVE_SCHEMATIC_DIR = DELIVERY_ROOT / "schematics"


def material(shell: str, frame: str, coil: str, glass: str, accent: str) -> dict[str, str]:
    """建立单座建筑的材料角色表。角色只影响造型，不代表机器成型条件。"""

    return {"shell": shell, "frame": frame, "coil": coil, "glass": glass, "accent": accent}


SPECS: list[dict] = [
    {
        "key": "abyss_1", "stage": "海渊 I", "tier": 15, "voltage": "MAX+1",
        "size": (33, 25, 33), "design": "双腔采集舱",
        "concept": "两座独立采集腔由低位能量脊相连，外露检修路径表达第一次跨入扩展电压。",
        "palette": material("gtlcore:component_assembly_line_casing_max", "gtceu:max_machine_casing", "gtlcore:qft_coil[active=false]", "gtceu:tempered_glass", "gtlcore:power_core[active=false]"),
        "builder": "abyss_1",
    },
    {
        "key": "abyss_2", "stage": "海渊 II", "tier": 16, "voltage": "MAX+2",
        "size": (41, 29, 41), "design": "四臂稳流厅",
        "concept": "中央稳流腔向四个维护节点伸出对称臂，顶部线圈环负责视觉上的能量汇聚。",
        "palette": material("gtlcore:component_assembly_line_casing_max", "gtlcore:advanced_stellar_containment_casing", "gtceu:superconducting_coil[active=false]", "gtceu:fusion_glass", "gtlcore:power_core[active=false]"),
        "builder": "abyss_2",
    },
    {
        "key": "abyss_3", "stage": "海渊 III", "tier": 17, "voltage": "MAX+3",
        "size": (49, 33, 49), "design": "三腔分离庭",
        "concept": "三个高度不同的分离腔沿纵轴错落布置，桥梁和侧向支柱形成可读的工艺顺序。",
        "palette": material("gtlcore:advanced_stellar_containment_casing", "gtlcore:component_assembly_line_casing_max", "gtlcore:qft_coil[active=false]", "gtceu:fusion_glass", "gtlcore:power_core[active=false]"),
        "builder": "abyss_3",
    },
    {
        "key": "abyss_4", "stage": "海渊 IV", "tier": 18, "voltage": "MAX+4",
        "size": (57, 37, 57), "design": "嵌套稳定环",
        "concept": "三层方形稳定环围绕中央核心，角部塔柱承担承重与隔离的视觉职责。",
        "palette": material("gtlcore:advanced_stellar_containment_casing", "gtlcore:graviton_field_constraint_casing", "gtceu:superconducting_coil[active=false]", "gtceu:fusion_glass", "gtlcore:power_core[active=false]"),
        "builder": "abyss_4",
    },
    {
        "key": "imaginary_1", "stage": "虚数 I", "tier": 19, "voltage": "MAX+5",
        "size": (65, 41, 65), "design": "观测十字庭",
        "concept": "中央观测舱向八个方向分发测量节点，宽阔的留白区表现稳定的观测距离。",
        "palette": material("gtlcore:component_assembly_line_casing_uev", "gtlcore:advanced_stellar_containment_casing", "gtlcore:qft_coil[active=false]", "gtceu:fusion_glass", "gtlcore:power_core[active=false]"),
        "builder": "imaginary_1",
    },
    {
        "key": "imaginary_2", "stage": "虚数 II", "tier": 20, "voltage": "MAX+6",
        "size": (73, 45, 73), "design": "双环锚定台",
        "concept": "两座错位环形平台通过中央锚定柱相连，入口、输出和供能面被分置在四侧。",
        "palette": material("gtlcore:component_assembly_line_casing_uiv", "gtlcore:graviton_field_constraint_casing", "gtlcore:qft_coil[active=false]", "gtlcore:infinity_glass", "gtlcore:power_core[active=false]"),
        "builder": "imaginary_2",
    },
    {
        "key": "imaginary_3", "stage": "虚数 III", "tier": 21, "voltage": "MAX+7",
        "size": (81, 49, 81), "design": "分布式解析网",
        "concept": "中央解析节点通过交叉梁连接六个远端模块，表现空间信息被分布式处理。",
        "palette": material("gtlcore:component_assembly_line_casing_uiv", "gtlcore:dimensionally_transcendent_casing", "gtlcore:advanced_fusion_coil[active=false]", "gtlcore:infinity_glass", "gtlcore:power_core[active=false]"),
        "builder": "imaginary_3",
    },
    {
        "key": "imaginary_4", "stage": "虚数 IV", "tier": 22, "voltage": "MAX+8",
        "size": (89, 53, 89), "design": "维度桥接环",
        "concept": "上下两层观测环由四座桥接塔贯通，中央轴线成为可辨认的维护通道。",
        "palette": material("gtlcore:component_assembly_line_casing_uxv", "gtlcore:dimensionally_transcendent_casing", "gtlcore:advanced_fusion_coil[active=false]", "gtlcore:infinity_glass", "gtlcore:power_module_5[active=false]"),
        "builder": "imaginary_4",
    },
    {
        "key": "quantum_1", "stage": "量子 I", "tier": 23, "voltage": "MAX+9",
        "size": (97, 57, 97), "design": "嵌套量子环",
        "concept": "四层不同高度的量子环围绕悬空核心，环间留白表达量子态隔离。",
        "palette": material("gtlcore:component_assembly_line_casing_uxv", "gtlcore:ultimate_stellar_containment_casing", "gtlcore:advanced_fusion_coil[active=false]", "gtlcore:infinity_glass", "gtlcore:power_module_5[active=false]"),
        "builder": "quantum_1",
    },
    {
        "key": "quantum_2", "stage": "量子 II", "tier": 24, "voltage": "MAX+10",
        "size": (113, 65, 113), "design": "四节点量子格",
        "concept": "四个大型节点以方格关系运行，中央交叉核心负责交换和再分配。",
        "palette": material("gtlcore:component_assembly_line_casing_opv", "gtlcore:ultimate_stellar_containment_casing", "gtlcore:advanced_compressed_fusion_coil[active=false]", "gtlcore:infinity_glass", "gtlcore:power_module_5[active=false]"),
        "builder": "quantum_2",
    },
    {
        "key": "quantum_3", "stage": "量子 III", "tier": 25, "voltage": "MAX+11",
        "size": (129, 73, 129), "design": "偏移轨道阵",
        "concept": "不同高度的偏移轨道围绕主轴展开，非对称连接展示对世界泡的主动取样。",
        "palette": material("gtlcore:component_assembly_line_casing_opv", "gtlcore:dimensionally_transcendent_casing", "gtlcore:advanced_compressed_fusion_coil[active=false]", "gtlcore:infinity_glass", "gtlcore:power_module_5[active=false]"),
        "builder": "quantum_3",
    },
    {
        "key": "quantum_4", "stage": "量子 IV", "tier": 26, "voltage": "MAX+12",
        "size": (145, 81, 145), "design": "多环跃迁井",
        "concept": "多层跃迁环和八条径向梁围出中央深井，结构重点从外露机械转向空间组织。",
        "palette": material("gtlcore:component_assembly_line_casing_opv", "gtlcore:graviton_field_constraint_casing", "gtlcore:advanced_compressed_fusion_coil[active=false]", "gtlcore:infinity_glass", "gtlcore:power_module_5[active=false]"),
        "builder": "quantum_4",
    },
    {
        "key": "finality_1", "stage": "终焉 I", "tier": 27, "voltage": "MAX+13",
        "size": (161, 89, 161), "design": "文明轴塔",
        "concept": "中央高塔和四座低矮支塔组成文明轴线，外围环带为安全距离而保留。",
        "palette": material("gtlcore:component_assembly_line_casing_opv", "gtlcore:dimensionally_transcendent_casing", "gtlcore:advanced_compressed_fusion_coil[active=false]", "gtlcore:infinity_glass", "gtlcore:power_core[active=false]"),
        "builder": "finality_1",
    },
    {
        "key": "finality_2", "stage": "终焉 II", "tier": 28, "voltage": "MAX+14",
        "size": (193, 97, 193), "design": "双重圣环",
        "concept": "两道巨大圣环在不同高度运行，中央主轴连接上下核心而不填满环内空间。",
        "palette": material("gtlcore:component_assembly_line_casing_opv", "gtlcore:ultimate_stellar_containment_casing", "gtlcore:advanced_compressed_fusion_coil[active=false]", "gtlcore:infinity_glass", "gtlcore:power_module_5[active=false]"),
        "builder": "finality_2",
    },
    {
        "key": "finality_3", "stage": "终焉 III", "tier": 29, "voltage": "MAX+15",
        "size": (225, 105, 225), "design": "世界泡轮回庭",
        "concept": "三层轮回庭院由八条放射梁连接，中心核心、环带和外缘接口形成清晰的层级。",
        "palette": material("gtlcore:dimensionally_transcendent_casing", "gtlcore:ultimate_stellar_containment_casing", "gtlcore:advanced_compressed_fusion_coil[active=false]", "gtlcore:infinity_glass", "gtlcore:power_module_5[active=false]"),
        "builder": "finality_3",
    },
    {
        "key": "finality_4", "stage": "终焉 IV", "tier": 30, "voltage": "MAX+16",
        "size": (257, 113, 257), "design": "树海朝觐轴",
        "concept": "中央树海轴、分层枝桠和四重外环共同构成终审前的文明奇观级设施。",
        "palette": material("gtlcore:dimensionally_transcendent_casing", "gtlcore:graviton_field_constraint_casing", "gtlcore:advanced_compressed_fusion_coil[active=false]", "gtlcore:infinity_glass", "gtlcore:power_module_5[active=false]"),
        "builder": "finality_4",
    },
]


class StructureBuilder:
    """用稀疏几何写入完整体素数组，所有实体方块均占满一个方格。"""

    def __init__(self, width: int, height: int, length: int, palette: Iterable[str]):
        self.width, self.height, self.length = width, height, length
        self.palette = list(dict.fromkeys([AIR, *palette, CORE, INTERFACE]))
        self.index = {name: number for number, name in enumerate(self.palette)}
        if max(self.index.values()) >= 128:
            raise ValueError("调色板过大，当前生成器要求每个索引使用单字节变长编码")
        self.blocks = bytearray(width * height * length)

    def flat_index(self, x: int, y: int, z: int) -> int:
        if not (0 <= x < self.width and 0 <= y < self.height and 0 <= z < self.length):
            raise ValueError(f"结构坐标越界: ({x}, {y}, {z}) / {self.width}×{self.height}×{self.length}")
        return (y * self.length + z) * self.width + x

    def put(self, x: int, y: int, z: int, block: str) -> None:
        self.blocks[self.flat_index(x, y, z)] = self.index[block]

    def clear(self, x: int, y: int, z: int) -> None:
        self.put(x, y, z, AIR)

    def box(self, x1: int, y1: int, z1: int, x2: int, y2: int, z2: int, block: str) -> None:
        for y in range(min(y1, y2), max(y1, y2) + 1):
            for z in range(min(z1, z2), max(z1, z2) + 1):
                for x in range(min(x1, x2), max(x1, x2) + 1):
                    self.put(x, y, z, block)

    def hollow_box(self, x1: int, y1: int, z1: int, x2: int, y2: int, z2: int, block: str) -> None:
        for y in range(min(y1, y2), max(y1, y2) + 1):
            for z in range(min(z1, z2), max(z1, z2) + 1):
                for x in range(min(x1, x2), max(x1, x2) + 1):
                    if x in (x1, x2) or y in (y1, y2) or z in (z1, z2):
                        self.put(x, y, z, block)

    def square_ring(self, cx: int, cz: int, radius: int, y: int, block: str, thickness: int = 1) -> None:
        for layer in range(thickness):
            r = radius - layer
            if r < 1:
                continue
            for x in range(cx - r, cx + r + 1):
                self.put(x, y, cz - r, block)
                self.put(x, y, cz + r, block)
            for z in range(cz - r + 1, cz + r):
                self.put(cx - r, y, z, block)
                self.put(cx + r, y, z, block)

    def pillar(self, x: int, z: int, y1: int, y2: int, block: str, width: int = 1) -> None:
        half = (width - 1) // 2
        self.box(x - half, y1, z - half, x + half, y2, z + half, block)

    def beam_x(self, x1: int, x2: int, y: int, z: int, block: str, width: int = 1) -> None:
        half = (width - 1) // 2
        self.box(min(x1, x2), y - half, z - half, max(x1, x2), y + half, z + half, block)

    def beam_z(self, x: int, y: int, z1: int, z2: int, block: str, width: int = 1) -> None:
        half = (width - 1) // 2
        self.box(x - half, y - half, min(z1, z2), x + half, y + half, max(z1, z2), block)

    def node(self, cx: int, cz: int, radius: int, y1: int, y2: int, roles: dict[str, str]) -> None:
        """生成一个带空腔、环带、立柱和观察窗的完整方块节点。"""

        self.square_ring(cx, cz, radius, y1, roles["shell"], 2)
        self.square_ring(cx, cz, radius, y2, roles["frame"], 2)
        mid = (y1 + y2) // 2
        self.square_ring(cx, cz, radius - 1, mid, roles["coil"], 1)
        self.square_ring(cx, cz, radius - 2, mid + 1, roles["glass"], 1)
        for dx, dz in ((-radius, -radius), (-radius, radius), (radius, -radius), (radius, radius)):
            self.pillar(cx + dx, cz + dz, y1, y2, roles["frame"], 2)
        self.pillar(cx, cz, y1 + 1, y2 - 1, roles["accent"], 1)

    def base(self, roles: dict[str, str]) -> None:
        """生成承重底座和四向维护脊，中心区域保持可进入的留白。"""

        self.box(1, 0, 1, self.width - 2, 0, self.length - 2, roles["frame"])
        self.square_ring(self.width // 2, self.length // 2, min(self.width, self.length) // 2 - 2, 1, roles["shell"], 2)
        cx, cz = self.width // 2, self.length // 2
        self.beam_x(2, self.width - 3, 2, cz, roles["frame"], 2)
        self.beam_z(cx, 2, 2, self.length - 3, roles["frame"], 2)
        for x, z in ((2, 2), (2, self.length - 3), (self.width - 3, 2), (self.width - 3, self.length - 3)):
            self.pillar(x, z, 1, min(7, self.height - 2), roles["accent"], 2)

    def interface(self, x: int, y: int, z: int, role: str, inward: tuple[int, int, int], records: list[dict]) -> None:
        """放置普通钻石矿接口占位，并清出至少两格内侧检修空间。"""

        self.put(x, y, z, INTERFACE)
        ix, iy, iz = inward
        for step in range(1, 3):
            px, py, pz = x + ix * step, y + iy * step, z + iz * step
            if 0 <= px < self.width and 0 <= py < self.height and 0 <= pz < self.length:
                self.clear(px, py, pz)
        records.append({"pos": [x, y, z], "role": role})

    def finalize_markers(self) -> tuple[list[dict], list[dict]]:
        """统一放置核心和六个接口，返回核心与接口坐标说明。"""

        cx, cz = self.width // 2, self.length // 2
        core_y = max(4, self.height // 2)
        for x in range(cx - 1, cx + 2):
            for z in range(cz - 1, cz + 2):
                self.clear(x, core_y, z)
        self.put(cx, core_y, cz, CORE)
        records: list[dict] = []
        y = min(3, self.height - 3)
        self.interface(cx - 3, y, 0, "物品输入", (0, 0, 1), records)
        self.interface(cx + 3, y, 0, "流体输入", (0, 0, 1), records)
        self.interface(cx - 3, y, self.length - 1, "物品输出", (0, 0, -1), records)
        self.interface(cx + 3, y, self.length - 1, "流体输出", (0, 0, -1), records)
        self.interface(0, y, cz, "能源接口·左", (1, 0, 0), records)
        self.interface(self.width - 1, y, cz, "能源接口·右", (-1, 0, 0), records)
        return [{"pos": [cx, core_y, cz], "role": "主机核心"}], records

    def counts(self) -> collections.Counter[str]:
        return collections.Counter(self.palette[index] for index in self.blocks if index != 0)


def design_abyss_1(builder: StructureBuilder, roles: dict[str, str]) -> None:
    builder.base(roles)
    cx, cz = builder.width // 2, builder.length // 2
    for x in (cx - 9, cx + 9):
        builder.node(x, cz, 5, 3, builder.height - 5, roles)
    builder.beam_x(cx - 8, cx + 8, builder.height // 2, cz, roles["coil"], 2)
    builder.square_ring(cx, cz, 11, builder.height - 4, roles["glass"], 2)


def design_abyss_2(builder: StructureBuilder, roles: dict[str, str]) -> None:
    builder.base(roles)
    cx, cz = builder.width // 2, builder.length // 2
    builder.node(cx, cz, 8, 4, builder.height - 5, roles)
    offset = 13
    for x, z in ((cx - offset, cz), (cx + offset, cz), (cx, cz - offset), (cx, cz + offset)):
        builder.node(x, z, 4, 5, builder.height - 7, roles)
    builder.beam_x(cx - offset + 4, cx + offset - 4, 3, cz, roles["frame"], 2)
    builder.beam_z(cx, 3, cz - offset + 4, cz + offset - 4, roles["frame"], 2)
    builder.square_ring(cx, cz, 15, builder.height - 3, roles["coil"], 1)


def design_abyss_3(builder: StructureBuilder, roles: dict[str, str]) -> None:
    builder.base(roles)
    cx, cz = builder.width // 2, builder.length // 2
    for index, (x, z) in enumerate(((cx - 14, cz - 8), (cx, cz + 10), (cx + 14, cz - 8))):
        builder.node(x, z, 6, 3 + index * 2, builder.height - 6 - index, roles)
    builder.beam_x(cx - 12, cx + 12, builder.height // 2, cz - 2, roles["coil"], 2)
    builder.beam_z(cx, builder.height // 2 + 2, cz - 7, cz + 8, roles["frame"], 2)
    for x in (4, builder.width - 5):
        builder.pillar(x, cz, 2, builder.height - 4, roles["accent"], 2)


def design_abyss_4(builder: StructureBuilder, roles: dict[str, str]) -> None:
    builder.base(roles)
    cx, cz = builder.width // 2, builder.length // 2
    for radius, y, block in ((10, 4, roles["shell"]), (16, 10, roles["coil"]), (23, builder.height - 5, roles["frame"])):
        builder.square_ring(cx, cz, radius, y, block, 2)
    for x, z in ((cx - 18, cz - 18), (cx - 18, cz + 18), (cx + 18, cz - 18), (cx + 18, cz + 18)):
        builder.pillar(x, z, 2, builder.height - 4, roles["accent"], 2)
    builder.node(cx, cz, 6, 5, builder.height - 7, roles)


def design_imaginary_1(builder: StructureBuilder, roles: dict[str, str]) -> None:
    builder.base(roles)
    cx, cz = builder.width // 2, builder.length // 2
    builder.node(cx, cz, 9, 5, builder.height - 6, roles)
    distance = 22
    for x, z in ((cx - distance, cz), (cx + distance, cz), (cx, cz - distance), (cx, cz + distance),
                 (cx - distance, cz - distance), (cx - distance, cz + distance),
                 (cx + distance, cz - distance), (cx + distance, cz + distance)):
        builder.node(x, z, 4, 7, builder.height - 9, roles)
        builder.beam_x(cx, x, builder.height // 2, z, roles["coil"], 1)
        builder.beam_z(x, builder.height // 2, cz, z, roles["coil"], 1)
    builder.square_ring(cx, cz, 29, builder.height - 3, roles["glass"], 2)


def design_imaginary_2(builder: StructureBuilder, roles: dict[str, str]) -> None:
    builder.base(roles)
    cx, cz = builder.width // 2, builder.length // 2
    for x, z, y in ((cx - 15, cz, 7), (cx + 15, cz, 11)):
        builder.node(x, z, 10, y, builder.height - y - 5, roles)
    for radius, y in ((20, 5), (29, builder.height - 5)):
        builder.square_ring(cx, cz, radius, y, roles["frame"], 2)
    builder.beam_x(cx - 25, cx + 25, builder.height // 2, cz, roles["coil"], 2)
    builder.beam_z(cx, builder.height // 2, cz - 25, cz + 25, roles["coil"], 2)


def design_imaginary_3(builder: StructureBuilder, roles: dict[str, str]) -> None:
    builder.base(roles)
    cx, cz = builder.width // 2, builder.length // 2
    builder.node(cx, cz, 8, 6, builder.height - 6, roles)
    points = ((cx - 25, cz - 14), (cx + 25, cz - 14), (cx - 25, cz + 14),
              (cx + 25, cz + 14), (cx - 8, cz - 27), (cx + 8, cz + 27))
    for index, (x, z) in enumerate(points):
        builder.node(x, z, 5, 5 + index % 3 * 3, builder.height - 9, roles)
        builder.beam_x(min(cx, x), max(cx, x), 12 + index % 2 * 4, z, roles["frame"], 1)
        builder.beam_z(x, 12 + index % 2 * 4, min(cz, z), max(cz, z), roles["coil"], 1)
    builder.square_ring(cx, cz, 34, builder.height - 4, roles["glass"], 1)


def design_imaginary_4(builder: StructureBuilder, roles: dict[str, str]) -> None:
    builder.base(roles)
    cx, cz = builder.width // 2, builder.length // 2
    for y, radius, block in ((5, 17, roles["shell"]), (builder.height // 2, 28, roles["coil"]),
                             (builder.height - 5, 36, roles["frame"])):
        builder.square_ring(cx, cz, radius, y, block, 2)
    for x, z in ((cx - 30, cz - 30), (cx - 30, cz + 30), (cx + 30, cz - 30), (cx + 30, cz + 30)):
        builder.node(x, z, 6, 8, builder.height - 10, roles)
        builder.beam_x(cx, x, builder.height // 2, z, roles["frame"], 2)
        builder.beam_z(x, builder.height // 2, cz, z, roles["coil"], 2)


def design_quantum_1(builder: StructureBuilder, roles: dict[str, str]) -> None:
    builder.base(roles)
    cx, cz = builder.width // 2, builder.length // 2
    for y, radius in ((6, 17), (builder.height // 3, 27), (builder.height * 2 // 3, 37), (builder.height - 6, 45)):
        builder.square_ring(cx, cz, radius, y, roles["coil" if y != 6 else "shell"], 2)
    builder.node(cx, cz, 8, 12, builder.height - 12, roles)
    for x, z in ((cx - 34, cz), (cx + 34, cz), (cx, cz - 34), (cx, cz + 34)):
        builder.pillar(x, z, 3, builder.height - 7, roles["frame"], 2)


def design_quantum_2(builder: StructureBuilder, roles: dict[str, str]) -> None:
    builder.base(roles)
    cx, cz = builder.width // 2, builder.length // 2
    offset = 30
    for x, z in ((cx - offset, cz - offset), (cx + offset, cz - offset),
                 (cx - offset, cz + offset), (cx + offset, cz + offset)):
        builder.node(x, z, 10, 8, builder.height - 10, roles)
    for x in (cx - offset, cx + offset):
        builder.beam_z(x, builder.height // 2, cz - offset + 9, cz + offset - 9, roles["coil"], 2)
    for z in (cz - offset, cz + offset):
        builder.beam_x(cx - offset + 9, cx + offset - 9, builder.height // 2, z, roles["coil"], 2)
    builder.node(cx, cz, 9, 5, builder.height - 6, roles)
    builder.square_ring(cx, cz, 50, builder.height - 4, roles["frame"], 2)


def design_quantum_3(builder: StructureBuilder, roles: dict[str, str]) -> None:
    builder.base(roles)
    cx, cz = builder.width // 2, builder.length // 2
    centers = ((cx - 30, cz - 18), (cx + 24, cz - 25), (cx + 31, cz + 20),
               (cx - 18, cz + 31), (cx - 35, cz + 5))
    for index, (x, z) in enumerate(centers):
        builder.node(x, z, 9, 7 + index * 2, builder.height - 10 - index, roles)
        builder.beam_x(min(cx, x), max(cx, x), 15 + index * 2, z, roles["frame"], 2)
        builder.beam_z(x, 15 + index * 2, min(cz, z), max(cz, z), roles["coil"], 1)
    for radius, y in ((22, 5), (39, builder.height // 2), (58, builder.height - 5)):
        builder.square_ring(cx, cz, radius, y, roles["glass" if y != builder.height // 2 else "coil"], 2)


def design_quantum_4(builder: StructureBuilder, roles: dict[str, str]) -> None:
    builder.base(roles)
    cx, cz = builder.width // 2, builder.length // 2
    builder.node(cx, cz, 11, 8, builder.height - 8, roles)
    for index, (x, z) in enumerate(((cx - 45, cz), (cx + 45, cz), (cx, cz - 45), (cx, cz + 45),
                                     (cx - 32, cz - 32), (cx - 32, cz + 32),
                                     (cx + 32, cz - 32), (cx + 32, cz + 32))):
        builder.node(x, z, 7, 6 + index % 3 * 4, builder.height - 9, roles)
        builder.beam_x(min(cx, x), max(cx, x), builder.height // 2, z, roles["frame"], 2)
        builder.beam_z(x, builder.height // 2, min(cz, z), max(cz, z), roles["coil"], 2)
    for y, radius in ((6, 30), (builder.height // 2, 51), (builder.height - 6, 65)):
        builder.square_ring(cx, cz, radius, y, roles["coil"], 2)


def design_finality_1(builder: StructureBuilder, roles: dict[str, str]) -> None:
    builder.base(roles)
    cx, cz = builder.width // 2, builder.length // 2
    builder.hollow_box(cx - 13, 4, cz - 13, cx + 13, builder.height - 6, cz + 13, roles["shell"])
    builder.square_ring(cx, cz, 20, 8, roles["coil"], 2)
    builder.square_ring(cx, cz, 64, builder.height - 6, roles["frame"], 2)
    for x, z in ((cx - 45, cz - 45), (cx - 45, cz + 45), (cx + 45, cz - 45), (cx + 45, cz + 45)):
        builder.node(x, z, 9, 6, builder.height - 10, roles)
        builder.beam_x(cx, x, builder.height // 2, z, roles["frame"], 2)
        builder.beam_z(x, builder.height // 2, cz, z, roles["coil"], 2)
    builder.pillar(cx, cz, 5, builder.height - 3, roles["accent"], 3)


def design_finality_2(builder: StructureBuilder, roles: dict[str, str]) -> None:
    builder.base(roles)
    cx, cz = builder.width // 2, builder.length // 2
    for y, radius, block in ((7, 28, roles["shell"]), (builder.height // 2, 58, roles["coil"]),
                             (builder.height - 7, 82, roles["frame"])):
        builder.square_ring(cx, cz, radius, y, block, 3)
    builder.pillar(cx, cz, 4, builder.height - 4, roles["accent"], 3)
    for x, z in ((cx - 70, cz), (cx + 70, cz), (cx, cz - 70), (cx, cz + 70)):
        builder.node(x, z, 11, 10, builder.height - 12, roles)
        builder.beam_x(min(cx, x), max(cx, x), builder.height // 2, z, roles["frame"], 3)
        builder.beam_z(x, builder.height // 2, min(cz, z), max(cz, z), roles["coil"], 3)


def design_finality_3(builder: StructureBuilder, roles: dict[str, str]) -> None:
    builder.base(roles)
    cx, cz = builder.width // 2, builder.length // 2
    builder.node(cx, cz, 13, 9, builder.height - 9, roles)
    for radius, y, block in ((35, 6, roles["shell"]), (70, builder.height // 2, roles["coil"]),
                             (100, builder.height - 7, roles["frame"])):
        builder.square_ring(cx, cz, radius, y, block, 3)
    points = ((cx - 86, cz), (cx + 86, cz), (cx, cz - 86), (cx, cz + 86),
              (cx - 62, cz - 62), (cx - 62, cz + 62), (cx + 62, cz - 62), (cx + 62, cz + 62))
    for index, (x, z) in enumerate(points):
        builder.node(x, z, 8, 8 + index % 3 * 3, builder.height - 11, roles)
        builder.beam_x(min(cx, x), max(cx, x), builder.height // 2, z, roles["frame"], 2)
        builder.beam_z(x, builder.height // 2, min(cz, z), max(cz, z), roles["coil"], 2)


def design_finality_4(builder: StructureBuilder, roles: dict[str, str]) -> None:
    builder.base(roles)
    cx, cz = builder.width // 2, builder.length // 2
    builder.pillar(cx, cz, 2, builder.height - 3, roles["accent"], 3)
    for y, radius, block in ((7, 30, roles["shell"]), (builder.height // 3, 58, roles["coil"]),
                             (builder.height * 2 // 3, 86, roles["coil"]), (builder.height - 8, 120, roles["frame"])):
        builder.square_ring(cx, cz, radius, y, block, 3)
    for y, length, width in ((18, 50, 3), (builder.height // 2, 90, 3), (builder.height - 20, 118, 3)):
        builder.beam_x(cx - length, cx + length, y, cz, roles["frame"], width)
        builder.beam_z(cx, y, cz - length, cz + length, roles["coil"], width)
    branches = ((-1, -1), (-1, 1), (1, -1), (1, 1))
    for level, distance in enumerate((38, 75, 108)):
        y = 12 + level * (builder.height // 3)
        for sx, sz in branches:
            x, z = cx + sx * distance, cz + sz * distance
            builder.node(x, z, 9 if level < 2 else 11, y, min(builder.height - 10, y + 24), roles)
            builder.beam_x(min(cx, x), max(cx, x), y + 8, z, roles["frame"], 2)
            builder.beam_z(x, y + 8, min(cz, z), max(cz, z), roles["coil"], 2)


DESIGNS: dict[str, Callable[[StructureBuilder, dict[str, str]], None]] = {
    **{f"abyss_{i}": globals()[f"design_abyss_{i}"] for i in range(1, 5)},
    **{f"imaginary_{i}": globals()[f"design_imaginary_{i}"] for i in range(1, 5)},
    **{f"quantum_{i}": globals()[f"design_quantum_{i}"] for i in range(1, 5)},
    **{f"finality_{i}": globals()[f"design_finality_{i}"] for i in range(1, 5)},
}


def encode_varints(values: bytearray) -> bytearray:
    """按 Sponge 规范写无符号 varint。"""

    encoded = bytearray()
    for value in values:
        number = int(value)
        while number >= 0x80:
            encoded.append((number & 0x7F) | 0x80)
            number >>= 7
        encoded.append(number)
    return encoded


def write_schematic(path: Path, builder: StructureBuilder, name: str) -> None:
    """写入 gzip 压缩的 Sponge Schematic v2 根标签。"""

    palette = nbt.Compound({block: nbt.Int(index) for block, index in builder.index.items()})
    payload = nbt.Compound(
        {
            "Version": nbt.Int(2),
            "DataVersion": nbt.Int(3465),
            "Width": nbt.Short(builder.width),
            "Height": nbt.Short(builder.height),
            "Length": nbt.Short(builder.length),
            "Offset": nbt.IntArray([0, 0, 0]),
            "Palette": palette,
            "PaletteMax": nbt.Int(len(builder.palette)),
            "BlockData": nbt.ByteArray(encode_varints(builder.blocks)),
            "BlockEntities": nbt.List[nbt.Compound]([]),
            "Entities": nbt.List[nbt.Compound]([]),
            "Metadata": nbt.Compound({"Name": nbt.String(name)}),
        }
    )
    file = nbt.File(payload, gzipped=True, root_name="Schematic")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as raw:
        with gzip.GzipFile(fileobj=raw, mode="wb", compresslevel=9, mtime=0) as compressed:
            file.write(compressed)


def decode_varints(data: Iterable[int], expected: int) -> list[int]:
    """解码 BlockData 并检查每个体素都有且只有一个调色板索引。"""

    result: list[int] = []
    value = 0
    shift = 0
    for raw in data:
        byte = int(raw) & 0xFF
        value |= (byte & 0x7F) << shift
        if byte & 0x80:
            shift += 7
            if shift > 28:
                raise ValueError("BlockData 中存在过长 varint")
        else:
            result.append(value)
            value = 0
            shift = 0
    if shift:
        raise ValueError("BlockData 以未完成的 varint 结尾")
    if len(result) != expected:
        raise ValueError(f"BlockData 数量错误: {len(result)} != {expected}")
    return result


def verify_schematic(path: Path, expected: tuple[int, int, int]) -> dict:
    """离线校验 NBT、尺寸、调色板、坐标范围和旧版命名空间。"""

    with gzip.open(path, "rb") as compressed:
        root = nbt.File.parse(compressed)
    if root.root_name != "Schematic":
        raise ValueError(f"根标签不是 Schematic: {root.root_name}")
    width, height, length = int(root["Width"]), int(root["Height"]), int(root["Length"])
    if (width, height, length) != expected:
        raise ValueError(f"尺寸错误: {(width, height, length)} != {expected}")
    if int(root["Version"]) != 2 or int(root["DataVersion"]) != 3465:
        raise ValueError("Schematic 版本或 DataVersion 不符合规范")
    palette = {str(key): int(value) for key, value in root["Palette"].items()}
    if palette.get(AIR) != 0:
        raise ValueError("minecraft:air 必须是调色板索引0")
    forbidden = [key for key in palette if key.startswith(FORBIDDEN_PREFIXES)]
    if forbidden:
        raise ValueError(f"发现旧版 HK3GTL 方块: {forbidden}")
    indices = decode_varints(root["BlockData"], width * height * length)
    inverse = {value: key for key, value in palette.items()}
    if any(index not in inverse for index in indices):
        raise ValueError("BlockData 引用了不存在的调色板索引")
    counts = collections.Counter(inverse[index] for index in indices if index != 0)
    if counts[CORE] < 1 or counts[INTERFACE] != 6:
        raise ValueError(f"核心或接口数量错误: 核心={counts[CORE]}, 接口={counts[INTERFACE]}")
    return {
        "size": [width, height, length],
        "palette": palette,
        "non_air_blocks": sum(counts.values()),
        "block_counts": dict(counts),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def stage_status(block_id: str) -> str:
    """返回材料核验边界，避免把静态资源证据误报为完整科技树证据。"""

    if block_id.startswith("minecraft:"):
        return "项目指定标记；不纳入普通建材阶段判断"
    return "已核对指定实例 JAR 的注册、方块状态和完整模型；最终配方、科技门槛与碰撞箱仍需运行时核验"


def write_html(manifest: list[dict]) -> None:
    """生成结构交付说明，不生成预览器或额外可视化文件。"""

    rows = []
    for item in manifest:
        material_text = "；".join(f"{m['id']} × {m['count']}" for m in item["materials"])
        interface_text = "；".join(f"{x['role']} ({','.join(map(str, x['pos']))})" for x in item["interfaces"])
        rows.append(
            "<tr>"
            f"<td><code>{html.escape(item['file'])}</code></td>"
            f"<td>{html.escape(item['stage'])}<br>tier {item['tier']} · {html.escape(item['voltage_label'])}</td>"
            f"<td>{' × '.join(map(str, item['size']))}</td>"
            f"<td>{html.escape(item['design'])}<br>{html.escape(item['concept'])}</td>"
            f"<td>{html.escape(material_text)}</td>"
            f"<td>{html.escape(interface_text)}<br>核心 {item['core'][0]['pos']}</td>"
            f"<td>{html.escape(item['runtime_status'])}</td>"
            "</tr>"
        )
    text = f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>内测5十六级结构文件交付 v1</title>
<style>
body{{max-width:1700px;margin:auto;padding:28px;background:#0b1020;color:#edf3ff;font:15px/1.7 system-ui,"Microsoft YaHei",sans-serif}}
h1,h2{{color:#78e7de}}section{{background:#141e32;border:1px solid #405270;border-radius:10px;padding:16px;margin:16px 0}}
table{{border-collapse:collapse;width:100%;font-size:12px}}th,td{{border-bottom:1px solid #405270;padding:8px;text-align:left;vertical-align:top}}th{{color:#78e7de;background:#182943;position:sticky;top:0}}code{{color:#ffd392}}.warn{{border-left:4px solid #ff9f7a;padding-left:14px}}
</style></head><body>
<h1>内测5十六级结构文件交付 v1</h1>
<p>生成日期：2026-09-24。实例输出目录：<code>{html.escape(str(SCHEMATIC_DIR))}</code>；项目归档副本：<code>{html.escape(str(ARCHIVE_SCHEMATIC_DIR))}</code>。</p>
<section class="warn"><h2>本次交付边界</h2><ul>
<li>十六个文件均为 Sponge Schematic v2，Version=2、DataVersion=3465，gzip 压缩等级 9。</li>
<li>实体构件只使用完整 1×1×1 方块；没有楼梯、半砖、栏杆、栅栏、门、活板门、管线或文字实体。</li>
<li><code>minecraft:diamond_block</code> 只表示主机核心；六个 <code>minecraft:diamond_ore</code> 只表示物品、流体和能源接口占位。</li>
<li>材料只来自指定 Prism 实例中核对过的 GTCEu/GTLCore 资源，未引用任何 <code>hk3gtl:*</code> 旧版方块。</li>
<li>结构文件、Pattern 成型和机器功能分开验收；本次没有改 Java、KubeJS、配方、控制器或玩家存档。</li>
</ul></section>
<section><h2>坐标与高度</h2><p>本地原点为结构包围盒西北下角，默认粘贴底部世界 Y=-60。所有文件最高占用方块均低于 Y=236。核心、接口坐标和材料数量以同目录 <code>manifest.json</code> 为准。</p></section>
<section><h2>十六座建筑</h2><div style="overflow:auto"><table><thead><tr><th>文件</th><th>阶段</th><th>尺寸</th><th>设计概念</th><th>实际材料数量</th><th>核心与接口</th><th>状态</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div></section>
<section><h2>尚未完成的验收</h2><ol><li>在指定 Prism 实例中创建全新存档，逐个粘贴并检查区块加载、方块注册和视觉材质。</li><li>根据最终确认的控制器与 Pattern，重新映射核心和接口，完成成型测试；不能把本文件直接当作可运行机器证明。</li><li>通过游戏内 JEI/GuideMe 或运行时导出核对普通建材的实际配方、科技门槛、碰撞箱和阶段可达性；静态 JAR 模型证据不能替代这一步。</li></ol></section>
<footer>生成工具：tools/structure_delivery/generate_schematics.py。未生成预览器、预览网页或额外可视化资源。</footer>
</body></html>"""
    (DELIVERY_ROOT / "内测5十六级结构文件交付_v1.html").write_text(text, encoding="utf-8")


def build_all() -> list[dict]:
    SCHEMATIC_DIR.mkdir(parents=True, exist_ok=True)
    DELIVERY_ROOT.mkdir(parents=True, exist_ok=True)
    ARCHIVE_SCHEMATIC_DIR.mkdir(parents=True, exist_ok=True)
    manifest: list[dict] = []
    for spec in SPECS:
        builder = StructureBuilder(spec["size"][0], spec["size"][1], spec["size"][2], spec["palette"].values())
        DESIGNS[spec["builder"]](builder, spec["palette"])
        cores, interfaces = builder.finalize_markers()
        filename = f"GT_Multiblock_{spec['key']}.schem"
        output = SCHEMATIC_DIR / filename
        write_schematic(output, builder, filename)
        shutil.copy2(output, ARCHIVE_SCHEMATIC_DIR / filename)
        verification = verify_schematic(output, spec["size"])
        counts = verification["block_counts"]
        ordinary = sum(value for key, value in counts.items() if key not in (CORE, INTERFACE))
        sources = collections.Counter("GTCEu" if key.startswith("gtceu:") else "GTLCore" if key.startswith("gtlcore:") else "原版标记" for key in counts)
        materials = [
            {
                "id": block_id,
                "count": counts[block_id],
                "source": "原版标记" if block_id.startswith("minecraft:") else block_id.split(":", 1)[0],
                "stage_evidence": stage_status(block_id),
            }
            for block_id in sorted(counts)
        ]
        manifest.append(
            {
                "file": filename, "key": spec["key"], "stage": spec["stage"], "tier": spec["tier"],
                "voltage_label": spec["voltage"], "size": list(spec["size"]), "origin": [0, 0, 0],
                "recommended_world_y": -60, "world_height_range": [-60, -60 + spec["size"][1] - 1],
                "paste_anchor": "本地坐标(0,0,0)为结构包围盒西北下角；核心与接口坐标均为本地坐标",
                "design": spec["design"], "concept": spec["concept"], "core": cores, "interfaces": interfaces,
                "materials": materials, "ordinary_material_blocks": ordinary, "source_counts": dict(sources),
                "sha256": verification["sha256"],
                "runtime_status": "结构文件已离线校验；尚未迁移 Pattern，也未宣称机器已经成型或可运行",
            }
        )
        print(f"已生成 {filename}: {spec['size']}，非空气方块 {verification['non_air_blocks']}，SHA256 {verification['sha256'][:12]}")
    (DELIVERY_ROOT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_html(manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="生成并离线校验内测5十六级 Sponge Schematic")
    parser.add_argument("--verify-only", action="store_true", help="只校验已经生成的十六个文件")
    args = parser.parse_args()
    if args.verify_only:
        for spec in SPECS:
            path = SCHEMATIC_DIR / f"GT_Multiblock_{spec['key']}.schem"
            result = verify_schematic(path, spec["size"])
            print(f"校验通过 {path.name}: {result['non_air_blocks']} 个非空气方块")
    else:
        build_all()


if __name__ == "__main__":
    main()

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
