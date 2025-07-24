"""
Digital Signal Processing utilities for IQ data.
"""

import numpy as np
from scipy import signal
from typing import Optional, Tuple, Union
import logging

logger = logging.getLogger(__name__)


class DSPUtils:
    """Utility class for common DSP operations on IQ data."""
    
    @staticmethod
    def frequency_shift(iq_data: np.ndarray, shift_freq: float, sample_rate: float) -> np.ndarray:
        """
        Apply frequency shift to IQ data.
        
        Args:
            iq_data: Complex IQ data
            shift_freq: Frequency shift in Hz (positive = shift up, negative = shift down)
            sample_rate: Sample rate in Hz
            
        Returns:
            Frequency-shifted IQ data
        """
        t = np.arange(len(iq_data)) / sample_rate
        shift_signal = np.exp(1j * 2 * np.pi * shift_freq * t)
        return iq_data * shift_signal
    
    @staticmethod
    def low_pass_filter(
        iq_data: np.ndarray,
        cutoff_freq: float,
        sample_rate: float,
        filter_order: int = 5,
        filter_type: str = "butterworth"
    ) -> np.ndarray:
        """
        Apply low-pass filter to IQ data.
        
        Args:
            iq_data: Complex IQ data
            cutoff_freq: Cutoff frequency in Hz
            sample_rate: Sample rate in Hz
            filter_order: Filter order
            filter_type: Filter type ('butterworth', 'chebyshev', 'elliptic')
            
        Returns:
            Filtered IQ data
        """
        nyquist = sample_rate / 2
        normalized_cutoff = cutoff_freq / nyquist
        
        if normalized_cutoff >= 1.0:
            logger.warning(f"Cutoff frequency {cutoff_freq} >= Nyquist frequency {nyquist}")
            return iq_data
        
        if filter_type == "butterworth":
            b, a = signal.butter(filter_order, normalized_cutoff, btype='low')
        elif filter_type == "chebyshev":
            b, a = signal.cheby1(filter_order, 0.5, normalized_cutoff, btype='low')
        elif filter_type == "elliptic":
            b, a = signal.ellip(filter_order, 0.5, 40, normalized_cutoff, btype='low')
        else:
            raise ValueError(f"Unknown filter type: {filter_type}")
        
        # Apply filter to real and imaginary parts separately
        filtered_real = signal.filtfilt(b, a, np.real(iq_data))
        filtered_imag = signal.filtfilt(b, a, np.imag(iq_data))
        
        return filtered_real + 1j * filtered_imag
    
    @staticmethod
    def band_pass_filter(
        iq_data: np.ndarray,
        low_freq: float,
        high_freq: float,
        sample_rate: float,
        filter_order: int = 5
    ) -> np.ndarray:
        """
        Apply band-pass filter to IQ data.
        
        Args:
            iq_data: Complex IQ data
            low_freq: Low cutoff frequency in Hz
            high_freq: High cutoff frequency in Hz
            sample_rate: Sample rate in Hz
            filter_order: Filter order
            
        Returns:
            Filtered IQ data
        """
        nyquist = sample_rate / 2
        low_normalized = low_freq / nyquist
        high_normalized = high_freq / nyquist
        
        if high_normalized >= 1.0:
            logger.warning(f"High cutoff frequency {high_freq} >= Nyquist frequency {nyquist}")
            high_normalized = 0.99
        
        b, a = signal.butter(filter_order, [low_normalized, high_normalized], btype='band')
        
        # Apply filter to real and imaginary parts separately
        filtered_real = signal.filtfilt(b, a, np.real(iq_data))
        filtered_imag = signal.filtfilt(b, a, np.imag(iq_data))
        
        return filtered_real + 1j * filtered_imag
    
    @staticmethod
    def decimate(
        iq_data: np.ndarray,
        decimation_factor: int,
        filter_before: bool = True
    ) -> np.ndarray:
        """
        Decimate IQ data by an integer factor.
        
        Args:
            iq_data: Complex IQ data
            decimation_factor: Integer decimation factor
            filter_before: Whether to apply anti-aliasing filter before decimation
            
        Returns:
            Decimated IQ data
        """
        if decimation_factor == 1:
            return iq_data
        
        if filter_before:
            # Apply anti-aliasing filter
            # Design a low-pass filter with cutoff at Fs/(2*decimation_factor)
            b, a = signal.butter(8, 1/decimation_factor, btype='low')
            
            # Apply filter
            filtered_real = signal.filtfilt(b, a, np.real(iq_data))
            filtered_imag = signal.filtfilt(b, a, np.imag(iq_data))
            filtered_data = filtered_real + 1j * filtered_imag
        else:
            filtered_data = iq_data
        
        # Decimate
        return filtered_data[::decimation_factor]
    
    @staticmethod
    def resample(
        iq_data: np.ndarray,
        original_rate: float,
        target_rate: float,
        method: str = "polyphase"
    ) -> np.ndarray:
        """
        Resample IQ data to a different sample rate.
        
        Args:
            iq_data: Complex IQ data
            original_rate: Original sample rate in Hz
            target_rate: Target sample rate in Hz
            method: Resampling method ('polyphase', 'fft')
            
        Returns:
            Resampled IQ data
        """
        if abs(original_rate - target_rate) < 1e-6:
            return iq_data
        
        resampling_ratio = target_rate / original_rate
        new_length = int(len(iq_data) * resampling_ratio)
        
        if method == "polyphase":
            # Use scipy's polyphase resampling
            resampled_real = signal.resample_poly(np.real(iq_data), int(target_rate), int(original_rate))
            resampled_imag = signal.resample_poly(np.imag(iq_data), int(target_rate), int(original_rate))
        elif method == "fft":
            # Use FFT-based resampling
            resampled_real = signal.resample(np.real(iq_data), new_length)
            resampled_imag = signal.resample(np.imag(iq_data), new_length)
        else:
            raise ValueError(f"Unknown resampling method: {method}")
        
        return resampled_real + 1j * resampled_imag
    
    @staticmethod
    def remove_dc_offset(iq_data: np.ndarray) -> np.ndarray:
        """
        Remove DC offset from IQ data.
        
        Args:
            iq_data: Complex IQ data
            
        Returns:
            IQ data with DC offset removed
        """
        dc_offset = np.mean(iq_data)
        return iq_data - dc_offset
    
    @staticmethod
    def normalize_power(iq_data: np.ndarray, target_power: float = 1.0) -> np.ndarray:
        """
        Normalize the power of IQ data.
        
        Args:
            iq_data: Complex IQ data
            target_power: Target average power
            
        Returns:
            Power-normalized IQ data
        """
        current_power = np.mean(np.abs(iq_data)**2)
        if current_power > 0:
            scale_factor = np.sqrt(target_power / current_power)
            return iq_data * scale_factor
        else:
            return iq_data
    
    @staticmethod
    def apply_agc(
        iq_data: np.ndarray,
        target_amplitude: float = 0.5,
        attack_rate: float = 0.01,
        decay_rate: float = 0.001
    ) -> np.ndarray:
        """
        Apply Automatic Gain Control (AGC) to IQ data.
        
        Args:
            iq_data: Complex IQ data
            target_amplitude: Target amplitude level
            attack_rate: Rate of gain increase (0-1)
            decay_rate: Rate of gain decrease (0-1)
            
        Returns:
            AGC-processed IQ data
        """
        magnitude = np.abs(iq_data)
        gain = np.ones(len(iq_data))
        current_gain = 1.0
        
        for i in range(len(iq_data)):
            # Calculate desired gain
            if magnitude[i] > 0:
                desired_gain = target_amplitude / magnitude[i]
            else:
                desired_gain = current_gain
            
            # Update gain with attack/decay rates
            if desired_gain > current_gain:
                current_gain += attack_rate * (desired_gain - current_gain)
            else:
                current_gain += decay_rate * (desired_gain - current_gain)
            
            gain[i] = current_gain
        
        return iq_data * gain
    
    @staticmethod
    def hilbert_transform(real_signal: np.ndarray) -> np.ndarray:
        """
        Convert real signal to complex IQ using Hilbert transform.
        
        Args:
            real_signal: Real-valued signal
            
        Returns:
            Complex IQ data
        """
        analytic_signal = signal.hilbert(real_signal)
        return analytic_signal
    
    @staticmethod
    def quadrature_demod(iq_data: np.ndarray, gain: float = 1.0) -> np.ndarray:
        """
        Perform quadrature demodulation (FM demodulation).
        
        Args:
            iq_data: Complex IQ data
            gain: Demodulation gain
            
        Returns:
            Demodulated signal
        """
        # Calculate instantaneous phase
        phase = np.angle(iq_data)
        
        # Unwrap phase to avoid discontinuities
        unwrapped_phase = np.unwrap(phase)
        
        # Calculate derivative (instantaneous frequency)
        inst_freq = np.diff(unwrapped_phase)
        
        # Prepend first value to maintain length
        inst_freq = np.concatenate([[inst_freq[0]], inst_freq])
        
        return inst_freq * gain
    
    @staticmethod
    def envelope_detector(iq_data: np.ndarray) -> np.ndarray:
        """
        Extract envelope (magnitude) from IQ data.
        
        Args:
            iq_data: Complex IQ data
            
        Returns:
            Envelope (magnitude) signal
        """
        return np.abs(iq_data)
    
    @staticmethod
    def create_window(length: int, window_type: str = "hann") -> np.ndarray:
        """
        Create a window function.
        
        Args:
            length: Window length
            window_type: Window type ('hann', 'hamming', 'blackman', 'kaiser')
            
        Returns:
            Window function
        """
        if window_type == "hann":
            return signal.windows.hann(length)
        elif window_type == "hamming":
            return signal.windows.hamming(length)
        elif window_type == "blackman":
            return signal.windows.blackman(length)
        elif window_type == "kaiser":
            return signal.windows.kaiser(length, beta=8.6)
        else:
            raise ValueError(f"Unknown window type: {window_type}")
    
    @staticmethod
    def fir_filter_design(
        cutoff: Union[float, Tuple[float, float]],
        sample_rate: float,
        filter_type: str = "lowpass",
        num_taps: int = 101,
        window: str = "hann"
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Design an FIR filter.
        
        Args:
            cutoff: Cutoff frequency(ies) in Hz
            sample_rate: Sample rate in Hz
            filter_type: Filter type ('lowpass', 'highpass', 'bandpass', 'bandstop')
            num_taps: Number of filter taps
            window: Window function name
            
        Returns:
            Tuple of (filter coefficients, frequency response)
        """
        nyquist = sample_rate / 2
        
        if filter_type in ["lowpass", "highpass"]:
            normalized_cutoff = cutoff / nyquist
            if filter_type == "lowpass":
                taps = signal.firwin(num_taps, normalized_cutoff, window=window)
            else:  # highpass
                taps = signal.firwin(num_taps, normalized_cutoff, window=window, pass_zero=False)
        
        elif filter_type in ["bandpass", "bandstop"]:
            if not isinstance(cutoff, (list, tuple)) or len(cutoff) != 2:
                raise ValueError("Bandpass/bandstop filters require two cutoff frequencies")
            
            low_cutoff, high_cutoff = cutoff
            normalized_cutoffs = [low_cutoff / nyquist, high_cutoff / nyquist]
            
            if filter_type == "bandpass":
                taps = signal.firwin(num_taps, normalized_cutoffs, window=window, pass_zero=False)
            else:  # bandstop
                taps = signal.firwin(num_taps, normalized_cutoffs, window=window)
        
        else:
            raise ValueError(f"Unknown filter type: {filter_type}")
        
        # Calculate frequency response
        w, h = signal.freqz(taps, worN=1024)
        freq_response = w * sample_rate / (2 * np.pi)
        
        return taps, (freq_response, h)
    
    @staticmethod
    def matched_filter(signal_data: np.ndarray, template: np.ndarray) -> np.ndarray:
        """
        Apply matched filter to detect a known signal template.
        
        Args:
            signal_data: Input signal
            template: Template signal to match
            
        Returns:
            Matched filter output
        """
        # Flip and conjugate the template for matched filtering
        matched_template = np.conj(template[::-1])
        
        # Perform convolution
        return np.convolve(signal_data, matched_template, mode='full')
    
    @staticmethod
    def estimate_noise_power(iq_data: np.ndarray, percentile: float = 25) -> float:
        """
        Estimate noise power from IQ data.
        
        Args:
            iq_data: Complex IQ data
            percentile: Percentile to use for noise estimation
            
        Returns:
            Estimated noise power
        """
        power = np.abs(iq_data)**2
        noise_power = np.percentile(power, percentile)
        return float(noise_power)