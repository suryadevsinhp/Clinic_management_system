# IQ Audio Decoder

A comprehensive Python toolkit for decoding audio from IQ (In-phase/Quadrature) recordings. This toolkit provides multiple approaches to decode frequency hopping or unknown IQ signals into audio files.

## Features

- **Multiple Demodulation Types**: FM, AM, USB, LSB
- **Various File Formats**: Support for complex64, float32, int16, int8 data types
- **Frequency Analysis**: Automatic spectrum analysis to identify signals
- **Frequency Hopping Support**: Try multiple frequency offsets automatically
- **GNU Radio Integration**: Advanced signal processing using GNU Radio
- **Audio Processing**: Proper filtering, decimation, and normalization

## Installation

### Basic Requirements

```bash
pip install -r requirements.txt
```

### For GNU Radio Support (Optional but Recommended)

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install gnuradio gnuradio-dev
```

**Or via Python:**
```bash
pip install gnuradio
```

## Quick Start

### 1. Basic Usage

```bash
# Decode FM audio from IQ file
python iq_audio_decoder.py your_file.iq -d fm -o decoded_audio.wav

# Try different modulation types
python iq_audio_decoder.py your_file.iq -d am -o decoded_am.wav
python iq_audio_decoder.py your_file.iq -d usb -o decoded_usb.wav
```

### 2. For Frequency Hopping Signals

```bash
# Try different frequency offsets
python iq_audio_decoder.py your_file.iq -f -100000 -d fm -o audio_minus100k.wav
python iq_audio_decoder.py your_file.iq -f 0 -d fm -o audio_center.wav
python iq_audio_decoder.py your_file.iq -f 100000 -d fm -o audio_plus100k.wav
```

### 3. Different Data Types

```bash
# For different IQ file formats
python iq_audio_decoder.py file.dat -t float32 -d fm    # Interleaved float32
python iq_audio_decoder.py file.raw -t int16 -d fm     # RTL-SDR format
python iq_audio_decoder.py file.bin -t int8 -d fm      # Some SDR formats
```

## Command Line Options

### Basic Python Decoder

```
python iq_audio_decoder.py [OPTIONS] input_file

Options:
  -o, --output      Output WAV file path
  -s, --sample-rate Sample rate in Hz (default: 2.4MHz)
  -f, --frequency   Center frequency offset in Hz
  -d, --demod       Demodulation type: fm, am, usb, lsb
  -t, --type        Data type: complex64, float32, int16, int8
  -b, --bandwidth   Audio bandwidth in Hz
  --no-plot         Disable spectrum plot
```

### GNU Radio Decoder

```
python gnuradio_iq_decoder.py [OPTIONS] input_file

Options:
  -o, --output      Output WAV file path
  -s, --sample-rate Sample rate in Hz (default: 2.4MHz)
  -f, --frequency   Center frequency offset in Hz
  -d, --demod       Demodulation type: fm, am, ssb
```

## Programming Examples

### Basic Python Usage

```python
from iq_audio_decoder import IQAudioDecoder

# Initialize decoder
decoder = IQAudioDecoder(sample_rate=2.4e6)

# Decode FM audio
audio = decoder.decode_audio(
    filename='recording.iq',
    demod_type='fm',
    output_file='decoded.wav'
)
```

### For Unknown Signals

```python
# Analyze spectrum first
decoder = IQAudioDecoder(sample_rate=2.4e6)
iq_data = decoder.load_iq_data('unknown.iq', 'complex64')
decoder.analyze_spectrum(iq_data)  # Shows frequency peaks

# Try different frequencies and modulations
frequencies = [-200e3, -100e3, 0, 100e3, 200e3]
modulations = ['fm', 'am', 'usb', 'lsb']

for freq in frequencies:
    for mod in modulations:
        audio = decoder.decode_audio(
            filename='unknown.iq',
            center_freq=freq,
            demod_type=mod,
            output_file=f'decoded_{mod}_{int(freq/1000)}khz.wav'
        )
```

### Frequency Hopping Example

```python
# For frequency hopping signals, try multiple offsets
decoder = IQAudioDecoder(sample_rate=2.4e6)

# Common frequency hops (adjust based on your signal)
hop_frequencies = [-500e3, -250e3, 0, 250e3, 500e3]

for i, freq in enumerate(hop_frequencies):
    audio = decoder.decode_audio(
        filename='hopping_signal.iq',
        center_freq=freq,
        demod_type='fm',
        bandwidth=200e3,  # 200 kHz bandwidth
        output_file=f'hop_{i}_audio.wav'
    )
```

## File Format Guide

### Common IQ File Types

| Extension | Data Type | Description |
|-----------|-----------|-------------|
| `.iq` | complex64 | GNU Radio default format |
| `.dat` | float32 | Interleaved I/Q float32 |
| `.raw` | int16 | RTL-SDR format |
| `.bin` | int8 | Some SDR formats |
| `.cfile` | complex64 | GNU Radio complex file |

### Data Type Details

- **complex64**: Direct complex samples (8 bytes per sample)
- **float32**: Interleaved I/Q as float32 (8 bytes per sample)
- **int16**: Interleaved I/Q as signed 16-bit integers (4 bytes per sample)
- **int8**: Interleaved I/Q as signed 8-bit integers (2 bytes per sample)

## Troubleshooting

### Common Issues

1. **"No audio output"**
   - Try different demodulation types (FM, AM, USB, LSB)
   - Check frequency offset - signal might not be at center
   - Verify sample rate matches your recording
   - Use spectrum analysis to find signals

2. **"Noisy audio"**
   - Reduce bandwidth parameter
   - Try different frequency offsets
   - Check if signal strength is adequate

3. **"File not found errors"**
   - Verify file path and permissions
   - Check file format matches data type parameter

### Finding the Right Parameters

1. **Start with spectrum analysis:**
   ```python
   decoder = IQAudioDecoder(sample_rate=your_sample_rate)
   iq_data = decoder.load_iq_data('your_file.iq', 'complex64')
   decoder.analyze_spectrum(iq_data)  # Look for peaks
   ```

2. **Try multiple frequency offsets** based on spectrum peaks

3. **Test different modulation types** - signals might use AM, FM, or SSB

4. **Adjust bandwidth** - narrower for better noise rejection

## Performance Tips

### For Large Files

- Use GNU Radio decoder for better performance
- Process files in chunks if memory limited
- Use appropriate data types (int8/int16 for smaller files)

### For Frequency Hopping

- Create multiple short audio files for each frequency
- Use automated scripts to try all combinations
- Monitor spectrum in real-time if possible

## Examples

Run the example script to see all features:

```bash
python example_usage.py
```

This will:
1. Create a test FM signal
2. Demonstrate different demodulation techniques
3. Show frequency hopping detection
4. Analyze unknown signals step by step

## License

This project is provided as-is for educational and research purposes.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve this toolkit.