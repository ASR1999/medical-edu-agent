#!/usr/bin/env python3
"""
Convert HuggingFace Whisper Model to CTranslate2 Format

This script converts a fine-tuned Whisper model (in HuggingFace format)
to CTranslate2 format for faster inference.

Usage:
    python convert_to_ct2.py
    
Or with custom paths:
    python convert_to_ct2.py --model_path ./medasr-v2 --output_path ../backend/ct2_models/medasr-v2-ct2
"""

import argparse
import os
import sys
from pathlib import Path

try:
    import ctranslate2
    from transformers import WhisperProcessor
except ImportError:
    print("❌ Error: Required packages not installed.")
    print("\nPlease install:")
    print("  pip install ctranslate2>=3.20.0 transformers>=4.35.0")
    sys.exit(1)


def convert_whisper_to_ct2(
    model_path: str,
    output_path: str,
    quantization: str = "float16",
    force: bool = False
):
    """
    Convert Whisper model to CTranslate2 format.
    
    Args:
        model_path: Path to HuggingFace Whisper model directory
        output_path: Path where CT2 model will be saved
        quantization: Quantization type (float32, float16, int8, int8_float16)
        force: Overwrite existing output directory
    """
    model_path = Path(model_path).resolve()
    output_path = Path(output_path).resolve()
    
    # Validate input
    if not model_path.exists():
        raise FileNotFoundError(f"Model path does not exist: {model_path}")
    
    config_file = model_path / "config.json"
    if not config_file.exists():
        raise FileNotFoundError(f"config.json not found in {model_path}")
    
    print("=" * 60)
    print("🔄 Whisper Model → CTranslate2 Conversion")
    print("=" * 60)
    print(f"\n📂 Input Model: {model_path}")
    print(f"📂 Output Path: {output_path}")
    print(f"⚙️  Quantization: {quantization}")
    print()
    
    # Check if output exists
    if output_path.exists() and not force:
        print(f"⚠️  Output directory already exists: {output_path}")
        response = input("Overwrite? [y/N]: ")
        if response.lower() != 'y':
            print("❌ Conversion cancelled.")
            return False
    
    # Remove existing directory if needed
    import shutil
    if output_path.exists():
        print(f"   Removing existing directory...")
        shutil.rmtree(output_path)
    
    try:
        # Convert model
        print("🔄 Converting model (this may take a few minutes)...")
        print("   Loading model weights...")
        
        converter = ctranslate2.converters.TransformersConverter(
            model_name_or_path=str(model_path),
            copy_files=[
                "config.json",
                "preprocessor_config.json", 
                "vocab.json",
                "tokenizer.json",
                "merges.txt",
                "normalizer.json",
                "added_tokens.json",
                "special_tokens_map.json"
            ]
        )
        
        print(f"   Quantizing to {quantization}...")
        converter.convert(
            output_dir=str(output_path),
            quantization=quantization
        )
        
        print("\n✅ Conversion successful!")
        print(f"\n📦 CT2 model saved to: {output_path}")
        
        # Verify output files
        print("\n📋 Verifying output files...")
        expected_files = ["model.bin", "config.json"]
        missing_files = []
        for file in expected_files:
            file_path = output_path / file
            if file_path.exists():
                size_mb = file_path.stat().st_size / (1024 * 1024)
                print(f"   ✅ {file} ({size_mb:.1f} MB)")
            else:
                print(f"   ❌ {file} (MISSING)")
                missing_files.append(file)
        
        if missing_files:
            print(f"\n⚠️  Warning: Some files are missing: {missing_files}")
            return False
        
        # Load processor to verify
        print("\n🧪 Testing model load...")
        try:
            processor = WhisperProcessor.from_pretrained(str(model_path))
            model = ctranslate2.models.Whisper(str(output_path))
            print("   ✅ Model loads successfully!")
            print(f"   ℹ️  Model device: {model.device}")
            print(f"   ℹ️  Compute type: {model.compute_type}")
        except Exception as e:
            print(f"   ⚠️  Warning: Could not load model: {e}")
        
        print("\n" + "=" * 60)
        print("✅ CONVERSION COMPLETE")
        print("=" * 60)
        print(f"\n📍 Next steps:")
        print(f"   1. Update backend config to use this model:")
        print(f"      MODEL_PATH = '{output_path}'")
        print(f"   2. Restart backend service")
        print(f"   3. Test ASR endpoint")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during conversion: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Convert HuggingFace Whisper to CTranslate2",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Default paths
    default_input = Path(__file__).parent / "medasr-v2"
    default_output = Path(__file__).parent.parent / "backend" / "ct2_models" / "medasr-v2-ct2"
    
    parser.add_argument(
        "--model_path",
        type=str,
        default=str(default_input),
        help="Path to HuggingFace Whisper model directory"
    )
    
    parser.add_argument(
        "--output_path",
        type=str,
        default=str(default_output),
        help="Path where CT2 model will be saved"
    )
    
    parser.add_argument(
        "--quantization",
        type=str,
        default="float16",
        choices=["float32", "float16", "int8", "int8_float16"],
        help="Quantization precision"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing output directory without prompting"
    )
    
    args = parser.parse_args()
    
    success = convert_whisper_to_ct2(
        model_path=args.model_path,
        output_path=args.output_path,
        quantization=args.quantization,
        force=args.force
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

