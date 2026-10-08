from biocontrolos.process.base import Action, ActionKind
from biocontrolos.process.fermentation.adapter import FermentationAdapter


def test_adapter_returns_state():
    adapter = FermentationAdapter()

    state = adapter.get_state()

    expected_variables = {
        "biomass",
        "substrate",
        "penicillin",
        "dissolved_oxygen",
        "pH",
        "temperature",
        "volume",
    }

    assert set(state.values.keys()) == expected_variables


def test_adapter_returns_observation():
    adapter = FermentationAdapter()

    observation = adapter.get_observation()

    expected_variables = {
        "dissolved_oxygen",
        "pH",
        "temperature",
        "volume",
        "substrate",
    }

    assert set(observation.values.keys()) == expected_variables
    assert observation.source == "indpensim"


def test_wait_action_advances_process():
    adapter = FermentationAdapter()

    before = adapter.get_state()

    wait_action = Action(
        kind=ActionKind.WAIT,
    )

    after = adapter.transition_model(wait_action)

    assert after.values != before.values


def test_valid_control_action():
    adapter = FermentationAdapter()

    action = Action(
        kind=ActionKind.CONTROL,
        values={"substrate_feed": 50.0},
    )

    assert adapter.validate_action(action)


def test_invalid_control_action():
    adapter = FermentationAdapter()

    action = Action(
        kind=ActionKind.CONTROL,
        values={"substrate_feed": 500.0},
    )

    assert not adapter.validate_action(action)


def test_quality_attributes_exist():
    adapter = FermentationAdapter()

    quality = adapter.get_quality_attributes()

    assert "penicillin_concentration" in quality
    assert "biomass_concentration" in quality
    assert "substrate_concentration" in quality