# Walkthrough Spoken Narration Script

**Project Code**: `PROJECT-002`  
**Project Title**: Network Intrusion Detection Using Ensemble Machine Learning and Anomaly Detection  
**Target Video Duration**: 03:00 (180.0s)

---

### Segment 1: Introduction & Architecture Overview (00:00 - 00:20)
> *"Hello and welcome to the demonstration of Project 02: Network Intrusion Detection Using Ensemble Machine Learning and Anomaly Detection. Here we see CyberShield AI, an autonomous network security monitoring portal designed for modern enterprise perimeters. Operating live on port 5002, our system couples a high-precision supervised ensemble of Random Forest and Extra Trees with an unsupervised Isolation Forest anomaly detector. The dashboard provides an interactive packet inspector, empirical model benchmarks, a transactional SQLite security event stream, and real-time threat intelligence analytics."*

### Segment 2: Neptune SYN Flood DoS Interception (00:20 - 00:45)
> *"We begin our demonstration by loading a high-rate Denial-of-Service attack vector—the Neptune SYN flood. Notice the packet parameters: a TCP connection with connection flag S0 indicating a SYN request with no ACK, a high connection count of 250 in the past two seconds, and an SYN error rate of 1.0. When we trigger analysis, the dual inference engine processes the 111-dimensional feature vector in under 60 milliseconds. The ensemble identifies the threat as a DoS attack with 82.1% confidence and Critical Attack severity. The automated defense engine immediately issues a Block command to throttle the hostile source host."*

### Segment 3: Port Sweep Reconnaissance Probe (00:45 - 01:10)
> *"Next, we simulate a network reconnaissance probe—the Port Sweep attack. The attacker is probing multiple ports using TCP RST responses, marked by flag RSTR and an elevated reject error rate. Analyzing this inbound packet, the ensemble correctly categorizes the behavior as a Probe reconnaissance sweep with High Alert severity. The automated mitigation system flags the IP address for immediate perimeter blacklisting, preventing horizontal movement within the subnet."*

### Segment 4: Benign Legitimate Web Browsing (01:10 - 01:30)
> *"In our third scenario, we verify that legitimate traffic passes unimpeded without false alarms. Here is a standard benign HTTP web session with an established SF flag, normal payload sizes, and a successful login status. Executing analysis, the model reports Normal classification with 97.9% confidence and Benign threat status. The defense engine marks the traffic as Allowed."*

### Segment 5: Password Brute-Force R2L Attempt (01:30 - 01:50)
> *"Now we evaluate an unauthorized remote-to-local access attempt—a brute-force password guess over Telnet. Notice the hot indicator and five consecutive failed login attempts with logged_in set to zero. The model identifies this pattern as an R2L intrusion with 63.5% confidence and High Alert status, prompting the defense policy to revoke session tokens and block the authentication origin."*

### Segment 6: Zero-Day Out-of-Distribution Anomaly Detection (01:50 - 02:15)
> *"One of the greatest challenges in cybersecurity is detecting zero-day attacks that have never been seen before. Here we test a novel data exfiltration pattern with an unusual protocol flag and massive UDP payload volume. While supervised classifiers might fail to match a known signature, our unsupervised Isolation Forest measures the anomalous isolation path length, driving the anomaly score to 76.6%. The system triggers a Suspicious Anomaly verdict and routes the flow to a sandbox analyzer."*

### Segment 7: Model Benchmarks & Defense Taxonomy (02:15 - 02:30)
> *"Switching to the Model Benchmarks tab, we review our empirical evaluation on 4,509 held-out NSL-KDD test packets. The Random Forest classifier achieves an outstanding 98.34% accuracy and 0.9833 weighted F1-score, complemented by the Extra Trees classifier at 98.03% accuracy. The table below displays our complete five-class signature taxonomy and automated response rules."*

### Segment 8: Security Event Incident Audit Log (02:30 - 02:45)
> *"Navigating to the Security Event Logs tab, we observe the persistent transactional audit trail stored in our SQLite database. Every inspected connection is recorded with its timestamp, source and destination IP addresses, protocol, predicted classification, threat level, anomaly risk score, and executed mitigation action."*

### Segment 9: Threat Intelligence Analytics & Conclusion (02:45 - 03:00)
> *"Finally, on the Threat Intelligence Analytics tab, we see the real-time aggregated metrics across all inspected sessions. Out of our total inspected packets, the system has successfully isolated malicious intrusions while permitting benign traffic, maintaining an average inference latency under 60 milliseconds. This concludes our demonstration of Project 02, proving a robust, production-ready intrusion detection solution for modern cyber defense."*
