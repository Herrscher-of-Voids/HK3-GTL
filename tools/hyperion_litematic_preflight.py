"""对负责人指定的休伯利安原稿执行离线分段与预算预检。"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import nbtlib
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "deliveries/休伯利安_用户指定新舰体_20261001/休伯利安.litematic"
OUTPUT = ROOT / "logs/hyperion-preflight-20261106/scan-manifest.json"
EXPECTED_SHA256 = "2238856E3358F88802EB71F59A8D7765A50397FA6BF111D63E992BEF2723B91C"
SEGMENT_EDGE = 16
DECODE_BATCH_SIZE = 1_000_000


def unpack_batches(words: np.ndarray, total: int, bits: int, batch_size: int):
    """按存储顺序分批解码紧凑方块索引，避免一次展开全部包围盒。"""
    mask = np.uint64((1 << bits) - 1)
    for start in range(0, total, batch_size):
        positions = np.arange(start, min(start + batch_size, total), dtype=np.uint64)
        bit_positions = positions * bits
        word_indices = bit_positions >> 6
        shifts = bit_positions & 63
        values = words[word_indices] >> shifts
        crosses = shifts + bits > 64
        if np.any(crosses):
            values[crosses] |= words[word_indices[crosses] + 1] << (64 - shifts[crosses])
        values &= mask
        yield start, values.astype(np.uint16)


def state_name(state) -> str:
    name = str(state["Name"])
    properties = state.get("Properties")
    if not properties:
        return name
    fields = ",".join(f"{key}={properties[key]}" for key in sorted(properties))
    return f"{name}[{fields}]"


def segment_geometry(width: int, height: int, depth: int, edge: int):
    counts = (
        math.ceil(width / edge),
        math.ceil(height / edge),
        math.ceil(depth / edge),
    )
    segments = []
    for sx in range(counts[0]):
        x = sx * edge
        for sy in range(counts[1]):
            y = sy * edge
            for sz in range(counts[2]):
                z = sz * edge
                size = (
                    min(edge, width - x),
                    min(edge, height - y),
                    min(edge, depth - z),
                )
                segments.append({
                    "coordinate": [x, y, z],
                    "size": list(size),
                    "cells": size[0] * size[1] * size[2],
                    "non_air": 0,
                })
    return counts, segments


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def inspect_region(name: str, region, edge: int, batch_size: int) -> dict:
    signed_size = [int(region["Size"][axis]) for axis in "xyz"]
    width, height, depth = (abs(value) for value in signed_size)
    volume = width * height * depth
    palette = region["BlockStatePalette"]
    bits = max(2, (len(palette) - 1).bit_length())
    words = np.asarray(region["BlockStates"], dtype=np.int64).view(np.uint64)
    if len(words) != (volume * bits + 63) // 64:
        raise ValueError(f"{name}: 压缩方块数组长度不匹配")

    air_ids = [index for index, state in enumerate(palette) if str(state["Name"]) == "minecraft:air"]
    if air_ids != [0]:
        raise ValueError(f"{name}: 空气必须唯一且位于调色板索引0")
    air_id = air_ids[0]
    palette_counts = np.zeros(len(palette), dtype=np.uint64)
    tile_counts, segments = segment_geometry(width, height, depth, edge)
    tile_y_count, tile_z_count = tile_counts[1], tile_counts[2]
    non_air = 0

    for start, ids in unpack_batches(words, volume, bits, batch_size):
        end = start + len(ids)
        if int(ids.max(initial=0)) >= len(palette):
            raise ValueError(f"{name}: 方块索引超出调色板")
        palette_counts += np.bincount(ids.astype(np.int64), minlength=len(palette)).astype(np.uint64)

        positions = np.arange(start, end, dtype=np.uint64)
        occupied = ids != air_id
        if not np.any(occupied):
            continue
        non_air_positions = positions[occupied]
        x = non_air_positions % width
        y = non_air_positions // (width * depth)
        z = (non_air_positions // width) % depth
        tile_ids = ((x // edge) * tile_y_count + (y // edge)) * tile_z_count + z // edge
        segment_counts = np.bincount(tile_ids.astype(np.int64), minlength=len(segments))
        for index in np.flatnonzero(segment_counts):
            segments[int(index)]["non_air"] += int(segment_counts[index])
        non_air += len(non_air_positions)

    if int(palette_counts.sum()) != volume:
        raise ValueError(f"{name}: 调色板计数与包围盒体积不一致")
    if sum(segment["cells"] for segment in segments) != volume:
        raise ValueError(f"{name}: 分段存在缺口或重叠")
    if sum(segment["non_air"] for segment in segments) != non_air:
        raise ValueError(f"{name}: 分段占用计数不守恒")

    palette_summary = [
        {"state": state_name(state), "count": int(count)}
        for state, count in zip(palette, palette_counts)
    ]
    block_entities = len(region.get("TileEntities", []))
    entities = len(region.get("Entities", []))
    return {
        "name": name,
        "signed_size": signed_size,
        "position": [int(region["Position"][axis]) for axis in "xyz"],
        "storage_local_axes_only": True,
        "volume": volume,
        "non_air": non_air,
        "block_entities": block_entities,
        "entities": entities,
        "palette_bits": bits,
        "palette": palette_summary,
        "segment_grid": list(tile_counts),
        "segment_count": len(segments),
        "segment_edge": edge,
        "max_segment_cells": max(segment["cells"] for segment in segments),
        "segments": segments,
    }


def build_manifest(source: Path, output: Path, edge: int, batch_size: int) -> dict:
    actual_hash = sha256(source)
    if actual_hash != EXPECTED_SHA256:
        raise ValueError(f"原稿SHA256不符：{actual_hash}")
    schematic = nbtlib.load(source)
    regions = [
        inspect_region(name, region, edge, batch_size)
        for name, region in schematic["Regions"].items()
    ]
    total_blocks = sum(region["non_air"] for region in regions)
    total_entities = sum(region["entities"] for region in regions)
    total_block_entities = sum(region["block_entities"] for region in regions)
    if total_blocks != int(schematic["Metadata"]["TotalBlocks"]):
        raise ValueError("非空气方块总数与Litematica元数据不一致")
    if (total_blocks, total_block_entities, len(regions)) != (1_469_258, 3_402, 1):
        raise ValueError("指定原稿的已核验方块、方块实体或区域数量发生变化")

    result = {
        "checked_at": "2026-11-06",
        "source": str(source.relative_to(ROOT)).replace("\\", "/"),
        "source_sha256": actual_hash,
        "region_count": len(regions),
        "non_air_blocks": total_blocks,
        "block_entities": total_block_entities,
        "entities": total_entities,
        "segment_edge": edge,
        "regions": regions,
        "result": {
            "passed": True,
            "segment_cells_equal_source_volume": True,
            "segment_non_air_sum_equal_source": True,
            "runtime_or_game_performance_verified": False,
            "note": "分段覆盖Litematica存储局部坐标；未定向到游戏世界，也不构成H01结构或运行批准。",
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="休伯利安原稿离线分段预检")
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--edge", type=int, default=SEGMENT_EDGE)
    parser.add_argument("--batch-size", type=int, default=DECODE_BATCH_SIZE)
    args = parser.parse_args()
    if args.edge != SEGMENT_EDGE or args.batch_size < 1:
        parser.error("分段边长固定为16；解码批大小必须为正数")
    result = build_manifest(args.source.resolve(), args.output.resolve(), args.edge, args.batch_size)
    print(json.dumps({
        "passed": result["result"]["passed"],
        "source_sha256": result["source_sha256"],
        "non_air_blocks": result["non_air_blocks"],
        "block_entities": result["block_entities"],
        "segments": sum(region["segment_count"] for region in result["regions"]),
        "max_segment_cells": max(region["max_segment_cells"] for region in result["regions"]),
        "output": str(args.output),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
