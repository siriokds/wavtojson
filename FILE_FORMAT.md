# WAV to JSON Format Documentation

> **Download Instructions:** To save this documentation, click the download button (⬇️) in the top-right corner of this document panel, or copy the content and save it as `WAV_JSON_Format_Documentation.md`

## Overview

This document describes the JSON format used by the `wavtojson.py` script to convert WAV audio files into a structured JSON representation. The format preserves all original audio data and metadata while offering multiple compression options to optimize file size.

## File Structure

The JSON output follows this hierarchical structure:

```json
{
  "file_info": { ... },
  "format": { ... },
  "audio_properties": { ... },
  "data": { ... },
  "metadata": { ... }
}
```

## Detailed Schema

### 1. `file_info` Section

Contains basic file information:

```json
{
  "file_info": {
    "filename": "example.wav",
    "file_size_bytes": 1234567
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `filename` | string | Original WAV filename |
| `file_size_bytes` | integer | Size of the original WAV file in bytes |

### 2. `format` Section

Describes the original WAV format properties:

```json
{
  "format": {
    "format_name": "WAV",
    "compression_type": "NONE",
    "compression_name": "not compressed"
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `format_name` | string | Always "WAV" |
| `compression_type` | string | WAV compression type (usually "NONE" for PCM) |
| `compression_name` | string | Human-readable compression description |

### 3. `audio_properties` Section

Contains all audio technical specifications:

```json
{
  "audio_properties": {
    "sample_rate_hz": 44100,
    "channels": 2,
    "sample_width_bytes": 2,
    "sample_type": "int16",
    "total_frames": 220500,
    "duration_seconds": 5.0,
    "bit_depth": 16
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `sample_rate_hz` | integer | Sample rate in Hz (e.g., 44100, 48000) |
| `channels` | integer | Number of audio channels (1=mono, 2=stereo) |
| `sample_width_bytes` | integer | Bytes per sample (1, 2, or 4) |
| `sample_type` | string | Data type: "uint8", "int16", or "int32" |
| `total_frames` | integer | Total number of audio frames |
| `duration_seconds` | float | Duration in seconds |
| `bit_depth` | integer | Bit depth (8, 16, or 32) |

### 4. `data` Section

Contains the actual audio sample data with compression information:

```json
{
  "data": {
    "samples": "UklGRs6R...",
    "samples_count": 220500,
    "channel_layout": "2_channels",
    "compression": "base64",
    "data_format": "raw_binary_base64"
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `samples` | varies | Audio sample data (format depends on compression) |
| `samples_count` | integer | Total number of sample frames |
| `channel_layout` | string | "mono" or "{n}_channels" |
| `compression` | string | Compression method used ("none", "base64", "gzip_base64") |
| `data_format` | string | Data format description |

### 5. `metadata` Section

Additional metadata and conversion information:

```json
{
  "metadata": {
    "created_by": "WAV to JSON Converter",
    "notes": "Converted from example.wav"
  }
}
```

## Compression Methods

The converter supports three compression methods for the audio data:

### 1. No Compression (`none`)

**Usage:** `python wavtojson.py file.wav none`

**Format:** Audio samples stored as JSON arrays
- **Mono:** `[sample1, sample2, sample3, ...]`
- **Stereo:** `[[left1, right1], [left2, right2], ...]`

**Pros:** Human-readable, easy to parse
**Cons:** Very large file size (10-20x original WAV)

**Example:**
```json
{
  "data": {
    "samples": [0, 1024, -512, 2048, ...],
    "compression": "none",
    "data_format": "sample_array"
  }
}
```

### 2. Base64 Encoding (`base64`) - Default

**Usage:** `python wavtojson.py file.wav` or `python wavtojson.py file.wav base64`

**Format:** Raw binary data encoded as base64 string

**Pros:** ~75% size reduction, preserves exact binary data
**Cons:** Not human-readable

**Example:**
```json
{
  "data": {
    "samples": "UklGRs6RAAAWQVZFZm10...",
    "compression": "base64",
    "data_format": "raw_binary_base64"
  }
}
```

### 3. Gzip + Base64 (`gzip_base64`)

**Usage:** `python wavtojson.py file.wav gzip_base64`

**Format:** Binary data compressed with gzip, then encoded as base64

**Pros:** Maximum compression (~85-90% size reduction)
**Cons:** Not human-readable, requires decompression

**Example:**
```json
{
  "data": {
    "samples": "H4sIAAAAAAAAC1RiYWRh...",
    "compression": "gzip_base64",
    "data_format": "raw_binary_base64"
  }
}
```

## Data Types and Sample Formats

The converter handles different sample formats based on the original WAV file:

| Bit Depth | Sample Width | Data Type | Range |
|-----------|--------------|-----------|-------|
| 8-bit | 1 byte | uint8 | 0 to 255 |
| 16-bit | 2 bytes | int16 | -32,768 to 32,767 |
| 32-bit | 4 bytes | int32 | -2,147,483,648 to 2,147,483,647 |

## File Size Comparison

For a typical 5-second stereo WAV file (44.1kHz, 16-bit):

| Method | Approximate Size | Ratio |
|--------|-----------------|-------|
| Original WAV | 882 KB | 100% |
| JSON (none) | ~15 MB | 1700% |
| JSON (base64) | ~1.2 MB | 135% |
| JSON (gzip_base64) | ~200-400 KB | 25-45% |

## Converting Back to WAV

The `json_to_wav()` function can reconstruct the original WAV file from any of the JSON formats:

```python
json_to_wav("audio.json", "reconstructed.wav")
```

The function automatically detects the compression method used and applies the appropriate decompression.

## Usage Examples

### Basic Conversion
```bash
# Convert with default base64 compression
python wavtojson.py myaudio.wav
# Creates: myaudio.json
```

### Maximum Compression
```bash
# Convert with gzip compression for smallest file
python wavtojson.py myaudio.wav gzip_base64
# Creates: myaudio.json (smallest possible)
```

### Debug/Development
```bash
# Convert without compression for human-readable output
python wavtojson.py myaudio.wav none
# Creates: myaudio.json (readable but large)
```

## Error Handling

The converter handles various error conditions:

- **File not found:** Clear error message with file path
- **Unsupported sample width:** Only 8, 16, and 32-bit samples supported
- **Invalid compression type:** Must be "none", "base64", or "gzip_base64"
- **Corrupted WAV files:** Standard Python wave module error handling

## Compatibility

- **Python Version:** Requires Python 3.6+
- **Dependencies:** Only standard library modules (json, wave, struct, os, sys, base64, gzip)
- **Platform:** Cross-platform (Windows, macOS, Linux)
- **WAV Support:** Standard PCM WAV files (uncompressed)

## Technical Notes

### Byte Order
All binary data uses little-endian byte order (`<` format in struct), which is standard for WAV files.

### Memory Usage
Large WAV files may require significant memory during conversion. The script loads the entire audio data into memory before processing.

### Precision
The conversion process is lossless - the reconstructed WAV file will be bit-identical to the original when using base64 or gzip_base64 compression methods.
