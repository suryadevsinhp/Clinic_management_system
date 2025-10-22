"""
File handler for IQ data formats - supports all common SDR file types.
"""

import numpy as np
import struct
import os
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import soundfile as sf
import logging

logger = logging.getLogger(__name__)


class FileHandler:
    """Handles loading and saving of IQ data in various formats."""
    
    # Data type mappings
    DTYPE_MAP = {
        'complex64': np.complex64,
        'complex128': np.complex128,
        'float32': np.float32,
        'float64': np.float64,
        'int16': np.int16,
        'int8': np.int8,
        'uint16': np.uint16,
        'uint8': np.uint8,
    }
    
    # File extension hints
    EXTENSION_HINTS = {
        '.iq': 'complex64',
        '.cfile': 'complex64',
        '.dat': 'complex64',
        '.bin': 'complex64',
        '.raw': 'int16',
        '.cu8': 'uint8',
        '.cs8': 'int8',
        '.cu16': 'uint16',
        '.cs16': 'int16',
        '.cf32': 'complex64',
        '.cf64': 'complex128',
        '.i16': 'int16',
        '.i8': 'int8',
        '.u8': 'uint8',
        '.u16': 'uint16',
        '.complex': 'complex64',
        '.float': 'float32',
    }
    
    def get_file_info(self, filepath: str, data_type: str = "auto") -> Dict[str, Any]:
        """
        Get comprehensive information about an IQ file.
        
        Args:
            filepath: Path to the IQ file
            data_type: Data type hint
            
        Returns:
            Dictionary with file information
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        file_size = filepath.stat().st_size
        
        if data_type == "auto":
            data_type = self.auto_detect_format(filepath)
        
        # Calculate samples and duration estimates
        dtype = self.DTYPE_MAP[data_type]
        bytes_per_sample = dtype().itemsize
        
        if data_type.startswith('complex'):
            sample_count = file_size // bytes_per_sample
        else:
            sample_count = file_size // (bytes_per_sample * 2)  # I and Q
        
        return {
            'filename': filepath.name,
            'file_size_bytes': file_size,
            'file_size_mb': file_size / (1024 * 1024),
            'detected_format': data_type,
            'estimated_samples': sample_count,
            'bytes_per_sample': bytes_per_sample,
            'extension': filepath.suffix.lower()
        }
    
    def auto_detect_format(self, filepath: Path) -> str:
        """Auto-detect the most likely data format."""
        ext = filepath.suffix.lower()
        
        if ext in self.EXTENSION_HINTS:
            return self.EXTENSION_HINTS[ext]
        
        # Fallback to complex64
        return 'complex64'
    
    def load_iq_data(self, filepath: str, data_type: str, sample_rate: float, 
                     max_samples: Optional[int] = None) -> np.ndarray:
        """
        Load IQ data from file.
        
        Args:
            filepath: Path to IQ file
            data_type: Data type
            sample_rate: Sample rate (for reference)
            max_samples: Maximum samples to load (None for all)
            
        Returns:
            Complex IQ data array
        """
        filepath = Path(filepath)
        
        if data_type == "auto":
            data_type = self.auto_detect_format(filepath)
        
        logger.info(f"Loading IQ data: {filepath.name}, format: {data_type}")
        
        # Load based on data type
        if data_type in ['complex64', 'complex128']:
            dtype = self.DTYPE_MAP[data_type]
            data = np.fromfile(filepath, dtype=dtype, count=max_samples)
            
        else:
            # Handle real data types (interleaved I/Q)
            dtype = self.DTYPE_MAP[data_type]
            count = max_samples * 2 if max_samples else -1
            raw_data = np.fromfile(filepath, dtype=dtype, count=count)
            
            # Ensure even number of samples
            if len(raw_data) % 2 != 0:
                raw_data = raw_data[:-1]
            
            # Convert to complex
            iq_pairs = raw_data.reshape(-1, 2)
            data = iq_pairs[:, 0] + 1j * iq_pairs[:, 1]
            
            # Normalize integer data
            if dtype in [np.int16, np.int8, np.uint16, np.uint8]:
                if dtype == np.uint8:
                    data = (data.astype(np.float32) - 127.5) / 127.5
                elif dtype == np.uint16:
                    data = (data.astype(np.float32) - 32767.5) / 32767.5
                elif dtype == np.int8:
                    data = data.astype(np.float32) / 127.0
                elif dtype == np.int16:
                    data = data.astype(np.float32) / 32767.0
        
        logger.info(f"Loaded {len(data)} complex samples")
        return data
    
    def save_audio(self, audio_data: np.ndarray, filepath: str, 
                   sample_rate: float = 48000) -> None:
        """Save audio data to WAV file."""
        # Ensure audio is in valid range
        audio_data = np.clip(audio_data, -1.0, 1.0)
        
        # Save using soundfile
        sf.write(filepath, audio_data, int(sample_rate), format='WAV')
        logger.info(f"Saved audio: {filepath} ({len(audio_data)} samples)")
    
    def save_spectrum_data(self, spectrum_data: Dict[str, Any], filepath: str) -> None:
        """Save spectrum analysis data."""
        np.savez_compressed(filepath, **spectrum_data)
        logger.info(f"Saved spectrum data: {filepath}")
    
    def load_spectrum_data(self, filepath: str) -> Dict[str, Any]:
        """Load spectrum analysis data."""
        data = np.load(filepath)
        return {key: data[key] for key in data.files}