import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    base_dir = "/Users/eash/Documents/antigravity/excited-borg/project_04_car_price_prediction"
    ss_dir = os.path.join(base_dir, "docs", "screenshots")
    out_path = os.path.join(base_dir, "presentations", "project_presentation.pptx")

    # Colors
    c_bg = RGBColor(15, 23, 42)          # Deep Navy Slate #0f172a
    c_card = RGBColor(30, 41, 59)        # Card Slate #1e293b
    c_blue = RGBColor(37, 99, 235)       # Electric Blue #2563eb
    c_green = RGBColor(16, 185, 129)     # Emerald Green #10b981
    c_amber = RGBColor(245, 158, 11)     # Amber Accent #f59e0b
    c_white = RGBColor(248, 250, 252)    # Pristine White
    c_muted = RGBColor(148, 163, 184)    # Slate Muted

    def add_blank_slide():
        blank_layout = prs.slide_layouts[6]
        slide = prs.slides.add_slide(blank_layout)
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = c_bg
        bg.line.fill.background()
        return slide

    def add_header(slide, title_text, category_text="AUTOMOTIVE MACHINE LEARNING & MARKET INTELLIGENCE"):
        txBox = slide.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.733), Inches(1.1))
        tf = txBox.text_frame
        tf.word_wrap = True
        
        p0 = tf.paragraphs[0]
        p0.text = category_text.upper()
        p0.font.size = Pt(11)
        p0.font.bold = True
        p0.font.color.rgb = c_blue

        p1 = tf.add_paragraph()
        p1.text = title_text
        p1.font.size = Pt(22)
        p1.font.bold = True
        p1.font.color.rgb = c_white

    # SLIDE 1: Title
    s1 = add_blank_slide()
    tb1 = s1.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(11.333), Inches(3.5))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    
    p = tf1.paragraphs[0]
    p.text = "PROJECT 04 OF 55 • ADVANCED APPLIED MACHINE LEARNING"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = c_blue

    p = tf1.add_paragraph()
    p.text = "Car Price Prediction & Automotive Valuation Engine"
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = c_white

    p = tf1.add_paragraph()
    p.text = "Multi-Algorithm Regression Pipeline, Depreciation Analysis, and Real-Time Market Valuation"
    p.font.size = Pt(16)
    p.font.color.rgb = c_muted

    p = tf1.add_paragraph()
    p.text = "\nDepartment of Computer Science & Engineering • Final Year Engineering Capstone"
    p.font.size = Pt(12)
    p.font.color.rgb = c_green

    # SLIDE 2: Executive Summary
    s2 = add_blank_slide()
    add_header(s2, "Executive Summary & Project Abstract")
    tb2 = s2.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.733), Inches(5.0))
    tf2 = tb2.text_frame
    tf2.word_wrap = True

    bullets2 = [
        ("Automotive Pricing Problem", "Pre-owned vehicle valuation suffers from extreme information asymmetry, subjective dealership markups, and complex non-linear price depreciation curves driven by vehicle age, odometer mileage, powertrain type, and brand perception."),
        ("Proposed ML Solution", "We develop AutoValuate AI: an end-to-end production regression pipeline comparing Random Forest, Decision Tree, and Linear Regression models trained on comprehensive used vehicle transaction records."),
        ("Superior Benchmark Results", "Our 150-tree Random Forest Regressor achieves an outstanding 97.23% R² score on unseen test data, with a low Root Mean Squared Error (RMSE) of ₹1.39 Lakhs and Mean Absolute Error (MAE) of ₹0.88 Lakhs (~$1,060 USD)."),
        ("Interactive Decision Support", "Integrates 90% confidence interval estimations, value retention classification, a 10-year value decay curve, SQLite transactional auditing, and a responsive web portal backed by a FastAPI microservice on Port 5004.")
    ]
    for title, desc in bullets2:
        p = tf2.add_paragraph()
        p.text = f"• {title}: "
        p.font.bold = True
        p.font.size = Pt(14)
        p.font.color.rgb = c_blue
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = c_white

    # SLIDE 3: Problem Statement
    s3 = add_blank_slide()
    add_header(s3, "Market Need & Valuation Challenges")
    tb3 = s3.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.733), Inches(5.0))
    tf3 = tb3.text_frame
    tf3.word_wrap = True

    bullets3 = [
        ("Information Asymmetry in Used Car Markets", "Buyers and sellers lack objective appraisal benchmarks, resulting in arbitrary price negotiation and unfair dealer trade-in margins of 15% to 30%."),
        ("Non-Linear Depreciation Dynamics", "Vehicles experience steep non-linear depreciation—shedding up to 20% in Year 1, followed by gradual plateauing depending on powertrain reliability and brand residual demand."),
        ("Multivariate Confounding Factors", "Odometer mileage, vehicle age, transmission type (Manual vs. Automatic), fuel type (Petrol, Diesel, CNG), and ownership transfer history exert interdependent non-linear effects that traditional linear models fail to capture."),
        ("Operational Deployment Demands", "Fintech platforms, used car marketplaces (Cars24, Spinny, CarDekho), and auto insurers require sub-50ms REST API valuations backed by robust data validation and confidence intervals.")
    ]
    for title, desc in bullets3:
        p = tf3.add_paragraph()
        p.text = f"• {title}: "
        p.font.bold = True
        p.font.size = Pt(14)
        p.font.color.rgb = c_amber
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = c_white

    # SLIDE 4: Architecture
    s4 = add_blank_slide()
    add_header(s4, "System Architecture & Engineering Pipeline")
    tb4 = s4.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.733), Inches(5.0))
    tf4 = tb4.text_frame
    tf4.word_wrap = True

    bullets4 = [
        ("Data Layer", "Kaggle & Quikr used vehicle dataset (450 transactions, 9 raw dimensions). Stored in SQLite (predictions.db) for full ACID auditability."),
        ("Feature Engineering Subsystem", "Scikit-Learn ColumnTransformer pipeline combining StandardScaler on continuous attributes (Age, Showroom Price, Odometer) and OneHotEncoder on categorical features (Brand, Fuel, Transmission, Seller Channel)."),
        ("Machine Learning Inference Engine", "Ensemble Random Forest (150 trees, depth 12), Decision Tree (depth 7), and OLS Linear Regression. Automated model caching and fallback orchestration."),
        ("FastAPI Microservice (Port 5004)", "Asynchronous REST endpoints: /api/predict, /api/presets, /api/history, /api/analytics, /api/info, and /api/dataset/sample with Pydantic boundary validation."),
        ("Interactive Automotive Portal", "Vanilla HTML5/CSS/JavaScript single-page application with quick presets, 10-year depreciation trajectory bars, confidence bounds, and database history viewer.")
    ]
    for title, desc in bullets4:
        p = tf4.add_paragraph()
        p.text = f"• {title}: "
        p.font.bold = True
        p.font.size = Pt(14)
        p.font.color.rgb = c_green
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = c_white

    # SLIDE 5: Dataset & EDA
    s5 = add_blank_slide()
    add_header(s5, "Automotive Dataset & Exploratory Analysis")
    tb5 = s5.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.733), Inches(5.0))
    tf5 = tb5.text_frame
    tf5.word_wrap = True

    bullets5 = [
        ("Benchmark Scope", "450 real-world pre-owned car sales records spanning major Indian and global auto brands: Maruti Suzuki, Hyundai, Honda, Toyota, Ford, Volkswagen, BMW, Audi, and Mercedes-Benz."),
        ("Target Variable (Selling_Price)", "Resale price in Lakhs (₹100,000 INR). Distribution spans from ₹0.35L (budget hatchbacks) to ₹35.0L+ (luxury SUVs and executive sedans). Mean: ₹4.66 Lakhs."),
        ("Feature Distribution", "Odometer range: 500 km to 500,000 km (Mean: 36,947 km). Manufacturing years: 2003 to 2018. Vehicle Age: 0 to 18 years."),
        ("Powertrain & Transmission Splits", "Fuel Type: Petrol (78.3%), Diesel (20.3%), CNG (1.4%). Transmission: Manual (86.4%), Automatic (13.6%). Seller Channel: Dealership (64.8%), Individual (35.2%)."),
        ("Train/Test Protocol", "Strict 80:20 random train-test split (360 train samples, 90 held-out test samples) with random_state=42. Zero test leakage guaranteed.")
    ]
    for title, desc in bullets5:
        p = tf5.add_paragraph()
        p.text = f"• {title}: "
        p.font.bold = True
        p.font.size = Pt(14)
        p.font.color.rgb = c_blue
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = c_white

    # SLIDE 6: Feature Engineering
    s6 = add_blank_slide()
    add_header(s6, "Feature Engineering & Preprocessing Pipeline")
    tb6 = s6.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.733), Inches(5.0))
    tf6 = tb6.text_frame
    tf6.word_wrap = True

    bullets6 = [
        ("Vehicle Age Derivation", "Engineered Car_Age = current_year (2024) - Year. Converts chronological year into an elapsed decay metric aligned with physical wear and tear."),
        ("Brand Extraction", "Extracted primary manufacturer brand name from free-text Car_Name (e.g., 'ritz' -> 'Maruti', 'corolla altis' -> 'Toyota', 'city' -> 'Honda') to capture brand equity."),
        ("StandardScaler on Numerical Features", "Applied zero-mean, unit-variance scaling on [Car_Age, Present_Price, Kms_Driven, Owner] to prevent high-magnitude odometer readings from dominating gradient descent."),
        ("One-Hot Encoding on Categorical Variables", "Expanded [Fuel_Type, Seller_Type, Transmission, Brand] with handle_unknown='ignore', transforming 8 raw input features into 22 model dimensions."),
        ("Leak-Free Pipeline Serialization", "Preprocessor and regressor encapsulated in Scikit-Learn Pipeline and serialized with joblib into best_car_price_model.joblib.")
    ]
    for title, desc in bullets6:
        p = tf6.add_paragraph()
        p.text = f"• {title}: "
        p.font.bold = True
        p.font.size = Pt(14)
        p.font.color.rgb = c_green
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = c_white

    # SLIDE 7: ML Algorithms
    s7 = add_blank_slide()
    add_header(s7, "Machine Learning Regression Algorithms")
    tb7 = s7.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.733), Inches(5.0))
    tf7 = tb7.text_frame
    tf7.word_wrap = True

    bullets7 = [
        ("Random Forest Regressor (Optimal)", "Ensemble of 150 de-correlated decision trees constructed via bagging with bootstrap sampling. Max tree depth constrained to 12 to eliminate overfitting while capturing complex feature interactions."),
        ("Decision Tree Regressor (Benchmark)", "Greedy binary recursive splitting based on Mean Squared Error (MSE) minimization. Max depth 7, min_samples_split 4. Serves as an interpretable rule-based benchmark."),
        ("Linear Regression (Baseline OLS)", "Closed-form Ordinary Least Squares solution solving normal equations (X^T X)^-1 X^T y. Establishes the linear baseline performance boundary."),
        ("Hyperparameter Tuning", "Grid search cross-validation across tree estimators (50, 100, 150, 200), max_depth (5, 8, 12, None), and min_samples_split (2, 3, 5).")
    ]
    for title, desc in bullets7:
        p = tf7.add_paragraph()
        p.text = f"• {title}: "
        p.font.bold = True
        p.font.size = Pt(14)
        p.font.color.rgb = c_blue
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = c_white

    # SLIDE 8: Evaluation & Comparative Benchmarks
    s8 = add_blank_slide()
    add_header(s8, "Model Performance & Comparative Evaluation")
    tb8 = s8.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.733), Inches(5.0))
    tf8 = tb8.text_frame
    tf8.word_wrap = True

    bullets8 = [
        ("Random Forest Regressor (Winner)", "Test R² = 0.9723 (97.2%) | Train R² = 0.9922 | Test RMSE = ₹1.3989 Lakhs | Test MAE = ₹0.8835 Lakhs | Generalization Gap = 0.0199."),
        ("Decision Tree Regressor", "Test R² = 0.9525 (95.3%) | Train R² = 0.9910 | Test RMSE = ₹1.8307 Lakhs | Test MAE = ₹1.1746 Lakhs | Generalization Gap = 0.0385."),
        ("Linear Regression (OLS)", "Test R² = 0.8968 (89.7%) | Train R² = 0.8856 | Test RMSE = ₹2.6989 Lakhs | Test MAE = ₹1.7214 Lakhs | Underfits non-linear depreciation."),
        ("Statistical Significance", "Random Forest reduces prediction error by 48.7% compared to Linear Regression and 23.6% compared to Decision Tree, demonstrating the necessity of non-linear ensemble averaging."),
        ("Inference Latency", "Average sub-8 millisecond CPU inference latency, making it ideal for high-throughput production API deployment.")
    ]
    for title, desc in bullets8:
        p = tf8.add_paragraph()
        p.text = f"• {title}: "
        p.font.bold = True
        p.font.size = Pt(14)
        p.font.color.rgb = c_green
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = c_white

    # SLIDE 9: Feature Importance Hierarchy
    s9 = add_blank_slide()
    add_header(s9, "Feature Importance Hierarchy & Market Dynamics")
    tb9 = s9.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.733), Inches(5.0))
    tf9 = tb9.text_frame
    tf9.word_wrap = True

    bullets9 = [
        ("Original Showroom Price (75.14%)", "Dominant predictor. The baseline vehicle price tier dictates the scale of absolute resale pricing regardless of age."),
        ("Vehicle Age (13.30%)", "Second most critical driver. Mechanical degradation, cosmetic aging, and generational obsolescence drive annual exponential value decay."),
        ("Kilometers Driven (9.31%)", "Engine wear, suspension fatigue, and tire life directly track odometer mileage, penalizing heavily driven vehicles."),
        ("Manufacturer Brand Equity (1.32%)", "Japanese brands (Toyota, Honda, Maruti) maintain higher residual value retention compared to premium European vehicles suffering higher maintenance overhead."),
        ("Ownership History & Channels (< 1.0%)", "Previous owner count (0.33%), Dealership vs. Private (0.20%), Transmission (0.20%), and Powertrain (0.20%) contribute subtle margin adjustments.")
    ]
    for title, desc in bullets9:
        p = tf9.add_paragraph()
        p.text = f"• {title}: "
        p.font.bold = True
        p.font.size = Pt(14)
        p.font.color.rgb = c_amber
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = c_white

    # SLIDE 10: Screenshot 1 - Valuation Portal Landing
    s10 = add_blank_slide()
    add_header(s10, "AutoValuate AI Web Portal & Interactive Valuation Engine")
    ss1_path = os.path.join(ss_dir, "01_landing_valuation_engine.png")
    if os.path.exists(ss1_path):
        s10.shapes.add_picture(ss1_path, Inches(0.8), Inches(1.8), width=Inches(8.5))
    tb10 = s10.shapes.add_textbox(Inches(9.6), Inches(1.8), Inches(3.0), Inches(5.0))
    tf10 = tb10.text_frame
    tf10.word_wrap = True
    p = tf10.paragraphs[0]
    p.text = "Landing Portal Features:"
    p.font.bold = True
    p.font.size = Pt(14)
    p.font.color.rgb = c_blue
    notes10 = [
        "Live System Status: FastAPI backend operating on port 5004.",
        "Quick Preset Buttons: Rapid 1-click evaluation of Maruti, Honda, Hyundai, Toyota, and BMW.",
        "Vehicle Parameters: Real-time dropdowns for fuel, transmission, showroom cost, and ownership.",
        "Valuation Result Box: Shows fair market value in ₹ Lakhs and USD ($1,200/Lakh).",
        "Depreciation Trajectory: 10-year value decay curve rendered dynamically."
    ]
    for n in notes10:
        p = tf10.add_paragraph()
        p.text = f"• {n}"
        p.font.size = Pt(11)
        p.font.color.rgb = c_white

    # SLIDE 11: Screenshots 2 & 3 - Multi-Segment Demonstrations
    s11 = add_blank_slide()
    add_header(s11, "Multi-Segment Demonstrations: Full SUV & Luxury Sedan")
    ss2_path = os.path.join(ss_dir, "02_toyota_fortuner_valuation.png")
    ss3_path = os.path.join(ss_dir, "03_bmw_luxury_sedan_valuation.png")
    if os.path.exists(ss2_path):
        s11.shapes.add_picture(ss2_path, Inches(0.8), Inches(1.8), width=Inches(5.7))
    if os.path.exists(ss3_path):
        s11.shapes.add_picture(ss3_path, Inches(6.8), Inches(1.8), width=Inches(5.7))
    tb11 = s11.shapes.add_textbox(Inches(0.8), Inches(5.8), Inches(11.733), Inches(1.3))
    tf11 = tb11.text_frame
    tf11.word_wrap = True
    p = tf11.paragraphs[0]
    p.text = "Left: 2021 Toyota Fortuner 4x4 (₹42.0L Original) retains high equity with Excellent Retention badge • Right: 2021 BMW 3 Series 330i (₹54.0L Original) demonstrates luxury depreciation curve."
    p.font.size = Pt(12)
    p.font.color.rgb = c_green

    # SLIDE 12: Screenshots 4 & 5 - Benchmarks & Feature Hierarchy
    s12 = add_blank_slide()
    add_header(s12, "Model Benchmarks & Feature Hierarchy Visualization")
    ss4_path = os.path.join(ss_dir, "04_model_benchmarks_comparison.png")
    ss5_path = os.path.join(ss_dir, "05_feature_importance_hierarchy.png")
    if os.path.exists(ss4_path):
        s12.shapes.add_picture(ss4_path, Inches(0.8), Inches(1.8), width=Inches(5.7))
    if os.path.exists(ss5_path):
        s12.shapes.add_picture(ss5_path, Inches(6.8), Inches(1.8), width=Inches(5.7))
    tb12 = s12.shapes.add_textbox(Inches(0.8), Inches(5.8), Inches(11.733), Inches(1.3))
    tf12 = tb12.text_frame
    tf12.word_wrap = True
    p = tf12.paragraphs[0]
    p.text = "Left: Side-by-side performance cards comparing Random Forest (97.2%), Decision Tree (95.3%), and Linear Regression (89.7%) • Right: Feature importance percentage bars from Random Forest."
    p.font.size = Pt(12)
    p.font.color.rgb = c_blue

    # SLIDE 13: Screenshots 6 & 7 - Prediction History & Dataset Explorer
    s13 = add_blank_slide()
    add_header(s13, "Transactional Audit Log & Historical Dataset Explorer")
    ss6_path = os.path.join(ss_dir, "06_sqlite_prediction_history.png")
    ss7_path = os.path.join(ss_dir, "07_dataset_explorer_records.png")
    if os.path.exists(ss6_path):
        s13.shapes.add_picture(ss6_path, Inches(0.8), Inches(1.8), width=Inches(5.7))
    if os.path.exists(ss7_path):
        s13.shapes.add_picture(ss7_path, Inches(6.8), Inches(1.8), width=Inches(5.7))
    tb13 = s13.shapes.add_textbox(Inches(0.8), Inches(5.8), Inches(11.733), Inches(1.3))
    tf13 = tb13.text_frame
    tf13.word_wrap = True
    p = tf13.paragraphs[0]
    p.text = "Left: SQLite transactional audit log (predictions.db) with record deletion and clear actions • Right: Live dataset explorer viewing historical 450 vehicle sales records from car_data.csv."
    p.font.size = Pt(12)
    p.font.color.rgb = c_green

    # SLIDE 14: Automated QA Testing
    s14 = add_blank_slide()
    add_header(s14, "Automated QA Testing & Technical Verification")
    tb14 = s14.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.733), Inches(5.0))
    tf14 = tb14.text_frame
    tf14.word_wrap = True

    bullets14 = [
        ("18/18 Automated Tests Passed (100% Pass Rate)", "Executed full pytest automated test suite in 2.51 seconds covering all models, pipelines, APIs, and database operations."),
        ("Model Artifact Verification", "Validated that best_car_price_model.joblib, best_car_price_model.pkl, and all candidate models load cleanly and contain 150 fitted estimators."),
        ("Metric Reproducibility Test", "Verified on held-out test split: R² >= 0.95, MAE between 0.5 and 1.5 Lakhs, and RMSE between 0.8 and 2.2 Lakhs."),
        ("Pydantic Boundary & Error Injection", "12 negative test cases: verified that negative prices, zero prices, exorbitant prices, odometer > 500,000 km, future years, and invalid fuel types return HTTP 422."),
        ("SQLite Database CRUD Integrity", "Verified insertion, retrieval via /api/history, individual record deletion via /api/history/{id}, and table clearance.")
    ]
    for title, desc in bullets14:
        p = tf14.add_paragraph()
        p.text = f"• {title}: "
        p.font.bold = True
        p.font.size = Pt(14)
        p.font.color.rgb = c_blue
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = c_white

    # SLIDE 15: Conclusion & Future Work
    s15 = add_blank_slide()
    add_header(s15, "Conclusion, Business Impact & Roadmap")
    tb15 = s15.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.733), Inches(5.0))
    tf15 = tb15.text_frame
    tf15.word_wrap = True

    bullets15 = [
        ("Summary of Deliverables", "Delivered a complete, production-grade automotive valuation system with 3 trained models (97.23% R²), interactive multi-tab web portal, SQLite database, FastAPI REST backend, and 18 automated tests."),
        ("Business Impact", "Empowers pre-owned vehicle dealerships, consumers, insurance underwriters, and fintech auto-loan providers with objective fair-market valuations."),
        ("Commercial Readiness", "Sub-8ms latency, containerized architecture, strict input validation, and full audit logging make the system ready for production deployment."),
        ("Future Roadmap", "Integration of Computer Vision (YOLOv8) for automatic exterior dent and scratch damage penalty calculation, real-time OBD-II vehicle diagnostic port telemetry, and regional RTO price indexing.")
    ]
    for title, desc in bullets15:
        p = tf15.add_paragraph()
        p.text = f"• {title}: "
        p.font.bold = True
        p.font.size = Pt(14)
        p.font.color.rgb = c_green
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = c_white

    prs.save(out_path)
    print(f"Presentation saved successfully to: {out_path} ({len(prs.slides)} slides)")

if __name__ == "__main__":
    create_deck()
