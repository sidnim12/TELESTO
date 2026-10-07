"""Minimal TELESTO smoke test for the IndPenSim fermentation simulator."""

from pathlib import Path
import sys

import numpy as np


# ---------------------------------------------------------------------------
# Locate the external simulator
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SIMULATOR_ROOT = PROJECT_ROOT / "external" / "pensimpy-simulator"

if not SIMULATOR_ROOT.exists():
    raise FileNotFoundError(
        f"Simulator not found at: {SIMULATOR_ROOT}"
    )

sys.path.insert(0, str(SIMULATOR_ROOT))


# ---------------------------------------------------------------------------
# Import simulator
# ---------------------------------------------------------------------------

from simulator.simulation_runner import indpensim_run  # noqa: E402


# ---------------------------------------------------------------------------
# Run one deterministic batch
# ---------------------------------------------------------------------------

BATCH_FLAGS = {
    "Batch_fault_order_reference": [0],
    "Control_strategy": [0],
    "Batch_length": [0],
    "Raman_spec": [0],
}


def main() -> None:
    print("TELESTO - Simulator Smoke Test")
    print("=" * 60)

    result = indpensim_run(1, BATCH_FLAGS)

    # Required trajectories
    time = np.asarray(result.S.t, dtype=float)
    substrate = np.asarray(result.S.y, dtype=float)
    penicillin = np.asarray(result.P.y, dtype=float)
    biomass = np.asarray(result.X.y, dtype=float)
    volume = np.asarray(result.V.y, dtype=float)

    # Basic structural checks
    assert len(time) > 0, "No simulation samples returned."
    assert len(substrate) == len(time), "Substrate trajectory length mismatch."
    assert len(penicillin) == len(time), "Penicillin trajectory length mismatch."
    assert len(biomass) == len(time), "Biomass trajectory length mismatch."
    assert len(volume) == len(time), "Volume trajectory length mismatch."

    # Numerical checks
    assert np.all(np.isfinite(time)), "Non-finite time values found."
    assert np.all(np.isfinite(substrate)), "Non-finite substrate values found."
    assert np.all(np.isfinite(penicillin)), "Non-finite penicillin values found."
    assert np.all(np.isfinite(biomass)), "Non-finite biomass values found."
    assert np.all(np.isfinite(volume)), "Non-finite volume values found."

    # Batch duration check
    assert time[-1] > time[0], "Simulation did not advance in time."

    print(f"Samples:          {len(time)}")
    print(f"Batch duration:   {time[-1] - time[0]:.2f} h")
    print(f"Final substrate:  {substrate[-1]:.4f} g/L")
    print(f"Final penicillin: {penicillin[-1]:.4f} g/L")
    print(f"Final biomass:    {biomass[-1]:.4f} g/L")
    print(f"Final volume:     {volume[-1]:.2f} L")

    print("=" * 60)
    print("PASS: IndPenSim is running correctly inside TELESTO.")


if __name__ == "__main__":
    main()