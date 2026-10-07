"""Fed-batch microbial fermentation process integration for TELESTO.

This package contains the TELESTO-owned interface around the external
IndPenSim/PenSimPy fermentation simulator.

The external simulator must not be accessed directly by other TELESTO
components. Future control, RL, state estimation, and decision-making
modules should interact with the fermentation process through this package.
"""

from .simulator import DEFAULT_BATCH_FLAGS, FermentationBatch, FermentationSimulator

__all__ = ["DEFAULT_BATCH_FLAGS", "FermentationBatch", "FermentationSimulator"]
