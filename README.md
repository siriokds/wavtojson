# WAV to JSON Converter

A Python utility that converts WAV audio files to structured JSON format and back, preserving all audio data and metadata. Perfect for audio processing, data analysis, or when you need to work with audio data in JSON-based workflows.

## 🎵 Features

- **Lossless conversion** between WAV and JSON formats
- **Multiple compression options** to optimize file size (up to 90% reduction)
- **Bidirectional conversion** - WAV ↔ JSON
- **Complete metadata preservation** (sample rate, channels, bit depth, etc.)
- **Cross-platform compatibility** (Windows, macOS, Linux)
- **No external dependencies** - uses only Python standard library

## 📦 Installation

No installation required! Just download the script:

```bash
git clone https://github.com/siriokds/wav-to-json-converter.git
cd wav-to-json-converter
```

**Requirements:**
- Python 3.6 or higher
- No additional packages needed

## 🚀 Quick Start

### Convert WAV to JSON
```bash
# Basic conversion (default base64 compression)
python wavtojson.py myaudio.wav

# Maximum compression
python wavtojson.py myaudio.wav gzip_base64

# No compression (human-readable but large)
python wavtojson.py myaudio.wav none
```

### Convert JSON back to WAV
```bash
# Reconstruct original WAV file
python wavtojson.py myaudio.json
# Creates: myaudio_reconstructed.wav
```

## 📊 Compression Comparison

For a typical 5-second stereo WAV file (44.1kHz, 16-bit):

| Method | File Size | Space Savings | Use Case |
|--------|-----------|---------------|----------|
| `none` | ~15 MB | ❌ Large | Development/debugging |
| `base64` | ~1.2 MB | ✅ 75% smaller | Balanced size/compatibility |
| `gzip_base64` | ~300 KB | 🚀 **90% smaller** | Maximum compression |

## 🛠️ Usage Examples

### Basic Operations

```bash
# Convert a WAV file to JSON
python wavtojson.py song.wav
# Output: song.json

# Convert back to WAV
python wavtojson.py song.json
# Output: song_reconstructed.wav
```

### Advanced Compression

```bash
# Minimum file size (best for storage/transmission)
python wavtojson.py podcast.wav gzip_base64

# Human-readable format (best for analysis)
python wavtojson.py speech.wav none

# Balanced approach (default)
python wavtojson.py music.wav base64
```

### Batch Processing Example

```bash
# Convert multiple files
for file in *.wav; do
    python wavtojson.py "$file" gzip_base64
done
```

## 📋 Command Line Options

```
Usage: python wavtojson.py <input_file> [compression_type]

Arguments:
  input_file        WAV file to convert to JSON, or JSON file to convert back to WAV
  compression_type  Compression method for WAV→JSON conversion (optional)

Compression Types:
  none        Store samples as JSON array (largest, human-readable)
  base64      Store raw data as base64 string (medium size, default)
  gzip_base64 Compress with gzip then base64 (smallest size)

Examples:
  python wavtojson.py audio.wav                    # WAV → JSON (base64)
  python wavtojson.py audio.wav gzip_base64        # WAV → JSON (max compression)
  python wavtojson.py audio.json                   # JSON → WAV
```

## 📁 Output Structure

The JSON output contains complete audio information:

```json
{
  "file_info": {
    "filename": "example.wav",
    "file_size_bytes": 1234567
  },
  "audio_properties": {
    "sample_rate_hz": 44100,
    "channels": 2,
    "bit_depth": 16,
    "duration_seconds": 5.0
  },
  "data": {
    "samples": "UklGRs6R...",
    "compression": "base64"
  }
}
```

📖 **For complete format specification, see [FILE_FORMAT.md](FILE_FORMAT.md)**

## 🎯 Use Cases

### Audio Development
```bash
# Create readable audio data for analysis
python wavtojson.py recording.wav none
# Examine the JSON to understand audio structure
```

### Data Storage & Transmission
```bash
# Minimize storage space
python wavtojson.py audio.wav gzip_base64
# 90% smaller files for efficient storage/transfer
```

### Audio Processing Pipelines
```bash
# Convert to JSON for p