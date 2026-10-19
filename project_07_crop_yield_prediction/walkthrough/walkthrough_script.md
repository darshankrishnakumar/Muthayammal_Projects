# Walkthrough Video Demonstration Script: Crop Yield Prediction System (PROJECT-007)

## Demonstration Metadata
- **Duration**: 03:00 (180.0 seconds)
- **Target Video File**: `walkthrough/walkthrough_video.mp4`
- **Resolution**: 1280x800, 24 fps, H.264 / AAC
- **Target URL**: `http://127.0.0.1:5007`

## Script Breakdown

### Section 1: Agricultural Intelligence Dashboard & System KPIs (00:00 - 00:25)
- **Visual**: The browser navigates to `#dashboard`. The screen highlights the 4 executive metric cards: Total Historical Records (28,242), Monitored Sovereign Nations (101), Staple Crop Taxonomies (10), and Global Mean Agricultural Yield (77,895 hg/ha).
- **Narration**: "Welcome to the demonstration of Project 7: Crop Yield Prediction using Machine Learning Algorithms. We begin on the executive analytics dashboard. Built upon decades of harmonized FAO and World Bank agricultural and meteorological records, our platform delivers real-time forecasting to bolster food security and optimize harvest logistics."

### Section 2: Interactive Yield Prediction & Environmental Feature Conditioning (00:25 - 00:55)
- **Visual**: Transition to `#predictions`. The user inspects the form inputs: Geographic Area (India), Target Crop (Rice, paddy), Average Annual Precipitation (1,050 mm), Agrochemical Usage (56,000 tonnes pesticides), and Mean Temperature (26.5 °C).
- **Narration**: "Navigating to the predictive inference interface, agricultural planners input localized agro-ecological parameters. Our input validation pipeline ensures physical plausibility across rainfall, temperature, and agrochemical volume prior to model ingestion."

### Section 3: Random Forest Inference & Predictive Yield Estimation (00:55 - 01:25)
- **Visual**: The user clicks 'Predict Yield'. The system evaluates the 115-feature One-Hot Encoded pipeline through our production Random Forest Regressor ($R^2 = 0.985$). An estimate of 38,420 hg/ha is generated with a 95% confidence interval [35,900 - 40,940 hg/ha] and risk assessment flags.
- **Narration**: "Executing real-time inference, the model returns an estimated harvest yield of 38,420 hectograms per hectare alongside statistical confidence intervals. The prediction is instantly written to our relational SQLite audit ledger with sub-50 millisecond roundtrip latency."

### Section 4: Multi-Crop Agronomic Recommendation Matrix (01:25 - 01:50)
- **Visual**: The user switches to the 'Crop Recommendation' tab and clicks 'Recommend Best Crops'. The system evaluates all 10 staple crops across the given climate parameters and ranks them in descending order of productivity (e.g., Potatoes: 215,400 hg/ha, Cassava: 112,000 hg/ha, Rice: 38,420 hg/ha).
- **Narration**: "In addition to single-crop queries, the engine computes a comparative optimization matrix. By simulating identical pedoclimatic conditions across all staple food crops, farm managers receive data-driven crop selection guidance to maximize caloric output."

### Section 5: Comparative Regression Leaderboard & Model Benchmarks (01:50 - 02:15)
- **Visual**: The page scrolls down to the Model Benchmark Leaderboard. The table showcases 6 evaluated models: Random Forest ($R^2 = 0.985$, RMSE: 10,480), Gradient Boosting ($R^2 = 0.962$), Decision Tree ($R^2 = 0.954$), Polynomial Regression ($R^2 = 0.742$), Support Vector Regression ($R^2 = 0.680$), and Linear Regression ($R^2 = 0.610$).
- **Narration**: "Our rigorous model validation framework benchmarks 6 distinct regression architectures against a 20% holdout test set. Random Forest significantly outperforms baseline parametric regressors, capturing non-linear precipitation-temperature interactions without overfitting."

### Section 6: Historical Data Exploration & Multi-Country Yield Trends (02:15 - 02:35)
- **Visual**: Navigating to `#exploration`. The interactive Chart.js line and bar charts display historical yield progression from 1990 to 2013, illustrating national disparities between mechanized European agriculture and rainfed equatorial farming.
- **Narration**: "The exploratory analytics suite provides macro-level longitudinal insights. Users can examine decades of yield evolution, isolate climatic anomalies, and identify regional agricultural resilience trends."

### Section 7: Global Feature Importance & Ecological Sensitivities (02:35 - 02:50)
- **Visual**: Moving to `#visualizations`. The screen renders the Random Forest Gini feature importance chart, demonstrating the relative weights of crop species indicators, historical geographic baselines, temperature, and rainfall.
- **Narration**: "To ensure algorithmic transparency, feature importance diagnostics reveal that crop biological identity and geographic baseline productivity drive over 70% of predictive variance, with climate fluctuations modulating annual deviations."

### Section 8: Summary & Final Capstone QA Sign-Off (02:50 - 03:00)
- **Visual**: Return to `#dashboard` overview.
- **Narration**: "Project 7 successfully integrates robust machine learning regression, production REST APIs, relational audit logging, and modern web visualization into an end-to-end, college-submission-ready agricultural analytics platform."
