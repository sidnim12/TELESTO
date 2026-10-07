# CLAUDE.md — PenSimPy Simulator

## Project summary

Python translation of IndPenSim V2 (MATLAB). ODE-based fed-batch penicillin fermentation simulator. Entry point is `run.py` at the root; all simulation code lives in `simulator/`.

## Repository layout

```
pensimpy-simulator/
├── simulator/        # Python package — all simulation logic
├── run.py            # Run one batch, print row-by-row to stdout
├── requirements.txt  # numpy, scipy only
├── README.md
├── CLAUDE.md
├── .gitignore
└── .claudeignore
```

GitHub: https://github.com/ErnstHolger/pensimpy-simulator (default branch: `main`)

## Key facts

- **Package name**: `simulator` (directory `simulator/` with `__init__.py`)
- **Entry point**: `python run.py` from repo root
- **ODE state**: 33 variables, integrated with `scipy.solve_ivp` (Radau)
- **Parameters**: 105-element numpy array, some sampled stochastically per batch
- **Raman output**: each row includes `raman_spectrum=[...]` (2200-element intensity vector when `Raman_spec` flag ≥ 1)
- **Raman data**: reference spectra loaded from `../pensimpy-simulation/IndPenSim_V2.01/reference_Specra.txt` (sibling repo)
- **No external services**: no QuestDB, NATS, or Qdrant — output is stdout only

## Import pattern

`run.py` adds its own directory to `sys.path` so `simulator` resolves as a top-level package:

```python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from simulator.simulation_runner import indpensim_run
```

Do not move `run.py` into a subdirectory without updating this.

## Raman reference data path

`simulator/raman_sim.py` resolves the reference file relative to `__file__`:

```python
data_dir = Path(__file__).parent.parent / '..' / 'pensimpy-simulation' / 'IndPenSim_V2.01'
```

This assumes `pensimpy-simulation/` is a sibling of `pensimpy-simulator/` under `c:/repos/`.

## Dependencies

Only `numpy` and `scipy`. Do not re-add `questdb`, `nats-py`, or `qdrant-client`.

## Code style

- All simulation modules use relative imports (`from .channel import ...`)
- Batch configuration is passed as a dict of lists (one entry per batch)
- Channel objects have `.t` (time vector) and `.y` (value vector)
- `Batch` is a plain namespace; channels are assigned as attributes
