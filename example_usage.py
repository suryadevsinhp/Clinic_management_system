#!/usr/bin/env python3
"""
Example usage of the IQ Audio Decoder
Demonstrates various ways to decode audio from IQ recordings
"""

from iq_audio_decoder import IQAudioDecoder
import numpy as np
import matplotlib.pyplot as plt

def example_basic_usage():
    """Basic example of decoding an IQ file"""
    print("=== Basic Usage Example ===")
    
    # Initialize decoder with 2.4 MHz sample rate (common for SDR)
    decoder = IQAudioDecoder(sample_rate=2.4e6)
    
    # Example: Decode FM audio from an IQ file
    # Replace 'your_iq_file.iq' with your actual IQ file
    iq_filename = "your_iq_file.iq"
    
    try:
        audio = decoder.decode_audio(
            filename=iq_filename,
            demod_type='fm',
            output_file='decoded_fm_audio.wav'
        )
        print("FM decoding completed!")
    except FileNotFoundError:
        print(f"IQ file '{iq_filename}' not found. Please provide a valid IQ file.")

def example_frequency_hopping():
    """Example for frequency hopping signals"""
    print("\n=== Frequency Hopping Example ===")
    
    decoder = IQAudioDecoder(sample_rate=2.4e6)
    iq_filename = "your_iq_file.iq"
    
    # Try different frequency offsets to find signals
    frequency_offsets = [-500e3, -250e3, 0, 250e3, 500e3]  # -500kHz to +500kHz
    
    for i, freq_offset in enumerate(frequency_offsets):
        try:
            print(f"Trying frequency offset: {freq_offset/1e3:.1f} kHz")
            audio = decoder.decode_audio(
                filename=iq_filename,
                center_freq=freq_offset,
                demod_type='fm',
                bandwidth=200e3,  # 200 kHz bandwidth
                output_file=f'decoded_audio_offset_{i}.wav'
            )
            print(f"Audio saved as: decoded_audio_offset_{i}.wav")
        except FileNotFoundError:
            print(f"IQ file '{iq_filename}' not found.")
            break

def example_different_modulations():
    """Example trying different demodulation types"""
    print("\n=== Different Modulation Types Example ===")
    
    decoder = IQAudioDecoder(sample_rate=2.4e6)
    iq_filename = "your_iq_file.iq"
    
    modulations = ['fm', 'am', 'usb', 'lsb']
    
    for mod_type in modulations:
        try:
            print(f"Trying {mod_type.upper()} demodulation...")
            audio = decoder.decode_audio(
                filename=iq_filename,
                demod_type=mod_type,
                output_file=f'decoded_{mod_type}_audio.wav'
            )
            print(f"{mod_type.upper()} audio saved as: decoded_{mod_type}_audio.wav")
        except FileNotFoundError:
            print(f"IQ file '{iq_filename}' not found.")
            break

def example_different_data_types():
    """Example for different IQ data formats"""
    print("\n=== Different Data Types Example ===")
    
    decoder = IQAudioDecoder(sample_rate=2.4e6)
    
    # Common IQ file formats and their typical extensions
    file_formats = [
        ('your_file.iq', 'complex64'),    # GNU Radio format
        ('your_file.dat', 'float32'),     # Interleaved float32
        ('your_file.raw', 'int16'),       # RTL-SDR format
        ('your_file.bin', 'int8')         # Some SDR formats
    ]
    
    for filename, data_type in file_formats:
        try:
            print(f"Trying to decode {filename} as {data_type}...")
            audio = decoder.decode_audio(
                filename=filename,
                data_type=data_type,
                demod_type='fm',
                output_file=f'decoded_{data_type}_audio.wav'
            )
            print(f"Successfully decoded {filename}")
        except FileNotFoundError:
            print(f"File '{filename}' not found.")
        except Exception as e:
            print(f"Error decoding {filename}: {e}")

def create_test_signal():
    """Create a test IQ signal with FM modulated audio for testing"""
    print("\n=== Creating Test Signal ===")
    
    # Parameters
    sample_rate = 2.4e6
    duration = 5.0  # seconds
    carrier_freq = 100e3  # 100 kHz carrier
    audio_freq = 1000  # 1 kHz audio tone
    fm_deviation = 75e3  # 75 kHz FM deviation
    
    # Time vector
    t = np.arange(0, duration, 1/sample_rate)
    
    # Audio signal (1 kHz tone)
    audio_signal = np.sin(2 * np.pi * audio_freq * t)
    
    # FM modulate the audio
    instantaneous_freq = carrier_freq + fm_deviation * audio_signal
    phase = 2 * np.pi * np.cumsum(instantaneous_freq) / sample_rate
    
    # Create IQ signal
    iq_signal = np.exp(1j * phase).astype(np.complex64)
    
    # Add some noise
    noise_power = 0.01
    noise = (np.random.randn(len(iq_signal)) + 1j * np.random.randn(len(iq_signal))) * np.sqrt(noise_power)
    iq_signal += noise
    
    # Save test signal
    test_filename = 'test_fm_signal.iq'
    iq_signal.tofile(test_filename)
    print(f"Test signal saved as: {test_filename}")
    
    # Decode the test signal
    decoder = IQAudioDecoder(sample_rate=sample_rate)
    audio = decoder.decode_audio(
        filename=test_filename,
        center_freq=carrier_freq,
        demod_type='fm',
        bandwidth=200e3,
        output_file='decoded_test_audio.wav'
    )
    
    print("Test signal decoded successfully!")
    return test_filename

def analyze_unknown_signal():
    """Example of analyzing an unknown signal step by step"""
    print("\n=== Analyzing Unknown Signal ===")
    
    # This is the recommended approach when you don't know the signal parameters
    decoder = IQAudioDecoder(sample_rate=2.4e6)
    iq_filename = "your_unknown_signal.iq"
    
    try:
        # Step 1: Load and analyze spectrum
        print("Step 1: Loading IQ data and analyzing spectrum...")
        iq_data = decoder.load_iq_data(iq_filename, 'complex64')
        if iq_data is not None:
            decoder.analyze_spectrum(iq_data, show_plot=True)
            
            # Step 2: Try different demodulation types
            print("\nStep 2: Trying different demodulation types...")
            
            # Common frequency offsets to try based on spectrum analysis
            freq_offsets = [0, -100e3, 100e3, -200e3, 200e3]
            
            for freq_offset in freq_offsets:
                for mod_type in ['fm', 'am']:
                    try:
                        print(f"Trying {mod_type.upper()} at {freq_offset/1e3:.1f} kHz offset...")
                        audio = decoder.decode_audio(
                            filename=iq_filename,
                            center_freq=freq_offset,
                            demod_type=mod_type,
                            bandwidth=200e3,
                            output_file=f'unknown_{mod_type}_{int(freq_offset/1e3)}khz.wav'
                        )
                        print(f"Saved: unknown_{mod_type}_{int(freq_offset/1e3)}khz.wav")
                    except Exception as e:
                        print(f"Error with {mod_type} at {freq_offset/1e3:.1f} kHz: {e}")
                        
    except FileNotFoundError:
        print(f"File '{iq_filename}' not found.")
        print("Creating a test signal instead...")
        create_test_signal()

def main():
    """Run all examples"""
    print("IQ Audio Decoder - Example Usage")
    print("=" * 40)
    
    # Create a test signal for demonstration
    test_file = create_test_signal()
    
    # Run examples with the test signal
    example_basic_usage()
    example_frequency_hopping()
    example_different_modulations()
    example_different_data_types()
    
    print("\n" + "=" * 40)
    print("Examples completed!")
    print("\nTo use with your own IQ files:")
    print("1. Replace 'your_iq_file.iq' with your actual file path")
    print("2. Adjust sample_rate to match your recording")
    print("3. Try different demodulation types and frequency offsets")
    print("4. Use the spectrum analysis to identify signal locations")

if __name__ == "__main__":
    main()