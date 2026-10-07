"""Substrate prediction from Raman spectra.

Equivalent to Substrate_prediction.m.
"""

import numpy as np
from pathlib import Path

# Try to load PLS model at import time
_pls_model = None


def _load_pls_model():
    """Load the PLS model from the .mat file."""
    global _pls_model
    if _pls_model is not None:
        return _pls_model
    try:
        from scipy.io import loadmat
        data_dir = Path(__file__).parent.parent / 'IndPenSim_V2.01'
        mat_file = data_dir / 'PAA_PLS_model.mat'
        _pls_model = loadmat(str(mat_file))
        return _pls_model
    except Exception as e:
        print(f"Warning: Could not load PLS model: {e}")
        return None


def substrate_prediction(k, X, h, T):
    """Predict PAA concentration from Raman spectra using PLS model.

    Parameters:
        k: Current simulation sample (0-based).
        X: Batch data structure.
        h: Sampling time.
        T: Simulation duration.

    Returns:
        X: Updated batch data with PAA predictions.
    """
    try:
        from scipy.signal import savgol_filter
    except ImportError:
        print("Warning: scipy not available for Savitzky-Golay filter")
        return X

    model = _load_pls_model()
    if model is None:
        return X

    j = k - 1
    if j < 0:
        return X

    # Initialize PAA_pred channel if needed
    if not hasattr(X, 'PAA_pred'):
        from .channel import create_channel
        N = int(T / h)
        X.PAA_pred = create_channel('PAA prediction', 'mg/L', 'h',
                                     np.zeros(N), np.zeros(N))

    # Apply Savitzky-Golay filter
    spectrum = X.Raman_Spec.Intensity[:, j]
    Raman_Spec_sg = savgol_filter(spectrum, window_length=5, polyorder=2)

    # First derivative
    Raman_Spec_sg_d = np.diff(Raman_Spec_sg)

    # Extract PAA-relevant peaks (MATLAB indices 350:500 and 800:860, 0-based: 349:500 and 799:860)
    PAA_peaks_idx = list(range(349, 500)) + list(range(799, 860))
    PAA_peaks_Spec = Raman_Spec_sg_d[PAA_peaks_idx]

    # PLS prediction
    b = model['b']
    No_LV = 4
    X.PAA_pred.y[j] = np.dot(PAA_peaks_Spec, b[No_LV - 1, :len(PAA_peaks_Spec)])

    # Smoothing
    if j > 20:
        X.PAA_pred.y[j] = (X.PAA_pred.y[j - 1] + X.PAA_pred.y[j - 2] + X.PAA_pred.y[j]) / 3.0

    return X
