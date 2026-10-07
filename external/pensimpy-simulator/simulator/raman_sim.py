"""Raman spectroscopy simulation.

Equivalent to Raman_Sim.m - generates simulated Raman spectra.
"""

import numpy as np
from pathlib import Path


def _smooth(data, window_size):
    """Simple moving average smoothing (equivalent to MATLAB's smooth)."""
    if window_size < 1:
        return data
    window_size = int(window_size)
    if window_size % 2 == 0:
        window_size += 1
    kernel = np.ones(window_size) / window_size
    # Pad edges
    pad = window_size // 2
    padded = np.pad(data, pad, mode='edge')
    smoothed = np.convolve(padded, kernel, mode='valid')
    return smoothed[:len(data)]


def _gaussian_peak(center, width, array_size):
    """Generate a Gaussian peak in an array."""
    peak = np.zeros(array_size)
    length = width * 2
    std_dev = width / 2.0
    for x in range(-length, length + 1):
        idx = x + center
        if 0 <= idx < array_size:
            peak[idx] = (std_dev * np.sqrt(2 * np.pi))**(-1) * np.exp(-0.5 * (x / std_dev)**2)
    return peak


def raman_sim(k, X, h, T):
    """Generate simulated Raman spectra.

    Parameters:
        k: Current simulation sample (0-based).
        X: Batch data structure.
        h: Sampling time.
        T: Simulation duration.

    Returns:
        X: Updated batch data with Raman spectra.
    """
    N = int(T / h)
    Wavenumber_max = 2200

    # Build intensity shift
    Intensity_shift1 = np.ones(Wavenumber_max)
    for j in range(Wavenumber_max):
        b_val = (j + 1) / (Wavenumber_max * 0.5)
        Intensity_shift1[j] = np.exp(b_val) - 0.5

    # Spectral parameters
    a_coeff = -0.00178143846614472 * 0.1
    b_coeff = 1.05644816081515
    c_coeff = -0.0681439987249108 * 0.1
    d_coeff = -0.02

    Product_S = X.P.y[k] / 40.0
    Biomass_S = X.X.y[k] / 40.0
    Viscosity_S = X.Viscosity.y[k] / 100.0
    Time_S = (k + 1) / N

    Intensity_increase = (a_coeff * Biomass_S + b_coeff * Product_S +
                          c_coeff * Viscosity_S + d_coeff * Time_S)
    scaling_factor = 370000
    Gluc_increase = 800000 * 3 / 1400
    PAA_increase = 1700000 / 1000
    Prod_increase = 100000

    # Load reference spectra
    data_dir = Path(__file__).parent.parent / '..' / 'pensimpy-simulation' / 'IndPenSim_V2.01'
    ref_file = data_dir / 'reference_Specra.txt'
    reference_Spectra = np.loadtxt(ref_file)

    # Initialize Raman_Spec if not present
    if not hasattr(X, 'Raman_Spec'):
        class RamanSpec:
            pass
        X.Raman_Spec = RamanSpec()
        X.Raman_Spec.Wavelength = reference_Spectra[:Wavenumber_max, 0]
        X.Raman_Spec.Intensity = np.zeros((Wavenumber_max, N))

    reference_spectra = reference_Spectra[:Wavenumber_max, 1]
    New_Spectra = Intensity_increase * Intensity_shift1 * scaling_factor + reference_spectra

    # Add noise
    random_number = np.random.randint(1, 4, size=Wavenumber_max)
    noise_factor = 50
    random_noise = np.zeros(Wavenumber_max)
    for i in range(Wavenumber_max):
        if random_number[i] == 1:
            random_noise[i] = 0
        elif random_number[i] == 2:
            random_noise[i] = noise_factor
        else:
            random_noise[i] = -noise_factor

    random_noise_summed = np.cumsum(random_noise)
    random_noise_summed_smooth = _smooth(random_noise_summed, 25)

    New_Spectra_noise = New_Spectra + 10 * random_noise_summed_smooth

    # Glucose peaks
    Glucose_peak_a = _gaussian_peak(219, 70, Wavenumber_max)
    Glucose_peak_b = _gaussian_peak(639, 20, Wavenumber_max) / 4.3
    Glucose_peak_c = _gaussian_peak(1053, 100, Wavenumber_max)
    total_peaks_G = Glucose_peak_a + Glucose_peak_b + Glucose_peak_c

    # PAA peaks
    PAA_peak_a = _gaussian_peak(419, 60, Wavenumber_max)
    PAA_peak_b_raw = np.zeros(Wavenumber_max)
    peakb = 839
    peakb_width = 15
    peakb_length = peakb_width * 2
    peakb_std_dev = peakb_width / 2.0
    for x in range(-peakb_length, peakb_length + 1):
        idx = x + peakb
        if 0 <= idx < Wavenumber_max:
            PAA_peak_b_raw[idx] = ((peakb_std_dev * np.sqrt(2 * np.pi))**(-1) *
                                    np.exp(-0.5 * (x / peakb_std_dev)**2) / 4.3)
    total_peaks_PAA = PAA_peak_a + PAA_peak_b_raw

    # Product peaks
    Product_peak_a = np.zeros(Wavenumber_max)
    peakPa = 800
    peakPa_width = 30
    peakPa_length = peakPa_width * 4
    peakPa_std_dev = peakPa_width / 2.0
    for x in range(-peakPa_length, peakPa_length + 1):
        idx = x + peakPa
        if 0 <= idx < Wavenumber_max:
            Product_peak_a[idx] = ((peakPa_std_dev * np.sqrt(2 * np.pi))**(-1) *
                                   np.exp(-0.5 * (x / peakPa_std_dev)**2))

    Product_peak_b = np.zeros(Wavenumber_max)
    peakPb = 1200
    peakPb_width = 30
    peakPb_length = peakPb_width * 30
    peakPb_std_dev = peakPb_width / 2.0
    for x in range(-peakPb_length, peakPb_length + 1):
        idx = x + peakPb
        if 0 <= idx < Wavenumber_max:
            Product_peak_b[idx] = ((peakPb_std_dev * np.sqrt(2 * np.pi))**(-1) *
                                   np.exp(-0.5 * (x / peakPb_std_dev)**2))
    total_peaks_P = Product_peak_a + Product_peak_b

    K_G = 0.005
    Substrate_raman = X.S.y[k]
    PAA_raman = X.PAA.y[k]

    final_spectra = (New_Spectra_noise +
                     total_peaks_G * Gluc_increase * Substrate_raman / (K_G + Substrate_raman) +
                     total_peaks_PAA * PAA_increase * PAA_raman +
                     total_peaks_P * Prod_increase * X.P.y[k])

    X.Raman_Spec.Intensity[:, k] = final_spectra

    return X
