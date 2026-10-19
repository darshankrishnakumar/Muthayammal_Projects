# Limitations & Future Work

## 1. Current System Limitations
- **Optical Backlighting Dependency**: The system requires controlled side-profile silhouettes to accurately detect egg poles and calculate maximum breadth without shell pattern interference.
- **Uniformity of Orientation**: The egg must be positioned horizontally or vertically on the inspection conveyor to allow accurate detection of major and minor ellipse axes.
- **Sub-Species Variations**: Current calibration focuses on standard Gallus gallus domesticus; wildfowl and duck eggs require calibrated aspect ratio thresholds.

## 2. Industrial Research Roadmap
- **High-Speed Conveyor Integration**: Coupling optical sensors with pneumatic diverter valves capable of sorting 36,000 eggs/hour on industrial grader lines.
- **Hyperspectral Blood Vessel Candling**: Augmenting geometric morphology with 575 nm hemoglobin absorption spectra at Day 3 of incubation for dual-modality cross-verification.
- **Embedded Edge Deployment**: Compiling the neural weights to ONNX/TensorRT for micro-edge TPU inference on Raspberry Pi 5.
