import numpy as np
import pytest

from biocontrolos.process.fermentation.simulator import (
    FermentationBatch,
    FermentationSimulator,
)


@pytest.fixture(scope="module")
def seeded_batches() -> tuple[FermentationBatch, FermentationBatch, FermentationBatch]:
    batch_1 = FermentationSimulator(seed=42).run_batch()
    batch_2 = FermentationSimulator(seed=42).run_batch()
    batch_3 = FermentationSimulator(seed=43).run_batch()
    return batch_1, batch_2, batch_3


def _major_trajectories(batch: FermentationBatch) -> tuple[np.ndarray, ...]:
    return (
        batch.biomass,
        batch.substrate,
        batch.penicillin,
        batch.dissolved_oxygen,
        batch.pH,
        batch.temperature,
        batch.volume,
    )


def test_baseline_batch_integrity(seeded_batches):
    batch, _, _ = seeded_batches
    trajectories = _major_trajectories(batch)

    assert batch.samples > 0
    assert batch.duration_hours > 0
    assert np.all(np.isfinite(batch.time))
    assert np.all(np.diff(batch.time) > 0)
    assert all(len(values) == batch.samples for values in trajectories)
    assert all(np.all(np.isfinite(values)) for values in trajectories)


def test_same_seed_produces_same_batch(seeded_batches):
    batch_1, batch_2, _ = seeded_batches

    np.testing.assert_array_equal(batch_1.time, batch_2.time)
    np.testing.assert_array_equal(batch_1.substrate, batch_2.substrate)
    np.testing.assert_array_equal(batch_1.penicillin, batch_2.penicillin)
    np.testing.assert_array_equal(batch_1.biomass, batch_2.biomass)
    np.testing.assert_array_equal(
        batch_1.dissolved_oxygen,
        batch_2.dissolved_oxygen,
    )
    np.testing.assert_array_equal(batch_1.pH, batch_2.pH)
    np.testing.assert_array_equal(batch_1.temperature, batch_2.temperature)
    np.testing.assert_array_equal(batch_1.volume, batch_2.volume)


def test_different_seed_changes_at_least_one_trajectory(seeded_batches):
    batch_1, _, batch_3 = seeded_batches

    assert any(
        not np.array_equal(first, third)
        for first, third in zip(
            _major_trajectories(batch_1),
            _major_trajectories(batch_3),
            strict=True,
        )
    )
