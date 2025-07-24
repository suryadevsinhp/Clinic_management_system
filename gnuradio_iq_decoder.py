#!/usr/bin/env python3
"""
GNU Radio IQ Audio Decoder
Advanced IQ audio decoding using GNU Radio blocks for better performance
and more sophisticated signal processing capabilities.
"""

try:
    from gnuradio import gr, analog, audio, blocks, filter as gr_filter
    from gnuradio.filter import firdes
    GNURADIO_AVAILABLE = True
except ImportError:
    print("GNU Radio not available. Install GNU Radio for advanced features.")
    GNURADIO_AVAILABLE = False

import numpy as np
import argparse
import os
import time

class GNURadioIQDecoder(gr.top_block):
    """GNU Radio-based IQ decoder flowgraph"""
    
    def __init__(self, input_file, sample_rate, center_freq=0, 
                 demod_type='fm', audio_rate=48000, output_file=None):
        gr.top_block.__init__(self, "IQ Audio Decoder")
        
        if not GNURADIO_AVAILABLE:
            raise ImportError("GNU Radio is not available")
        
        self.sample_rate = sample_rate
        self.audio_rate = audio_rate
        self.center_freq = center_freq
        self.demod_type = demod_type.lower()
        self.output_file = output_file
        
        # Calculate decimation
        self.audio_decimation = int(sample_rate / audio_rate)
        self.intermediate_rate = sample_rate / self.audio_decimation
        
        # File source
        self.file_source = blocks.file_source(
            gr.sizeof_gr_complex, input_file, False)
        
        # Frequency translation (if needed)
        if center_freq != 0:
            self.freq_xlating_fir = filter.freq_xlating_fir_filter_ccc(
                1, [1], center_freq, sample_rate)
            self.connect(self.file_source, self.freq_xlating_fir)
            source_block = self.freq_xlating_fir
        else:
            source_block = self.file_source
        
        # Low-pass filter
        cutoff_freq = audio_rate / 2
        transition_width = audio_rate / 10
        
        lpf_taps = firdes.low_pass(
            1, sample_rate, cutoff_freq, transition_width,
            firdes.WIN_HAMMING, 6.76)
        
        self.low_pass_filter = gr_filter.fir_filter_ccf(
            self.audio_decimation, lpf_taps)
        
        self.connect(source_block, self.low_pass_filter)
        
        # Demodulation
        if self.demod_type == 'fm':
            # FM demodulation
            max_dev = 75000  # Maximum deviation in Hz
            self.fm_demod = analog.fm_demod_cf(
                channel_rate=self.intermediate_rate,
                audio_decim=1,
                deviation=max_dev,
                audio_pass=15000,
                audio_stop=16000,
                gain=1.0,
                tau=75e-6)
            
            self.connect(self.low_pass_filter, self.fm_demod)
            demod_output = self.fm_demod
            
        elif self.demod_type == 'am':
            # AM demodulation
            self.am_demod = analog.am_demod_cf(
                channel_rate=self.intermediate_rate,
                audio_decim=1,
                audio_pass=5000,
                audio_stop=5500)
            
            self.connect(self.low_pass_filter, self.am_demod)
            demod_output = self.am_demod
            
        elif self.demod_type == 'ssb':
            # SSB demodulation (USB)
            self.ssb_demod = blocks.complex_to_real(1)
            self.connect(self.low_pass_filter, self.ssb_demod)
            demod_output = self.ssb_demod
            
        else:
            raise ValueError(f"Unsupported demodulation type: {self.demod_type}")
        
        # Audio processing
        # High-pass filter to remove DC
        hp_cutoff = 100  # 100 Hz high-pass
        hp_taps = firdes.high_pass(
            1, self.intermediate_rate, hp_cutoff, 50,
            firdes.WIN_HAMMING, 6.76)
        
        self.high_pass_filter = gr_filter.fir_filter_fff(1, hp_taps)
        self.connect(demod_output, self.high_pass_filter)
        
        # Volume control
        self.volume = blocks.multiply_const_ff(0.3)
        self.connect(self.high_pass_filter, self.volume)
        
        # Output options
        if output_file:
            # File sink for WAV output
            self.file_sink = blocks.wavfile_sink(
                output_file, 1, int(self.intermediate_rate), 16)
            self.connect(self.volume, self.file_sink)
        
        # Optional audio output (uncomment to hear audio in real-time)
        # self.audio_sink = audio.sink(int(self.intermediate_rate), "", True)
        # self.connect(self.volume, self.audio_sink)

def decode_with_gnuradio(input_file, sample_rate, center_freq=0, 
                        demod_type='fm', output_file=None):
    """
    Decode IQ file using GNU Radio
    
    Args:
        input_file: Path to IQ file
        sample_rate: Sample rate of IQ data
        center_freq: Center frequency offset
        demod_type: Demodulation type ('fm', 'am', 'ssb')
        output_file: Output WAV file path
    """
    if not GNURADIO_AVAILABLE:
        print("GNU Radio not available. Please install GNU Radio.")
        return False
    
    print(f"Starting GNU Radio decoder...")
    print(f"Input: {input_file}")
    print(f"Sample rate: {sample_rate/1e6:.1f} MHz")
    print(f"Center frequency: {center_freq/1e3:.1f} kHz")
    print(f"Demodulation: {demod_type.upper()}")
    
    try:
        # Create and run flowgraph
        tb = GNURadioIQDecoder(
            input_file=input_file,
            sample_rate=sample_rate,
            center_freq=center_freq,
            demod_type=demod_type,
            output_file=output_file
        )
        
        tb.start()
        
        # Monitor progress
        start_time = time.time()
        try:
            while tb.file_source.work_time() > 0:
                time.sleep(0.1)
                elapsed = time.time() - start_time
                if elapsed > 1:  # Print status every second
                    print(f"Processing... ({elapsed:.1f}s)", end='\r')
        except:
            pass
        
        tb.wait()
        tb.stop()
        
        print(f"\nDecoding completed!")
        if output_file:
            print(f"Output saved to: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"Error during GNU Radio decoding: {e}")
        return False

def main():
    """Command line interface for GNU Radio IQ decoder"""
    parser = argparse.ArgumentParser(
        description='Decode audio from IQ files using GNU Radio')
    
    parser.add_argument('input_file', help='Input IQ file path')
    parser.add_argument('-o', '--output', help='Output WAV file path')
    parser.add_argument('-s', '--sample-rate', type=float, default=2.4e6,
                       help='IQ sample rate (Hz, default: 2.4MHz)')
    parser.add_argument('-f', '--frequency', type=float, default=0,
                       help='Center frequency offset (Hz, default: 0)')
    parser.add_argument('-d', '--demod', choices=['fm', 'am', 'ssb'],
                       default='fm', help='Demodulation type (default: fm)')
    
    args = parser.parse_args()
    
    # Set output filename if not provided
    if not args.output:
        base_name = os.path.splitext(args.input_file)[0]
        args.output = f"{base_name}_gnuradio_{args.demod}.wav"
    
    # Check if GNU Radio is available
    if not GNURADIO_AVAILABLE:
        print("GNU Radio is not installed.")
        print("Install GNU Radio with: sudo apt-get install gnuradio")
        print("Or use pip: pip install gnuradio")
        return
    
    # Decode using GNU Radio
    success = decode_with_gnuradio(
        input_file=args.input_file,
        sample_rate=args.sample_rate,
        center_freq=args.frequency,
        demod_type=args.demod,
        output_file=args.output
    )
    
    if success:
        print("GNU Radio decoding completed successfully!")
    else:
        print("GNU Radio decoding failed!")

if __name__ == "__main__":
    main()