#!/usr/bin/env python3
"""
IQ Audio Decoder
A comprehensive tool for decoding audio from IQ recordings.
Supports various file formats and demodulation techniques.
"""

import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt
import soundfile as sf
from scipy.fft import fft, fftfreq
import argparse
import os
from typing import Tuple, Optional, Union
import warnings
warnings.filterwarnings('ignore')

class IQAudioDecoder:
    def __init__(self, sample_rate: float = 2.4e6):
        """
        Initialize the IQ Audio Decoder
        
        Args:
            sample_rate: Sample rate of the IQ data (Hz)
        """
        self.sample_rate = sample_rate
        self.audio_sample_rate = 48000  # Standard audio sample rate
        
    def load_iq_data(self, filename: str, data_type: str = 'complex64') -> np.ndarray:
        """
        Load IQ data from various file formats
        
        Args:
            filename: Path to the IQ file
            data_type: Data type ('complex64', 'float32', 'int16', 'int8')
            
        Returns:
            Complex IQ data array
        """
        print(f"Loading IQ data from {filename}...")
        
        try:
            if data_type == 'complex64':
                # Direct complex data
                iq_data = np.fromfile(filename, dtype=np.complex64)
            elif data_type == 'float32':
                # Interleaved I/Q float32
                data = np.fromfile(filename, dtype=np.float32)
                iq_data = data[::2] + 1j * data[1::2]
            elif data_type == 'int16':
                # Interleaved I/Q int16
                data = np.fromfile(filename, dtype=np.int16)
                # Normalize to [-1, 1]
                data = data.astype(np.float32) / 32768.0
                iq_data = data[::2] + 1j * data[1::2]
            elif data_type == 'int8':
                # Interleaved I/Q int8
                data = np.fromfile(filename, dtype=np.int8)
                # Normalize to [-1, 1]
                data = data.astype(np.float32) / 128.0
                iq_data = data[::2] + 1j * data[1::2]
            else:
                raise ValueError(f"Unsupported data type: {data_type}")
                
            print(f"Loaded {len(iq_data)} IQ samples")
            return iq_data
            
        except Exception as e:
            print(f"Error loading IQ data: {e}")
            return None
    
    def analyze_spectrum(self, iq_data: np.ndarray, show_plot: bool = True) -> None:
        """
        Analyze and plot the frequency spectrum of IQ data
        
        Args:
            iq_data: Complex IQ data
            show_plot: Whether to display the plot
        """
        print("Analyzing frequency spectrum...")
        
        # Calculate FFT
        fft_data = fft(iq_data[:min(len(iq_data), 1024*1024)])  # Use up to 1M samples
        freqs = fftfreq(len(fft_data), 1/self.sample_rate)
        
        # Calculate power spectrum
        power_db = 20 * np.log10(np.abs(fft_data) + 1e-12)
        
        if show_plot:
            plt.figure(figsize=(12, 6))
            plt.plot(freqs/1e6, power_db)
            plt.xlabel('Frequency (MHz)')
            plt.ylabel('Power (dB)')
            plt.title('IQ Data Frequency Spectrum')
            plt.grid(True)
            plt.show()
        
        # Find peak frequencies
        peaks, _ = signal.find_peaks(power_db, height=np.max(power_db) - 20)
        peak_freqs = freqs[peaks]
        
        print(f"Found {len(peaks)} significant peaks:")
        for i, freq in enumerate(peak_freqs[:10]):  # Show top 10 peaks
            print(f"  Peak {i+1}: {freq/1e6:.3f} MHz")
    
    def frequency_shift(self, iq_data: np.ndarray, shift_freq: float) -> np.ndarray:
        """
        Frequency shift (mix down) the IQ data
        
        Args:
            iq_data: Complex IQ data
            shift_freq: Frequency to shift by (Hz)
            
        Returns:
            Frequency-shifted IQ data
        """
        t = np.arange(len(iq_data)) / self.sample_rate
        lo = np.exp(-1j * 2 * np.pi * shift_freq * t)
        return iq_data * lo
    
    def lowpass_filter(self, data: np.ndarray, cutoff_freq: float, order: int = 5) -> np.ndarray:
        """
        Apply lowpass filter to data
        
        Args:
            data: Input data
            cutoff_freq: Cutoff frequency (Hz)
            order: Filter order
            
        Returns:
            Filtered data
        """
        nyquist = self.sample_rate / 2
        normal_cutoff = cutoff_freq / nyquist
        b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
        return signal.filtfilt(b, a, data)
    
    def decimate_signal(self, data: np.ndarray, decimation_factor: int) -> np.ndarray:
        """
        Decimate signal to reduce sample rate
        
        Args:
            data: Input data
            decimation_factor: Factor to decimate by
            
        Returns:
            Decimated data
        """
        return signal.decimate(data, decimation_factor, ftype='fir')
    
    def fm_demodulate(self, iq_data: np.ndarray) -> np.ndarray:
        """
        FM demodulation using phase differentiation
        
        Args:
            iq_data: Complex IQ data
            
        Returns:
            Demodulated audio signal
        """
        print("Performing FM demodulation...")
        
        # Calculate instantaneous phase
        phase = np.unwrap(np.angle(iq_data))
        
        # Differentiate to get frequency
        audio = np.diff(phase)
        
        # Remove DC component
        audio = audio - np.mean(audio)
        
        return audio
    
    def am_demodulate(self, iq_data: np.ndarray) -> np.ndarray:
        """
        AM demodulation using magnitude detection
        
        Args:
            iq_data: Complex IQ data
            
        Returns:
            Demodulated audio signal
        """
        print("Performing AM demodulation...")
        
        # Calculate magnitude
        audio = np.abs(iq_data)
        
        # Remove DC component
        audio = audio - np.mean(audio)
        
        return audio
    
    def ssb_demodulate(self, iq_data: np.ndarray, mode: str = 'usb') -> np.ndarray:
        """
        Single Sideband (SSB) demodulation
        
        Args:
            iq_data: Complex IQ data
            mode: 'usb' for upper sideband, 'lsb' for lower sideband
            
        Returns:
            Demodulated audio signal
        """
        print(f"Performing SSB demodulation ({mode.upper()})...")
        
        if mode.lower() == 'usb':
            # Upper sideband: take real part
            audio = np.real(iq_data)
        else:
            # Lower sideband: take imaginary part
            audio = np.imag(iq_data)
        
        # Remove DC component
        audio = audio - np.mean(audio)
        
        return audio
    
    def process_audio(self, audio: np.ndarray, target_sample_rate: int = None) -> np.ndarray:
        """
        Process demodulated audio for output
        
        Args:
            audio: Demodulated audio signal
            target_sample_rate: Target sample rate for output
            
        Returns:
            Processed audio signal
        """
        if target_sample_rate is None:
            target_sample_rate = self.audio_sample_rate
        
        print("Processing audio...")
        
        # Calculate decimation factor
        decimation_factor = int(self.sample_rate / target_sample_rate)
        
        if decimation_factor > 1:
            # Apply anti-aliasing filter before decimation
            cutoff = target_sample_rate / 2 * 0.8  # 80% of Nyquist
            audio = self.lowpass_filter(audio, cutoff)
            
            # Decimate
            audio = self.decimate_signal(audio, decimation_factor)
            self.sample_rate = self.sample_rate / decimation_factor
        
        # Normalize audio
        if np.max(np.abs(audio)) > 0:
            audio = audio / np.max(np.abs(audio)) * 0.8
        
        return audio
    
    def save_audio(self, audio: np.ndarray, filename: str, sample_rate: int = None) -> None:
        """
        Save audio to file
        
        Args:
            audio: Audio signal
            filename: Output filename
            sample_rate: Sample rate for output file
        """
        if sample_rate is None:
            sample_rate = self.audio_sample_rate
        
        print(f"Saving audio to {filename}...")
        
        # Ensure audio is real
        if np.iscomplexobj(audio):
            audio = np.real(audio)
        
        # Convert to appropriate data type
        audio = np.clip(audio, -1.0, 1.0)
        
        try:
            sf.write(filename, audio, sample_rate)
            print(f"Audio saved successfully to {filename}")
        except Exception as e:
            print(f"Error saving audio: {e}")
    
    def decode_audio(self, filename: str, 
                    center_freq: float = 0,
                    demod_type: str = 'fm',
                    data_type: str = 'complex64',
                    bandwidth: float = None,
                    output_file: str = None) -> np.ndarray:
        """
        Main function to decode audio from IQ file
        
        Args:
            filename: IQ file path
            center_freq: Center frequency offset for mixing (Hz)
            demod_type: Demodulation type ('fm', 'am', 'usb', 'lsb')
            data_type: IQ data type
            bandwidth: Audio bandwidth (Hz)
            output_file: Output audio file path
            
        Returns:
            Decoded audio signal
        """
        # Load IQ data
        iq_data = self.load_iq_data(filename, data_type)
        if iq_data is None:
            return None
        
        # Analyze spectrum
        self.analyze_spectrum(iq_data)
        
        # Frequency shift if needed
        if center_freq != 0:
            print(f"Frequency shifting by {center_freq/1e6:.3f} MHz...")
            iq_data = self.frequency_shift(iq_data, center_freq)
        
        # Apply bandwidth filter if specified
        if bandwidth is not None:
            print(f"Applying bandwidth filter: {bandwidth/1e3:.1f} kHz...")
            iq_data = self.lowpass_filter(iq_data, bandwidth/2)
        
        # Demodulate based on type
        if demod_type.lower() == 'fm':
            audio = self.fm_demodulate(iq_data)
        elif demod_type.lower() == 'am':
            audio = self.am_demodulate(iq_data)
        elif demod_type.lower() in ['usb', 'lsb']:
            audio = self.ssb_demodulate(iq_data, demod_type.lower())
        else:
            raise ValueError(f"Unsupported demodulation type: {demod_type}")
        
        # Process audio for output
        audio = self.process_audio(audio)
        
        # Save audio if output file specified
        if output_file:
            self.save_audio(audio, output_file)
        
        return audio


def main():
    parser = argparse.ArgumentParser(description='Decode audio from IQ recordings')
    parser.add_argument('input_file', help='Input IQ file path')
    parser.add_argument('-o', '--output', help='Output audio file path')
    parser.add_argument('-s', '--sample-rate', type=float, default=2.4e6,
                       help='IQ sample rate (Hz, default: 2.4MHz)')
    parser.add_argument('-f', '--frequency', type=float, default=0,
                       help='Center frequency offset (Hz, default: 0)')
    parser.add_argument('-d', '--demod', choices=['fm', 'am', 'usb', 'lsb'], 
                       default='fm', help='Demodulation type (default: fm)')
    parser.add_argument('-t', '--type', choices=['complex64', 'float32', 'int16', 'int8'],
                       default='complex64', help='IQ data type (default: complex64)')
    parser.add_argument('-b', '--bandwidth', type=float,
                       help='Audio bandwidth (Hz)')
    parser.add_argument('--no-plot', action='store_true',
                       help='Disable spectrum plot')
    
    args = parser.parse_args()
    
    # Create decoder
    decoder = IQAudioDecoder(sample_rate=args.sample_rate)
    
    # Set output filename if not provided
    if not args.output:
        base_name = os.path.splitext(args.input_file)[0]
        args.output = f"{base_name}_{args.demod}_audio.wav"
    
    # Decode audio
    try:
        audio = decoder.decode_audio(
            filename=args.input_file,
            center_freq=args.frequency,
            demod_type=args.demod,
            data_type=args.type,
            bandwidth=args.bandwidth,
            output_file=args.output
        )
        
        if audio is not None:
            print(f"\nDecoding completed successfully!")
            print(f"Output saved to: {args.output}")
            print(f"Audio length: {len(audio)/decoder.audio_sample_rate:.2f} seconds")
        else:
            print("Decoding failed!")
            
    except Exception as e:
        print(f"Error during decoding: {e}")


if __name__ == "__main__":
    main()