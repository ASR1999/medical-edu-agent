# Whisper Fine-Tuning for Medical ASR

This directory contains the pipeline for fine-tuning Whisper on medical audio.

## Data Sourcing

You cannot easily download a ready-made medical speech dataset due to HIPAA and privacy concerns. You must find open-source, anonymized datasets. Good places to start:

- **MIMIC-IV:** While mostly text, it sometimes has associated clinical notes that can be paired with other data.
- **Public Medical Speech Datasets:** Search for datasets like "Medical VCTK", "MeS" (Medical Speech), or datasets from challenges like i2b2.
- **Kaggle:** Search for "medical speech" or "doctor patient conversation".

Place your raw audio files (`.wav`) and a metadata file (e.g., `metadata.csv` or `data.json`) mapping audio filenames to their transcriptions in the `/data` folder.