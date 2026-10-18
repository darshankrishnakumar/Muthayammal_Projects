# Limitations & Future Roadmap

## Known Limitations

1. **Static Historical Horizon**:
   - The primary dataset reflects historical pricing trends in the Indian domestic market. External dynamic shocks (such as sudden jet fuel price surges, geopolitical route closures, or post-pandemic capacity swings) are not factored into historical regression models without continuous online retraining.
2. **Discrete Booking Lead Time**:
   - The dataset captures booking records without fine-grained multi-day time-series trajectories for single flight seats. While arrival, departure, and seasonality dates are fully captured, tracking real-time fare fluctuations 30 days prior to departure would require streaming live GDS/Amadeus API feeds.
3. **Regional Route Coverage**:
   - The current dataset focuses predominantly on tier-1 Indian metros (Delhi, Mumbai, Banglore, Kolkata, Chennai, Hyderabad, Cochin). Extension to regional UDAN tier-2/3 routes requires supplemental data gathering.

---

## Future Roadmap

1. **Integration with Live Aviation APIs**:
   - Integrate live feeds from Skyscanner, Amadeus, or AviationStack APIs to capture real-time dynamic inventory availability.
2. **Attention & Transformer Architectures**:
   - Experiment with Temporal Fusion Transformers (TFT) and Informer architectures to better model long-range seasonal dependencies across holiday travel spikes.
3. **Fairness & Price Surges Detection**:
   - Implement an alert subsystem detecting algorithmic surge pricing and advising users on optimal booking windows ("Buy Now" vs. "Wait 48h").
4. **Cloud-Native Deployment**:
   - Package application into lightweight Docker containers and deploy onto Google Cloud Run with automated CI/CD GitHub Actions.
