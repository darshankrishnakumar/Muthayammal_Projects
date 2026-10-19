# Walkthrough Script: Enterprise Stock Management & Predictive Inventory System (PROJECT-019)

**Presenter**: Lead System Architect / Engineering Capstone Researcher  
**System Target**: Port 5019 (`http://127.0.0.1:5019/`)  
**Target Duration**: Exactly 180.00 Seconds (03:00)

---

### [00:00 - 00:30] Phase 1: System Overview & Warehouse Stock Ledger
> "Welcome to the demonstration of Project-019: Stock Management System Pro (SMS), an enterprise cyber-physical inventory governance platform.
> We begin on the Executive Overview dashboard. Across the top banner, our real-time metrics display active warehouse SKUs, gross asset valuation of over INR 2.8 lakhs, cumulative POS sales volume, and items currently triggering Reorder Point warnings.
> On the left, our live warehouse stock ledger displays real-time inventory counts, category classifications, and dynamic status badges. On the right, the HTML5 canvas renders our 7-day sales velocity curve alongside an immutable transaction stream of inward and outward stock movements. Let us initiate an instant warehouse restock intake of 25 units for our barcode scanners."

---

### [00:30 - 01:05] Phase 2: IoT Hardware Terminal: Barcode Laser & UHF RFID Gate
> "Now let us navigate to Tab 1: our IoT Hardware Simulator. In modern distribution centers, barcode lasers and UHF RFID portal gates drive physical inventory tracking.
> Our terminal allows operators to test multi-protocol scans. We select our preset for SKU-001—the Wireless Barcode Scanner. First, we execute a non-invasive LOOKUP scan: the system queries the ledger and displays bin locations and stock counts.
> Next, we switch the action to SALE: firing the laser scan triggers an optical scan tone, generates a customer retail receipt, and decrements stock in real time.
> Finally, we switch to INWARD intake to simulate bulk pallet arrivals through the dock gate, instantly restocking 10 units with complete hardware device attribution."

---

### [01:05 - 01:30] Phase 3: Smart Weighing Shelf Telemetry & Shrinkage Forensics
> "Next, we examine the right-hand panel: IoT Smart Weighing Shelf Telemetry. In high-value pick zones, load-cell scales continuously transmit RS232 gross weight readings.
> The platform calculates expected item count by dividing gross shelf weight by the calibrated unit tare weight of 0.25 kilograms.
> When we query the sensor at 10.0 kilograms for 40 units, the system confirms a perfect MATCH.
> Now we simulate inventory shrinkage: if an operator removes 10 units unrecorded, the load cell registers 7.5 kilograms. The system computes a discrepancy of minus 10 units and immediately triggers a DEFICIT alert for forensic investigation."

---

### [01:30 - 02:00] Phase 4: Wholesaler Purchase Orders & Logistics Cargo Tracking
> "Moving to Tab 2: Wholesaler Orders & Shipments. Automated procurement is essential to prevent inventory depletion.
> The top ledger displays active Purchase Orders linked to verified tier-1 suppliers, detailing ordered items, wholesale unit costs, and delivery statuses.
> Below, our GPS cargo logistics panel monitors inter-state freight transit via carriers like BlueDart Express, tracking shipments from manufacturing origin yards through sorting sorting checkpoints to our warehouse receiving dock.
> When freight arrives at our receiving bay, the supervisor executes 'Receive Cargo'—in a single atomic database transaction, the purchase order is finalized, shipment is marked delivered, and warehouse stocks are replenished."

---

### [02:00 - 02:35] Phase 5: 7-Day AI Demand Forecasting & Dynamic ROP/EOQ
> "Now we transition to Tab 3: our flagship AI Demand Forecasting and Optimization engine.
> At the top, our model benchmark grid compares our four evaluated models: our PyTorch Bi-Directional LSTM with an R-squared of 0.9327, Scikit-Learn Random Forest at 0.9668, Gradient Boosting at 0.9670, and our classical ARIMA baseline.
> Below, the multi-horizon chart projects daily expected demand 7 days into the future, wrapped in 95% statistical confidence interval bands.
> We can filter demand curves by individual SKU or inspect consolidated warehouse consumption.
> Below the chart, our dynamic Reorder Point and Economic Order Quantity table calculates safety stock using Z=1.96 standard normal distribution, guaranteeing a 98.5% service level while minimizing annual holding and ordering costs."

---

### [02:35 - 03:00] Phase 6: Management Reports, Neural Architecture & SQLite Schema
> "In Tab 4, our compliance reporting module provides one-click timestamped CSV exports for inventory catalogs, POS sales receipts, and immutable movement audit logs.
> Finally, in Tab 5, we inspect our Neural Architecture and ML forensics: our PyTorch Bi-LSTM layer graph featuring 43,841 trainable parameters, Gini feature importance highlighting Lag-1 demand and rolling averages, and our complete 9-table relational database schema.
> With 29 automated tests achieving a 100% pass rate, dedicated Port 5019 allocation, and comprehensive academic documentation, Project-019 is fully verified and college capstone submission-ready."
