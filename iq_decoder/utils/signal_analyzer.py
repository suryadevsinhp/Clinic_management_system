"""
Signal analyzer for IQ data - detects signal characteristics and parameters.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.fft import fft, fftfreq, fftshift
import logging
from typing import Dict, Any, Optional, Tuple, List

logger = logging.getLogger(__name__)


class SignalAnalyzer:
    """Analyzes IQ signals to detect characteristics and parameters."""
    
    def __init__(self, sample_rate: float = 2.048e6):
        """
        Initialize the signal analyzer.
        
        Args:
            sample_rate: Sample rate of the IQ data in Hz
        """
        self.sample_rate = sample_rate
        
    def analyze(
        self,
        iq_data: np.ndarray,
        plot: bool = False,
        save_plot: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive signal analysis.
        
        Args:
            iq_data: Complex IQ data
            plot: Whether to show plots
            save_plot: Filename to save plot (optional)
            
        Returns:
            Dictionary with analysis results
        """
        logger.info("Starting signal analysis...")
        
        results = {
            "basic_stats": self._basic_statistics(iq_data),
            "frequency_analysis": self._frequency_analysis(iq_data),
            "power_analysis": self._power_analysis(iq_data),
            "modulation_hints": self._detect_modulation_hints(iq_data),
            "time_analysis": self._time_domain_analysis(iq_data)
        }
        
        if plot or save_plot:
            self._create_analysis_plots(iq_data, results, show=plot, save_path=save_plot)
        
        logger.info("Signal analysis completed")
        return results
    
    def _basic_statistics(self, iq_data: np.ndarray) -> Dict[str, Any]:
        """Calculate basic signal statistics."""
        i_data = np.real(iq_data)
        q_data = np.imag(iq_data)
        magnitude = np.abs(iq_data)
        phase = np.angle(iq_data)
        
        return {
            "sample_count": len(iq_data),
            "duration_seconds": len(iq_data) / self.sample_rate,
            "i_mean": float(np.mean(i_data)),
            "i_std": float(np.std(i_data)),
            "q_mean": float(np.mean(q_data)),
            "q_std": float(np.std(q_data)),
            "magnitude_mean": float(np.mean(magnitude)),
            "magnitude_std": float(np.std(magnitude)),
            "magnitude_max": float(np.max(magnitude)),
            "phase_std": float(np.std(phase)),
            "dc_offset": complex(np.mean(iq_data)),
            "dynamic_range_db": float(20 * np.log10(np.max(magnitude) / (np.mean(magnitude) + 1e-10)))
        }
    
    def _frequency_analysis(self, iq_data: np.ndarray) -> Dict[str, Any]:
        """Analyze frequency domain characteristics."""
        # Use a subset for FFT if data is very large
        max_fft_size = 2**20  # 1M samples max for FFT
        if len(iq_data) > max_fft_size:
            fft_data = iq_data[:max_fft_size]
            logger.info(f"Using first {max_fft_size} samples for FFT analysis")
        else:
            fft_data = iq_data
        
        # Compute FFT
        fft_result = fftshift(fft(fft_data))
        freqs = fftshift(fftfreq(len(fft_data), 1/self.sample_rate))
        power_spectrum = 20 * np.log10(np.abs(fft_result) + 1e-10)
        
        # Find peak frequencies
        peaks, properties = signal.find_peaks(
            power_spectrum,
            height=np.max(power_spectrum) - 20,  # Peaks within 20dB of max
            distance=len(power_spectrum) // 100  # Minimum separation
        )
        
        peak_freqs = freqs[peaks]
        peak_powers = power_spectrum[peaks]
        
        # Sort by power
        sorted_indices = np.argsort(peak_powers)[::-1]
        peak_freqs = peak_freqs[sorted_indices]
        peak_powers = peak_powers[sorted_indices]
        
        # Estimate occupied bandwidth (90% power)
        total_power = np.sum(np.abs(fft_result)**2)
        cumulative_power = np.cumsum(np.abs(fft_result)**2)
        bw_indices = np.where((cumulative_power >= 0.05 * total_power) & 
                             (cumulative_power <= 0.95 * total_power))[0]
        
        if len(bw_indices) > 0:
            bandwidth_90 = freqs[bw_indices[-1]] - freqs[bw_indices[0]]
        else:
            bandwidth_90 = 0
        
        return {
            "center_frequency_estimate": float(freqs[np.argmax(power_spectrum)]),
            "peak_frequencies": peak_freqs[:10].tolist(),  # Top 10 peaks
            "peak_powers_db": peak_powers[:10].tolist(),
            "bandwidth_90_percent": float(abs(bandwidth_90)),
            "spectral_centroid": float(np.sum(freqs * np.abs(fft_result)**2) / np.sum(np.abs(fft_result)**2)),
            "max_power_db": float(np.max(power_spectrum)),
            "noise_floor_db": float(np.percentile(power_spectrum, 10))
        }
    
    def _power_analysis(self, iq_data: np.ndarray) -> Dict[str, Any]:
        """Analyze power characteristics."""
        magnitude = np.abs(iq_data)
        power = magnitude**2
        
        # Calculate average power
        avg_power = np.mean(power)
        peak_power = np.max(power)
        
        # Peak-to-average power ratio
        papr = peak_power / avg_power if avg_power > 0 else 0
        
        # Power distribution analysis
        power_hist, power_bins = np.histogram(10 * np.log10(power + 1e-10), bins=100)
        
        return {
            "average_power": float(avg_power),
            "peak_power": float(peak_power),
            "papr_db": float(10 * np.log10(papr + 1e-10)),
            "rms_power": float(np.sqrt(np.mean(power))),
            "power_std": float(np.std(power)),
            "power_distribution_mode": float(power_bins[np.argmax(power_hist)])
        }
    
    def _detect_modulation_hints(self, iq_data: np.ndarray) -> Dict[str, Any]:
        """Detect hints about the modulation type."""
        magnitude = np.abs(iq_data)
        phase = np.angle(iq_data)
        
        # Instantaneous frequency
        unwrapped_phase = np.unwrap(phase)
        inst_freq = np.diff(unwrapped_phase) * self.sample_rate / (2 * np.pi)
        
        # Phase variations
        phase_diff = np.diff(unwrapped_phase)
        phase_std = np.std(phase_diff)
        
        # Amplitude variations
        amplitude_var = np.var(magnitude) / (np.mean(magnitude)**2 + 1e-10)
        
        # Constellation analysis (simplified)
        # Sample every Nth point to reduce computation
        step = max(1, len(iq_data) // 10000)
        sampled_iq = iq_data[::step]
        
        # Quantize to detect digital modulation patterns
        mag_levels = self._detect_amplitude_levels(np.abs(sampled_iq))
        phase_levels = self._detect_phase_levels(np.angle(sampled_iq))
        
        # Modulation hints based on characteristics
        hints = []
        
        if amplitude_var < 0.1 and phase_std > 0.5:
            hints.append("PSK (constant amplitude, varying phase)")
        
        if amplitude_var > 0.3 and phase_std < 0.3:
            hints.append("ASK/OOK (varying amplitude, constant phase)")
        
        if amplitude_var > 0.1 and phase_std > 0.3:
            hints.append("QAM (varying amplitude and phase)")
        
        if len(mag_levels) <= 2 and len(phase_levels) > 2:
            hints.append("BPSK/QPSK (few amplitude levels, multiple phases)")
        
        freq_var = np.var(inst_freq) if len(inst_freq) > 0 else 0
        if freq_var > 1000:  # Arbitrary threshold
            hints.append("FM/FSK (frequency modulation)")
        
        if not hints:
            hints.append("Unknown modulation")
        
        return {
            "amplitude_variation": float(amplitude_var),
            "phase_variation": float(phase_std),
            "frequency_variation": float(freq_var),
            "amplitude_levels": len(mag_levels),
            "phase_levels": len(phase_levels),
            "likely_modulations": hints,
            "constellation_points": len(sampled_iq)
        }
    
    def _detect_amplitude_levels(self, amplitudes: np.ndarray, threshold: float = 0.1) -> List[float]:
        """Detect discrete amplitude levels in the signal."""
        # Use clustering to find amplitude levels
        hist, bins = np.histogram(amplitudes, bins=50)
        
        # Find peaks in histogram
        peaks, _ = signal.find_peaks(hist, height=len(amplitudes) * 0.01)
        
        levels = []
        for peak in peaks:
            level = (bins[peak] + bins[peak + 1]) / 2
            levels.append(level)
        
        return sorted(levels)
    
    def _detect_phase_levels(self, phases: np.ndarray) -> List[float]:
        """Detect discrete phase levels in the signal."""
        # Wrap phases to [-π, π]
        wrapped_phases = np.angle(np.exp(1j * phases))
        
        # Use histogram to find phase clusters
        hist, bins = np.histogram(wrapped_phases, bins=36)  # 10-degree bins
        
        # Find peaks
        peaks, _ = signal.find_peaks(hist, height=len(phases) * 0.01)
        
        levels = []
        for peak in peaks:
            level = (bins[peak] + bins[peak + 1]) / 2
            levels.append(level)
        
        return sorted(levels)
    
    def _time_domain_analysis(self, iq_data: np.ndarray) -> Dict[str, Any]:
        """Analyze time domain characteristics."""
        magnitude = np.abs(iq_data)
        
        # Autocorrelation analysis
        max_lag = min(1000, len(iq_data) // 10)
        autocorr = np.correlate(magnitude, magnitude, mode='full')
        autocorr = autocorr[autocorr.size // 2:][:max_lag]
        autocorr = autocorr / autocorr[0]  # Normalize
        
        # Find periodic patterns
        peaks, _ = signal.find_peaks(autocorr[1:], height=0.3)
        
        # Symbol rate estimation (rough)
        if len(peaks) > 0:
            # Use the most prominent peak
            main_peak = peaks[np.argmax(autocorr[peaks + 1])] + 1
            estimated_symbol_period = main_peak
            estimated_symbol_rate = self.sample_rate / estimated_symbol_period
        else:
            estimated_symbol_rate = None
        
        # Signal activity detection
        threshold = np.mean(magnitude) + 2 * np.std(magnitude)
        active_samples = np.sum(magnitude > threshold)
        activity_ratio = active_samples / len(magnitude)
        
        return {
            "estimated_symbol_rate": float(estimated_symbol_rate) if estimated_symbol_rate else None,
            "autocorr_peaks": peaks.tolist()[:5] if len(peaks) > 0 else [],
            "signal_activity_ratio": float(activity_ratio),
            "burst_detected": activity_ratio < 0.8  # Arbitrary threshold
        }
    
    def _create_analysis_plots(
        self,
        iq_data: np.ndarray,
        results: Dict[str, Any],
        show: bool = False,
        save_path: Optional[str] = None
    ):
        """Create comprehensive analysis plots."""
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        fig.suptitle('IQ Signal Analysis', fontsize=16)
        
        # Time domain plot
        time = np.arange(len(iq_data)) / self.sample_rate
        max_points = 10000  # Limit points for plotting
        if len(iq_data) > max_points:
            step = len(iq_data) // max_points
            plot_time = time[::step]
            plot_iq = iq_data[::step]
        else:
            plot_time = time
            plot_iq = iq_data
        
        axes[0, 0].plot(plot_time, np.real(plot_iq), label='I', alpha=0.7)
        axes[0, 0].plot(plot_time, np.imag(plot_iq), label='Q', alpha=0.7)
        axes[0, 0].set_xlabel('Time (s)')
        axes[0, 0].set_ylabel('Amplitude')
        axes[0, 0].set_title('Time Domain')
        axes[0, 0].legend()
        axes[0, 0].grid(True)
        
        # Frequency domain plot
        fft_size = min(8192, len(iq_data))
        fft_data = iq_data[:fft_size]
        fft_result = fftshift(fft(fft_data))
        freqs = fftshift(fftfreq(fft_size, 1/self.sample_rate)) / 1e6  # MHz
        power_spectrum = 20 * np.log10(np.abs(fft_result) + 1e-10)
        
        axes[0, 1].plot(freqs, power_spectrum)
        axes[0, 1].set_xlabel('Frequency (MHz)')
        axes[0, 1].set_ylabel('Power (dB)')
        axes[0, 1].set_title('Power Spectrum')
        axes[0, 1].grid(True)
        
        # Constellation plot
        step = max(1, len(iq_data) // 5000)
        constellation = iq_data[::step]
        axes[0, 2].scatter(np.real(constellation), np.imag(constellation), alpha=0.5, s=1)
        axes[0, 2].set_xlabel('In-phase')
        axes[0, 2].set_ylabel('Quadrature')
        axes[0, 2].set_title('Constellation Diagram')
        axes[0, 2].grid(True)
        axes[0, 2].axis('equal')
        
        # Magnitude vs time
        magnitude = np.abs(plot_iq)
        axes[1, 0].plot(plot_time, magnitude)
        axes[1, 0].set_xlabel('Time (s)')
        axes[1, 0].set_ylabel('Magnitude')
        axes[1, 0].set_title('Signal Magnitude')
        axes[1, 0].grid(True)
        
        # Phase vs time
        phase = np.angle(plot_iq)
        axes[1, 1].plot(plot_time, phase)
        axes[1, 1].set_xlabel('Time (s)')
        axes[1, 1].set_ylabel('Phase (rad)')
        axes[1, 1].set_title('Signal Phase')
        axes[1, 1].grid(True)
        
        # Histogram of magnitudes
        axes[1, 2].hist(np.abs(iq_data[::max(1, len(iq_data)//10000)]), bins=50, alpha=0.7)
        axes[1, 2].set_xlabel('Magnitude')
        axes[1, 2].set_ylabel('Count')
        axes[1, 2].set_title('Magnitude Distribution')
        axes[1, 2].grid(True)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            logger.info(f"Analysis plot saved to {save_path}")
        
        if show:
            plt.show()
        else:
            plt.close()
    
    def estimate_center_frequency(self, iq_data: np.ndarray) -> float:
        """Estimate the center frequency of the dominant signal."""
        analysis = self._frequency_analysis(iq_data)
        return analysis["center_frequency_estimate"]
    
    def estimate_bandwidth(self, iq_data: np.ndarray) -> float:
        """Estimate the signal bandwidth."""
        analysis = self._frequency_analysis(iq_data)
        return analysis["bandwidth_90_percent"]