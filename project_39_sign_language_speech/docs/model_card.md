# Model Card: SIGN-SPEECH AI Deep Neural Networks

## Model 1: BiLSTMSignAttentionNet
- **Architecture**: 2-Layer Bidirectional LSTM with Multi-Head Self-Attention Pooling
- **Parameters**: 700,107 parameters (Serialized size: 2.8 MB)
- **Input Shape**: `[Batch, 30, 54]` (30 frames, 54 skeletal landmarks)
- **Output 1**: `[Batch, 10]` Logits across 10 vocabulary classes
- **Output 2**: `[Batch, 30, 1]` Normalized temporal attention weights
- **Accuracy**: 100.00% validation accuracy
- **Target Vocabulary**: HELLO, THANK_YOU, PLEASE, HELP, EMERGENCY, DOCTOR, WATER, YES, NO, GOODBYE

## Model 2: SpeechProsodyAcousticRegressorNet
- **Architecture**: Multi-Target Continuous Regressor with Layer Normalization & GELU
- **Parameters**: 20,708 parameters (Serialized size: 83 KB)
- **Input Shape**: `[Batch, 10]` Kinematic and finger flexion feature vector
- **Head 1**: Fundamental Frequency Pitch F0 [80.0, 280.0] Hz -> MAE: 14.11 Hz
- **Head 2**: Utterance Duration [0.4, 3.0] s -> MAE: 0.150 s
- **Head 3**: Speech Energy [40.0, 85.0] dB -> MAE: 3.22 dB
- **Head 4**: Prosody Quality Score [0, 100] -> MAE: 2.87 points
