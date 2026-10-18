# Career Guidance Machine Learning System 🎓🤖

An intelligent, multi-dimensional Career Guidance & Job Role Recommendation platform built with Machine Learning (XGBoost, Random Forest, and Decision Tree classifiers) and a full-stack web interface.

---

## 🌟 Highlights & Capabilities
- **Multi-Class Career Prediction**: Evaluates 38 candidate parameters across academics, coding skills, hackathons, certifications, cognitive styles, and work preferences to recommend the ideal job role among 34 distinct tech roles.
- **Alternative Pathways & Confidence**: Provides prediction confidence percentages along with 3 top alternative career trajectories.
- **Actionable Career Blueprint**: Generates recommended technology roadmaps, required industry tools, certification paths, and expected salary ranges.
- **Audit History & Database**: Automatically persists every assessment into a SQLite database (`career_guidance.db`) with full review and deletion capabilities.
- **Ready-To-Test Candidate Presets**: 1-click test profiles for Full-Stack, Cloud/DevOps, Cybersecurity, Database, and UI/UX.

---

## 🚀 Quick Start (Running the Project)

### Option 1: One-Click Launch (Windows)
Double-click `run.bat`. It will automatically launch the server and open your browser at `http://localhost:5055`.

### Option 2: Command Line (Cross-Platform)
1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Start the Web App**:
   ```bash
   python app.py
   ```
3. **Open in Browser**:
   Navigate to `http://localhost:5055`.

---

## 🧪 Automated Testing
To run the automated validation test suite:
```bash
python test_model.py
```
This tests:
- Engine cache initialization and feature encoding
- Accuracy metrics across test splits
- Prediction consistency across test profiles
- SQLite assessment logging and record retrieval

---

## 📁 Repository Structure
- `app.py`: Flask web application and REST API endpoints
- `career_engine.py`: Machine Learning engine (XGBoost, Random Forest, Decision Tree) & insights
- `database.py`: SQLite database subsystem for assessment logging
- `career_pred.csv`: Student profile dataset (20,000 rows × 39 features)
- `model_cache.joblib`: Pre-trained model weights & encoders for instant startup
- `templates/index.html`: Responsive web user interface
- `test_model.py`: Automated test suite
- `verify_connection.py`: Live backend and database connectivity verifier
- `run.bat`: Windows one-click launcher
- `requirements.txt`: Python package dependencies
