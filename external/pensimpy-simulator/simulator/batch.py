"""Batch data structure for IndPenSim.

Equivalent to createBatch.m - creates a batch structure with all channels.
"""

import numpy as np
from .channel import create_channel


class Batch:
    """Container for all simulation channels (state and manipulated variables)."""
    pass


def create_batch(h, T):
    """Create a batch structure with a given time duration.

    Parameters:
        h: Sample time (hours).
        T: Batch duration (hours).

    Returns:
        Batch object with all channels initialized to zeros.
    """
    N = int(T / h)
    t = np.zeros(N)
    y = np.zeros(N)

    X = Batch()

    # Manipulated variables
    X.Fg = create_channel('Aeration rate', 'L/h', 'h', t, y)
    X.RPM = create_channel('Agitator RPM', 'RPM', 'h', t, y)
    X.Fs = create_channel('Sugar feed rate', 'L/h', 'h', t, y)
    X.sc = create_channel('Substrate feed concentration', 'g/L', 'h', t, y)
    X.abc = create_channel('Acid/base feed concentration', 'moles', 'h', t, y)
    X.Fa = create_channel('Acid flow rate', 'L/h', 'h', t, y)
    X.Fb = create_channel('Base flow rate', 'L/h', 'h', t, y)
    X.Fc = create_channel('Heating/cooling water flow rate', 'L/h', 'h', t, y)
    X.Fh = create_channel('Heating water flow rate', 'L/h', 'h', t, y)

    # Additional manipulated variables
    X.Fw = create_channel('Water for injection/dilution', 'L/h', 'h', t, y)
    X.pressure = create_channel('Air head pressure', 'bar', 'h', t, y)
    X.Fremoved = create_channel('Dumped broth flow', 'L/h', 'h', t, y)

    # State variables
    X.S = create_channel('Substrate concentration', 'g/L', 'h', t, y)
    X.DO2 = create_channel('Dissolved oxygen concentration', 'mg/L', 'h', t, y)
    X.X = create_channel('Biomass concentration', 'g/L', 'h', t, y)
    X.P = create_channel('Penicillin concentration', 'g/L', 'h', t, y)
    X.V = create_channel('Vessel Volume', 'L', 'h', t, y)
    X.Wt = create_channel('Vessel Weight', 'Kg', 'h', t, y)
    X.pH = create_channel('pH', 'pH', 'h', t, y)
    X.T = create_channel('Temperature', 'K', 'h', t, y)
    X.Q = create_channel('Generated heat', 'kJ', 'h', t, y)

    # Extended state variables
    X.a0 = create_channel('type a0 biomass concentration', 'g/L', 'h', t, y)
    X.a1 = create_channel('type a1 biomass concentration', 'g/L', 'h', t, y)
    X.a3 = create_channel('type a3 biomass concentration', 'g/L', 'h', t, y)
    X.a4 = create_channel('type a4 biomass concentration', 'g/L', 'h', t, y)
    X.n0 = create_channel('state n0', '-', 'h', t, y)
    X.n1 = create_channel('state n1', '-', 'h', t, y)
    X.n2 = create_channel('state n2', '-', 'h', t, y)
    X.n3 = create_channel('state n3', '-', 'h', t, y)
    X.n4 = create_channel('state n4', '-', 'h', t, y)
    X.n5 = create_channel('state n5', '-', 'h', t, y)
    X.n6 = create_channel('state n6', '-', 'h', t, y)
    X.n7 = create_channel('state n7', '-', 'h', t, y)
    X.n8 = create_channel('state n8', '-', 'h', t, y)
    X.n9 = create_channel('state n9', '-', 'h', t, y)
    X.nm = create_channel('state nm', '-', 'h', t, y)
    X.phi0 = create_channel('state phi0', '-', 'h', t, y)
    X.CO2outgas = create_channel('carbon dioxide percent in off-gas', '%', 'h', t, y)
    X.Culture_age = create_channel('Cell culture age', 'h', 'h', t, y)
    X.Fpaa = create_channel('PAA flow', 'PAA flow (L/h)', 'h', t, y)
    X.PAA = create_channel('PAA concentration', 'PAA (g L^{-1})', 'h', t, y)
    X.PAA_offline = create_channel('PAA concentration offline', 'PAA (g L^{-1})', 'h', t, y)
    X.Foil = create_channel('Oil flow', 'L/hr', 'h', t, y)
    X.NH3 = create_channel('NH_3 concentration', 'NH3 (g L^{-1})', 'h', t, y)
    X.NH3_offline = create_channel('NH_3 concentration off-line', 'NH3 (g L^{-1})', 'h', t, y)
    X.OUR = create_channel('Oxygen Uptake Rate', '(g min^{-1})', 'h', t, y)
    X.O2 = create_channel('Oxygen in percent in off-gas', 'O2 (%)', 'h', t, y)
    X.mup = create_channel('Specific growth rate of Penicillin', 'mu_P (h^{-1})', 'h', t, y)
    X.mux = create_channel('Specific growth rate of Biomass', 'mu_X (h^{-1})', 'h', t, y)
    X.P_offline = create_channel('Offline Penicillin concentration', 'P(g L^{-1})', 'h', t, y)
    X.X_CER = create_channel('Biomass concentration from CER', 'g min^{-1}', 'h', t, y)
    X.X_offline = create_channel('Offline Biomass concentration', 'X(g L^{-1})', 'h', t, y)
    X.CER = create_channel('Carbon evolution rate', 'g/h', 'h', t, y)
    X.mu_X_calc = create_channel('Biomass specific growth rate', 'hr^{-1}', 'h', t, y)
    X.mu_P_calc = create_channel('Penicillin specific growth rate', 'hr^{-1}', 'h', t, y)
    X.F_discharge_cal = create_channel('Discharge rate', 'L hr^{-1}', 'h', t, y)
    X.NH3_shots = create_channel('Ammonia shots', 'kgs', 'h', t, y)
    X.CO2_d = create_channel('Dissolved CO_2', '(mg L^{-1})', 'h', t, y)
    X.Viscosity = create_channel('Viscosity', 'centPoise', 'h', t, y)
    X.Viscosity_offline = create_channel('Viscosity', 'centPoise', 'h', t, y)
    X.Fault_ref = create_channel('Fault reference', 'Fault ref', 'h', t, y)
    X.Control_ref = create_channel('0 - Recipe driven 1 - Operator controlled',
                                   'Control ref', 'Batch number', t, y)
    X.PAT_ref = create_channel('1- No Raman spec, 1-Raman spec recorded,2-PAT control',
                               'PAT ref', 'Batch number', t, y)
    X.Batch_ref = create_channel('Batch reference', 'Batch ref', 'Batch ref', t, y)

    # PRBS noise tracking
    X.PRBS_noise_addition = np.zeros(N)

    return X
