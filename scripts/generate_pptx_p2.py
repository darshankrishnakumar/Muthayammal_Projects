import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    base_dir = "/Users/eash/Documents/antigravity/excited-borg/project_02_network_intrusion_anomaly"
    ss_dir = os.path.join(base_dir, "docs", "screenshots")
    out_path = os.path.join(base_dir, "presentations", "project_presentation.pptx")

    # Colors
    c_bg = RGBColor(11, 15, 25)         # #0b0f19
    c_card = RGBColor(18, 28, 48)       # #121c30
    c_cyan = RGBColor(56, 189, 248)     # #38bdf8
    c_blue = RGBColor(2, 132, 199)      # #0284c7
    c_white = RGBColor(248, 250, 252)   # #f8fafc
    c_muted = RGBColor(148, 163, 184)   # #94a3b8
    c_green = RGBColor(16, 185, 129)    # #10b981
    c_red = RGBColor(239, 68, 68)       # #ef4444

    def add_blank_slide():
        blank_layout = prs.slide_layouts[6]
        slide = prs.slides.add_slide(blank_layout)
        # Background shape
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = c_bg
        bg.line.fill.background()
        return slide

    def add_header(slide, title_text, category_text="CYBERSHIELD AI / NETWORK SECURITY"):
        # Header banner
        txBox = slide.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.733), Inches(1.1))
        tf = txBox.text_frame
        tf.word_wrap = True
        
        p0 = tf.paragraphs[0]
        p0.text = category_text.upper()
        p0.font.size = Pt(11)
        p0.font.bold = True
        p0.font.color.rgb = c_cyan

        p1 = tf.add_paragraph()
        p1.text = title_text
        p1.font.size = Pt(22)
        p1.font.bold = True
        p1.font.color.rgb = c_white

    # ----------------- SLIDE 1: TITLE SLIDE -----------------
    s1 = add_blank_slide()
    tb1 = s1.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(11.333), Inches(3.5))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    
    p = tf1.paragraphs[0]
    p.text = "PROJECT 02 OF 55 • AUTONOMOUS CYBER DEFENSE"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = c_cyan

    p = tf1.add_paragraph()
    p.text = "Network Intrusion Detection Using Ensemble Machine Learning and Anomaly Detection"
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = c_white

    p = tf1.add_paragraph()
    p.text = "A Dual-Engine Architecture Combining Random Forest, Extra Trees, and Isolation Forest on NSL-KDD Network Traffic"
    p.font.size = Pt(16)
    p.font.color.rgb = c_muted

    p = tf1.add_paragraph()
    p.text = "\nDepartment of Computer Science & Engineering • Final Year Engineering Capstone"
    p.font.size = Pt(12)
    p.font.color.rgb = c_cyan

    # ----------------- SLIDE 2: EXECUTIVE SUMMARY -----------------
    s2 = add_blank_slide()
    add_header(s2, "Executive Summary & Problem Statement")
    tb2 = s2.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.733), Inches(5.0))
    tf2 = tb2.text_frame
    tf2.word_wrap = True

    bullets = [
        ("The Challenge: Escalating Cyber Threats", "Modern corporate and cloud perimeters face multi-gigabit traffic volumes with automated evasion attacks, sophisticated reconnaissance sweeps, and zero-day intrusion attempts that easily bypass static signature firewalls."),
        ("Core Limitation of Legacy IDS", "Rule-based Network Intrusion Detection Systems (e.g., Snort) cannot detect novel polymorphic variants and suffer from either catastrophic false-positive rates or slow manual signature update cycles."),
        ("Proposed Solution: Dual-Engine NIDS", "We design and implement CyberShield AI, a hybrid framework coupling a high-precision supervised ensemble (Random Forest + Extra Trees achieving 98.34% accuracy) with an unsupervised Isolation Forest anomaly detector for zero-day threat discovery."),
        ("Operational SOC Portal", "Delivered as an end-to-end production application: asynchronous FastAPI REST microservice, transactional SQLite audit database, and responsive dark-mode Security Operations Center (SOC) dashboard.")
    ]
    for title, desc in bullets:
        p = tf2.add_paragraph()
        p.text = f"• {title}: "
        p.font.bold = True
        p.font.size = Pt(15)
        p.font.color.rgb = c_cyan
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = c_white

    # ----------------- SLIDE 3: ATTACK TAXONOMY -----------------
    s3 = add_blank_slide()
    add_header(s3, "Taxonomy of Network Attacks in Enterprise Perimeters")
    tb3 = s3.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.733), Inches(5.0))
    tf3 = tb3.text_frame
    tf3.word_wrap = True

    attacks = [
        ("DoS (Denial of Service)", "Saturating host resources, memory, or connection state tables. Examples: Neptune (SYN flood), Smurf (ICMP broadcast amplification), Pod, Teardrop, Apache2."),
        ("Probe (Surveillance & Reconnaissance)", "Probing a network of computers to discover active services, open ports, and operating system fingerprints. Examples: PortSweep, IP Sweep, Nmap, Satan, Mscan, Saint."),
        ("R2L (Remote to Local)", "An unauthorized remote attacker attempts to exploit vulnerabilities to gain local user privileges. Examples: Guess_Passwd (brute force), FTP_Write, Imap, Phf, WarezMaster."),
        ("U2R (User to Root)", "A local unprivileged user executes buffer overflows or kernel race conditions to gain superuser / root privileges. Examples: Buffer_Overflow, Rootkit, LoadModule, Perl."),
        ("Zero-Day & Anomalous Traffic", "Novel, unseen out-of-distribution traffic patterns lacking historical signatures that require unsupervised isolation tree analysis.")
    ]
    for title, desc in attacks:
        p = tf3.add_paragraph()
        p.text = f"🛡️ {title}: "
        p.font.bold = True
        p.font.size = Pt(14)
        p.font.color.rgb = c_green if "Normal" in title else c_red
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = c_white

    # ----------------- SLIDE 4: SYSTEM ARCHITECTURE -----------------
    s4 = add_blank_slide()
    add_header(s4, "System Architecture: End-to-End Pipeline")
    tb4 = s4.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.733), Inches(5.0))
    tf4 = tb4.text_frame
    tf4.word_wrap = True

    arch_steps = [
        ("Layer 1 — Traffic Ingestion & Normalization", "Raw connection vectors (protocols, connection flags, payload byte counters, sliding-window traffic rates) are ingested via REST API or PCAP feed."),
        ("Layer 2 — Feature Transformation (111 Dimensions)", "Continuous parameters normalized via StandardScaler; categorical headers (protocol_type, service, flag) encoded via OneHotEncoder."),
        ("Layer 3 — Dual-Inference Machine Learning Engine", "1. Supervised Ensemble (Random Forest + Extra Trees, 200 total estimators) calculates multi-class attack probability distribution.\n2. Unsupervised Isolation Forest computes path length decision score for out-of-distribution anomaly risk."),
        ("Layer 4 — Automated Mitigation & SOC Response", "System maps classification and anomaly risk to actionable perimeter countermeasures: ALLOW, RATE-LIMIT/THROTTLE, BLACKLIST IP, REVOKE CREDENTIALS, or QUARANTINE HOST."),
        ("Layer 5 — Transactional Audit & Threat Analytics", "All packet telemetry, inference verdicts, and latencies persist atomically to SQLite3 database (`nids.db`).")
    ]
    for title, desc in arch_steps:
        p = tf4.add_paragraph()
        p.text = f"⚙️ {title}"
        p.font.bold = True
        p.font.size = Pt(14)
        p.font.color.rgb = c_cyan
        p_desc = tf4.add_paragraph()
        p_desc.text = desc
        p_desc.font.size = Pt(13)
        p_desc.font.color.rgb = c_white

    # ----------------- SLIDE 5: DATASET SPECIFICATIONS -----------------
    s5 = add_blank_slide()
    add_header(s5, "NSL-KDD Benchmark Dataset & Feature Engineering")
    tb5 = s5.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.733), Inches(5.0))
    tf5 = tb5.text_frame
    tf5.word_wrap = True

    ds_points = [
        ("Dataset Provenance", "NSL-KDD Network Intrusion Benchmark (University of New Brunswick / DARPA). Resolves redundant records present in legacy KDD'99 to ensure unbiased evaluation."),
        ("Dataset Volume", "22,544 full connection records. Partitioned into 18,035 training samples (80%) and 4,509 held-out testing samples (20%)."),
        ("Feature Groups", "• Basic Features: duration, protocol_type, service, flag, src_bytes, dst_bytes\n• Content Features: hot, num_failed_logins, logged_in, num_compromised, root_shell, su_attempted\n• Time-based Traffic Features: count, srv_count, serror_rate, rerror_rate, same_srv_rate\n• Host-based Traffic Features: dst_host_count, dst_host_srv_count, dst_host_diff_srv_rate"),
        ("Dimensional Transformation", "One-hot expansion across protocol services (http, private, telnet, ftp, smtp, etc.) and connection flags yields an expanded 111-dimensional feature space.")
    ]
    for title, desc in ds_points:
        p = tf5.add_paragraph()
        p.text = f"📊 {title}: "
        p.font.bold = True
        p.font.size = Pt(14)
        p.font.color.rgb = c_cyan
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = c_white

    # ----------------- SLIDE 6: ENSEMBLE CLASSIFICATION -----------------
    s6 = add_blank_slide()
    add_header(s6, "Ensemble Machine Learning Architecture")
    tb6 = s6.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.733), Inches(5.0))
    tf6 = tb6.text_frame
    tf6.word_wrap = True

    ens_points = [
        ("Ensemble Strategy: Soft-Voting Hybrid", "Combines bootstrap-aggregated Random Forest with Extremely Randomized Trees (Extra Trees) to minimize both variance and feature correlation."),
        ("Random Forest Classifier (100 Trees)", "Evaluates sub-sampled feature splits with Gini impurity. Achieves 98.34% test accuracy and 0.9833 weighted F1-score across 5 attack classes."),
        ("Extra Trees Classifier (100 Trees)", "Randomizes split cutpoints for faster convergence and enhanced generalization on rare intrusion classes. Achieves 98.03% test accuracy and 0.9800 weighted F1-score."),
        ("Consensus & Soft Probability Weighting", "Final multi-class probability is synthesized via: P(y=c|x) = 0.55 * P_RF(c|x) + 0.45 * P_ET(c|x). Provides calibrated confidence scoring for SOC operators.")
    ]
    for title, desc in ens_points:
        p = tf6.add_paragraph()
        p.text = f"🌳 {title}: "
        p.font.bold = True
        p.font.size = Pt(14)
        p.font.color.rgb = c_green
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = c_white

    # ----------------- SLIDE 7: ANOMALY DETECTION -----------------
    s7 = add_blank_slide()
    add_header(s7, "Unsupervised Anomaly Detection (Isolation Forest)")
    tb7 = s7.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.733), Inches(5.0))
    tf7 = tb7.text_frame
    tf7.word_wrap = True

    anom_points = [
        ("The Need for Unsupervised Detection", "Supervised models cannot classify attacks that have never been seen before. Zero-day exploits appear as novel clusters in high-dimensional feature space."),
        ("Isolation Forest Mechanism", "Isolates anomalies by recursively partitioning feature dimensions. Anomalous points require significantly fewer partitions (shorter path lengths) to isolate: s(x, n) = 2^(-E(h(x)) / c(n))."),
        ("Contamination Tuning", "Configured with contamination = 0.18 to match realistic perimeter intrusion proportions."),
        ("Dual Alert Threshold", "When supervised ensemble classifies a packet as 'Normal' but Isolation Forest yields an anomaly risk > 55%, the system elevates threat status to 'SUSPICIOUS_ANOMALY' and routes packet to a secure sandbox.")
    ]
    for title, desc in anom_points:
        p = tf7.add_paragraph()
        p.text = f"⚡ {title}: "
        p.font.bold = True
        p.font.size = Pt(14)
        p.font.color.rgb = RGBColor(168, 85, 247)
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = c_white

    # ----------------- SLIDE 8: SCREENSHOT 1 (LANDING / INSPECTOR) -----------------
    s8 = add_blank_slide()
    add_header(s8, "SOC Operations Portal & Real-Time Packet Inspector", "APPLICATION DEMONSTRATION")
    img_path = os.path.join(ss_dir, "01_soc_landing_inspector.png")
    if os.path.exists(img_path):
        s8.shapes.add_picture(img_path, Inches(0.8), Inches(1.6), Inches(11.733), Inches(5.2))

    # ----------------- SLIDE 9: SCREENSHOT 2 (NEPTUNE SYN FLOOD) -----------------
    s9 = add_blank_slide()
    add_header(s9, "Denial-of-Service Interception: Neptune SYN Flood", "ATTACK MITIGATION SCENARIO 1")
    img_path = os.path.join(ss_dir, "02_neptune_syn_flood.png")
    if os.path.exists(img_path):
        s9.shapes.add_picture(img_path, Inches(0.8), Inches(1.6), Inches(11.733), Inches(5.2))

    # ----------------- SLIDE 10: SCREENSHOT 3 (PORT SWEEP PROBE) -----------------
    s10 = add_blank_slide()
    add_header(s10, "Perimeter Surveillance Interception: Port Sweep Reconnaissance", "ATTACK MITIGATION SCENARIO 2")
    img_path = os.path.join(ss_dir, "03_portsweep_probe.png")
    if os.path.exists(img_path):
        s10.shapes.add_picture(img_path, Inches(0.8), Inches(1.6), Inches(11.733), Inches(5.2))

    # ----------------- SLIDE 11: SCREENSHOT 4 (ZERO-DAY ANOMALY) -----------------
    s11 = add_blank_slide()
    add_header(s11, "Zero-Day Exfiltration: Isolation Forest Anomaly Detection", "UNSUPERVISED ZERO-DAY SCENARIO")
    img_path = os.path.join(ss_dir, "04_zero_day_anomaly.png")
    if os.path.exists(img_path):
        s11.shapes.add_picture(img_path, Inches(0.8), Inches(1.6), Inches(11.733), Inches(5.2))

    # ----------------- SLIDE 12: SCREENSHOT 5 (BENCHMARKS) -----------------
    s12 = add_blank_slide()
    add_header(s12, "Empirical Evaluation Benchmarks & Attack Taxonomy", "PERFORMANCE BENCHMARKS")
    img_path = os.path.join(ss_dir, "05_model_benchmarks_tab.png")
    if os.path.exists(img_path):
        s12.shapes.add_picture(img_path, Inches(0.8), Inches(1.6), Inches(11.733), Inches(5.2))

    # ----------------- SLIDE 13: SCREENSHOT 6 (AUDIT LOGS) -----------------
    s13 = add_blank_slide()
    add_header(s13, "Transactional Security Event Audit Log (SQLite Database)", "DATABASE & INCIDENT AUDIT")
    img_path = os.path.join(ss_dir, "06_security_event_log_tab.png")
    if os.path.exists(img_path):
        s13.shapes.add_picture(img_path, Inches(0.8), Inches(1.6), Inches(11.733), Inches(5.2))

    # ----------------- SLIDE 14: SCREENSHOT 7 (THREAT ANALYTICS) -----------------
    s14 = add_blank_slide()
    add_header(s14, "Threat Intelligence Analytics & Incident Breakdown", "ANALYTICS & REPORTING")
    img_path = os.path.join(ss_dir, "07_threat_analytics_tab.png")
    if os.path.exists(img_path):
        s14.shapes.add_picture(img_path, Inches(0.8), Inches(1.6), Inches(11.733), Inches(5.2))

    # ----------------- SLIDE 15: CONCLUSION & IMPACT -----------------
    s15 = add_blank_slide()
    add_header(s15, "Project Conclusion & Engineering Achievements")
    tb15 = s15.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.733), Inches(5.0))
    tf15 = tb15.text_frame
    tf15.word_wrap = True

    concl_points = [
        ("Rigorous Empirical Performance", "Random Forest + Extra Trees ensemble achieved 98.34% test accuracy and 0.9833 weighted F1-score across 4,509 held-out NSL-KDD test packets with sub-60ms inference latency."),
        ("Hybrid Defense Coverage", "Coupled supervised multi-class attack attribution (DoS, Probe, R2L, U2R) with unsupervised Isolation Forest zero-day anomaly detection."),
        ("Complete End-to-End Delivery", "Delivered as a production-grade web application: asynchronous FastAPI REST service, transactional SQLite3 audit storage, and intuitive cybersecurity SOC dashboard."),
        ("Full QA & Reproducibility", "Backed by 19 automated tests (100% passing), verified H.264 demonstration recording, comprehensive academic documentation, and clear deployment instructions.")
    ]
    for title, desc in concl_points:
        p = tf15.add_paragraph()
        p.text = f"🏆 {title}: "
        p.font.bold = True
        p.font.size = Pt(14)
        p.font.color.rgb = c_cyan
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = c_white

    prs.save(out_path)
    print(f"15-Slide Presentation saved to {out_path}")

if __name__ == "__main__":
    create_deck()
