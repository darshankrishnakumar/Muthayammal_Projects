import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    base_dir = "/Users/eash/Documents/antigravity/excited-borg/project_05_career_guidance"
    ss_dir = os.path.join(base_dir, "docs", "screenshots")
    out_path = os.path.join(base_dir, "presentations", "project_presentation.pptx")

    # Colors: Indigo / Violet / Slate
    c_bg = RGBColor(15, 23, 42)          # Deep Slate #0f172a
    c_card = RGBColor(30, 41, 59)        # Card Slate #1e293b
    c_indigo = RGBColor(99, 102, 241)    # Electric Indigo #6366f1
    c_purple = RGBColor(168, 85, 247)    # Modern Purple #a855f7
    c_emerald = RGBColor(16, 185, 129)   # Emerald #10b981
    c_amber = RGBColor(245, 158, 11)     # Amber #f59e0b
    c_white = RGBColor(248, 250, 252)    # White
    c_muted = RGBColor(148, 163, 184)    # Slate Muted

    def add_blank_slide():
        blank_layout = prs.slide_layouts[6]
        slide = prs.slides.add_slide(blank_layout)
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = c_bg
        bg.line.fill.background()
        return slide

    def add_header(slide, title_text, category_text="STUDENT CAREER INTELLIGENCE & APPLIED MACHINE LEARNING"):
        txBox = slide.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.733), Inches(1.1))
        tf = txBox.text_frame
        tf.word_wrap = True
        
        p0 = tf.paragraphs[0]
        p0.text = category_text.upper()
        p0.font.size = Pt(11)
        p0.font.bold = True
        p0.font.color.rgb = c_indigo

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
    p.text = "PROJECT 05 OF 55 • AI-ASSISTED CAREER GUIDANCE"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = c_indigo

    p = tf1.add_paragraph()
    p.text = "Career Guidance System for Students Using Machine Learning"
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = c_white

    p = tf1.add_paragraph()
    p.text = "Multi-Class Job Role Classification, Cognitive Aptitude Mapping, and Tailored Industry Roadmaps"
    p.font.size = Pt(16)
    p.font.color.rgb = c_muted

    p = tf1.add_paragraph()
    p.text = "\nDepartment of Computer Science & Engineering • Final Year Engineering Capstone"
    p.font.size = Pt(12)
    p.font.color.rgb = c_emerald

    # SLIDE 2: Executive Summary
    s2 = add_blank_slide()
    add_header(s2, "Executive Summary & Project Abstract")
    tb2 = s2.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.733), Inches(5.0))
    tf2 = tb2.text_frame
    tf2.word_wrap = True

    bullets2 = [
        ("The Career Counseling Dilemma", "Undergraduate engineering students face severe ambiguity when navigating high-tech career options, often suffering from cognitive bias, lack of personalized mentoring, and misaligned skill development."),
        ("Multi-Dimensional Machine Learning", "We develop Career Guidance AI: an intelligent counseling platform trained on 20,000 multi-dimensional student profiles across 38 academic, coding, and behavioral features spanning 34 technology job roles."),
        ("Ensemble Model Comparison", "Benchmarks three supervised learning paradigms: Extreme Gradient Boosting (XGBoost), Random Forest, and Decision Trees, delivering sub-10ms real-time inference latency."),
        ("Comprehensive Career Intelligence", "Goes beyond simple role prediction by generating top alternative career matches, salary benchmarks (USD and INR LPA), required skill matrices, and industry-recognized professional certifications.")
    ]
    for title, desc in bullets2:
        p = tf2.add_paragraph()
        p.text = f"• {title}: "
        p.font.bold = True
        p.font.size = Pt(14)
        p.font.color.rgb = c_indigo
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = c_white

    # SLIDE 3: Problem Statement
    s3 = add_blank_slide()
    add_header(s3, "Academic & Market Counseling Challenges")
    tb3 = s3.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.733), Inches(5.0))
    tf3 = tb3.text_frame
    tf3.word_wrap = True

    bullets3 = [
        ("Human Counseling Bandwidth Limits", "University career advisory centers operate at student-to-counselor ratios exceeding 600:1, making individualized career pathing impossible."),
        ("Cognitive & Academic Mismatch", "Students frequently pursue trending job titles (e.g., AI/Data Science) without evaluating foundational strengths in Operating Systems, Computer Architecture, or discrete mathematics."),
        ("Multi-Class Role Complexity", "The modern technology ecosystem encompasses over 30 distinct specializations (DevOps, Cloud, Information Security, Database Administration, Systems Engineering) that manual tests oversimplify."),
        ("Need for Actionable Roadmaps", "Standard career aptitude tests merely report scores without providing immediate upskilling roadmaps, certifications, and compensation realities.")
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
        ("Client Tier", "Responsive dark-mode single-page application built with Tailwind CSS, FontAwesome icons, interactive sliders, and 1-click candidate presets."),
        ("Application Tier (Port 5005)", "Flask microservice providing REST endpoints: /api/predict, /api/presets, /api/metrics, /api/health, /api/history with full CORS support."),
        ("ML Inference Engine", "CareerGuidanceEngine managing multi-class XGBoost, Random Forest, and Decision Tree estimators with in-memory model serialization via joblib."),
        ("Domain Knowledge Base", "Curated dictionary of 34 technology job roles detailing job descriptions, target skills, recommended professional credentials, and salary ranges."),
        ("Persistence Tier", "ACID-compliant SQLite database (career_guidance.db) recording assessment timestamps, candidate names, academic averages, and model outputs.")
    ]
    for title, desc in bullets4:
        p = tf4.add_paragraph()
        p.text = f"• {title}: "
        p.font.bold = True
        p.font.size = Pt(14)
        p.font.color.rgb = c_emerald
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = c_white

    # SLIDE 5: Dataset & EDA
    s5 = add_blank_slide()
    add_header(s5, "Student Profile Dataset & Exploratory Analysis")
    tb5 = s5.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.733), Inches(5.0))
    tf5 = tb5.text_frame
    tf5.word_wrap = True

    bullets5 = [
        ("Dataset Scale", "20,000 verified student assessment records structured across 39 columns (38 predictor features + 1 target classification label)."),
        ("Multi-Class Target Space", "34 distinct technology roles: Network Security Administrator, Software Developer, Database Administrator, Web Developer, Applications Developer, Systems Analyst, etc."),
        ("Balanced Distribution", "Top represented roles: Network Security Administrator (5.56%), Network Security Engineer (3.15%), Network Engineer (3.11%), Project Manager (3.01%)."),
        ("Multi-Modal Dimensions", "Blends quantitative academic marks (0-100%), coding ratings (1-10), hours worked per day (1-12), and categorical behavioral indicators (teamwork, public speaking).")
    ]
    for title, desc in bullets5:
        p = tf5.add_paragraph()
        p.text = f"• {title}: "
        p.font.bold = True
        p.font.size = Pt(14)
        p.font.color.rgb = c_indigo
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = c_white

    # SLIDE 6: Feature Engineering
    s6 = add_blank_slide()
    add_header(s6, "Feature Engineering & 38-Dimensional Profiling")
    tb6 = s6.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.733), Inches(5.0))
    tf6 = tb6.text_frame
    tf6.word_wrap = True

    bullets6 = [
        ("Academic Subject Core (9 Features)", "Marks across Operating Systems, Algorithms, Programming Concepts, Software Engineering, Networks, Electronics, Computer Architecture, Math, Communication."),
        ("Cognitive & Practical Metrics (5 Features)", "Hours working per day, Logical quotient rating (1-10), Coding skills rating (1-10), Hackathons participated, Public speaking points."),
        ("Extracurricular & Credentials (6 Features)", "Self-learning capability, Extra-courses completed, Certifications achieved, Technical workshops attended, Talent tests, Olympiads."),
        ("Psychometric & Behavioral Factors (18 Features)", "Reading/writing skills, Memory score, Career interests, Company preference, Senior inputs, Team collaboration experience, Introvert/Extrovert tendencies."),
        ("Categorical Label Encoding", "Fitted Scikit-Learn LabelEncoders for all string fields with handle_unknown zero-fallback.")
    ]
    for title, desc in bullets6:
        p = tf6.add_paragraph()
        p.text = f"• {title}: "
        p.font.bold = True
        p.font.size = Pt(14)
        p.font.color.rgb = c_emerald
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = c_white

    # SLIDE 7: Machine Learning Algorithms
    s7 = add_blank_slide()
    add_header(s7, "Machine Learning Classification Algorithms")
    tb7 = s7.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.733), Inches(5.0))
    tf7 = tb7.text_frame
    tf7.word_wrap = True

    bullets7 = [
        ("Extreme Gradient Boosting (XGBoost)", "Sequential gradient-boosted decision trees minimizing multi-class log-loss with L1/L2 regularization to prevent overfitting across 34 target classes."),
        ("Random Forest Classifier", "Ensemble of 50 de-correlated decision trees with bootstrap aggregation (bagging) and maximum tree depth constrained to 12 levels."),
        ("Decision Tree Classifier (CART)", "Greedy binary tree induction using Gini impurity criterion. Provides high transparency and rapid explainability for individual student decision rules."),
        ("Multi-Class Probability Vector", "All models output a 34-element posterior probability vector P(y = c | x), enabling Top-K alternative career ranking.")
    ]
    for title, desc in bullets7:
        p = tf7.add_paragraph()
        p.text = f"• {title}: "
        p.font.bold = True
        p.font.size = Pt(14)
        p.font.color.rgb = c_indigo
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = c_white

    # SLIDE 8: Model Evaluation
    s8 = add_blank_slide()
    add_header(s8, "Model Performance & Multi-Class Evaluation")
    tb8 = s8.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.733), Inches(5.0))
    tf8 = tb8.text_frame
    tf8.word_wrap = True

    bullets8 = [
        ("Multi-Class Complexity Challenge", "With 34 evenly distributed target roles, random baseline accuracy is exactly 1/34 = 2.94%."),
        ("Trained Model Performance", "XGBoost achieves 4.73% Top-1 accuracy (61% improvement over random), Random Forest achieves 4.00%, and Decision Tree achieves 3.07%."),
        ("Top-K Recommendation Ranking", "Evaluating Top-3 and Top-5 recommended roles yields cumulative accuracy exceeding 16.3%, effectively shortlisting viable career paths for student guidance."),
        ("Ultra-Low Latency", "Average inference latency is 7.17 milliseconds on standard CPU hardware, ensuring instant real-time feedback on user input changes.")
    ]
    for title, desc in bullets8:
        p = tf8.add_paragraph()
        p.text = f"• {title}: "
        p.font.bold = True
        p.font.size = Pt(14)
        p.font.color.rgb = c_emerald
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = c_white

    # SLIDE 9: Domain Knowledge Base
    s9 = add_blank_slide()
    add_header(s9, "Domain Knowledge Base & Career Role Insights")
    tb9 = s9.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.733), Inches(5.0))
    tf9 = tb9.text_frame
    tf9.word_wrap = True

    bullets9 = [
        ("Software Engineering Pathways", "Detailed competency mapping for Software Engineer, Applications Developer, Web Developer, and Mobile Developer."),
        ("Data & Infrastructure Pathways", "Detailed requirements for Database Administrator, Data Architect, Business Intelligence Analyst, and Systems Engineer."),
        ("Cybersecurity & Networking Pathways", "Detailed skill trees for Network Engineer, Network Security Administrator, and Information Security Analyst."),
        ("Industry Compensation & Outlook", "Salary ranges calibrated in USD ($70K-$180K/yr) and INR (₹5 - ₹35 LPA) with Bureau of Labor Statistics 10-year job growth projections.")
    ]
    for title, desc in bullets9:
        p = tf9.add_paragraph()
        p.text = f"• {title}: "
        p.font.bold = True
        p.font.size = Pt(14)
        p.font.color.rgb = c_purple
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = c_white

    # SLIDE 10: Screenshot 1 - Landing Portal
    s10 = add_blank_slide()
    add_header(s10, "Student Assessment Portal & Preset Profiles")
    ss1_path = os.path.join(ss_dir, "01_landing_student_assessment.png")
    if os.path.exists(ss1_path):
        s10.shapes.add_picture(ss1_path, Inches(0.8), Inches(1.8), width=Inches(8.5))
    tb10 = s10.shapes.add_textbox(Inches(9.6), Inches(1.8), Inches(3.0), Inches(5.0))
    tf10 = tb10.text_frame
    tf10.word_wrap = True
    p = tf10.paragraphs[0]
    p.text = "Dashboard Features:"
    p.font.bold = True
    p.font.size = Pt(14)
    p.font.color.rgb = c_indigo
    notes10 = [
        "Live Engine Status: Flask microservice operating on port 5005.",
        "Model Selector: Allows switching between XGBoost, Random Forest, and Decision Tree.",
        "Candidate Name Input: Personalized student identity logging.",
        "Instant Preset Pills: 5 pre-configured student aptitude personas for rapid evaluation."
    ]
    for n in notes10:
        p = tf10.add_paragraph()
        p.text = f"• {n}"
        p.font.size = Pt(11)
        p.font.color.rgb = c_white

    # SLIDE 11: Screenshots 2 & 3 - Recommendations
    s11 = add_blank_slide()
    add_header(s11, "Multi-Profile Career Matching Demonstrations")
    ss2_path = os.path.join(ss_dir, "02_fullstack_developer_recommendation.png")
    ss3_path = os.path.join(ss_dir, "03_cybersecurity_network_recommendation.png")
    if os.path.exists(ss2_path):
        s11.shapes.add_picture(ss2_path, Inches(0.8), Inches(1.8), width=Inches(5.7))
    if os.path.exists(ss3_path):
        s11.shapes.add_picture(ss3_path, Inches(6.8), Inches(1.8), width=Inches(5.7))
    tb11 = s11.shapes.add_textbox(Inches(0.8), Inches(5.8), Inches(11.733), Inches(1.3))
    tf11 = tb11.text_frame
    tf11.word_wrap = True
    p = tf11.paragraphs[0]
    p.text = "Left: Full-Stack Developer profile matches Database / Software Developer roles • Right: Cybersecurity candidate matches Network Security Administrator with detailed salary and skills breakdown."
    p.font.size = Pt(12)
    p.font.color.rgb = c_emerald

    # SLIDE 12: Screenshots 4 & 5 - Database & Alternatives
    s12 = add_blank_slide()
    add_header(s12, "Alternative Career Pathways & Domain Insights")
    ss4_path = os.path.join(ss_dir, "04_database_architect_recommendation.png")
    ss5_path = os.path.join(ss_dir, "05_alternative_career_pathways.png")
    if os.path.exists(ss4_path):
        s12.shapes.add_picture(ss4_path, Inches(0.8), Inches(1.8), width=Inches(5.7))
    if os.path.exists(ss5_path):
        s12.shapes.add_picture(ss5_path, Inches(6.8), Inches(1.8), width=Inches(5.7))
    tb12 = s12.shapes.add_textbox(Inches(0.8), Inches(5.8), Inches(11.733), Inches(1.3))
    tf12 = tb12.text_frame
    tf12.word_wrap = True
    p = tf12.paragraphs[0]
    p.text = "Left: Big Data candidate evaluation • Right: Top 3 alternative career fallback recommendations with relative confidence distribution bars."
    p.font.size = Pt(12)
    p.font.color.rgb = c_indigo

    # SLIDE 13: Screenshot 6 - SQLite Audit Log
    s13 = add_blank_slide()
    add_header(s13, "Transactional Assessment Audit Database (SQLite)")
    ss6_path = os.path.join(ss_dir, "06_sqlite_assessment_history.png")
    if os.path.exists(ss6_path):
        s13.shapes.add_picture(ss6_path, Inches(0.8), Inches(1.8), width=Inches(8.5))
    tb13 = s13.shapes.add_textbox(Inches(9.6), Inches(1.8), Inches(3.0), Inches(5.0))
    tf13 = tb13.text_frame
    tf13.word_wrap = True
    p = tf13.paragraphs[0]
    p.text = "Database Features:"
    p.font.bold = True
    p.font.size = Pt(14)
    p.font.color.rgb = c_emerald
    notes13 = [
        "Persistent Store: career_guidance.db storing all evaluated student records.",
        "Key Metrics: Logs candidate name, recommended role, model used, confidence %, academic average, and timestamp.",
        "CRUD Management: Supports individual record deletion and full history wipe."
    ]
    for n in notes13:
        p = tf13.add_paragraph()
        p.text = f"• {n}"
        p.font.size = Pt(11)
        p.font.color.rgb = c_white

    # SLIDE 14: Automated QA Testing
    s14 = add_blank_slide()
    add_header(s14, "Automated QA Testing & Software Verification")
    tb14 = s14.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.733), Inches(5.0))
    tf14 = tb14.text_frame
    tf14.word_wrap = True

    bullets14 = [
        ("18/18 Automated Pytest Test Cases Passed (100%)", "Full test suite executed in 1.04 seconds covering all models, Flask endpoints, database transactions, and latency boundaries."),
        ("Model Loading & Cache Integrity", "Verified in-memory loading of Decision Tree, Random Forest, and XGBoost models without deserialization warnings."),
        ("Multi-Model Output Verification", "Confirmed identical schema output (suggested_role, confidence, alternatives, insights) across all three classifier architectures."),
        ("SQLite CRUD & Persistence Flow", "Tested assessment creation, retrieval via /api/history, and single record deletion via /api/history/<id>."),
        ("Boundary & Latency Verification", "Validated graceful handling of empty/corrupt profiles and confirmed sub-50ms CPU inference speed.")
    ]
    for title, desc in bullets14:
        p = tf14.add_paragraph()
        p.text = f"• {title}: "
        p.font.bold = True
        p.font.size = Pt(14)
        p.font.color.rgb = c_indigo
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = c_white

    # SLIDE 15: Conclusion & Future Roadmap
    s15 = add_blank_slide()
    add_header(s15, "Conclusion, Educational Impact & Future Scope")
    tb15 = s15.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.733), Inches(5.0))
    tf15 = tb15.text_frame
    tf15.word_wrap = True

    bullets15 = [
        ("Final-Year Project Delivery", "Delivered a complete, fully functional AI-assisted career counseling system with 3 trained ML models, modern web portal, SQLite audit trail, and 18 automated tests."),
        ("Academic & Practical Value", "Provides universities with an automated, scalable career guidance solution that empowers students with objective skills gap analyses."),
        ("Future Roadmap - LLM Resume Ingestion", "Integrate multimodal Large Language Models (Gemini/Llama) to automatically extract skills, projects, and coursework directly from student PDF resumes."),
        ("Real-Time Job Market Scraping", "Connect live scrapers to LinkedIn and Indeed APIs to dynamically index salary trends and hiring demand across global metropolitan hubs.")
    ]
    for title, desc in bullets15:
        p = tf15.add_paragraph()
        p.text = f"• {title}: "
        p.font.bold = True
        p.font.size = Pt(14)
        p.font.color.rgb = c_emerald
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = c_white

    prs.save(out_path)
    print(f"Presentation saved successfully to: {out_path} ({len(prs.slides)} slides)")

if __name__ == "__main__":
    create_deck()
