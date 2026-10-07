"""Seed QuestDB + Qdrant with N historical batches, then stream one live batch."""

import http.client
import json
import os
import sys
import time
import urllib.parse
import uuid
from datetime import datetime, timezone

import numpy as np

# Path setup: project root (for simulator.*) and runtime dir (for questdb_sender, run)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(1, os.path.dirname(os.path.abspath(__file__)))

from simulator.simulation_runner import indpensim_run
from questdb_sender import (
    PROCESS_CHANNELS, _make_conf_string, _batch_id, uns_path,
)
import run as run_module  # stream_batch, build_pv_payload, build_spectrum_payload

QUESTDB_HOST = os.environ.get('QUESTDB_HOST', 'localhost')
QUESTDB_HTTP_PORT = int(os.environ.get('QUESTDB_HTTP_PORT', '9000'))
QDRANT_HOST = os.environ.get('QDRANT_HOST', 'localhost')
QDRANT_PORT = int(os.environ.get('QDRANT_PORT', '6333'))
SIM_NUM_HISTORY = int(os.environ.get('SIM_NUM_HISTORY', '20'))
SIM_STREAM_INTERVAL = float(os.environ.get('SIM_STREAM_INTERVAL', '2.0'))

BATCH_FLAGS = {
    'Batch_fault_order_reference': [0],
    'Control_strategy': [0],
    'Batch_length': [0],
    'Raman_spec': [1],
}

QUESTDB_TABLES = [
    'batch_aligned',
    'batch_statistics',
    'process_data',
    'raman_intensities',
    'raman_wavelengths',
]


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def _questdb_exec(query, retries=30):
    """Execute a QuestDB DDL/DML statement via HTTP, waiting for the DB to be ready."""
    for attempt in range(retries):
        try:
            conn = http.client.HTTPConnection(QUESTDB_HOST, QUESTDB_HTTP_PORT, timeout=5)
            conn.request('GET', '/exec?query=' + urllib.parse.quote(query))
            resp = conn.getresponse()
            body = resp.read().decode()
            conn.close()
            if resp.status == 200:
                return json.loads(body)
            print(f'  QuestDB ({resp.status}): {body[:200]}')
            return None
        except Exception as exc:
            if attempt < retries - 1:
                print(f'  QuestDB not ready (attempt {attempt + 1}/{retries}): {exc}')
                time.sleep(2)
            else:
                raise


def clear_questdb():
    """Drop all simulation tables/views so we start from a clean state."""
    print('Clearing QuestDB tables...')
    for table in QUESTDB_TABLES:
        # batch_aligned is a materialized view — needs different DROP syntax
        if table == 'batch_aligned':
            result = _questdb_exec(f'DROP MATERIALIZED VIEW IF EXISTS {table}')
            if result is None:
                _questdb_exec(f'DROP VIEW IF EXISTS {table}')
        else:
            _questdb_exec(f'DROP TABLE IF EXISTS {table}')
        print(f'  Dropped {table}')
    print('QuestDB cleared.\n')


def clear_and_init_qdrant():
    """Delete + recreate the raman_spectra collection, return the client."""
    from qdrant_client import QdrantClient
    from qdrant_client.models import VectorParams, Distance

    print('Clearing Qdrant collection...')
    for attempt in range(30):
        try:
            client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT, timeout=10)
            names = [c.name for c in client.get_collections().collections]
            if 'raman_spectra' in names:
                client.delete_collection('raman_spectra')
                print('  Deleted existing raman_spectra collection')
            client.create_collection(
                collection_name='raman_spectra',
                vectors_config=VectorParams(size=2200, distance=Distance.EUCLID),
            )
            print('  Created fresh raman_spectra collection\n')
            return client
        except Exception as exc:
            if attempt < 29:
                print(f'  Qdrant not ready (attempt {attempt + 1}/30): {exc}')
                time.sleep(2)
            else:
                raise


# ---------------------------------------------------------------------------
# Fast historical batch storage (no streaming delay, no NATS)
# ---------------------------------------------------------------------------

def store_batch_fast(Xref, batch_no, qdrant_client):
    """Write a completed batch directly to QuestDB + Qdrant at full speed."""
    from questdb.ingress import Sender, TimestampNanos
    from qdrant_client.models import PointStruct

    bid = _batch_id(batch_no)
    n_samples = len(Xref.S.y)
    batch_start = datetime.now(timezone.utc)
    has_raman = (
        hasattr(Xref, 'Raman_Spec') and Xref.Raman_Spec is not None
        and hasattr(Xref.Raman_Spec, 'Intensity')
    )

    sender = Sender.from_conf(_make_conf_string())
    sender.establish()

    # -- Raman wavelengths (once per batch) --
    if has_raman:
        wavelength = Xref.Raman_Spec.Wavelength
        raman_uns = uns_path('pat', 'raman_spectrum')
        try:
            sender.row(
                'raman_wavelengths',
                symbols={'uns': raman_uns, 'batch_id': bid},
                columns={
                    'wavelengths': wavelength.astype(np.float64),
                    'min_cm1': float(wavelength.min()),
                    'max_cm1': float(wavelength.max()),
                },
                at=TimestampNanos(int(batch_start.timestamp() * 1e9)),
            )
            sender.flush()
        except Exception as exc:
            print(f'  Raman wavelengths error: {exc}')

    qdrant_batch = []

    for k in range(n_samples):
        batch_hours = float(Xref.S.t[k])
        ts = batch_start.timestamp() + batch_hours * 3600
        base_nanos = int(ts * 1e9)

        pv = run_module.build_pv_payload(Xref, k)

        # Process data → QuestDB narrow format
        try:
            for i, (_, var_name, unit) in enumerate(PROCESS_CHANNELS):
                if var_name in pv:
                    sender.row(
                        'process_data',
                        symbols={'uns': uns_path(unit, var_name), 'batch_id': bid},
                        columns={'value': pv[var_name], 'batch_time_h': pv['batch_time_h']},
                        at=TimestampNanos(base_nanos + i),
                    )
        except Exception as exc:
            print(f'  QuestDB PV error at k={k}: {exc}')

        # Preprocessed Raman → QuestDB + Qdrant
        if has_raman:
            spectrum = run_module.build_spectrum_payload(Xref, k)
            if spectrum is not None:
                try:
                    sender.row(
                        'raman_intensities',
                        symbols={'uns': uns_path('pat', 'raman_spectrum'), 'batch_id': bid},
                        columns={'spectrum': spectrum, 'batch_time_h': batch_hours},
                        at=TimestampNanos(base_nanos + len(PROCESS_CHANNELS)),
                    )
                except Exception as exc:
                    print(f'  QuestDB Raman error at k={k}: {exc}')

                if qdrant_client is not None:
                    point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f'{bid}_{k}'))
                    qdrant_batch.append(PointStruct(
                        id=point_id,
                        vector=spectrum.tolist(),
                        payload={'batch_id': bid, 'batch_time_h': batch_hours, 'sample_index': k},
                    ))

        # Flush every 50 samples
        if (k + 1) % 50 == 0 or k == n_samples - 1:
            try:
                sender.flush()
            except Exception as exc:
                print(f'  QuestDB flush error at k={k}: {exc}')

        # Qdrant batch upsert every 50 points
        if len(qdrant_batch) >= 50:
            try:
                qdrant_client.upsert(collection_name='raman_spectra', points=qdrant_batch)
                qdrant_batch = []
            except Exception as exc:
                print(f'  Qdrant upsert error at k={k}: {exc}')

        if k % 200 == 0 or k == n_samples - 1:
            print(f'    [{k + 1}/{n_samples}] t={batch_hours:.1f}h  '
                  f'P={pv.get("penicillin_conc", 0):.3f} g/L')

    # Flush remaining Qdrant points
    if qdrant_batch and qdrant_client is not None:
        try:
            qdrant_client.upsert(collection_name='raman_spectra', points=qdrant_batch)
        except Exception as exc:
            print(f'  Qdrant final flush error: {exc}')

    # Batch statistics
    if hasattr(Xref, 'Stats'):
        ts_end = int((batch_start.timestamp() + Xref.V.t[-1] * 3600) * 1e9)
        try:
            sender.row(
                'batch_statistics',
                symbols={'batch_id': bid},
                columns={
                    'batch_no': float(batch_no),
                    'batch_length_h': float(Xref.Stats.Batch_length),
                    'penicillin_harvested_during': float(Xref.Stats.Penicllin_harvested_during_batch),
                    'penicillin_harvested_end': float(Xref.Stats.Penicllin_harvested_end_of_batch),
                    'penicillin_yield_total': float(Xref.Stats.Penicllin_yield_total),
                    'n_samples': float(n_samples),
                },
                at=TimestampNanos(ts_end),
            )
            sender.flush()
        except Exception as exc:
            print(f'  QuestDB stats error: {exc}')

    sender.close()
    print(f'  → {bid}: {n_samples} samples stored, '
          f'P_final={Xref.P.y[-1]:.3f} g/L, '
          f'yield={Xref.Stats.Penicllin_yield_total / 1000:.1f} kg')


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    import asyncio

    print('=' * 60)
    print('IndPenSim — Seed & Run')
    print('=' * 60)

    # Step 1: Clear databases
    clear_questdb()
    qdrant_client = clear_and_init_qdrant()

    # Step 2: Run N historical batches at full speed (no NATS, no delay)
    print(f'Running {SIM_NUM_HISTORY} historical batches (fast mode)...')
    print('=' * 60)

    for batch_no in range(1, SIM_NUM_HISTORY + 1):
        print(f'\nHistorical batch {batch_no}/{SIM_NUM_HISTORY}:')
        t0 = time.perf_counter()
        Xref = indpensim_run(1, BATCH_FLAGS)
        print(f'  Simulation: {time.perf_counter() - t0:.1f}s')
        store_batch_fast(Xref, batch_no, qdrant_client)

    print(f'\n{SIM_NUM_HISTORY} historical batches stored in QuestDB + Qdrant.')
    print('=' * 60)

    # Step 3: Run live batch with full streaming (NATS + QuestDB, paced)
    live_batch_no = SIM_NUM_HISTORY + 1
    print(f'\nStarting live batch #{live_batch_no}...')

    t0 = time.perf_counter()
    Xref = indpensim_run(1, BATCH_FLAGS)
    elapsed = time.perf_counter() - t0

    print(f'Simulation completed in {elapsed:.2f}s')
    print(f'Samples:          {len(Xref.S.y)}')
    print(f'Batch length:     {Xref.V.t[-1]:.1f} h')
    print(f'Final penicillin: {Xref.P.y[-1]:.3f} g/L')
    print(f'Total yield:      {Xref.Stats.Penicllin_yield_total / 1000:.1f} kg')
    print('=' * 60)

    asyncio.run(run_module.stream_batch(
        Xref, live_batch_no, SIM_STREAM_INTERVAL,
        no_questdb=False, no_nats=False,
    ))


if __name__ == '__main__':
    main()
