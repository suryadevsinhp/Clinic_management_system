"""
IQ Signal Decoder - A comprehensive toolkit for IQ signal processing and demodulation.

This package provides tools for decoding both analog and digital signals from
IQ (In-phase/Quadrature) data files commonly used in Software Defined Radio (SDR).
"""

__version__ = "1.0.0"
__author__ = "IQ Signal Decoder Team"

from .core import IQDecoder
from .analog import AnalogDemodulator
from .digital import DigitalDemodulator
from .utils import SignalAnalyzer, FileHandler

__all__ = [
    "IQDecoder",
    "AnalogDemodulator", 
    "DigitalDemodulator",
    "SignalAnalyzer",
    "FileHandler",
]