"""Run one complete TELESTO fermentation batch."""

from biocontrolos.process.fermentation.simulator import FermentationSimulator


def main() -> None:
    print("TELESTO - Fermentation Batch")
    print("=" * 50)

    simulator = FermentationSimulator(seed=42)
    batch = simulator.run_batch()

    print(f"Samples:           {batch.samples}")
    print(f"Duration:          {batch.duration_hours:.2f} h")
    print(f"Final biomass:     {batch.biomass[-1]:.4f} g/L")
    print(f"Final substrate:   {batch.substrate[-1]:.4f} g/L")
    print(f"Final penicillin:  {batch.penicillin[-1]:.4f} g/L")
    print(f"Final DO:          {batch.dissolved_oxygen[-1]:.4f}")
    print(f"Final pH:          {batch.pH[-1]:.4f}")
    print(f"Final temperature: {batch.temperature[-1]:.4f} K")
    print(f"Final volume:      {batch.volume[-1]:.2f} L")

    print("=" * 50)
    print("PASS: TELESTO fermentation batch completed.")


if __name__ == "__main__":
    main()