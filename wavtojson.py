import json
import wave
import struct
import os
import sys
import base64
import gzip
from typing import Dict, List, Any

def wav_to_json(wav_file_path: str, json_file_path: str, compression: str = "base64") -> Dict[str, Any]:
    """
    Converte un file WAV in formato JSON mantenendo tutta la struttura e i sample.
    
    Args:
        wav_file_path (str): Percorso del file WAV di input
        json_file_path (str): Percorso del file JSON di output
        compression (str): Tipo di compressione: "none", "base64", "gzip_base64"
    
    Returns:
        Dict: Struttura dati del file WAV
    """
    
    if not os.path.exists(wav_file_path):
        raise FileNotFoundError(f"WAV file not found: {wav_file_path}")
    
    # Apre il file WAV
    with wave.open(wav_file_path, 'rb') as wav_file:
        # Estrae i parametri del file WAV
        frames = wav_file.readframes(-1)
        sample_rate = wav_file.getframerate()
        channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        n_frames = wav_file.getnframes()
        compression_type = wav_file.getcomptype()
        compression_name = wav_file.getcompname()
    
    # Determina il formato dei sample in base alla larghezza
    if sample_width == 1:
        fmt = 'B'  # unsigned char
        sample_type = "uint8"
    elif sample_width == 2:
        fmt = 'h'  # signed short
        sample_type = "int16"
    elif sample_width == 4:
        fmt = 'i'  # signed int
        sample_type = "int32"
    else:
        raise ValueError(f"Unsupported sample width: {sample_width}")
    
    # Converte i dati binari in formato più compatto
    samples_data = None
    compression_used = compression
    
    if compression == "none":
        # Mantiene i sample come lista (più leggibile ma più grande)
        if channels == 1:
            samples_data = list(struct.unpack(f'<{n_frames}{fmt}', frames))
        else:
            samples_data = []
            all_samples = struct.unpack(f'<{n_frames * channels}{fmt}', frames)
            for i in range(0, len(all_samples), channels):
                frame = []
                for ch in range(channels):
                    frame.append(all_samples[i + ch])
                samples_data.append(frame)
    
    elif compression == "base64":
        # Codifica i dati raw come base64 (molto più compatto)
        samples_data = base64.b64encode(frames).decode('ascii')
        
    elif compression == "gzip_base64":
        # Comprime con gzip poi codifica in base64 (massima compressione)
        compressed_frames = gzip.compress(frames)
        samples_data = base64.b64encode(compressed_frames).decode('ascii')
        
    else:
        raise ValueError(f"Invalid compression type: {compression}. Use 'none', 'base64', or 'gzip_base64'")
    
    # Crea la struttura JSON che replica quella del file WAV
    wav_data = {
        "file_info": {
            "filename": os.path.basename(wav_file_path),
            "file_size_bytes": os.path.getsize(wav_file_path)
        },
        "format": {
            "format_name": "WAV",
            "compression_type": compression_type,
            "compression_name": compression_name
        },
        "audio_properties": {
            "sample_rate_hz": sample_rate,
            "channels": channels,
            "sample_width_bytes": sample_width,
            "sample_type": sample_type,
            "total_frames": n_frames,
            "duration_seconds": n_frames / sample_rate if sample_rate > 0 else 0,
            "bit_depth": sample_width * 8
        },
        "data": {
            "samples": samples_data,
            "samples_count": n_frames,
            "channel_layout": "mono" if channels == 1 else f"{channels}_channels",
            "compression": compression_used,
            "data_format": "raw_binary_base64" if compression != "none" else "sample_array"
        },
        "metadata": {
            "created_by": "WAV to JSON Converter",
            "notes": f"Converted from {wav_file_path}"
        }
    }
    
    # Salva il JSON in modo compatto (senza indentazione per risparmiare spazio)
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(wav_data, json_file, separators=(',', ':'), ensure_ascii=False)
    
    # Calcola le dimensioni per il report
    json_size = os.path.getsize(json_file_path)
    wav_size = os.path.getsize(wav_file_path)
    compression_ratio = (json_size / wav_size) * 100
    
    print(f"Conversion completed!")
    print(f"WAV file: {wav_file_path} ({wav_size:,} bytes)")
    print(f"JSON file: {json_file_path} ({json_size:,} bytes)")
    print(f"Compression: {compression_used}")
    print(f"Size ratio: {compression_ratio:.1f}% of original")
    print(f"Sample rate: {sample_rate} Hz")
    print(f"Channels: {channels}")
    print(f"Duration: {wav_data['audio_properties']['duration_seconds']:.2f} seconds")
    print(f"Total samples: {n_frames}")
    
    return wav_data

def json_to_wav(json_file_path: str, wav_file_path: str) -> None:
    """
    Converte un file JSON (creato da wav_to_json) back in formato WAV.
    Supporta tutti i tipi di compressione.
    
    Args:
        json_file_path (str): Percorso del file JSON di input
        wav_file_path (str): Percorso del file WAV di output
    """
    
    with open(json_file_path, 'r', encoding='utf-8') as json_file:
        wav_data = json.load(json_file)
    
    # Estrae i parametri
    sample_rate = wav_data['audio_properties']['sample_rate_hz']
    channels = wav_data['audio_properties']['channels']
    sample_width = wav_data['audio_properties']['sample_width_bytes']
    samples_data = wav_data['data']['samples']
    compression = wav_data['data'].get('compression', 'none')
    
    # Ricostruisce i dati binari in base alla compressione usata
    if compression == "none":
        # I dati sono già come lista di sample
        fmt = 'B' if sample_width == 1 else 'h' if sample_width == 2 else 'i'
        if channels == 1:
            frames_data = struct.pack(f'<{len(samples_data)}{fmt}', *samples_data)
        else:
            interleaved = []
            for frame in samples_data:
                for channel_sample in frame:
                    interleaved.append(channel_sample)
            frames_data = struct.pack(f'<{len(interleaved)}{fmt}', *interleaved)
    
    elif compression == "base64":
        # Decodifica direttamente da base64
        frames_data = base64.b64decode(samples_data.encode('ascii'))
        
    elif compression == "gzip_base64":
        # Decodifica da base64 poi decomprime con gzip
        compressed_data = base64.b64decode(samples_data.encode('ascii'))
        frames_data = gzip.decompress(compressed_data)
        
    else:
        raise ValueError(f"Unsupported compression type: {compression}")
    
    # Crea il file WAV
    with wave.open(wav_file_path, 'wb') as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(frames_data)
    
    print(f"Reconstruction completed: {wav_file_path}")

# Esempio di utilizzo
if __name__ == "__main__":
    # Controlla se è stato fornito il parametro del file WAV
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python wavtojson.py <input_file.wav> [compression_type]")
        print("Example: python wavtojson.py miofile.wav")
        print("Example: python wavtojson.py miofile.wav gzip_base64")
        print("")
        print("Compression types:")
        print("  none        - Store samples as JSON array (largest, most readable)")
        print("  base64      - Store raw data as base64 string (medium size, default)")
        print("  gzip_base64 - Compress with gzip then base64 (smallest)")
        sys.exit(1)
    
    input_wav = sys.argv[1]
    compression = sys.argv[2] if len(sys.argv) == 3 else "base64"
    
    # Genera automaticamente il nome del file JSON
    base_name = os.path.splitext(input_wav)[0]
    output_json = f"{base_name}.json"
    
    try:
        # Converte WAV in JSON
        print(f"Converting {input_wav} to {output_json}...")
        wav_data = wav_to_json(input_wav, output_json, compression)
        
        # Opzionale: riconverti JSON in WAV per verifica
        # json_to_wav(output_json, "reconstructed.wav")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error during conversion: {e}")
        sys.exit(1)
