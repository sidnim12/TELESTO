"""TELESTO wrapper around the external IndPenSim fermentation simulator."""

import sys
from collections.abc import Callable
from dataclasses import dataclass
from importlib import import_module
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

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

_EXTERNAL_PACKAGE_NAME = "_telesto_indpensim"


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

    def _load_runner(self) -> Callable[..., object]:
        """Load IndPenSim under a private namespace.

        The vendored project calls its package ``simulator``, which is too
        generic to add to the global import path safely and clashes with this
        module's filename. Loading it under a TELESTO-owned alias preserves its
        relative imports without exposing that ambiguous top-level name.
        """

        package_root = self.simulator_root / "simulator"
        package_init = package_root / "__init__.py"
        if not package_init.is_file():
            raise FileNotFoundError(
                f"IndPenSim package entry point not found at: {package_init}"
            )

        if _EXTERNAL_PACKAGE_NAME not in sys.modules:
            spec = spec_from_file_location(
                _EXTERNAL_PACKAGE_NAME,
                package_init,
                submodule_search_locations=[str(package_root)],
            )
            if spec is None or spec.loader is None:
                raise ImportError(f"Unable to load IndPenSim from: {package_init}")

            module = module_from_spec(spec)
            sys.modules[_EXTERNAL_PACKAGE_NAME] = module
            try:
                spec.loader.exec_module(module)
            except Exception:
                sys.modules.pop(_EXTERNAL_PACKAGE_NAME, None)
                raise

        runner_module = import_module(f"{_EXTERNAL_PACKAGE_NAME}.simulation_runner")
        return runner_module.indpensim_run

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
