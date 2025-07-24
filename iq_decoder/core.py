"""
Core IQ Decoder class that provides the main interface for signal processing.
"""

import numpy as np
import logging
from typing import Optional, Union, Tuple, Dict, Any, List
from pathlib import Path

from .utils import SignalAnalyzer, FileHandler
from .analog import AnalogDemodulator
from .digital import DigitalDemodulator

logger = logging.getLogger(__name__)


class IQDecoder:
    """
    Main IQ decoder class that orchestrates signal processing and demodulation.
    
    This class provides a high-level interface for loading IQ data, analyzing signals,
    and applying various analog and digital demodulation techniques.
    """
    
    def __init__(self, sample_rate: float = 2.048e6, verbose: bool = False):
        """
        Initialize the IQ decoder.
        
        Args:
            sample_rate: Sample rate of the IQ data in Hz
            verbose: Enable verbose logging
        """
        self.sample_rate = sample_rate
        self.verbose = verbose
        
        # Initialize components
        self.file_handler = FileHandler()
        self.signal_analyzer = SignalAnalyzer(sample_rate=sample_rate)
        self.analog_demod = AnalogDemodulator(sample_rate=sample_rate)
        self.digital_demod = DigitalDemodulator(sample_rate=sample_rate)
        
        # Configure logging
        if verbose:
            logging.basicConfig(level=logging.INFO)
        
        logger.info(f"IQ Decoder initialized with sample rate: {sample_rate:e} Hz")
    
    def load_iq_data(
        self, 
        filepath: Union[str, Path],
        data_type: str = "auto",
        interleaved: bool = True,
        offset: int = 0,
        count: Optional[int] = None
    ) -> np.ndarray:
        """
        Load IQ data from file.
        
        Args:
            filepath: Path to the IQ data file
            data_type: Data type ('complex64', 'complex128', 'float32', 'int16', 'int8', 'auto')
            interleaved: Whether I/Q samples are interleaved (True) or separate (False)
            offset: Number of samples to skip from beginning
            count: Maximum number of samples to read (None for all)
            
        Returns:
            Complex IQ data array
        """
        return self.file_handler.load_iq_data(
            filepath=filepath,
            data_type=data_type,
            interleaved=interleaved,
            offset=offset,
            count=count
        )
    
    def analyze_signal(
        self,
        iq_data: np.ndarray,
        plot: bool = False,
        save_plot: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze the IQ signal to identify characteristics.
        
        Args:
            iq_data: Complex IQ data
            plot: Whether to show plots
            save_plot: Filename to save plot (optional)
            
        Returns:
            Dictionary with signal analysis results
        """
        return self.signal_analyzer.analyze(
            iq_data=iq_data,
            plot=plot,
            save_plot=save_plot
        )
    
    def decode_analog(
        self,
        iq_data: np.ndarray,
        demod_type: str = "fm",
        center_freq: float = 0.0,
        bandwidth: Optional[float] = None,
        output_rate: float = 48000,
        **kwargs
    ) -> np.ndarray:
        """
        Decode analog modulated signal.
        
        Args:
            iq_data: Complex IQ data
            demod_type: Demodulation type ('fm', 'am', 'usb', 'lsb', 'wfm')
            center_freq: Center frequency offset for tuning
            bandwidth: Signal bandwidth (auto-detect if None)
            output_rate: Output audio sample rate
            **kwargs: Additional demodulator-specific parameters
            
        Returns:
            Demodulated audio data
        """
        return self.analog_demod.demodulate(
            iq_data=iq_data,
            demod_type=demod_type,
            center_freq=center_freq,
            bandwidth=bandwidth,
            output_rate=output_rate,
            **kwargs
        )
    
    def decode_digital(
        self,
        iq_data: np.ndarray,
        modulation: str = "psk",
        symbol_rate: Optional[float] = None,
        **kwargs
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Decode digital modulated signal.
        
        Args:
            iq_data: Complex IQ data
            modulation: Modulation type ('psk', 'qpsk', 'fsk', 'gfsk', 'qam', 'oqpsk')
            symbol_rate: Symbol rate in symbols/second (auto-detect if None)
            **kwargs: Additional demodulator-specific parameters
            
        Returns:
            Tuple of (decoded bits, metadata dictionary)
        """
        return self.digital_demod.demodulate(
            iq_data=iq_data,
            modulation=modulation,
            symbol_rate=symbol_rate,
            **kwargs
        )
    
    def auto_decode(
        self,
        filepath: Union[str, Path],
        data_type: str = "auto",
        output_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Automatically analyze and decode IQ file with multiple techniques.
        
        Args:
            filepath: Path to IQ file
            data_type: Data type of IQ file
            output_dir: Directory to save outputs (optional)
            
        Returns:
            Dictionary with all decoding results
        """
        logger.info(f"Auto-decoding file: {filepath}")
        
        # Load IQ data
        iq_data = self.load_iq_data(filepath, data_type=data_type)
        logger.info(f"Loaded {len(iq_data)} IQ samples")
        
        # Analyze signal
        analysis = self.analyze_signal(iq_data, plot=False)
        logger.info(f"Signal analysis completed")
        
        results = {
            "file_info": {
                "filepath": str(filepath),
                "samples": len(iq_data),
                "duration": len(iq_data) / self.sample_rate,
                "data_type": data_type
            },
            "analysis": analysis,
            "analog_results": {},
            "digital_results": {}
        }
        
        # Try analog demodulation techniques
        analog_types = ["fm", "am", "usb", "lsb", "wfm"]
        for demod_type in analog_types:
            try:
                logger.info(f"Trying {demod_type.upper()} demodulation...")
                audio = self.decode_analog(iq_data, demod_type=demod_type)
                
                # Save audio if output directory specified
                if output_dir:
                    output_path = Path(output_dir) / f"{Path(filepath).stem}_{demod_type}.wav"
                    self.file_handler.save_audio(audio, str(output_path))
                    logger.info(f"Saved {demod_type} audio to {output_path}")
                
                results["analog_results"][demod_type] = {
                    "success": True,
                    "samples": len(audio),
                    "peak_amplitude": np.max(np.abs(audio)),
                    "rms": np.sqrt(np.mean(audio**2))
                }
                
            except Exception as e:
                logger.warning(f"{demod_type.upper()} demodulation failed: {e}")
                results["analog_results"][demod_type] = {
                    "success": False,
                    "error": str(e)
                }
        
        # Try digital demodulation techniques
        digital_types = ["psk", "qpsk", "fsk", "gfsk"]
        for modulation in digital_types:
            try:
                logger.info(f"Trying {modulation.upper()} demodulation...")
                bits, metadata = self.decode_digital(iq_data, modulation=modulation)
                
                # Save bits if output directory specified
                if output_dir:
                    output_path = Path(output_dir) / f"{Path(filepath).stem}_{modulation}.bin"
                    self.file_handler.save_bits(bits, str(output_path))
                    logger.info(f"Saved {modulation} bits to {output_path}")
                
                results["digital_results"][modulation] = {
                    "success": True,
                    "bit_count": len(bits),
                    "metadata": metadata
                }
                
            except Exception as e:
                logger.warning(f"{modulation.upper()} demodulation failed: {e}")
                results["digital_results"][modulation] = {
                    "success": False,
                    "error": str(e)
                }
        
        logger.info("Auto-decoding completed")
        return results
    
    def frequency_hop_decode(
        self,
        iq_data: np.ndarray,
        freq_list: List[float],
        demod_type: str = "fm",
        hop_duration: float = 0.1,
        **kwargs
    ) -> Dict[float, np.ndarray]:
        """
        Decode frequency hopping signals by trying different frequencies.
        
        Args:
            iq_data: Complex IQ data
            freq_list: List of frequencies to try
            demod_type: Demodulation type
            hop_duration: Duration per frequency in seconds
            **kwargs: Additional demodulation parameters
            
        Returns:
            Dictionary mapping frequencies to decoded audio
        """
        logger.info(f"Frequency hopping decode with {len(freq_list)} frequencies")
        
        hop_samples = int(hop_duration * self.sample_rate)
        results = {}
        
        for i, freq in enumerate(freq_list):
            start_idx = i * hop_samples
            end_idx = min(start_idx + hop_samples, len(iq_data))
            
            if start_idx >= len(iq_data):
                break
                
            segment = iq_data[start_idx:end_idx]
            
            try:
                audio = self.decode_analog(
                    segment,
                    demod_type=demod_type,
                    center_freq=freq,
                    **kwargs
                )
                results[freq] = audio
                logger.info(f"Decoded frequency {freq/1e3:.1f} kHz")
                
            except Exception as e:
                logger.warning(f"Failed to decode frequency {freq/1e3:.1f} kHz: {e}")
        
        return results