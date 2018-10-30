"""Estimate the rhythmicity of a neural oscillation by calculating the lagged coherence metric."""

import numpy as np
from scipy import signal

###################################################################################################
###################################################################################################

def lagged_coherence(x, f_range, s_rate, n_cycles=3, f_step=1, return_spectrum=False):
    """Quantify the rhythmicity of an oscillator using the lagged coherence measure.

    Parameters
    ----------
    x : array-like 1d
        voltage time series
    f_range : (low, high), Hz
        frequency range of the oscillator
    s_rate : float
        sampling rate
    n_cycles : float
        Number of cycles of the frequency of interest used to compute lagged coherence
    f_step : float, Hz
        step size to calculate lagged coherence in the frequency range.
    return_spectrum : bool
        if True, return the lagged coherence for all frequency values. otherwise, only return mean

    Returns
    -------
    lc : float (or numpy.array 1d)
        if return_spectrum is False: mean lagged coherence value in the frequency range of interest
        if return_spectrum is True: lagged coherence value for each frequency in the frequency range
    s_rate : numpy.array 1d
        Only returned if return_spectrum is True
        Frequencies (Hz) corresponding to the lagged coherence values in lc

    References
    ----------
    Fransen, A. M., van Ede, F., & Maris, E. (2015).
    Identifying neuronal oscillations using rhythmicity.
    Neuroimage, 118, 256-267.
    """

    # Identify Fourier components of interest
    freqs = np.arange(f_range[0], f_range[1] + f_step, f_step)

    # Calculate lagged coherence for each frequency
    n_freqs = len(freqs)
    lcs = np.zeros(n_freqs)
    for ind, freq in enumerate(freqs):
        lcs[ind] = _lagged_coherence_1freq(
            x, freq, s_rate, n_cycles=n_cycles, f_step=f_step)

    # Return desired measure of lagged coherence
    if return_spectrum:
        lc = lcs
        return lc, freqs
    else:
        lc = np.mean(lcs)
        return lc


def _lagged_coherence_1freq(x, f, s_rate, n_cycles=3, f_step=1):
    """Calculate lagged coherence of x at frequency f using the hanning-taper FFT method"""

    # Determine number of samples to be used in each window to compute lagged coherence
    n_samps = int(np.ceil(n_cycles * s_rate / f))

    # For each N-cycle chunk, calculate the fourier coefficient at the frequency of interest, f
    chunks = _nonoverlapping_chunks(x, n_samps)
    C = len(chunks)
    hann_window = signal.hanning(n_samps)
    fourier_f = np.fft.fftfreq(n_samps, 1 / float(s_rate))
    fourier_f_idx = np.argmin(np.abs(fourier_f - f))
    fourier_coes_rateoi = np.zeros(C, dtype=complex)
    for i2, c in enumerate(chunks):
        fourier_coef = np.fft.fft(c * hann_window)
        fourier_coes_rateoi[i2] = fourier_coef[fourier_f_idx]

    # Compute the lagged coherence value
    lcs_num = 0
    for i2 in range(C - 1):
        lcs_num += fourier_coes_rateoi[i2] * np.conj(fourier_coes_rateoi[i2 + 1])
    lcs_denom = np.sqrt(np.sum(
        np.abs(fourier_coes_rateoi[:-1])**2) * np.sum(np.abs(fourier_coes_rateoi[1:])**2))
    return np.abs(lcs_num / lcs_denom)


def _nonoverlapping_chunks(x, N):
    """Split x into nonoverlapping chunks of length N"""

    Nchunks = int(np.floor(len(x) / float(N)))
    chunks = np.reshape(x[:int(Nchunks * N)], (Nchunks, int(N)))

    return chunks
