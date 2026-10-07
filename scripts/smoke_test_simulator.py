"""Minimal TELESTO smoke test for the IndPenSim fermentation simulator."""

from biocontrolos.process.fermentation import FermentationSimulator


def main() -> None:
    print("TELESTO - Simulator Smoke Test")
    print("=" * 60)

    batch = FermentationSimulator().run_batch()

    print(f"Samples:          {batch.samples}")
    print(f"Batch duration:   {batch.duration_hours:.2f} h")
    print(f"Final substrate:  {batch.substrate[-1]:.4f} g/L")
    print(f"Final penicillin: {batch.penicillin[-1]:.4f} g/L")
    print(f"Final biomass:    {batch.biomass[-1]:.4f} g/L")
    print(f"Final volume:     {batch.volume[-1]:.2f} L")

    print("=" * 60)
    print("PASS: IndPenSim is running correctly inside TELESTO.")


if __name__ == "__main__":
    main()
