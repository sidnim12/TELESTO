"""Main simulation engine for IndPenSim.

Equivalent to indpensim.m - runs the ODE-based penicillin fermentation simulation.
"""

import numpy as np
from scipy.integrate import solve_ivp
from .batch import create_batch
from .ode_system import indpensim_ode
from .raman_sim import raman_sim
from .substrate_prediction import substrate_prediction


def indpensim(f_input, Xd, x0, h, T, solv, p, Ctrl_flags):
    """Run the IndPenSim simulation.

    Parameters:
        f_input: Controller function f_input(X, Xd, k, h, T, Ctrl_flags).
        Xd: Disturbance/industrial data.
        x0: Dict-like with initial conditions.
        h: Sampling time (hours).
        T: Experiment length (hours), must be multiple of h.
        solv: ODE solver selection (1=RK45, 2=BDF/Radau, 3=Radau).
        p: Parameter vector (from parameter_list).
        Ctrl_flags: Control flags.

    Returns:
        X: Batch structure with simulation results.
    """
    N = int(T / h)
    h_ode = h / 20.0
    t_vec = np.arange(0, T + h / 2, h)  # time vector

    # Create batch structure
    X = create_batch(h, T)

    # Convert pH to H+ concentration
    x0_pH = 10**(-x0['pH'])

    # Select ODE solver method
    solver_methods = {1: 'RK45', 2: 'Radau', 3: 'Radau'}
    method = solver_methods.get(solv, 'RK45')

    # Make a mutable copy of parameters
    p = np.array(p, dtype=float)

    # Main ODE loop
    for k in range(N):
        # Fill initial conditions at first step
        if k == 0:
            X.S.y[0] = x0['S']
            X.DO2.y[0] = x0['DO2']
            X.X.y[0] = x0['X']
            X.P.y[0] = x0['P']
            X.V.y[0] = x0['V']
            X.CO2outgas.y[0] = x0['CO2outgas']
            X.pH.y[0] = x0_pH
            X.T.y[0] = x0['T']

        # Get manipulated variables from controller
        u, X = f_input(X, Xd, k, h, T, Ctrl_flags)

        # Build initial conditions vector
        if k == 0:
            x00 = np.array([
                x0['S'], x0['DO2'], x0['O2'], x0['P'], x0['V'], x0['Wt'],
                x0_pH, x0['T'], 0, 4, x0['Culture_age'],
                x0['a0'], x0['a1'], x0['a3'], x0['a4'],
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                x0['CO2outgas'], 0, x0['PAA'], x0['NH3'], 0, 0
            ])
        else:
            x00 = np.array([
                X.S.y[k - 1], X.DO2.y[k - 1], X.O2.y[k - 1], X.P.y[k - 1],
                X.V.y[k - 1], X.Wt.y[k - 1], X.pH.y[k - 1], X.T.y[k - 1],
                X.Q.y[k - 1], X.Viscosity.y[k - 1], X.Culture_age.y[k - 1],
                X.a0.y[k - 1], X.a1.y[k - 1], X.a3.y[k - 1], X.a4.y[k - 1],
                X.n0.y[k - 1], X.n1.y[k - 1], X.n2.y[k - 1], X.n3.y[k - 1],
                X.n4.y[k - 1], X.n5.y[k - 1], X.n6.y[k - 1], X.n7.y[k - 1],
                X.n8.y[k - 1], X.n9.y[k - 1], X.nm.y[k - 1], X.phi0.y[k - 1],
                X.CO2outgas.y[k - 1], X.CO2_d.y[k - 1], X.PAA.y[k - 1],
                X.NH3.y[k - 1], 0, 0
            ])

        # Process disturbances
        distMuP = Xd.distMuP.y[k]
        distMuX = Xd.distMuX.y[k]
        distcs = Xd.distcs.y[k]
        distcoil = Xd.distcoil.y[k]
        distabc = Xd.distabc.y[k]
        distPAA = Xd.distPAA.y[k]
        distTcin = Xd.distTcin.y[k]
        distO_2in = Xd.distO_2in.y[k]

        u00 = np.array([
            Ctrl_flags.Inhib, u.Fs, u.Fg, u.RPM, u.Fc, u.Fh, u.Fb, u.Fa,
            h_ode, u.Fw, u.pressure, u.viscosity, u.Fremoved, u.Fpaa,
            u.Foil, u.NH3_shots, Ctrl_flags.Dis,
            distMuP, distMuX, distcs, distcoil, distabc, distPAA,
            distTcin, distO_2in, Ctrl_flags.Vis
        ])

        # Inhibition: reduce mu_p(max) after prolonged suboptimal conditions
        if Ctrl_flags.Inhib == 1 or Ctrl_flags.Inhib == 2:
            if k > 65:
                a1_diff = np.diff(X.mu_X_calc.y[k - 65:k])
                a2 = a1_diff < 0
                if np.sum(a2) >= 63:
                    p[1] = X.mu_X_calc.y[k - 1] * 5.0

        # Solve ODEs
        t_span = (t_vec[k], t_vec[k + 1])
        sol = solve_ivp(
            lambda t, y: indpensim_ode(t, y, u00, p),
            t_span, x00,
            method=method,
            max_step=h_ode,
            rtol=1e-6,
            atol=1e-9
        )

        y_sol = sol.y[:, -1]  # Take final values
        t_sol_end = sol.t[-1]

        # Enforce minimum values for numerical stability
        for n in range(31):
            if y_sol[n] <= 0:
                y_sol[n] = 0.001

        # Save manipulated variables
        X.Fg.t[k] = t_sol_end
        X.Fg.y[k] = u.Fg
        X.RPM.t[k] = t_sol_end
        X.RPM.y[k] = u.RPM
        X.Fpaa.t[k] = t_sol_end
        X.Fpaa.y[k] = u.Fpaa
        X.Fs.t[k] = t_sol_end
        X.Fs.y[k] = u.Fs
        X.Fa.t[k] = t_sol_end
        X.Fa.y[k] = u.Fa
        X.Fb.t[k] = t_sol_end
        X.Fb.y[k] = u.Fb
        X.Fc.t[k] = t_sol_end
        X.Fc.y[k] = u.Fc
        X.Foil.t[k] = t_sol_end
        X.Foil.y[k] = u.Foil
        X.Fh.t[k] = t_sol_end
        X.Fh.y[k] = u.Fh
        X.Fw.t[k] = t_sol_end
        X.Fw.y[k] = u.Fw
        X.pressure.t[k] = t_sol_end
        X.pressure.y[k] = u.pressure
        X.Fremoved.t[k] = t_sol_end
        X.Fremoved.y[k] = u.Fremoved

        # Save state variables
        X.S.y[k] = y_sol[0]
        X.S.t[k] = t_sol_end
        X.DO2.y[k] = y_sol[1]
        if X.DO2.y[k] < 2:
            X.DO2.y[k] = 1.0
        X.DO2.t[k] = t_sol_end
        X.O2.y[k] = y_sol[2]
        X.O2.t[k] = t_sol_end
        X.P.y[k] = y_sol[3]
        X.P.t[k] = t_sol_end
        X.V.y[k] = y_sol[4]
        X.V.t[k] = t_sol_end
        X.Wt.y[k] = y_sol[5]
        X.Wt.t[k] = t_sol_end
        X.pH.y[k] = y_sol[6]
        X.pH.t[k] = t_sol_end
        X.T.y[k] = y_sol[7]
        X.T.t[k] = t_sol_end
        X.Q.y[k] = y_sol[8]
        X.Q.t[k] = t_sol_end
        X.Viscosity.y[k] = y_sol[9]
        X.Viscosity.t[k] = t_sol_end
        X.Culture_age.y[k] = y_sol[10]
        X.Culture_age.t[k] = t_sol_end
        X.a0.y[k] = y_sol[11]
        X.a0.t[k] = t_sol_end
        X.a1.y[k] = y_sol[12]
        X.a1.t[k] = t_sol_end
        X.a3.y[k] = y_sol[13]
        X.a3.t[k] = t_sol_end
        X.a4.y[k] = y_sol[14]
        X.a4.t[k] = t_sol_end
        X.n0.y[k] = y_sol[15]
        X.n0.t[k] = t_sol_end
        X.n1.y[k] = y_sol[16]
        X.n1.t[k] = t_sol_end
        X.n2.y[k] = y_sol[17]
        X.n2.t[k] = t_sol_end
        X.n3.y[k] = y_sol[18]
        X.n3.t[k] = t_sol_end
        X.n4.y[k] = y_sol[19]
        X.n4.t[k] = t_sol_end
        X.n5.y[k] = y_sol[20]
        X.n5.t[k] = t_sol_end
        X.n6.y[k] = y_sol[21]
        X.n6.t[k] = t_sol_end
        X.n7.y[k] = y_sol[22]
        X.n7.t[k] = t_sol_end
        X.n8.y[k] = y_sol[23]
        X.n8.t[k] = t_sol_end
        X.n9.y[k] = y_sol[24]
        X.n9.t[k] = t_sol_end
        X.nm.y[k] = y_sol[25]
        X.nm.t[k] = t_sol_end
        X.phi0.y[k] = y_sol[26]
        X.phi0.t[k] = t_sol_end
        X.CO2outgas.y[k] = y_sol[27]
        X.CO2outgas.t[k] = t_sol_end
        X.CO2_d.t[k] = t_sol_end
        X.CO2_d.y[k] = y_sol[28]
        X.PAA.y[k] = y_sol[29]
        X.PAA.t[k] = t_sol_end
        X.NH3.y[k] = y_sol[30]
        X.NH3.t[k] = t_sol_end
        X.mu_P_calc.y[k] = y_sol[31]
        X.mu_P_calc.t[k] = t_sol_end
        X.mu_X_calc.y[k] = y_sol[32]
        X.mu_X_calc.t[k] = t_sol_end

        # Total biomass
        X.X.y[k] = X.a0.y[k] + X.a1.y[k] + X.a3.y[k] + X.a4.y[k]
        X.X.t[k] = t_sol_end

        X.Fault_ref.y[k] = u.Fault_ref
        X.Fault_ref.t[k] = t_sol_end
        X.Control_ref.y[k] = Ctrl_flags.PRBS
        X.Control_ref.t[k] = Ctrl_flags.Batch_Num
        X.PAT_ref.y[k] = Ctrl_flags.Raman_spec
        X.PAT_ref.t[k] = Ctrl_flags.Batch_Num
        X.Batch_ref.t[k] = Ctrl_flags.Batch_Num
        X.Batch_ref.y[k] = Ctrl_flags.Batch_Num

        # OUR / CER calculations
        O2_in = 0.204
        X.OUR.y[k] = ((32 * X.Fg.y[k] / 22.4) *
                       (O2_in - X.O2.y[k] * (0.7902 / (1 - X.O2.y[k] - X.CO2outgas.y[k] / 100))))
        X.OUR.t[k] = t_sol_end

        X.CER.y[k] = ((44 * X.Fg.y[k] / 22.4) *
                       (0.65 * X.CO2outgas.y[k] / 100) *
                       (0.7902 / (1 - O2_in - X.CO2outgas.y[k] / 100) - 0.0330))
        X.CER.t[k] = t_sol_end

        # Raman spectra
        if k > 10:
            if Ctrl_flags.Raman_spec == 1:
                X = raman_sim(k, X, h, T)
            elif Ctrl_flags.Raman_spec == 2:
                X = raman_sim(k, X, h, T)
                X = substrate_prediction(k, X, h, T)

        # Off-line measurements
        off_line_m = Ctrl_flags.Off_line_m
        delay = Ctrl_flags.Off_line_delay
        if (t_sol_end % off_line_m == 0 or t_sol_end == 1 or t_sol_end == T) and k >= delay:
            X.NH3_offline.y[k] = X.NH3.y[k - delay]
            X.NH3_offline.t[k] = X.NH3.t[k - delay]
            X.Viscosity_offline.y[k] = X.Viscosity.y[k - delay]
            X.Viscosity_offline.t[k] = X.Viscosity.t[k - delay]
            X.PAA_offline.y[k] = X.PAA.y[k - delay]
            X.PAA_offline.t[k] = X.PAA.t[k - delay]
            X.P_offline.y[k] = X.P.y[k - delay]
            X.P_offline.t[k] = X.P.t[k - delay]
            X.X_offline.y[k] = X.X.y[k - delay]
            X.X_offline.t[k] = X.X.t[k - delay]
        else:
            X.NH3_offline.y[k] = np.nan
            X.NH3_offline.t[k] = np.nan
            X.Viscosity_offline.y[k] = np.nan
            X.Viscosity_offline.t[k] = np.nan
            X.PAA_offline.y[k] = np.nan
            X.PAA_offline.t[k] = np.nan
            X.P_offline.y[k] = np.nan
            X.P_offline.t[k] = np.nan
            X.X_offline.y[k] = np.nan
            X.X_offline.t[k] = np.nan

    # Unit conversions
    X.pH.y = -np.log10(X.pH.y)       # Convert H+ concentration to pH
    X.Q.y = X.Q.y / 1000.0           # Convert heat to kcal

    return X
