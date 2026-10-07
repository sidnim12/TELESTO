"""Simulation runner for IndPenSim.

Equivalent to indpensim_run.m - wrapper file for running a single batch simulation.
"""

import numpy as np
from scipy.signal import lfilter

from .channel import create_channel
from .batch import Batch
from .parameters import parameter_list
from .controller import ControlFlags, fctrl_indpensim
from .indpensim import indpensim


def indpensim_run(Batch_no, Batch_run_flags):
    """Run a single batch simulation.

    Parameters:
        Batch_no: Batch number (1-based).
        Batch_run_flags: Dict with keys:
            - Batch_fault_order_reference: list of fault codes per batch
            - Control_strategy: list of control strategy flags per batch
            - Batch_length: list of batch length flags per batch
            - Raman_spec: list of Raman spec flags per batch

    Returns:
        Xref: Batch result structure with simulation data and statistics.
    """
    # Set up simulation flags
    Ctrl_flags = ControlFlags()
    Ctrl_flags.SBC = 0
    Ctrl_flags.PRBS = Batch_run_flags['Control_strategy'][Batch_no - 1]
    Ctrl_flags.Fixed_Batch_length = Batch_run_flags['Batch_length'][Batch_no - 1]
    Ctrl_flags.IC = 0
    Ctrl_flags.Inhib = 2
    Ctrl_flags.Dis = 1
    Ctrl_flags.Faults = Batch_run_flags['Batch_fault_order_reference'][Batch_no - 1]
    Ctrl_flags.Vis = 0
    Ctrl_flags.Raman_spec = Batch_run_flags['Raman_spec'][Batch_no - 1]
    Ctrl_flags.Batch_Num = Batch_no
    Ctrl_flags.Off_line_m = 12
    Ctrl_flags.Off_line_delay = 4
    Ctrl_flags.plots = 1
    Ctrl_flags.T_sp = 298.0
    Ctrl_flags.pH_sp = 6.5

    # Standard batch simulation with randomized initial conditions
    Ctrl_flags.SBC = 0
    Ctrl_flags.Vis = 0

    Optimum_Batch_length = 230
    if Ctrl_flags.Fixed_Batch_length == 1:
        np.random.seed(None)  # Random seed
        Batch_length_variation = 25 * np.random.randn()
        T = round(Optimum_Batch_length + Batch_length_variation)
    else:
        T = Optimum_Batch_length

    # Randomize each batch
    Random_seed_ref = int(np.ceil(np.random.rand() * 1000))
    Seed_ref = 31 + Random_seed_ref
    Rand_ref = 1

    # Initial conditions with randomization
    rng = np.random.RandomState(Seed_ref + Batch_no + Rand_ref)
    Rand_ref += 1
    initial_conds = 0.5 + 0.05 * rng.randn()

    rng = np.random.RandomState(Seed_ref + Batch_no + Rand_ref)
    Rand_ref += 1
    x0_mux = 0.41 + 0.025 * rng.randn()

    rng = np.random.RandomState(Seed_ref + Batch_no + Rand_ref)
    Rand_ref += 1
    x0_mup = 0.041 + 0.0025 * rng.randn()

    h = 0.2  # 12-minute sampling rate

    x0 = {}
    rng = np.random.RandomState(Seed_ref + Batch_no + Rand_ref)
    Rand_ref += 1
    x0['S'] = 1 + 0.1 * rng.randn()

    rng = np.random.RandomState(Seed_ref + Batch_no + Rand_ref)
    Rand_ref += 1
    x0['DO2'] = 15 + 0.5 * rng.randn()

    rng = np.random.RandomState(Seed_ref + Batch_no + Rand_ref)
    Rand_ref += 1
    x0['X'] = initial_conds + 0.1 * rng.randn()

    x0['P'] = 0.0

    rng = np.random.RandomState(Seed_ref + Batch_no + Rand_ref)
    Rand_ref += 1
    x0['V'] = 5.8e4 + 500 * rng.randn()

    rng = np.random.RandomState(Seed_ref + Batch_no + Rand_ref)
    Rand_ref += 1
    x0['Wt'] = 6.2e4 + 500 * rng.randn()

    rng = np.random.RandomState(Seed_ref + Batch_no + Rand_ref)
    Rand_ref += 1
    x0['CO2outgas'] = 0.038 + 0.001 * rng.randn()

    rng = np.random.RandomState(Seed_ref + Batch_no + Rand_ref)
    Rand_ref += 1
    x0['O2'] = 0.20 + 0.05 * rng.randn()

    rng = np.random.RandomState(Seed_ref + Batch_no + Rand_ref)
    Rand_ref += 1
    x0['pH'] = 6.5 + 0.1 * rng.randn()

    rng = np.random.RandomState(Seed_ref + Batch_no + Rand_ref)
    Rand_ref += 1
    x0['T'] = 297 + 0.5 * rng.randn()

    x0['a0'] = initial_conds * (1.0 / 3.0)
    x0['a1'] = initial_conds * (2.0 / 3.0)
    x0['a3'] = 0.0
    x0['a4'] = 0.0
    x0['Culture_age'] = 0.0

    rng = np.random.RandomState(Seed_ref + Batch_no + Rand_ref)
    Rand_ref += 1
    x0['PAA'] = 1400 + 50 * rng.randn()

    rng = np.random.RandomState(Seed_ref + Batch_no + Rand_ref)
    Rand_ref += 1
    x0['NH3'] = 1700 + 50 * rng.randn()

    rng = np.random.RandomState(Seed_ref + Batch_no + Rand_ref)
    Rand_ref += 1
    alpha_kla = 85 + 10 * rng.randn()

    rng = np.random.RandomState(Seed_ref + Batch_no + Rand_ref)
    Rand_ref += 1
    PAA_c = 530000 + 20000 * rng.randn()

    rng = np.random.RandomState(Seed_ref + Batch_no + Rand_ref)
    N_conc_paa = 2 * 75000 + 2000 * rng.randn()

    Batch_time = np.arange(0, T + h / 2, h)
    N_samples = len(Batch_time)

    # Create process disturbances using low-pass filter
    rng_dist = np.random.RandomState(Random_seed_ref + Batch_no)

    b1 = np.array([1 - 0.995])
    a1 = np.array([1, -0.995])

    # Penicillin specific growth rate disturbance
    v = rng_dist.randn(N_samples)
    distMuP = lfilter(b1, a1, 0.03 * v)

    # Biomass specific growth rate disturbance
    v = rng_dist.randn(N_samples)
    distMuX = lfilter(b1, a1, 0.25 * v)

    # Substrate inlet concentration disturbance
    v = rng_dist.randn(N_samples)
    distcs = lfilter(b1, a1, 5 * 300 * v)

    # Oil inlet concentration disturbance
    v = rng_dist.randn(N_samples)
    distcoil = lfilter(b1, a1, 300 * v)

    # Acid/Base concentration disturbance
    v = rng_dist.randn(N_samples)
    distabc = lfilter(b1, a1, 0.2 * v)

    # PAA concentration disturbance
    v = rng_dist.randn(N_samples)
    distPAA = lfilter(b1, a1, 300000 * v)

    # Coolant temperature disturbance
    v = rng_dist.randn(N_samples)
    distTcin = lfilter(b1, a1, 100 * v)

    # Oxygen inlet concentration disturbance
    v = rng_dist.randn(N_samples)
    distO_2in = lfilter(b1, a1, 0.02 * v)

    # Create disturbance structure
    Xinterp = Batch()
    Xinterp.distMuP = create_channel('Penicillin specific growth rate disturbance',
                                      'g/Lh', 'h', Batch_time, distMuP)
    Xinterp.distMuX = create_channel('Biomass specific growth rate disturbance',
                                      'hr^{-1}', 'h', Batch_time, distMuX)
    Xinterp.distcs = create_channel('Substrate concentration disturbance',
                                     'g L^{-1}', 'h', Batch_time, distcs)
    Xinterp.distcoil = create_channel('Oil concentration disturbance',
                                       'g L^{-1}', 'h', Batch_time, distcoil)
    Xinterp.distabc = create_channel('Acid/Base concentration disturbance',
                                      'g L^{-1}', 'h', Batch_time, distabc)
    Xinterp.distPAA = create_channel('Phenylacetic acid concentration disturbance',
                                      'g L^{-1}', 'h', Batch_time, distPAA)
    Xinterp.distTcin = create_channel('Coolant inlet temperature disturbance',
                                       'K', 'h', Batch_time, distTcin)
    Xinterp.distO_2in = create_channel('Oxygen inlet concentration',
                                        '%', 'h', Batch_time, distO_2in)
    Xinterp.NH3_shots = create_channel('Ammonia shots', 'kgs', 'h',
                                        Batch_time, np.zeros(N_samples))

    # Import parameter list
    par = parameter_list(x0_mup, x0_mux, alpha_kla, N_conc_paa, PAA_c)

    # Run simulation
    print('Running IndPenSim...')
    Xref = indpensim(fctrl_indpensim, Xinterp, x0, h, T, 2, par, Ctrl_flags)

    # Calculate statistics
    class Stats:
        pass
    Xref.Stats = Stats()
    Xref.Stats.Penicllin_harvested_during_batch = np.sum(Xref.Fremoved.y * Xref.P.y) * h
    Xref.Stats.Penicllin_harvested_end_of_batch = Xref.V.y[-1] * Xref.P.y[-1]
    Xref.Stats.Penicllin_yield_total = (Xref.V.y[-1] * Xref.P.y[-1] -
                                         Xref.Stats.Penicllin_harvested_during_batch)
    Xref.Stats.Batch_length = Xref.V.t[-1]

    print(f'Penicillin harvested during the batch: '
          f'{round(Xref.Stats.Penicllin_harvested_during_batch / 1000)} Kg')
    print(f'Final Penicillin yield at harvest: '
          f'{round(Xref.Stats.Penicllin_harvested_end_of_batch / 1000)} Kg')
    print(f'Total penicillin: '
          f'{round(Xref.Stats.Penicllin_yield_total / 1000)} Kg')

    return Xref
