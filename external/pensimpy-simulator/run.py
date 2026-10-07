"""Run IndPenSim batch simulation and print results row by row."""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from simulator.simulation_runner import indpensim_run


CHANNELS = [
    ('S',   'substrate_conc',       'g/L'),
    ('P',   'penicillin_conc',      'g/L'),
    ('X',   'biomass_conc',         'g/L'),
    ('V',   'volume',               'L'),
    ('Fg',  'air_flow',             'L/h'),
    ('DO2', 'dissolved_oxygen',     '%'),
    ('pH',  'pH',                   '-'),
    ('T',   'temperature',          'C'),
    ('Foil','oil_flow',             'L/h'),
    ('Fw',  'water_flow',           'L/h'),
    ('Fa',  'acid_flow',            'L/h'),
    ('Fb',  'base_flow',            'L/h'),
    ('Fs',  'substrate_feed',       'L/h'),
]


def print_row(k, Xref):
    t = float(Xref.S.t[k])
    parts = [f't={t:7.2f}h']
    for attr, name, unit in CHANNELS:
        ch = getattr(Xref, attr, None)
        if ch is not None and hasattr(ch, 'y') and k < len(ch.y):
            val = float(ch.y[k])
            if np.isfinite(val):
                parts.append(f'{name}={val:.4g}{unit}')

    raman = getattr(Xref, 'Raman_Spec', None)
    if raman is not None and hasattr(raman, 'Intensity') and raman.Intensity.ndim == 2:
        if k < raman.Intensity.shape[1]:
            spectrum = raman.Intensity[:, k].tolist()
            parts.append(f'raman_spectrum={spectrum}')

    print('  ' + '  '.join(parts))


def main():
    print('IndPenSim - Batch Simulation')
    print('=' * 60)

    batch_run_flags = {
        'Batch_fault_order_reference': [0],
        'Control_strategy': [0],
        'Batch_length': [0],
        'Raman_spec': [0],
    }

    start = time.perf_counter()
    Xref = indpensim_run(1, batch_run_flags)
    elapsed = time.perf_counter() - start

    n = len(Xref.S.y)
    print(f'Simulation completed in {elapsed:.2f}s  |  {n} samples')
    print(f'Batch length:     {Xref.V.t[-1]:.1f} h')
    print(f'Final biomass:    {Xref.X.y[-1]:.3f} g/L')
    print(f'Final penicillin: {Xref.P.y[-1]:.3f} g/L')
    print(f'Total yield:      {Xref.Stats.Penicllin_yield_total / 1000:.1f} kg')
    print('=' * 60)
    print('Row-by-row data:')
    print()

    for k in range(n):
        print_row(k, Xref)

    print()
    print('Done.')


if __name__ == '__main__':
    main()
