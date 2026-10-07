# PenSimPy Simulator

A Python translation of **IndPenSim V2** — an industrial penicillin fermentation batch simulator. Simulates ODE-based bioreactor dynamics and prints results row by row.

> Source: [github.com/ErnstHolger/pensimpy-simulator](https://github.com/ErnstHolger/pensimpy-simulator)

## Overview

IndPenSim models a fed-batch penicillin fermentation process. It generates realistic batch data including substrate feeds, dissolved oxygen, pH, temperature, Raman spectra, and penicillin yield — supporting both normal and fault conditions.

## Project Structure

```
pensimpy-simulator/
├── simulator/                 # Simulation package
│   ├── __init__.py
│   ├── batch.py              # Batch data structure
│   ├── batch_records.py      # Batch record generation and CSV export
│   ├── channel.py            # Channel/signal definitions
│   ├── controller.py         # Feed controllers and control flags
│   ├── indpensim.py          # Core ODE simulation engine
│   ├── main.py               # Multi-batch production run entry point
│   ├── ode_system.py         # 33-state ODE system definition
│   ├── parameters.py         # 105 model parameters
│   ├── pid_controller.py     # PID controller
│   ├── raman_sim.py          # Raman spectrum simulation
│   ├── simulation_runner.py  # High-level single-batch runner
│   └── substrate_prediction.py
├── run.py                    # Entry point — run a batch, print row by row
├── requirements.txt
├── .gitignore
└── .claudeignore
```

## Architecture

```
run.py
  └── simulation_runner.indpensim_run()
        ├── parameters.parameter_list()       # Build 105-element parameter vector
        ├── batch.create_batch()              # Allocate Channel arrays for T/h steps
        ├── controller.fctrl_indpensim()      # Compute manipulated variable inputs
        │     └── pid_controller.pid_simple3()
        ├── indpensim.indpensim()             # Step through ODE loop
        │     ├── ode_system.indpensim_ode()  # 33-state derivative function (scipy solve_ivp)
        │     ├── raman_sim.raman_sim()       # Simulate Raman spectrum at each step
        │     └── substrate_prediction.substrate_prediction()
        └── batch_records.generate_batch_records()  # Post-process to summary CSV
```

### Key concepts

| Concept | Description |
|---|---|
| **Channel** | Time-series container (`t`, `y` arrays) for one process variable |
| **Batch** | Collection of ~60 Channels covering the full fermentation run |
| **ODE state** | 33-element vector: biomass, substrate, penicillin, dissolved O₂, CO₂, pH, volume, temperature, viscosity, and feed flows |
| **Parameters** | 105-element numpy array encoding kinetic, mass transfer, and process constants |
| **ControlFlags** | Toggles for substrate-based control, PRBS, fixed batch length, fault injection |
| **Raman spectrum** | 2200-point intensity vector per sample, loaded from reference spectra and perturbed |

### Data flow

1. `parameter_list()` samples stochastic parameters (µ_p, µ_x, kLa) from normal distributions
2. `indpensim_run()` sets initial conditions and integrates the ODE over the batch horizon
3. At each time step `k`, `fctrl_indpensim()` computes feed rates; `indpensim_ode()` computes derivatives
4. `raman_sim()` appends a synthetic Raman spectrum to the batch at each step
5. After simulation, `generate_batch_records()` flattens channels to a tidy DataFrame / CSV

## Requirements

- Python 3.10+
- numpy
- scipy

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Run a batch and print row by row

```bash
python run.py
```

Output:

```
IndPenSim - Batch Simulation
============================================================
Simulation completed in 4.31s  |  530 samples
Batch length:     265.0 h
...
Row-by-row data:

  t=   0.00h  substrate_conc=15g/L  penicillin_conc=0g/L  biomass_conc=0.1g/L  ...  raman_spectrum=[...]
  t=   0.50h  ...
```

Each row also appends `raman_spectrum=[...]` — the 2200-element intensity
vector for that timestep when `Raman_spec` is enabled.

## Data dependency

The Raman simulator loads reference spectra from a sibling repository:

```
c:/repos/
├── pensimpy-simulator/             # this repo
└── pensimpy-simulation/
    └── IndPenSim_V2.01/
        └── reference_Specra.txt    # required by simulator/raman_sim.py
```

If the sibling repo is missing, runs with `Raman_spec=0` to skip Raman simulation.

### Generate multiple batches programmatically

```python
from simulator.main import run_production

raw_data, records = run_production()
```

## Batch configuration

| Flag | Values | Description |
|---|---|---|
| `Batch_fault_order_reference` | `0` = normal, `1`+ = fault code | Inject process faults |
| `Control_strategy` | `0` = recipe, `1` = closed-loop | Feed control mode |
| `Batch_length` | `0` = normal, `1` = extended | Batch duration |
| `Raman_spec` | `0` = off, `1` = standard, `2` = high-res | Raman spectrum mode |
