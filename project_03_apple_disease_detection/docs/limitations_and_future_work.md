# Limitations & Future Roadmap

## Known Limitations

1. **Complex Canopy Lighting Conditions**:
   - In field environments, direct overhead solar glare or deep canopy shadows can occasionally degrade foliar contrast. While data augmentation (color jitter, affine rotations) enhances robustness, handheld capture under diffused daylight or uniform illumination yields optimal results.
2. **Early-Stage Latent Infections**:
   - Visual CNN models detect macroscopic symptomatic fungal lesions on leaf surfaces. Pre-symptomatic or latent incubation phases (before cuticular eruption occurs) require supplemental hyperspectral or biochemical sensors.
3. **Multi-Pathogen Co-Infection**:
   - Occasionally, apple leaves simultaneously suffer from Apple Scab and Cedar Apple Rust. The current model ranks top predictions with confidence distributions, but multi-label segmentation can further delineate overlapping lesions.

---

## Future Roadmap

1. **Autonomous Orchard Drone Surveying**:
   - Integrate the lightweight MobileNetV2 model with unmanned aerial vehicles (UAVs) equipped with GPS waypoints to perform autonomous orchard canopy scouting.
2. **YOLOv10 / Mask R-CNN Instance Segmentation**:
   - Implement real-time bounding box and polygon mask segmentation to quantify leaf surface lesion percentages and estimate disease severity indices (DSI).
3. **Microclimate Infection Risk Forecasting**:
   - Couple image diagnosis with on-orchard IoT weather stations tracking temperature, relative humidity, and leaf wetness hours (Mills Scab Infection Periods) for predictive disease forecasting.
