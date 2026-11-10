"""Verify exported preview port blocks against their source metadata."""
import importlib

from check_i01_upgrade import read_structure


GENERATORS = (
    'build_i01_tidal_preview',
    'build_i01_stage2_preview',
    'build_i01_stage3_preview',
    'build_i01_stage4_preview',
    'build_i02_spectrum_preview',
    'build_i03_centrifuge_preview',
    'build_i04_stabilization_preview',
    'build_i05_regeneration_preview',
    'build_i06_fuel_blending_preview',
    'build_i07_calibration_preview',
    'build_i08_crystallization_preview',
)


def main():
    total = 0
    for name in GENERATORS:
        generator = importlib.import_module(name)
        data = generator.build()
        exported = list(generator.OUT.glob('*.nbt'))
        assert len(exported) == 1, (name, exported)
        cells = read_structure(exported[0])
        for port in data['ports']:
            pos = tuple(port['pos'])
            assert cells.get(pos) == 'hk3gtl:industrial_port_casing', (
                name, port['id'], pos, cells.get(pos))
        total += len(data['ports'])
        print(f"{data['key']}: {len(data['ports'])} ports, "
              f"{len(set(block['state'] for block in data['blocks']))} materials")
    print(f'Verified {total} exported ports.')


if __name__ == '__main__':
    main()
