# Phase 2 Remediation Plan & Final Submission Roadmap

**Objective**: Systematically address the 144 identified audit gaps and transition all 55 college projects from `PARTIALLY COMPLETE` to `VERIFIED COMPLETE` for college project evaluation.

---

## 1. Prioritized Remediation Roadmap

```
Phase 2 Audit Gaps Identified (144 Defects)
  ├── 1. Video Recording Sprint (55 Missing Videos) -> CRITICAL BLOCKER
  ├── 2. UI Screenshot Injection into PPTX (55 Decks) -> HIGH VALUE
  ├── 3. Model Weight Serialization (Tier 3 Scaffolds) -> MODERATE VALUE
  └── 4. Environment Dependency Alignment (Project 16 wfdb) -> LOW OVERHEAD
```

---

## 2. Action Plan by Workstream

### Workstream 1: Master Video Recording Sprint (55 Projects)
- **Tool Recommendation**: OBS Studio, macOS QuickTime Screen Recording (`Cmd+Shift+5`), or automated browser capture.
- **Recording Format**: MP4 (H.264 video codec, AAC audio, 1080p resolution, 30 fps).
- **Duration**: 2 minutes 30 seconds to 3 minutes 30 seconds per project.
- **Execution Order (by Priority)**:
  1. **Batch A (Tier 1 Web & ML Applications - 10 Projects)**:
     - `PROJECT-003` (Apple Disease Detection)
     - `PROJECT-004` (Car Price Prediction)
     - `PROJECT-005` (Career Guidance App)
     - `PROJECT-006` (Child Gait Analysis)
     - `PROJECT-007` (Crop Yield Prediction)
     - `PROJECT-008` (Customer Churn Prediction)
     - `PROJECT-012` (Egg Gender Prediction)
     - `PROJECT-014` (Fake News Detection)
     - `PROJECT-015` (Heart Disease Risk Assessment)
     - `PROJECT-018` (Dress Recommendation System)
  2. **Batch B (Modular College Platforms - 18 Projects)**:
     - `PROJECT-038` to `PROJECT-055`
  3. **Batch C (Interactive Prototypes & Scaffolds - 27 Projects)**:
     - `PROJECT-019` to `PROJECT-037`, followed by `001, 002, 009, 010, 011, 013, 016, 017`.
- **Validation Rule**: Once an MP4 file is recorded, place it at `<project_dir>/walkthrough/walkthrough_video.mp4`, verify file size $> 5 \text{ MB}$, and test playable status via media player.

### Workstream 2: Presentation Deck Customization (55 Decks)
- **Current State**: Standardized 8-slide decks containing accurate abstracts and architectures, but lacking real application screenshots.
- **Action**:
  - Run the application web servers.
  - Capture 2 high-resolution screenshots per project (e.g. Input Dashboard and Prediction Results / Data Analytics View).
  - Inject these screenshots into Slide 5 ("System Implementation & Working Interface") and Slide 6 ("Experimental Results & Evaluation Dashboard") using `python-pptx`.

### Workstream 3: Model Weight Serialization for Tier 3 Scaffolds (6 Projects)
- **Projects**: `PROJECT-001`, `002`, `009`, `010`, `011`, `013`.
- **Action**:
  - Replace `score = random.uniform(0.85, 0.99)` with pre-trained Scikit-Learn or PyTorch inference pipelines loaded from `.pkl` or `.pt` files.
  - Bundle reference test vectors in `tests/` to guarantee deterministic offline verification.

### Workstream 4: Environment Dependency Configuration (1 Project)
- **Project**: `PROJECT-016` (Medical Sensor Disease Prediction).
- **Action**: Run `pip install wfdb` in the Python virtual environment to allow `test_e2e_prediction.py` to execute against ECG signal samples.

---

## 3. Promotion Criteria to `VERIFIED COMPLETE`

A project may only be promoted to `VERIFIED COMPLETE` once all of the following conditions are met:
1. `walkthrough/walkthrough_video.mp4` exists, is non-zero, is verified playable, and demonstrates the project per `walkthrough_script.md`.
2. All unit, integration, and ML tests pass with exit code 0.
3. `presentations/project_presentation.pptx` contains at least one embedded UI screenshot.
4. `docs/technical_documentation.docx` reflects actual model evaluation numbers.
5. Master status dashboard is updated to reflect zero remaining defects.
