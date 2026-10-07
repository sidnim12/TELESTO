"""Model parameters for IndPenSim.

Equivalent to Parameter_list.m.
"""

import numpy as np


def parameter_list(x0_mup, x0_mux, alpha_kla, N_conc_paa, PAA_c):
    """Define model parameters and return as a numpy array.

    Parameters:
        x0_mup: Maximum specific growth rate of penicillin [h^-1].
        x0_mux: Maximum specific growth rate of biomass [h^-1].
        alpha_kla: kla constant [-].
        N_conc_paa: Concentration of N in F_PAA [mg/L].
        PAA_c: Concentration of PAA in F_PAA [mg/L].

    Returns:
        par: numpy array of 105 model parameters.
    """
    # Penicillin model parameters
    mu_p = x0_mup                   # hr^{-1}           par[0]
    mux_max = x0_mux                # hr^{-1}           par[1]
    ratio_mu_e_mu_b = 0.4           # (-)               par[2]
    P_std_dev = 0.0015              # g L^{-1}          par[3]
    mean_P = 0.002                  # g L^{-1}          par[4]
    mu_v = 1.71e-4                  # g g^{-1} hr^{-1}  par[5]
    mu_a = 3.5e-3                   # hr^{-1}           par[6]
    mu_diff = 5.36e-3               # hr^{-1}           par[7]
    beta_1 = 0.006                  # (-)               par[8]
    K_b = 0.05                      # g L^{-1}          par[9]
    K_diff = 0.75                   # g L^{-1}          par[10]
    K_diff_L = 0.09                 # g L^{-1}          par[11]
    K_e = 0.009                     # g L^{-1}          par[12]
    K_v = 0.05                      # g L^{-1}          par[13]
    delta_r = 0.75e-4               # cm                par[14]
    k_v = 3.22e-5                   # cm hr^{-1}        par[15]
    D = 2.66e-11                    # cm^{2} hr^{-1}    par[16]
    rho_a0 = 0.35                   # g cm^{-3}         par[17]
    rho_d = 0.18                    # g cm^{3}          par[18]
    mu_h = 0.003                    # hr^{-1}           par[19]
    r_0 = 1.5e-4                    # cm                par[20]
    delta_0 = 1e-4                  # cm                par[21]

    # Process related parameters
    Y_sx = 1.85                     # g g^{-1}          par[22]
    Y_sP = 0.9                      # g g^{-1}          par[23]
    m_s = 0.029                     # g g^{-1} hr^{-1}  par[24]
    c_oil = 1000.0                  # g L^{-1}          par[25]
    c_s = 600.0                     # g L^{-1}          par[26]
    Y_O2_X = 650.0                  # mg g^{-1}         par[27]
    Y_O2_P = 160.0                  # mg g^{-1}         par[28]
    m_O2_X = 17.5                   # mg g^{-1}         par[29]
    # alpha_kla                     # (-)               par[30]
    a = 0.38                        # (-)               par[31]
    b = 0.34                        # (-)               par[32]
    c = -0.38                       # (-)               par[33]
    d = 0.25                        # (-)               par[34]
    Henrys_c = 0.0251               # bar L mg^{-1}     par[35]
    n_imp = 3                       # (-)               par[36]
    r = 2.1                         # (m)               par[37]
    r_imp = 0.85                    # (m)               par[38]
    Po = 5                          # (-)               par[39]
    epsilon = 0.1                   # (-)               par[40]
    g = 9.81                        # m s^{-1}          par[41]
    R = 8.314                       # J K^{-1} mol^{-1} par[42]
    X_crit_DO2 = 0.1                # (%)               par[43]
    P_crit_DO2 = 0.3                # (%)               par[44]
    A_inhib = 1.0                   # -                 par[45]
    Tf = 288.0                      # K                 par[46]
    Tw = 288.0                      # K                 par[47]
    Tcin = 285.0                    # K                 par[48]
    Th = 333.0                      # K                 par[49]
    Tair = 290.0                    # K                 par[50]
    C_ps = 5.9                      # kJ kg^{-1} K^{-1} par[51]
    C_pw = 4.18                     # kJ g^{-1} K^{-1}  par[52]
    dealta_H_evap = 2430.7          # kJ kg^{-1}        par[53]
    U_jacket = 36.0                 # kW m^{2} K^{-1}   par[54]
    A_c = 105.0                     # m^2               par[55]
    Eg = 1.488e4                    # J mol^{-1}        par[56]
    Ed = 1.7325e5                   # J mol^{-1}        par[57]
    k_g = 450.0                     # (-)               par[58]
    k_d = 0.25e30                   # (-)               par[59]
    Y_QX = 25.0                     # kJ/g              par[60]
    abc = 0.033                     # mol L^{-1}        par[61]
    gamma1 = 0.0325e-5              # mol H+/g          par[62]
    gamma2 = 2.5e-11                # mol H+/g          par[63]
    m_ph = 0.0025                   # mol H+/g hr^{-1}  par[64]
    K1 = 1e-5                       # mol L^{-1}        par[65]
    K2 = 2.5e-8                     # mol L^{-1}        par[66]
    N_conc_oil = 20000.0            # mg L^{-1}         par[67]
    # N_conc_paa                    # g L^{-1}          par[68]
    N_conc_shot = 400000.0          # mg kg^{-1}        par[69]
    Y_NX = 10.0                     # mg N_2 / g X DW   par[70]
    Y_NP = 80.0                     # mg N_2 / g X DW   par[71]
    m_N = 0.03                      # g L^{-1} hr^{-1}  par[72]
    X_crit_N = 150.0                # mg L^{-1}         par[73]
    # PAA_c                         # mg L^{-1}         par[74]
    Y_PAA_P = 187.5                 # mg / g P          par[75]
    Y_PAA_X = 37.5 * 1.2            # mg / g X          par[76]
    m_PAA = 1.05                    # g g^{-1} P h^{-1} par[77]
    X_crit_PAA = 2400.0             # mg/L              par[78]
    P_crit_PAA = 200.0              # mg/L              par[79]
    B_1 = -0.6429e2                 # (-)               par[80]
    B_2 = -0.1825e1                 # (-)               par[81]
    B_3 = 0.3649                    # (-)               par[82]
    B_4 = 0.1280                    # (-)               par[83]
    B_5 = -4.9496e-4                # (-)               par[84]
    delta_c_o = 0.89                # (-)               par[85]
    k_3 = 0.005                     # (-)               par[86]
    k1 = 0.001                      # (-)               par[87]
    k2 = 0.0001                     # (-)               par[88]
    t1 = 1.0                        # h                 par[89]
    t2 = 250.0                      # h                 par[90]
    q_co2 = 0.123 * 1.1             # mg CO_2 / g X     par[91]
    X_crit_CO2 = 7570.0             # mg L^{-1}         par[92]
    alpha_evp = 5.24e-4             # L hr^{-1}         par[93]
    beta_T = 2.88                   # -                 par[94]
    pho_g = 1.54 * 1000             # kg m^{-3}         par[95]
    pho_oil = 0.90 * 1000           # kg m^{-3}         par[96]
    pho_w = 1000.0                  # kg m^{-3}         par[97]
    pho_paa = 1000.0                # kg m^{-3}         par[98]
    O_2_in = 0.21                   # (%)               par[99]
    N2_in = 0.79                    # (%)               par[100]
    C_CO2_in = 0.033                # (%)               par[101]
    Tv = 373.0                      # K                 par[102]
    T0 = 273.0                      # K                 par[103]
    alpha_1 = 2451.8                # kJ/m^3            par[104]

    par = np.array([
        mu_p, mux_max, ratio_mu_e_mu_b, P_std_dev, mean_P, mu_v, mu_a, mu_diff,
        beta_1, K_b, K_diff, K_diff_L, K_e, K_v, delta_r, k_v, D, rho_a0, rho_d,
        mu_h, r_0, delta_0,
        Y_sx, Y_sP, m_s, c_oil, c_s, Y_O2_X, Y_O2_P, m_O2_X, alpha_kla, a, b, c, d,
        Henrys_c, n_imp, r, r_imp, Po, epsilon, g, R, X_crit_DO2, P_crit_DO2, A_inhib,
        Tf, Tw, Tcin, Th, Tair, C_ps, C_pw, dealta_H_evap, U_jacket, A_c, Eg, Ed, k_g,
        k_d, Y_QX, abc, gamma1, gamma2, m_ph, K1, K2, N_conc_oil, N_conc_paa,
        N_conc_shot, Y_NX, Y_NP, m_N, X_crit_N, PAA_c,
        Y_PAA_P, Y_PAA_X, m_PAA, X_crit_PAA, P_crit_PAA, B_1,
        B_2, B_3, B_4, B_5, delta_c_o, k_3, k1, k2, t1, t2, q_co2,
        X_crit_CO2, alpha_evp, beta_T, pho_g, pho_oil, pho_w, pho_paa,
        O_2_in, N2_in, C_CO2_in, Tv, T0, alpha_1
    ])

    return par
