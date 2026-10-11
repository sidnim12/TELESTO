
"""Plot the trajectory of one complete TELESTO fermentation batch."""

from pathlib import Path

import matplotlib.pyplot as plt

from biocontrolos.process.fermentation.simulator import FermentationSimulator


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = (
    PROJECT_ROOT / "outputs" / "figures" / "fermentation_trajectory_seed_42.png"
)


def main() -> None:
    print("TELESTO - Fermentation Trajectory")
    print("=" * 50)

    simulator = FermentationSimulator(seed=42)
    batch = simulator.run_batch()

    time_hours = batch.time - batch.time[0]

    trajectories = [
        ("Biomass", batch.biomass, "Biomass (g/L)"),
        ("Substrate", batch.substrate, "Substrate (g/L)"),
        ("Penicillin", batch.penicillin, "Penicillin (g/L)"),
        ("Dissolved Oxygen", batch.dissolved_oxygen, "Dissolved oxygen"),
        ("pH", batch.pH, "pH"),
        ("Temperature", batch.temperature, "Temperature (K)"),
        ("Volume", batch.volume, "Volume (L)"),
    ]

    if len(time_hours) == 0:
        raise ValueError("The simulator returned an empty time trajectory.")

    for name, values, _ in trajectories:
        if len(values) != len(time_hours):
            raise ValueError(
                f"{name} has {len(values)} values, "
                f"but time has {len(time_hours)} samples."
            )

    fig, axes = plt.subplots(
        nrows=4,
        ncols=2,
        figsize=(14, 15),
        sharex=True,
    )
    flat_axes = axes.flatten()

    for ax, (title, values, ylabel) in zip(
        flat_axes, trajectories, strict=False
    ):
        ax.plot(time_hours, values, linewidth=1.6)
        ax.set_title(title)
        ax.set_ylabel(ylabel)
        ax.set_xlabel("Time (h)")
        ax.grid(True, alpha=0.3)

    # Seven plots use seven panels; hide the unused eighth panel.
    flat_axes[-1].set_visible(False)

    fig.suptitle(
        "TELESTO Baseline Fermentation Trajectory (seed=42)",
        fontsize=15,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.97))

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT_PATH, dpi=160, bbox_inches="tight")
    plt.close(fig)

    print(f"Samples:          {batch.samples}")
    print(f"Duration:         {batch.duration_hours:.2f} h")
    print(f"Figure saved to:  {OUTPUT_PATH.relative_to(PROJECT_ROOT)}")
    print("=" * 50)
    print("PASS: Fermentation trajectory plotted.")


if __name__ == "__main__":
    main()
