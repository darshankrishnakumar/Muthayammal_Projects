# Limitations and Future Work

## 1. Current Engineering Limitations

1. **Tabular-Only Feature Input**:
   Valuations are driven strictly by numerical and categorical parameters (Age, Mileage, Showroom Cost, Fuel, Transmission). The system currently does not ingest visual inspection photos to assess exterior physical body damage, repainting, or panel rust.

2. **Geographical Price Variations**:
   The current dataset is generalized across Indian pre-owned markets. It does not model micro-geographic RTO tax variations (e.g., higher road tax in Karnataka vs. lower tax in Haryana/Delhi) or local clean-air policy restrictions (e.g., 10-year diesel rule in NCR).

3. **Accidental & Maintenance History**:
   Insurance claim histories, flood damage records, and authorized service center maintenance logs are not directly linked into the feature space.

---

## 2. Future Engineering Roadmap

1. **Computer Vision Damage Deduction (YOLOv8)**:
   Integrate a computer vision pipeline where users upload photos of vehicle exterior panels. An object detection model detects dents, panel scratches, glass cracks, and tire tread wear, automatically subtracting quantified repair costs from the fair-market valuation.

2. **OBD-II Real-Time Telemetry**:
   Connect via Bluetooth/Wi-Fi to the vehicle's onboard OBD-II diagnostic port to read Diagnostic Trouble Codes (DTCs), engine compression health, catalytic converter efficiency, and genuine ECU odometer mileage to prevent odometer tampering fraud.

3. **Regional Real-Time Scraping & Indexing**:
   Deploy automated web scrapers tracking live listings across major automotive portals to continually update regional demand curves and inflation-adjusted depreciation rates.
