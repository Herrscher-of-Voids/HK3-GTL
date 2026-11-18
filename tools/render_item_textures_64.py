import json
from pathlib import Path

from texture_redraw_0002_r4 import world, process
from texture_redraw_0002_keys_r6 import eden, judah

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'src/main/resources/assets/hk3gtl'
REVIEW = json.loads((ROOT / 'logs/textures-redraw-0002-r3-20261114/art-review.json').read_text(encoding='utf-8'))
TARGETS = (set(REVIEW['active_nonfuel_redraw_ids']) - set(REVIEW['accepted_ids'])
           - set(REVIEW['excluded_item_ids']) - set(REVIEW['paused_fuel_ids']))
KEYS = {'imitation_star_of_eden': eden.draw, 'imitation_oath_of_judah': judah.draw}

for ident, draw in KEYS.items():
    if ident in TARGETS:
        draw().save(ASSETS / f'textures/item/{ident}.png')

for module in [world, process]:
    for ident in module.IDS:
        if ident in TARGETS and ident not in KEYS:
            module.draw(ident).save(ASSETS / f'textures/item/{ident}.png', optimize=True)
