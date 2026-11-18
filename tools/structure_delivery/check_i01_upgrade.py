"""Check that an I01 upgrade only replaces its controller and adds blocks.

Coordinates are aligned by each stage's controller, so structures may grow
in any direction without forcing a shared local origin or bounding box.
"""

import argparse
import json
from pathlib import Path

import nbtlib


def read_structure(path):
    root = nbtlib.load(path)
    palette = []
    for entry in root['palette']:
        state = str(entry['Name'])
        if 'Properties' in entry:
            props = ','.join(f'{key}={value}' for key, value in sorted(entry['Properties'].items()))
            state += f'[{props}]'
        palette.append(state)
    return {tuple(map(int, block['pos'])): palette[int(block['state'])]
            for block in root['blocks']}


def check_upgrade(previous, previous_controller, next_stage, next_controller):
    previous_controller = tuple(previous_controller)
    next_controller = tuple(next_controller)
    if previous_controller not in previous or next_controller not in next_stage:
        return ['Both stages must have a placed controller marker at the declared anchor.']
    offset = tuple(next_controller[i] - previous_controller[i] for i in range(3))
    errors = []
    for pos, state in previous.items():
        if pos == previous_controller:
            continue
        target = tuple(pos[i] + offset[i] for i in range(3))
        actual = next_stage.get(target)
        if actual != state:
            errors.append(f'{pos} -> {target}: expected {state}, found {actual or "air"}')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('previous', type=Path, help='Previous-stage vanilla structure NBT')
    parser.add_argument('next_stage', type=Path, help='Next-stage vanilla structure NBT')
    parser.add_argument('--previous-controller', nargs=3, type=int, required=True, metavar=('X', 'Y', 'Z'))
    parser.add_argument('--next-controller', nargs=3, type=int, required=True, metavar=('X', 'Y', 'Z'))
    args = parser.parse_args()
    previous = read_structure(args.previous)
    next_stage = read_structure(args.next_stage)
    errors = check_upgrade(previous, args.previous_controller, next_stage, args.next_controller)
    print(json.dumps({
        'compatible': not errors,
        'preserved_non_controller_blocks': len(previous) - 1,
        'added_blocks': len(next_stage) - len(previous),
        'mismatches': errors[:50], 'mismatch_count': len(errors),
    }, ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
