# Walkthrough Timestamps: Multilingual Speech Emotion Recognition Using Deep Learning (PROJECT-025)

**System Designation:** VOX-EMOTE  
**Dedicated Port:** Port 5025 (`http://127.0.0.1:5025/`)  
**Video Container:** `walkthrough/walkthrough_video.mp4` (H.264 / AAC, 1280x800, Exactly 180.000s / 03:00)

| Timestamp Interval | Phase | Feature Demonstrated | Visual & Technical Focus |
|---|---|---|---|
| **00:00 - 00:30** | Phase 1 | Cockpit Overview & Spectrogram Wave Canvas | Telematics metric strip, live audio frequency spectrogram, 8 language selectors |
| **00:30 - 01:00** | Phase 2 | Joy & Happiness Classification | Happy preset, 97.3% confidence, positive Valence (+0.81), Arousal (+0.65), pitch 245 Hz |
| **01:00 - 01:30** | Phase 3 | Angry Escalation Detection in German | Customer dispute audio, Valence -0.82, high Arousal +0.89, explosive RMS energy (0.84 dB) |
| **01:30 - 02:00** | Phase 4 | Fear & Anxiety Telemedicine in Hindi | Emergency triage, pitch F0 288 Hz, vocal fold jitter (1.8%) and shimmer (4.7%) micro-tremors |
| **02:00 - 02:30** | Phase 5 | Emotion Probability Radar & 13 MFCCs | 7-class posterior probability radar geometry, 13-channel cepstral coefficient bar chart |
| **02:30 - 03:00** | Phase 6 | SQLite Acoustic History Ledger & Conclusion | Transactional session stream, multilingual records (Spanish, Tamil, French, Mandarin, Japanese) |

*Status: Exact 180.0s recording rendered and verified via ffprobe.*
