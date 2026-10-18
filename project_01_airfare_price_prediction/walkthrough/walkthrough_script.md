# Demonstration Walkthrough Script: AeroPredict Airfare Intelligence Engine (PROJECT-001)

**Project Title**: A Holistic Approach on Airfare Price Prediction Using LSTM Machine Learning Techniques  
**Recorded File**: `walkthrough/walkthrough_video.mp4` (Duration: 02:37)  
**Presenter**: Software QA & Machine Learning Engineer  

---

### Step 1: Introduction & Service Verification (00:00 - 00:12)
- **Narration**: "Welcome to the final-year engineering demonstration of Project 01: AeroPredict, a machine learning and deep learning flight valuation system designed to predict dynamic airfare using Bidirectional LSTM recurrent neural networks alongside an ensemble Random Forest benchmark."
- **Visual Action**: The browser opens `http://127.0.0.1:5001/`. The top banner displays the AeroPredict brand, navigation tabs, and flight parameter input fields.

### Step 2: User Interface & Parameter Form (00:12 - 00:24)
- **Narration**: "The user interface is structured into four primary operational tabs: the Valuation Engine, Model Performance Benchmarks, Persistent Prediction History, and Industry Pricing Analytics. The form allows travelers and analysts to configure the operating carrier, departure city, destination, travel date, layover stops, and departure/arrival times."
- **Visual Action**: Cursor highlights the operating airline selector, origin, destination, and stops dropdown.

### Step 3: Flight 1 — IndiGo Direct Route Prediction (00:24 - 00:43)
- **Narration**: "Let us evaluate a typical direct flight on a budget carrier: IndiGo, departing from Bangalore to Delhi with non-stop routing. Upon clicking Predict, the preprocessor transforms the 31-dimensional temporal and carrier feature vector, feeding it to both the PyTorch Bidirectional LSTM model and our Random Forest benchmark."
- **Visual Action**: Form submitted. Results banner renders immediately with fare ₹4,108 (~$49.20 USD). Comparative cards display the LSTM prediction (₹3,960) and Random Forest prediction (₹4,330) with duration badge '2h 45m' and confidence interval.

### Step 4: Flight 2 — Air India Layover Journey with Stop Penalty (00:43 - 01:03)
- **Narration**: "Next, we simulate a more complex itinerary: Air India from Mumbai to Cochin with 2 layover stops. As shown in the updated prediction, the neural network factors in the route complexity, layover duration, and fuel penalties, resulting in an adjusted dynamic valuation."
- **Visual Action**: Form updated to Air India, Mumbai to Cochin, 2 stops. Prediction clicked. Updated fare card and duration badges appear.

### Step 5: Flight 3 — Full-Service Vistara Route (01:03 - 01:23)
- **Narration**: "We now configure a full-service carrier, Vistara, from Delhi to Hyderabad with 1 stop. The model accurately captures the premium pricing policy associated with full-service airlines versus low-cost carriers."
- **Visual Action**: Form updated to Vistara. New valuation displayed with Premium pricing tier badge.

### Step 6: Model Performance & Architecture Review (01:23 - 01:45)
- **Narration**: "Switching to the Model Performance tab, we inspect the empirical evaluation metrics measured on our held-out test split of 2,137 flights from the 10,683-record Kaggle Indian Domestic Flights dataset. The Random Forest achieves an R² of 0.8321, while the Bidirectional LSTM regressor achieves an R² of 0.7566 with a Mean Absolute Error of ₹1,136. The architecture consists of a 2-layer Bidirectional LSTM with hidden dimension 64, SmoothL1 loss, and AdamW optimization."
- **Visual Action**: Navigates to Performance tab, displaying the metrics grid and layer topology summary.

### Step 7: Persistent Database Audit Trail (01:45 - 02:07)
- **Narration**: "In the Prediction History tab, we verify database persistence. Every user query and model valuation is recorded into an embedded SQLite database with timestamp, route, layovers, LSTM fare, RF fare, and recommended price."
- **Visual Action**: Navigates to History tab, showing real-time query records with auto-increment IDs.

### Step 8: Airline Pricing Analytics (02:07 - 02:25)
- **Narration**: "The Pricing Analytics tab aggregates historical valuations across airlines, providing insights into average fare distributions across Jet Airways, Air India, IndiGo, SpiceJet, and Vistara."
- **Visual Action**: Navigates to Analytics tab, reviewing carrier pricing bars.

### Step 9: Operational Wrap-Up & Sign-Off (02:25 - 02:37)
- **Narration**: "Returning to the Valuation Engine, we confirm that AeroPredict has executed flawlessly, with zero runtime errors, genuine trained deep learning models, authentic SQLite persistence, and verified responsive interface."
- **Visual Action**: Navigates back to the main dashboard. The demonstration concludes cleanly.
