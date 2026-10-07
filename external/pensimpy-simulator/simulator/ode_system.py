"""ODE system for IndPenSim.

Equivalent to indpensim_ode.m - contains the ordinary differential equations.
"""

import numpy as np


def indpensim_ode(t, y, inp1, par):
    """Compute derivatives for the IndPenSim ODE system.

    Parameters:
        t: Current time.
        y: State vector (33 elements).
        inp1: Input parameter vector (26 elements).
        par: Model parameter vector (105 elements).

    Returns:
        dy: Derivative vector (33 elements).
    """
    # Unpack model parameters (0-indexed)
    mu_p = par[0]
    mux_max = par[1]
    ratio_mu_e_mu_b = par[2]
    P_std_dev = par[3]
    mean_P = par[4]
    mu_v = par[5]
    mu_a = par[6]
    mu_diff = par[7]
    beta_1 = par[8]
    K_b = par[9]
    K_diff = par[10]
    K_diff_L = par[11]
    K_e = par[12]
    K_v = par[13]
    delta_r = par[14]
    k_v = par[15]
    D = par[16]
    rho_a0 = par[17]
    rho_d = par[18]
    mu_h = par[19]
    r_0 = par[20]
    delta_0 = par[21]

    Y_sX = par[22]
    Y_sP = par[23]
    m_s = par[24]
    c_oil = par[25]
    c_s = par[26]
    Y_O2_X = par[27]
    Y_O2_P = par[28]
    m_O2_X = par[29]
    alpha_kla = par[30]
    a = par[31]
    b = par[32]
    c = par[33]
    d = par[34]
    Henrys_c = par[35]
    n_imp = par[36]
    r = par[37]
    r_imp = par[38]
    Po = par[39]
    epsilon = par[40]
    # g_const = par[41]  # not used directly in ODE
    R = par[42]
    X_crit_DO2 = par[43]
    P_crit_DO2 = par[44]
    A_inhib = par[45]
    Tf = par[46]
    Tw = par[47]
    Tcin = par[48]
    Th = par[49]
    Tair = par[50]
    C_ps = par[51]
    C_pw = par[52]
    dealta_H_evap = par[53]
    U_jacket = par[54]
    A_c = par[55]
    Eg = par[56]
    Ed = par[57]
    k_g = par[58]
    k_d = par[59]
    Y_QX = par[60]
    abc = par[61]
    gamma1 = par[62]
    gamma2 = par[63]
    m_ph = par[64]
    K1 = par[65]
    K2 = par[66]
    N_conc_oil = par[67]
    N_conc_paa = par[68]
    N_conc_shot = par[69]
    Y_NX = par[70]
    Y_NP = par[71]
    m_N = par[72]
    X_crit_N = par[73]
    PAA_c = par[74]
    Y_PAA_P = par[75]
    Y_PAA_X = par[76]
    m_PAA = par[77]
    X_crit_PAA = par[78]
    P_crit_PAA = par[79]
    B_1 = par[80]
    B_2 = par[81]
    B_3 = par[82]
    B_4 = par[83]
    B_5 = par[84]
    delta_c_0 = par[85]
    k3 = par[86]
    k1 = par[87]
    k2 = par[88]
    t1 = par[89]
    t2 = par[90]
    q_co2 = par[91]
    X_crit_CO2 = par[92]
    alpha_evp = par[93]
    beta_T = par[94]
    pho_g = par[95]
    pho_oil = par[96]
    pho_w = par[97]
    pho_paa = par[98]
    O_2_in = par[99]
    N2_in = par[100]
    C_CO2_in = par[101]
    Tv = par[102]
    T0 = par[103]
    alpha_1 = par[104]

    # Process inputs
    inhib_flag = inp1[0]
    Fs = inp1[1]
    Fg = inp1[2] / 60.0  # Convert from L/min to L/s (aeration rate)
    RPM = inp1[3]
    Fc = inp1[4]
    Fh = inp1[5]
    Fb = inp1[6]
    Fa = inp1[7]
    step1 = inp1[8]
    Fw = inp1[9]
    Fw = max(Fw, 0.0)  # Correct for negative flow values
    pressure = inp1[10]

    # Viscosity flag
    if inp1[25] == 0:
        viscosity = y[9]
    else:
        viscosity = inp1[11]

    F_discharge = inp1[12]
    Fpaa = inp1[13]
    Foil = inp1[14]
    NH3_shots = inp1[15]
    dist_flag = inp1[16]
    distMuP = inp1[17]
    distMuX = inp1[18]
    distsc = inp1[19]
    distcoil = inp1[20]
    distabc = inp1[21]
    distPAA = inp1[22]
    distTcin = inp1[23]
    distO_2_in = inp1[24]

    pho_b = 1100.0 + y[3] + y[11] + y[12] + y[13] + y[14]  # Broth density

    # Apply disturbances
    if dist_flag == 1:
        mu_p = mu_p + distMuP
        mux_max = mux_max + distMuX
        c_s = c_s + distsc
        c_oil = c_oil + distcoil
        abc = abc + distabc
        PAA_c = PAA_c + distPAA
        Tcin = Tcin + distTcin
        O_2_in = O_2_in + distO_2_in

    # Process parameters
    A_t1 = y[10] / (y[11] + y[12] + y[13] + y[14])  # Age-dependent term

    # Variables
    s = y[0]      # substrate g/L
    a_1 = y[12]   # Biomass (Extension) region A_1
    a_0 = y[11]   # Biomass (Branching) region A_0
    a_3 = y[13]   # Biomass degenerated
    total_X = y[11] + y[12] + y[13] + y[14]  # Total Biomass

    # Calculating liquid height in vessel
    h_b = (y[4] / 1000.0) / (np.pi * r**2)
    h_b = h_b * (1.0 - epsilon)  # Ungassed height

    # Calculating log mean pressure of vessel [bar]
    pressure_bottom = 1.0 + pressure + (pho_b * h_b) * 9.81e-5
    pressure_top = 1.0 + pressure
    if pressure_bottom > pressure_top and pressure_top > 0:
        log_mean_pressure = (pressure_bottom - pressure_top) / np.log(pressure_bottom / pressure_top)
    else:
        log_mean_pressure = pressure_top
    total_pressure = log_mean_pressure

    # Ensuring minimum value for viscosity
    if viscosity < 4:
        viscosity = 1.0

    DOstar_tp = (total_pressure * O_2_in) / Henrys_c  # in mg/L

    # Inhibition flags
    if inhib_flag == 0:
        pH_inhib = 1.0
        NH3_inhib = 1.0
        T_inhib = 1.0
        mu_h = 0.003
        DO_2_inhib_X = 1.0
        DO_2_inhib_P = 1.0
        CO2_inhib = 1.0
        PAA_inhib_X = 1.0
        PAA_inhib_P = 1.0

    elif inhib_flag == 1:
        # Inhibition: DO2, T, pH
        pH_inhib = 1.0 / (1.0 + (y[6] / K1) + (K2 / y[6]))
        NH3_inhib = 1.0
        T_inhib = (k_g * np.exp(-Eg / (R * y[7])) - k_d * np.exp(-Ed / (R * y[7]))) * 0 + 1
        CO2_inhib = 1.0
        DO_2_inhib_X = 0.5 * (1.0 - np.tanh(A_inhib * (X_crit_DO2 * DOstar_tp - y[1])))
        DO_2_inhib_P = 0.5 * (1.0 - np.tanh(A_inhib * (P_crit_DO2 * DOstar_tp - y[1])))
        PAA_inhib_X = 1.0
        PAA_inhib_P = 1.0
        # Temperature and pH effect on hydrolysis rate
        pH_val = -np.log10(y[6])
        k4 = np.exp(B_1 + B_2 * pH_val + B_3 * y[7] + B_4 * (pH_val**2) + B_5 * (y[7]**2))
        mu_h = k4

    elif inhib_flag == 2:
        # Full inhibition: DO2, T, pH, CO2_L, PAA, N
        pH_inhib = 1.0 / (1.0 + (y[6] / K1) + (K2 / y[6]))
        NH3_inhib = 0.5 * (1.0 - np.tanh(A_inhib * (X_crit_N - y[30])))
        T_inhib = k_g * np.exp(-Eg / (R * y[7])) - k_d * np.exp(-Ed / (R * y[7]))
        CO2_inhib = 0.5 * (1.0 + np.tanh(A_inhib * (X_crit_CO2 - y[28] * 1000.0)))
        DO_2_inhib_X = 0.5 * (1.0 - np.tanh(A_inhib * (X_crit_DO2 * DOstar_tp - y[1])))
        DO_2_inhib_P = 0.5 * (1.0 - np.tanh(A_inhib * (P_crit_DO2 * DOstar_tp - y[1])))
        PAA_inhib_X = 0.5 * (1.0 + np.tanh(X_crit_PAA - y[29]))
        PAA_inhib_P = 0.5 * (1.0 + np.tanh(-P_crit_PAA + y[29]))
        pH_val = -np.log10(y[6])
        k4 = np.exp(B_1 + B_2 * pH_val + B_3 * y[7] + B_4 * (pH_val**2) + B_5 * (y[7]**2))
        mu_h = k4
    else:
        pH_inhib = 1.0
        NH3_inhib = 1.0
        T_inhib = 1.0
        DO_2_inhib_X = 1.0
        DO_2_inhib_P = 1.0
        CO2_inhib = 1.0
        PAA_inhib_X = 1.0
        PAA_inhib_P = 1.0

    # Main rate equations for kinetic expressions
    # Penicillin inhibition curve
    P_inhib = 2.5 * P_std_dev * ((P_std_dev * np.sqrt(2 * np.pi))**(-1) *
              np.exp(-0.5 * ((s - mean_P) / P_std_dev)**2))

    # Specific growth rates of biomass regions with inhibition
    mu_a0 = ratio_mu_e_mu_b * mux_max * pH_inhib * NH3_inhib * T_inhib * DO_2_inhib_X * CO2_inhib * PAA_inhib_X
    mu_e = mux_max * pH_inhib * NH3_inhib * T_inhib * DO_2_inhib_X * CO2_inhib * PAA_inhib_X

    K_diff_val = par[10] - A_t1 * beta_1
    if K_diff_val < K_diff_L:
        K_diff_val = K_diff_L

    # Growing A_0 region
    r_b0 = mu_a0 * a_1 * s / (K_b + s)
    r_sb0 = Y_sX * r_b0

    # Non-growing A_1 region
    r_e1 = mu_e * a_0 * s / (K_e + s)
    r_se1 = Y_sX * r_e1

    # Differentiation (A_0 -> A_1)
    r_d1 = mu_diff * a_0 / (K_diff_val + s)
    r_m0 = m_s * a_0 / (K_diff_val + s)

    # Vacuole volume calculations
    phi = np.zeros(10)
    phi[0] = y[26]
    n_idx = 16  # y[16] is n0 (0-indexed)
    for k_vac in range(1, 10):
        r_mean_k = 1.5e-4 + (k_vac - 1) * delta_r
        phi[k_vac] = (4.0 * np.pi * r_mean_k**3 / 3.0) * y[n_idx] * delta_r
        n_idx += 1

    v_2 = np.sum(phi)
    rho_a1 = a_1 / (a_1 / rho_a0 + v_2) if (a_1 / rho_a0 + v_2) > 0 else rho_a0
    v_a1 = a_1 / (2.0 * rho_a1) - v_2

    # Penicillin produced from non-growing A_1 regions
    r_p = mu_p * rho_a0 * v_a1 * P_inhib * DO_2_inhib_P * PAA_inhib_P - mu_h * y[3]

    # Vacuole formation
    r_m1 = m_s * rho_a0 * v_a1 * s / (K_v + s)

    # Vacuole degeneration
    r_d4 = mu_a * a_3

    # Vacuole volume ODEs
    # dn0/dt
    dn0_dt = ((mu_v * v_a1) / (K_v + s)) * ((6.0 / np.pi) * ((r_0 + delta_0)**(-3))) - k_v * y[15]

    # dn1..dn9 using central difference scheme
    n = 16  # 0-indexed: y[16] is n1 in the ODE indexing
    dn1_dt = -k_v * ((y[n + 1] - y[n - 1]) / (2.0 * delta_r)) + D * (y[n + 1] - 2.0 * y[n] + y[n - 1]) / delta_r**2
    n += 1
    dn2_dt = -k_v * ((y[n + 1] - y[n - 1]) / (2.0 * delta_r)) + D * (y[n + 1] - 2.0 * y[n] + y[n - 1]) / delta_r**2
    n += 1
    dn3_dt = -k_v * ((y[n + 1] - y[n - 1]) / (2.0 * delta_r)) + D * (y[n + 1] - 2.0 * y[n] + y[n - 1]) / delta_r**2
    n += 1
    dn4_dt = -k_v * ((y[n + 1] - y[n - 1]) / (2.0 * delta_r)) + D * (y[n + 1] - 2.0 * y[n] + y[n - 1]) / delta_r**2
    n += 1
    dn5_dt = -k_v * ((y[n + 1] - y[n - 1]) / (2.0 * delta_r)) + D * (y[n + 1] - 2.0 * y[n] + y[n - 1]) / delta_r**2
    n += 1
    dn6_dt = -k_v * ((y[n + 1] - y[n - 1]) / (2.0 * delta_r)) + D * (y[n + 1] - 2.0 * y[n] + y[n - 1]) / delta_r**2
    n += 1
    dn7_dt = -k_v * ((y[n + 1] - y[n - 1]) / (2.0 * delta_r)) + D * (y[n + 1] - 2.0 * y[n] + y[n - 1]) / delta_r**2
    n += 1
    dn8_dt = -k_v * ((y[n + 1] - y[n - 1]) / (2.0 * delta_r)) + D * (y[n + 1] - 2.0 * y[n] + y[n - 1]) / delta_r**2
    n += 1
    dn9_dt = -k_v * ((y[n + 1] - y[n - 1]) / (2.0 * delta_r)) + D * (y[n + 1] - 2.0 * y[n] + y[n - 1]) / delta_r**2

    n_k = dn9_dt
    k_val = 10
    r_k = r_0 + (k_val - 2) * delta_r
    k_val2 = 12
    r_m = r_0 + (k_val2 - 2) * delta_r

    # Maximum vacuole volume department
    dn_m_dt = k_v * n_k / (r_m - r_k) - mu_a * y[25]
    n_k_y = y[24]

    # Mean vacuole
    dphi_0_dt = (mu_v * v_a1) / (K_v + s) - k_v * y[15] * (np.pi * (r_0 + delta_0)**3) / 6.0

    # Volume and Weight expressions
    F_evp = y[4] * alpha_evp * (np.exp(2.5 * (y[7] - T0) / (Tv - T0)) - 1.0)

    pho_feed = c_s / 1000.0 * pho_g + (1.0 - c_s / 1000.0) * pho_w
    dilution = Fs + Fb + Fa + Fw - F_evp + Fpaa

    # Change in Volume [L]
    dV1 = Fs + Fb + Fa + Fw + F_discharge / (pho_b / 1000.0) - F_evp + Fpaa
    # Change in Weight [kg]
    dWt = (Fs * pho_feed / 1000.0 + pho_oil / 1000.0 * Foil + Fb + Fa + Fw +
           F_discharge - F_evp + Fpaa * pho_paa / 1000.0)

    # ODEs for Biomass regions
    da_0_dt = r_b0 - r_d1 - y[11] * dilution / y[4]
    da_1_dt = r_e1 - r_b0 + r_d1 - (np.pi * ((r_k + r_m)**3) / 6.0) * rho_d * k_v * n_k_y - y[12] * dilution / y[4]
    da_3_dt = (np.pi * ((r_k + r_m)**3) / 6.0) * rho_d * k_v * n_k_y - r_d4 - y[13] * dilution / y[4]
    da_4_dt = r_d4 - y[14] * dilution / y[4]

    # Penicillin production
    dP_dt = r_p - y[3] * dilution / y[4]

    # Active Biomass rate
    X_1 = da_0_dt + da_1_dt + da_3_dt + da_4_dt
    X_t = y[11] + y[12] + y[13] + y[14]

    Qrxn_X = X_1 * Y_QX * y[4] * Y_O2_X / 1000.0
    Qrxn_P = dP_dt * Y_QX * y[4] * Y_O2_P / 1000.0
    Qrxn_t = Qrxn_X + Qrxn_P
    if Qrxn_t < 0:
        Qrxn_t = 0.0

    N_rpm = RPM / 60.0
    D_imp = 2.0 * r_imp
    unaerated_power = n_imp * Po * pho_b * (N_rpm**3) * (D_imp**5)
    Fg_safe = max(Fg, 1e-10)  # Prevent division by zero
    P_g = 0.706 * ((unaerated_power**2 * N_rpm * D_imp**3) / (Fg_safe**0.56))**0.45
    P_n = P_g / unaerated_power if unaerated_power > 0 else 1.0
    variable_power = (n_imp * Po * pho_b * (N_rpm**3) * (D_imp**5) * P_n) / 1000.0

    # Initialize derivative vector
    dy = np.zeros(33)

    # Substrate utilization [g/L]
    dy[0] = (-r_se1 - r_sb0 - r_m0 - r_m1
             - Y_sP * mu_p * rho_a0 * v_a1 * P_inhib * DO_2_inhib_P * PAA_inhib_P
             + Fs * c_s / y[4] + Foil * c_oil / y[4]
             - y[0] * dilution / y[4])

    # Dissolved oxygen [mg/L]
    V_s = Fg / (np.pi * r**2)
    T_val = y[7]
    V = y[4]
    V_m = y[4] / 1000.0
    h_b_val = (V / 1000.0) / (np.pi * r**2) * (1.0 - epsilon)
    P_air = (V_s * R * T_val * V_m / (22.4 * h_b_val)) * np.log(1.0 + pho_b * 9.81 * h_b_val / (pressure_top * 1e5)) if h_b_val > 0 else 0.0
    P_t1 = variable_power + P_air

    if viscosity <= 4:
        viscosity = 1.0
    vis_scaled = viscosity / 100.0
    oil_f = Foil / V if V > 0 else 0.0

    kla = alpha_kla * ((V_s**a) * ((P_t1 / V_m)**b) * (vis_scaled**c)) * (1.0 - oil_f**d) if V_m > 0 else 0.0
    OUR = (-X_1) * Y_O2_X - m_O2_X * X_t - dP_dt * Y_O2_P
    OTR = kla * (DOstar_tp - y[1])
    dy[1] = OUR + OTR - y[1] * dilution / y[4]

    # O_2 off-gas [%]
    Vg = epsilon * V_m
    Qfg_in = 60.0 * Fg * 1000.0 * 32.0 / 22.4
    denom = 1.0 - y[2] - y[27] / 100.0
    if abs(denom) < 1e-10:
        denom = 1e-10
    Qfg_out = 60.0 * Fg * (N2_in / denom) * 1000.0 * 32.0 / 22.4
    Vg_denom = Vg * 28.97 * 1000.0 / 22.4 if Vg > 0 else 1e-10
    dy[2] = (Qfg_in * O_2_in - Qfg_out * y[2] - 0.001 * OTR * V_m * 60.0) / Vg_denom

    # Penicillin production rate [g/L]
    dy[3] = r_p - y[3] * dilution / y[4]

    # Volume change [L]
    dy[4] = dV1

    # Weight change [Kg]
    dy[5] = dWt

    # pH
    pH_dis = Fs + Foil + Fb + Fa + F_discharge + Fw
    if -np.log10(max(y[6], 1e-14)) < 7:  # acidic
        cb = -abc
        ca = abc
        y6_val = y[6]
        pH_balance = 0
    else:  # basic
        cb = abc
        ca = -abc
        y6_val = 1e-14 / y[6] - y[6] if y[6] > 0 else 0.0
        pH_balance = 1

    B_val = (y6_val * y[4] + ca * Fa * step1 + cb * Fb * step1) / (y[4] + Fb * step1 + Fa * step1)
    B_val = -B_val

    if pH_balance == 1:  # basic
        disc = B_val**2 + 4e-14
        dy[6] = (-gamma1 * (r_b0 + r_e1 + r_d4 + r_d1 + m_ph * total_X)
                 - gamma1 * r_p - gamma2 * pH_dis
                 + ((-B_val - np.sqrt(max(disc, 0))) / 2.0 - y6_val))
    else:  # acidic
        disc = B_val**2 + 4e-14
        dy[6] = (+gamma1 * (r_b0 + r_e1 + r_d4 + r_d1 + m_ph * total_X)
                 + gamma1 * r_p + gamma2 * pH_dis
                 + ((-B_val + np.sqrt(max(disc, 0))) / 2.0 - y6_val))

    # Temperature [K]
    Ws = P_t1
    Qcon = U_jacket * A_c * (y[7] - Tair)
    Fc_safe = max(Fc, 1e-10)
    Fh_safe = max(Fh, 1e-10)
    dQ_dt = (Fs * pho_feed * C_ps * (Tf - y[7]) / 1000.0
             + Fw * pho_w * C_pw * (Tw - y[7]) / 1000.0
             - F_evp * pho_b * C_pw / 1000.0
             - dealta_H_evap * F_evp * pho_w / 1000.0
             + Qrxn_t + Ws
             - (alpha_1 / 1000.0) * Fc_safe**(beta_T + 1.0)
               * ((y[7] - Tcin) / (Fc_safe / 1000.0 + (alpha_1 * (Fc_safe / 1000.0)**beta_T) / 2.0 * pho_b * C_ps))
             - (alpha_1 / 1000.0) * Fh_safe**(beta_T + 1.0)
               * ((y[7] - Th) / (Fh_safe / 1000.0 + (alpha_1 * (Fh_safe / 1000.0)**beta_T) / 2.0 * pho_b * C_ps))
             - Qcon)

    dy[7] = dQ_dt / ((y[4] / 1000.0) * C_pw * pho_b) if (y[4] > 0 and pho_b > 0) else 0.0

    # Heat generation [kJ]
    dy[8] = dQ_dt

    # Viscosity
    dy[9] = 3.0 * np.cbrt(a_0) * (1.0 / (1.0 + np.exp(-k1 * (t - t1)))) * (1.0 / (1.0 + np.exp(-k2 * (t - t2)))) - k3 * Fw

    # Total X [g/L] (integral)
    dy[10] = y[11] + y[12] + y[13] + y[14]

    # Biomass regions
    dy[11] = da_0_dt   # Growing regions a0
    dy[12] = da_1_dt   # Non-growing regions a1
    dy[13] = da_3_dt   # Degenerated regions a3
    dy[14] = da_4_dt   # Autolysed biomass a4

    # Vacuole regions
    dy[15] = dn0_dt
    dy[16] = dn1_dt
    dy[17] = dn2_dt
    dy[18] = dn3_dt
    dy[19] = dn4_dt
    dy[20] = dn5_dt
    dy[21] = dn6_dt
    dy[22] = dn7_dt
    dy[23] = dn8_dt
    dy[24] = dn9_dt
    dy[25] = dn_m_dt
    dy[26] = dphi_0_dt

    # CO_2 [%]
    total_X_CO2 = y[11] + y[12]
    CER = total_X_CO2 * q_co2 * V
    dy[27] = ((60.0 * Fg * 44.0 * 1000.0 / 22.4) * C_CO2_in + CER
              - (60.0 * Fg * 44.0 * 1000.0 / 22.4) * y[27]) / Vg_denom

    # Dissolved CO_2 [mg/L]
    Henrys_c_co2 = np.exp(11.25 - 395.9 / (y[7] - 175.9)) / (44.0 * 100.0)
    C_star_CO2 = (total_pressure * y[27]) / Henrys_c_co2 if Henrys_c_co2 != 0 else 0.0
    dy[28] = kla * delta_c_0 * (C_star_CO2 - y[28]) - y[28] * dilution / y[4]

    # PAA [mg/L]
    dy[29] = (Fpaa * PAA_c / V - Y_PAA_P * dP_dt - Y_PAA_X * X_1
              - m_PAA * y[3] - y[29] * dilution / y[4])

    # N [mg/L]
    X_C_nitrogen = (-r_b0 - r_e1 - r_d1 - r_d4) * Y_NX
    P_C_nitrogen = -dP_dt * Y_NP
    dy[30] = ((NH3_shots * N_conc_shot) / y[4] + X_C_nitrogen + P_C_nitrogen
              - m_N * total_X + N_conc_paa * Fpaa / y[4]
              + N_conc_oil * Foil / y[4] - y[30] * dilution / y[4])

    dy[31] = mu_p   # Current penicillin growth rate
    dy[32] = mu_e   # Current biomass growth rate

    return dy
