import numpy as np

from biocontrolos.process.fermentation.simulator import FermentationSimulator


def test_same_seed_produces_same_batch():
    batch_1 = FermentationSimulator(seed=42).run_batch()
    batch_2 = FermentationSimulator(seed=42).run_batch()

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