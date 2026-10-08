"""TELESTO ProcessAdapter implementation for fed-batch fermentation."""

from datetime import datetime, timezone
from typing import Mapping

from biocontrolos.core.rewards import RewardOutcome
from biocontrolos.core.state import Observation, ProcessState

from biocontrolos.process.base import (
    Action,
    ActionKind,
    ProcessAdapter,
    ProcessConstraint,
)

from .simulator import FermentationBatch, FermentationSimulator


class FermentationAdapter(ProcessAdapter):
    """Expose fed-batch fermentation through the TELESTO process boundary.

    The adapter translates IndPenSim trajectories into TELESTO's generic
    ProcessAdapter interface.

    Important limitation:
    the current simulator wrapper runs a complete baseline batch but does not
    yet support action-conditioned step-by-step simulation. Therefore,
    transition_model() only advances the baseline trajectory for WAIT actions
    and explicitly rejects control actions until that capability is added.
    """

    # Initial TELESTO control surface.
    ACTION_LIMITS = {
        "substrate_feed": (0.0, 120.0),  # L/h
        "aeration": (0.0, 100.0),        # L/h
        "agitation": (0.0, 300.0),       # RPM
    }

    OBSERVATION_VARIABLES = (
        "dissolved_oxygen",
        "pH",
        "temperature",
        "volume",
        "substrate",
    )

    STATE_VARIABLES = (
        "biomass",
        "substrate",
        "penicillin",
        "dissolved_oxygen",
        "pH",
        "temperature",
        "volume",
    )

    def __init__(
        self,
        simulator: FermentationSimulator | None = None,
        batch: FermentationBatch | None = None,
    ) -> None:
        self.simulator = simulator or FermentationSimulator()
        self.batch = batch or self.simulator.run_batch()

        if self.batch.samples == 0:
            raise ValueError("Fermentation batch contains no samples.")

        self._index = 0

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _timestamp(self) -> datetime:
        """Return a timezone-aware timestamp for the current simulation step."""
        return datetime.now(timezone.utc)

    def _current_values(self) -> dict[str, float]:
        """Return the current process state from the simulation trajectory."""
        i = self._index

        return {
            "biomass": float(self.batch.biomass[i]),
            "substrate": float(self.batch.substrate[i]),
            "penicillin": float(self.batch.penicillin[i]),
            "dissolved_oxygen": self._get_dissolved_oxygen(i),
            "pH": self._get_ph(i),
            "temperature": self._get_temperature(i),
            "volume": float(self.batch.volume[i]),
        }

    def _get_dissolved_oxygen(self, index: int) -> float:
        """Return dissolved oxygen.

        The current FermentationBatch intentionally exposes only the core
        trajectories. DO will be added to the TELESTO-owned batch result when
        the simulator wrapper expands its state surface.
        """
        if not hasattr(self.batch, "dissolved_oxygen"):
            raise NotImplementedError(
                "Dissolved oxygen is not yet exposed by FermentationBatch."
            )

        return float(self.batch.dissolved_oxygen[index])

    def _get_ph(self, index: int) -> float:
        """Return pH from the TELESTO-owned batch."""
        if not hasattr(self.batch, "pH"):
            raise NotImplementedError(
                "pH is not yet exposed by FermentationBatch."
            )

        return float(self.batch.pH[index])

    def _get_temperature(self, index: int) -> float:
        """Return temperature from the TELESTO-owned batch."""
        if not hasattr(self.batch, "temperature"):
            raise NotImplementedError(
                "Temperature is not yet exposed by FermentationBatch."
            )

        return float(self.batch.temperature[index])

    # ------------------------------------------------------------------
    # ProcessAdapter implementation
    # ------------------------------------------------------------------

    def get_state(self) -> ProcessState:
        """Return the current process state."""
        return ProcessState(
            values=self._current_values(),
            timestamp=self._timestamp(),
        )

    def get_observation(self) -> Observation:
        """Return the currently observable process variables."""
        values = self._current_values()

        observation = {
            name: values[name]
            for name in self.OBSERVATION_VARIABLES
        }

        return Observation(
            values=observation,
            timestamp=self._timestamp(),
            source="indpensim",
        )

    def available_actions(self) -> tuple[Action, ...]:
        """Return the initial TELESTO action space."""
        return (
            Action(
                kind=ActionKind.CONTROL,
                values={"substrate_feed": 0.0},
                rationale="Adjust substrate feed rate.",
            ),
            Action(
                kind=ActionKind.CONTROL,
                values={"aeration": 0.0},
                rationale="Adjust aeration rate.",
            ),
            Action(
                kind=ActionKind.CONTROL,
                values={"agitation": 0.0},
                rationale="Adjust agitation speed.",
            ),
            Action(
                kind=ActionKind.WAIT,
                values={},
                rationale="Allow the process to continue without a new intervention.",
            ),
        )

    def transition_model(self, action: Action) -> ProcessState:
        """Return the next process state under the currently supported model.

        WAIT advances along the baseline IndPenSim trajectory.

        Action-conditioned simulation is deliberately not implemented yet,
        because the current IndPenSim wrapper does not expose a step(action)
        interface. We must not pretend that a control action changes the
        simulated process when it currently does not.
        """
        if not self.validate_action(action):
            raise ValueError("Invalid fermentation action.")

        if action.kind != ActionKind.WAIT:
            raise NotImplementedError(
                "Action-conditioned transitions are not available yet. "
                "The fermentation simulator must first support "
                "step(action) semantics."
            )

        if self._index >= self.batch.samples - 1:
            return self.get_state()

        self._index += 1
        return self.get_state()

    def get_constraints(self) -> tuple[ProcessConstraint, ...]:
        """Return initial hard process constraints."""
        return (
            ProcessConstraint(
                name="dissolved_oxygen_minimum",
                description="Dissolved oxygen must remain above the process safety floor.",
                hard=True,
            ),
            ProcessConstraint(
                name="ph_operating_window",
                description="pH must remain within the defined fermentation operating window.",
                hard=True,
            ),
            ProcessConstraint(
                name="temperature_operating_window",
                description="Temperature must remain within the defined operating window.",
                hard=True,
            ),
            ProcessConstraint(
                name="actuator_limits",
                description="Control inputs must remain within defined actuator limits.",
                hard=True,
            ),
        )

    def get_quality_attributes(self) -> Mapping[str, float]:
        """Return process quality/product attributes at the current state."""
        values = self._current_values()

        return {
            "penicillin_concentration": values["penicillin"],
            "biomass_concentration": values["biomass"],
            "substrate_concentration": values["substrate"],
        }

    def calculate_reward(self) -> RewardOutcome:
        """Return objective values without inventing a scalar reward function."""
        values = self._current_values()

        return RewardOutcome(
            objectives={
                "penicillin_concentration": values["penicillin"],
                "biomass_concentration": values["biomass"],
            },
            scalar_reward=None,
        )

    def estimate_process_risk(self, action: Action) -> float:
        """Return a constraint-only risk proxy.

        A predictive process-risk model is not implemented at this stage.
        Therefore:
            0.0 = action passes structural/limit checks
            1.0 = action violates the current action interface
        """
        return 0.0 if self.validate_action(action) else 1.0

    def get_sensor_definitions(
        self,
    ) -> Mapping[str, Mapping[str, object]]:
        """Describe the initial process observation channels."""
        return {
            "dissolved_oxygen": {
                "unit": "%",
                "type": "continuous",
                "role": "online",
            },
            "pH": {
                "unit": "pH",
                "type": "continuous",
                "role": "online",
            },
            "temperature": {
                "unit": "K",
                "type": "continuous",
                "role": "online",
            },
            "volume": {
                "unit": "L",
                "type": "continuous",
                "role": "online",
            },
            "substrate": {
                "unit": "g/L",
                "type": "continuous",
                "role": "online_or_delayed",
            },
        }

    def get_actuator_definitions(
        self,
    ) -> Mapping[str, Mapping[str, object]]:
        """Describe the initial control actuators."""
        return {
            "substrate_feed": {
                "unit": "L/h",
                "type": "continuous",
                "min": 0.0,
                "max": 120.0,
            },
            "aeration": {
                "unit": "L/h",
                "type": "continuous",
                "min": 0.0,
                "max": 100.0,
            },
            "agitation": {
                "unit": "RPM",
                "type": "continuous",
                "min": 0.0,
                "max": 300.0,
            },
        }

    def get_measurement_costs(self) -> Mapping[str, float]:
        """Return relative measurement costs for the initial testbed."""
        return {
            "dissolved_oxygen": 0.0,
            "pH": 0.0,
            "temperature": 0.0,
            "volume": 0.0,
            "substrate": 1.0,
        }

    def get_experiment_options(
        self,
    ) -> tuple[Mapping[str, object], ...]:
        """Return experimental options.

        No intervention experiment is exposed yet because the current
        simulator wrapper does not support action-conditioned experiments.
        """
        return ()

    def validate_action(self, action: Action) -> bool:
        """Validate action type and actuator limits."""
        if action.kind == ActionKind.WAIT:
            return not action.values

        if action.kind != ActionKind.CONTROL:
            return False

        if len(action.values) != 1:
            return False

        actuator, value = next(iter(action.values.items()))

        if actuator not in self.ACTION_LIMITS:
            return False

        if not isinstance(value, (int, float)):
            return False

        lower, upper = self.ACTION_LIMITS[actuator]

        return lower <= float(value) <= upper