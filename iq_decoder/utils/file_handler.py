"""
File handler for IQ data formats and audio output.
"""

import numpy as np
import struct
import logging
from pathlib import Path
from typing import Optional, Union, Tuple, Dict, Any
import soundfile as sf

logger = logging.getLogger(__name__)


class FileHandler:
    """Handles loading and saving of IQ data and audio files."""
    
    # Common data type mappings
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
    
    # Common file extensions and their likely formats
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
    }
    
    def __init__(self):
        """Initialize the file handler."""
        pass
    
    def auto_detect_format(self, filepath: Union[str, Path]) -> str:
        """
        Auto-detect the most likely data format based on file extension and size.
        
        Args:
            filepath: Path to the file
            
        Returns:
            Detected data type string
        """
        filepath = Path(filepath)
        
        # Check extension first
        ext = filepath.suffix.lower()
        if ext in self.EXTENSION_HINTS:
            detected = self.EXTENSION_HINTS[ext]
            logger.info(f"Format detected from extension '{ext}': {detected}")
            return detected
        
        # Fallback: analyze file size to guess format
        file_size = filepath.stat().st_size
        
        # Try different formats and see which gives reasonable sample counts
        candidates = ['complex64', 'int16', 'int8', 'uint8']
        best_format = 'complex64'  # default
        
        for fmt in candidates:
            dtype = self.DTYPE_MAP[fmt]
            bytes_per_sample = dtype().itemsize
            if fmt.startswith('complex'):
                bytes_per_sample *= 2  # I and Q components
            
            if file_size % bytes_per_sample == 0:
                sample_count = file_size // bytes_per_sample
                logger.info(f"Format {fmt}: {sample_count} samples")
                best_format = fmt
                break
        
        logger.info(f"Auto-detected format: {best_format}")
        return best_format
    
    def load_iq_data(
        self,
        filepath: Union[str, Path],
        data_type: str = "auto",
        interleaved: bool = True,
        offset: int = 0,
        count: Optional[int] = None
    ) -> np.ndarray:
        """
        Load IQ data from various file formats.
        
        Args:
            filepath: Path to the IQ data file
            data_type: Data type ('complex64', 'complex128', 'float32', 'int16', 'int8', 'auto')
            interleaved: Whether I/Q samples are interleaved (True) or separate (False)
            offset: Number of samples to skip from beginning
            count: Maximum number of samples to read (None for all)
            
        Returns:
            Complex IQ data array
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        if data_type == "auto":
            data_type = self.auto_detect_format(filepath)
        
        logger.info(f"Loading IQ data: {filepath}")
        logger.info(f"Data type: {data_type}, Interleaved: {interleaved}")
        
        # Handle complex data types
        if data_type in ['complex64', 'complex128']:
            dtype = self.DTYPE_MAP[data_type]
            data = np.fromfile(filepath, dtype=dtype, offset=offset, count=count)
            logger.info(f"Loaded {len(data)} complex samples")
            return data
        
        # Handle real data types (need to convert to complex)
        dtype = self.DTYPE_MAP[data_type]
        
        if interleaved:
            # I and Q samples are interleaved: I1, Q1, I2, Q2, ...
            raw_data = np.fromfile(filepath, dtype=dtype, offset=offset*2, count=count*2 if count else None)
            
            # Ensure even number of samples
            if len(raw_data) % 2 != 0:
                raw_data = raw_data[:-1]
            
            # Reshape and create complex data
            iq_pairs = raw_data.reshape(-1, 2)
            data = iq_pairs[:, 0] + 1j * iq_pairs[:, 1]
            
        else:
            # I and Q samples are in separate blocks: I1, I2, ... Q1, Q2, ...
            raw_data = np.fromfile(filepath, dtype=dtype, offset=offset, count=count*2 if count else None)
            
            # Split into I and Q parts
            half = len(raw_data) // 2
            i_data = raw_data[:half]
            q_data = raw_data[half:half*2]
            
            # Create complex data
            data = i_data + 1j * q_data
        
        # Normalize if needed
        if dtype in [np.int16, np.int8, np.uint16, np.uint8]:
            # Normalize integer data to [-1, 1] range
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
    
    def save_iq_data(
        self,
        iq_data: np.ndarray,
        filepath: Union[str, Path],
        data_type: str = "complex64"
    ) -> None:
        """
        Save IQ data to file.
        
        Args:
            iq_data: Complex IQ data
            filepath: Output file path
            data_type: Output data type
        """
        filepath = Path(filepath)
        
        if data_type in ['complex64', 'complex128']:
            dtype = self.DTYPE_MAP[data_type]
            iq_data.astype(dtype).tofile(filepath)
        else:
            # Convert complex to real interleaved format
            dtype = self.DTYPE_MAP[data_type]
            
            # Separate I and Q
            i_data = np.real(iq_data)
            q_data = np.imag(iq_data)
            
            # Normalize and convert if needed
            if dtype in [np.int16, np.int8, np.uint16, np.uint8]:
                if dtype == np.uint8:
                    i_data = np.clip(i_data * 127.5 + 127.5, 0, 255)
                    q_data = np.clip(q_data * 127.5 + 127.5, 0, 255)
                elif dtype == np.uint16:
                    i_data = np.clip(i_data * 32767.5 + 32767.5, 0, 65535)
                    q_data = np.clip(q_data * 32767.5 + 32767.5, 0, 65535)
                elif dtype == np.int8:
                    i_data = np.clip(i_data * 127, -128, 127)
                    q_data = np.clip(q_data * 127, -128, 127)
                elif dtype == np.int16:
                    i_data = np.clip(i_data * 32767, -32768, 32767)
                    q_data = np.clip(q_data * 32767, -32768, 32767)
            
            # Interleave and save
            interleaved = np.column_stack([i_data, q_data]).flatten()
            interleaved.astype(dtype).tofile(filepath)
        
        logger.info(f"Saved IQ data to {filepath}")
    
    def save_audio(
        self,
        audio_data: np.ndarray,
        filepath: Union[str, Path],
        sample_rate: float = 48000,
        format_type: str = "wav"
    ) -> None:
        """
        Save audio data to file.
        
        Args:
            audio_data: Audio samples
            filepath: Output file path
            sample_rate: Audio sample rate
            format_type: Audio format ('wav', 'flac', 'ogg')
        """
        filepath = Path(filepath)
        
        # Ensure audio is in valid range
        audio_data = np.clip(audio_data, -1.0, 1.0)
        
        # Use soundfile for high-quality audio output
        sf.write(str(filepath), audio_data, int(sample_rate), format=format_type.upper())
        
        logger.info(f"Saved audio to {filepath} ({len(audio_data)} samples at {sample_rate} Hz)")
    
    def save_bits(
        self,
        bits: np.ndarray,
        filepath: Union[str, Path],
        format_type: str = "binary"
    ) -> None:
        """
        Save decoded bits to file.
        
        Args:
            bits: Binary data (0s and 1s)
            filepath: Output file path
            format_type: Output format ('binary', 'hex', 'text')
        """
        filepath = Path(filepath)
        
        if format_type == "binary":
            # Pack bits into bytes
            bits_padded = np.pad(bits, (0, (8 - len(bits) % 8) % 8))
            bytes_data = np.packbits(bits_padded)
            bytes_data.tofile(filepath)
            
        elif format_type == "hex":
            # Save as hexadecimal text
            bits_padded = np.pad(bits, (0, (8 - len(bits) % 8) % 8))
            bytes_data = np.packbits(bits_padded)
            hex_string = bytes_data.tobytes().hex()
            with open(filepath, 'w') as f:
                f.write(hex_string)
                
        elif format_type == "text":
            # Save as binary text (0s and 1s)
            bit_string = ''.join(map(str, bits.astype(int)))
            with open(filepath, 'w') as f:
                f.write(bit_string)
        
        logger.info(f"Saved {len(bits)} bits to {filepath} (format: {format_type})")
    
    def get_file_info(self, filepath: Union[str, Path]) -> Dict[str, Any]:
        """
        Get information about an IQ file.
        
        Args:
            filepath: Path to the file
            
        Returns:
            Dictionary with file information
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        file_size = filepath.stat().st_size
        detected_format = self.auto_detect_format(filepath)
        
        # Calculate sample count
        dtype = self.DTYPE_MAP[detected_format]
        bytes_per_sample = dtype().itemsize
        if detected_format.startswith('complex'):
            sample_count = file_size // bytes_per_sample
        else:
            sample_count = file_size // (bytes_per_sample * 2)  # I and Q
        
        return {
            "filepath": str(filepath),
            "file_size": file_size,
            "detected_format": detected_format,
            "estimated_samples": sample_count,
            "bytes_per_sample": bytes_per_sample
        }