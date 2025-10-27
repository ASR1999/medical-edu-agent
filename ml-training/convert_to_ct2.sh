#!/bin/bash
# Convenience script to convert Whisper model to CTranslate2

echo "🔄 Converting medasr-v2 to CTranslate2 format..."
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.8+"
    exit 1
fi

# Check if required packages are installed
python3 -c "import ctranslate2, transformers" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 Installing required packages..."
    pip install ctranslate2>=3.20.0 transformers>=4.35.0
fi

# Run conversion
python3 convert_to_ct2.py "$@"

exit $?

