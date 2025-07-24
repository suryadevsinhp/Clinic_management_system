#!/usr/bin/env python3
"""
Test script for IQ Audio Decoder
Generates sample IQ data and tests decoding functionality
"""

import numpy as np
import matplotlib.pyplot as plt
from iq_audio_decoder import IQAudioDecoder
import os

def generate_test_iq_file(filename="test_signal.iq", duration=5.0, sample_rate=2.4e6):
    """
    Generate a test IQ file with FM modulated audio signal
    
    Args:
        filename: Output filename
        duration: Duration in seconds
        sample_rate: Sample rate in Hz
    """
    print(f"Generating test IQ file: {filename}")
    
    # Time vector
    t = np.arange(0, duration, 1/sample_rate)
    
    # Audio signal parameters
    audio_freq = 1000  # 1 kHz audio tone
    carrier_freq = 100e3  # 100 kHz offset from center
    fm_deviation = 75e3  # 75 kHz deviation (standard FM)
    
    # Generate audio signal (1 kHz tone with some modulation)
    audio_signal = np.sin(2 * np.pi * audio_freq * t)
    audio_signal += 0.3 * np.sin(2 * np.pi * audio_freq * 2.5 * t)  # Add harmonic
    
    # FM modulation
    phase = 2 * np.pi * carrier_freq * t + 2 * np.pi * fm_deviation * np.cumsum(audio_signal) / sample_rate
    
    # Generate IQ signal
    iq_signal = np.exp(1j * phase)
    
    # Add some noise
    noise_power = 0.1
    noise = noise_power * (np.random.randn(len(iq_signal)) + 1j * np.random.randn(len(iq_signal)))
    iq_signal += noise
    
    # Save as complex64
    iq_signal = iq_signal.astype(np.complex64)
    iq_signal.tofile(filename)
    
    print(f"Generated {len(iq_signal)} samples at {sample_rate/1e6:.1f} MHz")
    print(f"File size: {os.path.getsize(filename)} bytes")
    
    return filename

def test_basic_decoding():
    """Test basic FM decoding functionality"""
    print("\n=== Testing Basic FM Decoding ===")
    
    # Generate test file
    test_file = generate_test_iq_file()
    
    # Initialize decoder
    decoder = IQAudioDecoder(sample_rate=2.4e6)
    
    try:
        # Test FM decoding
        print("Testing FM demodulation...")
        audio = decoder.decode_audio(
            filename=test_file,
            demod_type='fm',
            center_freq=100e3,  # We know our test signal offset
            output_file='test_fm_output.wav'
        )
        
        if audio is not None:
            print(f"✓ FM decoding successful! Audio length: {len(audio)} samples")
            print(f"✓ Output saved to: test_fm_output.wav")
        else:
            print("✗ FM decoding failed")
            
    except Exception as e:
        print(f"✗ Error during FM decoding: {e}")
    
    # Test spectrum analysis
    print("\nTesting spectrum analysis...")
    try:
        iq_data = decoder.load_iq_data(test_file)
        decoder.analyze_spectrum(iq_data, show_plot=False)
        print("✓ Spectrum analysis completed")
    except Exception as e:
        print(f"✗ Error during spectrum analysis: {e}")

def test_auto_detection():
    """Test automatic signal detection"""
    print("\n=== Testing Automatic Signal Detection ===")
    
    test_file = "test_signal.iq"
    decoder = IQAudioDecoder(sample_rate=2.4e6)
    
    try:
        print("Testing automatic frequency detection...")
        audio = decoder.decode_audio(
            filename=test_file,
            demod_type='fm',
            center_freq=0,  # Use default center frequency
            output_file='test_auto_output.wav'
        )
        
        if audio is not None:
            print("✓ Auto-detection successful!")
        else:
            print("✗ Auto-detection failed")
            
    except Exception as e:
        print(f"✗ Error during auto-detection: {e}")

def test_frequency_hopping():
    """Test frequency hopping detection"""
    print("\n=== Testing Frequency Hopping Support ===")
    
    test_file = "test_signal.iq"
    decoder = IQAudioDecoder(sample_rate=2.4e6)
    
    try:
        print("Testing frequency hopping detection...")
        # Try multiple frequencies around our known signal
        frequencies = [80e3, 100e3, 120e3, 150e3]
        
        for i, freq in enumerate(frequencies):
            output_file = f'test_hop_{i}.wav'
            audio = decoder.decode_audio(
                filename=test_file,
                demod_type='fm',
                center_freq=freq,
                output_file=output_file
            )
            
            if audio is not None:
                print(f"✓ Signal found at {freq/1000:.1f} kHz")
            else:
                print(f"✗ No signal at {freq/1000:.1f} kHz")
                
    except Exception as e:
        print(f"✗ Error during frequency hopping test: {e}")

def main():
    """Run all tests"""
    print("IQ Audio Decoder Test Suite")
    print("=" * 40)
    
    # Run tests
    test_basic_decoding()
    test_auto_detection()
    test_frequency_hopping()
    
    print("\n=== Test Summary ===")
    print("Generated files:")
    for filename in ['test_signal.iq', 'test_fm_output.wav', 'test_auto_output.wav', 
                     'spectrum_analysis.png']:
        if os.path.exists(filename):
            print(f"✓ {filename} ({os.path.getsize(filename)} bytes)")
    
    print("\nTo use with your own IQ file:")
    print("python3 iq_audio_decoder.py your_file.iq --demod fm --output decoded_audio.wav")

if __name__ == "__main__":
    main()