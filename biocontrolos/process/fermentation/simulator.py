"""TELESTO wrapper around the external IndPenSim fermentation simulator."""

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Callable

import numpy as np


# ---------------------------------------------------------------------------
# Default IndPenSim configuration
# ---------------------------------------------------------------------------

DEFAULT_BATCH_FLAGS = {
    "Batch_fault_order_reference": [0],
    "Control_strategy": [0],
    "Batch_length": [0],
    "Raman_spec": [0],
}


# ---------------------------------------------------------------------------
# TELESTO-owned batch result
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class FermentationBatch:
    """Core fermentation trajectories returned to TELESTO."""

    time: np.ndarray
    substrate: np.ndarray
    penicillin: np.ndarray
    biomass: np.ndarray
    volume: np.ndarray

    @property
    def samples(self) -> int:
        return len(self.time)

    @property
    def duration_hours(self) -> float:
        return float(self.time[-1] - self.time[0])


# ---------------------------------------------------------------------------
# Simulator wrapper
# ---------------------------------------------------------------------------

class FermentationSimulator:
    """Wrapper around the external IndPenSim simulator.

    TELESTO code should use this class instead of importing IndPenSim directly.
    """

    def __init__(
        self,
        simulator_root: Path | None = None,
        batch_flags: dict | None = None,
    ) -> None:

        project_root = Path(__file__).resolve().parents[3]

        self.simulator_root = (
            simulator_root
            if simulator_root is not None
            else project_root / "external" / "pensimpy-simulator"
        )

        self.batch_flags = (
            batch_flags.copy()
            if batch_flags is not None
            else DEFAULT_BATCH_FLAGS.copy()
        )

        if not self.simulator_root.exists():
            raise FileNotFoundError(
                f"IndPenSim simulator not found at: {self.simulator_root}"
            )

    def _load_runner(self) -> Callable:
        """Load the external IndPenSim runner."""

        simulator_path = str(self.simulator_root)

        if simulator_path not in sys.path:
            sys.path.insert(0, simulator_path)

        from simulator.simulation_runner import indpensim_run

        return indpensim_run

    def run_batch(self) -> FermentationBatch:
        """Run one fermentation batch and return TELESTO-owned trajectories."""

        indpensim_run = self._load_runner()

        result = indpensim_run(
            1,
            self.batch_flags,
        )

        batch = FermentationBatch(
            time=np.asarray(result.S.t, dtype=float),
            substrate=np.asarray(result.S.y, dtype=float),
            penicillin=np.asarray(result.P.y, dtype=float),
            biomass=np.asarray(result.X.y, dtype=float),
            volume=np.asarray(result.V.y, dtype=float),
        )

        self._validate_batch(batch)

        return batch

    @staticmethod
    def _validate_batch(batch: FermentationBatch) -> None:
        """Check that the simulator returned a usable batch."""

        if batch.samples == 0:
            raise ValueError("IndPenSim returned no simulation samples.")

        trajectories = {
            "substrate": batch.substrate,
            "penicillin": batch.penicillin,
            "biomass": batch.biomass,
            "volume": batch.volume,
        }

        for name, values in trajectories.items():

            if len(values) != batch.samples:
                raise ValueError(
                    f"{name} trajectory length does not match time trajectory."
                )

            if not np.all(np.isfinite(values)):
                raise ValueError(
                    f"{name} trajectory contains non-finite values."
                )

        if not np.all(np.isfinite(batch.time)):
            raise ValueError("Time trajectory contains non-finite values.")

        if batch.duration_hours <= 0:
            raise ValueError("Simulation did not advance in time.")