"""Controller for IndPenSim.

Equivalent to fctrl_indpensim.m - provides manipulated variables to control the simulation.
"""

import numpy as np
from .pid_controller import pid_simple3


class ControlFlags:
    """Container for simulation control flags."""

    def __init__(self):
        self.SBC = 0
        self.PRBS = 0
        self.Fixed_Batch_length = 0
        self.IC = 0
        self.Inhib = 2
        self.Dis = 1
        self.Faults = 0
        self.Vis = 0
        self.Raman_spec = 0
        self.Batch_Num = 1
        self.Off_line_m = 12
        self.Off_line_delay = 4
        self.plots = 1
        self.T_sp = 298.0
        self.pH_sp = 6.5


class ControlOutput:
    """Container for control output (manipulated variables)."""

    def __init__(self):
        self.Fg = 0.0
        self.RPM = 100.0
        self.Fs = 0.0
        self.Fa = 0.0
        self.Fb = 0.0
        self.Fc = 0.0
        self.Fh = 0.0
        self.Fw = 0.0
        self.pressure = 0.0
        self.viscosity = 4.0
        self.Fremoved = 0.0
        self.Fpaa = 0.0
        self.Foil = 0.0
        self.NH3_shots = 0.0
        self.Fault_ref = 0
        self.d1 = 0
        self.tfl = 0


def fctrl_indpensim(X, Xd, k, h, T, Ctrl_flags):
    """Compute manipulated variables for the simulation.

    Parameters:
        X: Batch data structure.
        Xd: Disturbance/industrial data structure.
        k: Current simulation sample (0-based).
        h: Simulation sample period (hours).
        T: Simulation time duration (hours).
        Ctrl_flags: ControlFlags instance.

    Returns:
        u: ControlOutput with manipulated variables.
        X: Updated batch data structure.
    """
    u = ControlOutput()

    # pH controller
    pH_sensor_error = 0.0
    if Ctrl_flags.Faults == 8:
        pH_sensor_error = 0.1
        ramp_times = [0, 200, 800, 1750]
        ramp_vals = [0, 0, pH_sensor_error, pH_sensor_error]
        t_interp = np.arange(1, 1751)
        ramp_interp = np.interp(t_interp, ramp_times, ramp_vals)
        idx = min(k, len(ramp_interp) - 1)
        pH_sensor_error = ramp_interp[idx]
        u.Fault_ref = 1

    # Build pH error history
    pH_sp = Ctrl_flags.pH_sp
    if k <= 1:
        ph_err = pH_sp - (-np.log10(X.pH.y[0])) + pH_sensor_error
        ph_err1 = pH_sp - (-np.log10(X.pH.y[0])) + pH_sensor_error
    else:
        ph_err = pH_sp - (-np.log10(X.pH.y[k - 1])) + pH_sensor_error
        ph_err1 = -(-np.log10(X.pH.y[k - 2])) + pH_sensor_error

    # Build pH history
    if k <= 1:
        ph = -np.log10(X.pH.y[0])
        ph1 = -np.log10(X.pH.y[0])
        ph2 = -np.log10(X.pH.y[0])
    elif k == 2:
        ph = -np.log10(X.pH.y[1])
        ph1 = -np.log10(X.pH.y[0])
        ph2 = -np.log10(X.pH.y[0])
    else:
        ph = -np.log10(X.pH.y[k - 1])
        ph1 = -np.log10(X.pH.y[k - 2])
        ph2 = -np.log10(X.pH.y[k - 3])

    # pH control logic
    if ph_err >= -0.05:
        ph_on_off = 1
        if k == 0:
            Fb = pid_simple3(X.Fb.y[0], ph_err, ph_err1, ph, ph1, ph2,
                             0, 225, 8e-2, 4.0e-5, 8, h)
        else:
            Fb = pid_simple3(X.Fb.y[k - 1], ph_err, ph_err1, ph, ph1, ph2,
                             0, 225, 8e-2, 4.0e-5, 8, h)
        Fa = 0.0
    elif ph_err <= -0.05:
        ph_on_off = 1
        if k == 0:
            Fa = pid_simple3(X.Fa.y[0], ph_err, ph_err1, ph, ph1, ph2,
                             0, 225, 8e-2, 12.5, 0.125, h)
            Fb = 0.0
        else:
            Fa = pid_simple3(X.Fa.y[k - 1], ph_err, ph_err1, ph, ph1, ph2,
                             0, 225, 8e-2, 12.5, 0.125, h)
            Fb = X.Fb.y[k - 1] * 0.5
    else:
        ph_on_off = 0
        Fb = 0.0
        Fa = 0.0

    # Temperature controller
    T_sensor_error = 0.0
    if Ctrl_flags.Faults == 7:
        T_sensor_error = 0.4
        ramp_times = [0, 200, 800, 1750]
        ramp_vals = [0, 0, T_sensor_error, T_sensor_error]
        t_interp = np.arange(1, 1751)
        ramp_interp = np.interp(t_interp, ramp_times, ramp_vals)
        idx = min(k, len(ramp_interp) - 1)
        T_sensor_error = ramp_interp[idx]
        u.Fault_ref = 1

    # Build temperature error history
    T_sp = Ctrl_flags.T_sp
    if k <= 1:
        temp_err = T_sp - X.T.y[0] + T_sensor_error
        temp_err1 = T_sp - X.T.y[0] + T_sensor_error
    else:
        temp_err = T_sp - X.T.y[k - 1] + T_sensor_error
        temp_err1 = T_sp - X.T.y[k - 2] + T_sensor_error

    # Build temperature history
    if k <= 1:
        temp = X.T.y[0]
        temp1 = X.T.y[0]
        temp2 = X.T.y[0]
    elif k == 2:
        temp = X.T.y[1]
        temp1 = X.T.y[0]
        temp2 = X.T.y[0]
    else:
        temp = X.T.y[k - 1]
        temp1 = X.T.y[k - 2]
        temp2 = X.T.y[k - 3]

    # Temperature control logic
    if temp_err <= 0.05:
        temp_on_off = 0  # cooling
        if k == 0:
            Fc = pid_simple3(X.Fc.y[0], temp_err, temp_err1, temp, temp1, temp2,
                             0, 1.5e3, -300, 1.6, 0.005, h)
            Fh = 0.0
        else:
            Fc = pid_simple3(X.Fc.y[k - 1], temp_err, temp_err1, temp, temp1, temp2,
                             0, 1.5e3, -300, 1.6, 0.005, h)
            Fh = X.Fh.y[k - 1] * 0.1
    else:
        temp_on_off = 1  # heating
        if k == 0:
            Fh = pid_simple3(X.Fc.y[0], temp_err, temp_err1, temp, temp1, temp2,
                              0, 1.5e3, 50, 0.050, 1, h)
            Fc = 0.0
        else:
            Fh = pid_simple3(X.Fc.y[k - 1], temp_err, temp_err1, temp, temp1, temp2,
                              0, 1.5e3, 50, 0.050, 1, h)
            Fc = X.Fc.y[k - 1] * 0.3

    # Numerical stability
    Fc = max(Fc, 1e-4)
    Fh = max(Fh, 1e-4)

    # Sequential Batch Control
    if Ctrl_flags.SBC == 1:
        Foil = Xd.Foil.y[k]
        F_discharge = Xd.F_discharge_cal.y[k]
        pressure = Xd.pressure.y[k]
        Fpaa = Xd.Fpaa.y[k]
        Fw = Xd.Fw.y[k]
        viscosity = Xd.viscosity.y[k]
        Fg = Xd.Fg.y[k]
        Fs = Xd.Fs.y[k]

    if Ctrl_flags.SBC == 0:
        viscosity = 4.0

        # SBC - Fs
        Recipe_Fs = [15, 60, 80, 100, 120, 140, 160, 180, 200, 220, 240, 260, 280, 300, 320, 340, 360, 380, 400, 800, 1750]
        Recipe_Fs_sp = [8, 15, 30, 75, 150, 30, 37, 43, 47, 51, 57, 61, 65, 72, 76, 80, 84, 90, 116, 90, 80]
        Fs = Recipe_Fs_sp[-1]
        for sq in range(len(Recipe_Fs)):
            if k <= Recipe_Fs[sq]:
                Fs = Recipe_Fs_sp[sq]
                break

        # Add PRBS to Fs
        if Ctrl_flags.PRBS == 1:
            if k > 500 and k % 100 == 0:
                random_number = np.random.randint(1, 4)
                noise_factor = 15
                if random_number == 1:
                    random_noise = 0
                elif random_number == 2:
                    random_noise = noise_factor
                else:
                    random_noise = -noise_factor
                X.PRBS_noise_addition[k] = random_noise
            if k > 475:
                Fs = X.Fs.y[k - 1]
            if k > 500 and k % 100 == 0:
                Fs = X.Fs.y[k - 1] + X.PRBS_noise_addition[k]
        else:
            X.PRBS_noise_addition[k] = 0

        # SBC - Foil
        Recipe_Foil = [20, 80, 280, 300, 320, 340, 360, 380, 400, 1750]
        Recipe_Foil_sp = [22, 30, 35, 34, 33, 32, 31, 30, 29, 23]
        Foil = Recipe_Foil_sp[-1]
        for sq in range(len(Recipe_Foil)):
            if k <= Recipe_Foil[sq]:
                Foil = Recipe_Foil_sp[sq]
                break

        # SBC - Fg
        Recipe_Fg = [40, 100, 200, 450, 1000, 1250, 1750]
        Recipe_Fg_sp = [30, 42, 55, 60, 75, 65, 60]
        Fg = Recipe_Fg_sp[-1]
        for sq in range(len(Recipe_Fg)):
            if k <= Recipe_Fg[sq]:
                Fg = Recipe_Fg_sp[sq]
                break

        # SBC - pressure
        Recipe_pres = [62.5, 125, 150, 200, 500, 750, 1000, 1750]
        Recipe_pres_sp = [0.6, 0.7, 0.8, 0.9, 1.1, 1, 0.9, 0.9]
        pressure = Recipe_pres_sp[-1]
        for sq in range(len(Recipe_pres)):
            if k <= Recipe_pres[sq]:
                pressure = Recipe_pres_sp[sq]
                break

        # SBC - F_discharge
        Recipe_discharge = [500, 510, 650, 660, 750, 760, 850, 860, 950, 960,
                           1050, 1060, 1150, 1160, 1250, 1260, 1350, 1360, 1750]
        Recipe_discharge_sp = [0, 4000, 0, 4000, 0, 4000, 0, 4000, 0, 4000,
                              0, 4000, 0, 4000, 0, 4000, 0, 4000, 0]
        F_discharge = 0.0
        for sq in range(len(Recipe_discharge)):
            if k <= Recipe_discharge[sq]:
                F_discharge = -Recipe_discharge_sp[sq]
                break

        # SBC - Fw
        Recipe_water = [250, 375, 750, 800, 850, 1000, 1250, 1350, 1750]
        Recipe_water_sp = [0, 500, 100, 0, 400, 150, 250, 0, 100]
        Fw = Recipe_water_sp[-1]
        for sq in range(len(Recipe_water_sp)):
            if sq < len(Recipe_water) and k <= Recipe_water[sq]:
                Fw = Recipe_water_sp[sq]
                break

        # SBC - F_PAA
        Recipe_PAA = [25, 200, 1000, 1500, 1750]
        Recipe_PAA_sp = [5, 0, 10, 4, 0]
        Fpaa = Recipe_PAA_sp[-1]
        for sq in range(len(Recipe_PAA_sp)):
            if sq < len(Recipe_PAA) and k <= Recipe_PAA[sq]:
                Fpaa = Recipe_PAA_sp[sq]
                break

        # Add PRBS to Fpaa
        if Ctrl_flags.PRBS == 1:
            if k > 500 and k % 100 == 0:
                random_number = np.random.randint(1, 4)
                noise_factor = 1
                if random_number == 1:
                    random_noise = 0
                elif random_number == 2:
                    random_noise = noise_factor
                else:
                    random_noise = -noise_factor
                X.PRBS_noise_addition[k] = random_noise
            if k > 475:
                Fpaa = X.Fpaa.y[k - 1]
            if k > 500 and k % 100 == 0:
                Fpaa = X.Fpaa.y[k - 1] + X.PRBS_noise_addition[k]
        else:
            X.PRBS_noise_addition[k] = 0

        # NH3 shots
        if hasattr(Xd, 'NH3_shots'):
            Xd.NH3_shots.y[k] = 0

    # Process faults
    if Ctrl_flags.Faults == 1 or Ctrl_flags.Faults == 6:
        if 100 <= k <= 120:
            Fg = 20
            u.Fault_ref = 1
        if 500 <= k <= 550:
            Fg = 20
            u.Fault_ref = 1

    if Ctrl_flags.Faults == 2 or Ctrl_flags.Faults == 6:
        if 500 <= k <= 520:
            pressure = 2
            u.Fault_ref = 1
        if 1000 <= k <= 1200:
            pressure = 2
            u.Fault_ref = 1

    if Ctrl_flags.Faults == 3 or Ctrl_flags.Faults == 6:
        if 100 <= k <= 150:
            Fs = 2
            u.Fault_ref = 1
        if 380 <= k <= 460:
            Fs = 20
            u.Fault_ref = 1
        if 1000 <= k <= 1070:
            Fs = 20
            u.Fault_ref = 1

    if Ctrl_flags.Faults == 4 or Ctrl_flags.Faults == 6:
        if 400 <= k <= 420:
            Fb = 5
            u.Fault_ref = 1
        if 700 <= k <= 800:
            Fb = 10
            u.Fault_ref = 1

    if Ctrl_flags.Faults == 5 or Ctrl_flags.Faults == 6:
        if 350 <= k <= 450:
            Fc = 2
            u.Fault_ref = 1
        if 1200 <= k <= 1350:
            Fc = 10
            u.Fault_ref = 1

    # Raman-based PAA control
    if Ctrl_flags.Raman_spec == 2:
        PAA_sp = 1200.0
        if k <= 1:
            PAA_err = PAA_sp - X.PAA.y[0]
            PAA_err1 = PAA_sp - X.PAA.y[0]
        else:
            PAA_err = PAA_sp - X.PAA.y[k - 1]
            PAA_err1 = PAA_sp - X.PAA.y[k - 2]

        if k * h < 10:
            pass  # keep Fpaa as is
        else:
            if k <= 1:
                temp_paa = X.PAA_pred.y[0]
                temp_paa1 = X.PAA_pred.y[0]
                temp_paa2 = X.PAA_pred.y[0]
            elif k == 2:
                temp_paa = X.PAA_pred.y[1]
                temp_paa1 = X.PAA_pred.y[0]
                temp_paa2 = X.PAA_pred.y[0]
            else:
                temp_paa = X.PAA_pred.y[k - 2]
                temp_paa1 = X.PAA_pred.y[k - 3]
                temp_paa2 = X.PAA_pred.y[k - 4]

            if k == 0:
                Fpaa = pid_simple3(X.Fpaa.y[0], PAA_err, PAA_err1,
                                   temp_paa, temp_paa1, temp_paa2,
                                   0, 150, 0.1, 0.50, 0, h)
            else:
                Fpaa = pid_simple3(X.Fpaa.y[k - 1], PAA_err, PAA_err1,
                                   temp_paa, temp_paa1, temp_paa2,
                                   0, 150, 0.1, 0.50, 0, h)

    # Set control output
    u.Fg = Fg
    u.RPM = 100
    u.Fs = Fs
    u.Fa = Fa
    u.Fb = Fb
    u.Fc = Fc
    u.Fh = Fh
    u.d1 = ph_on_off
    u.tfl = temp_on_off
    u.Fw = Fw
    u.pressure = pressure
    u.viscosity = viscosity
    u.Fremoved = F_discharge
    u.Fpaa = Fpaa
    u.Foil = Foil
    nh3_val = Xd.NH3_shots.y[k] if hasattr(Xd, 'NH3_shots') and k < len(Xd.NH3_shots.y) else 0.0
    u.NH3_shots = nh3_val

    return u, X
