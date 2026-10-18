# Walkthrough Timestamps: A Holistic Approach on Airfare Price Prediction Using LSTM Machine Learning Techniques (PROJECT-001)

**Video File**: `walkthrough_video.mp4`  
**Video Resolution**: 1280x800 H.264 (High Profile) Progressive  
**Video Duration**: 02:37 (157.0 seconds)  
**File Size**: 1.55 MB (1,622,913 bytes)  
**Recording Verification**: VERIFIED PLAYABLE (100% End-to-End Workflow Demonstrated)

| Timestamp | Segment | Demonstration Topic & Visual Actions |
|---|---|---|
| **00:00 - 00:12** | Application Startup | Landing on AeroPredict Dashboard at `http://127.0.0.1:5001/` — Service health verified. |
| **00:12 - 00:24** | UI Overview | Visual inspection of flight configuration parameters form, carrier selection, and initial empty valuation state. |
| **00:24 - 00:43** | Flight 1 (IndiGo Direct) | Setting IndiGo, Bangalore to Delhi, non-stop flight. Executing prediction; displaying LSTM (₹3,960) vs Random Forest (₹4,330) comparative valuation. |
| **00:43 - 01:03** | Flight 2 (Air India Layover) | Configuring Air India from Mumbai to Cochin with 2 layover stops. Demonstrating stop penalty and travel duration impact on dynamic ticket fare. |
| **01:03 - 01:23** | Flight 3 (Vistara Route) | Selecting full-service carrier Vistara on Delhi to Hyderabad route; evaluating carrier tier premium factor and confidence interval. |
| **01:23 - 01:45** | Model Benchmarks & Metrics | Navigating to Model Performance tab. Reviewing empirical test metrics ($R^2 = 0.8321$ for RF, $R^2 = 0.7566$ for LSTM, MAE = ₹1,136) and Bidirectional LSTM layer topology. |
| **01:45 - 02:07** | SQLite Database Audit | Switching to Prediction History tab. Verifying persistent SQLite logs (`airfare.db`) displaying real query timestamps, routes, and auto-increment IDs. |
| **02:07 - 02:25** | Airline Pricing Analytics | Navigating to Pricing Analytics tab. Reviewing dynamically aggregated industry averages and query frequency per airline. |
| **02:25 - 02:37** | Operational Wrap-Up | Returning to Valuation Engine. Demonstrating clean, robust completion with zero console or runtime errors. |
