# Walkthrough Spoken Narration Script

**Project Code**: `PROJECT-003`  
**Project Title**: Apple Disease Detection Using Convolutional Neural Networks (CNN) & Grad-CAM  
**Target Video Duration**: 03:00 (180.0s)

---

### Segment 1: Introduction & Architecture Overview (00:00 - 00:20)
> *"Hello and welcome to the demonstration of Project 03: Apple Disease Detection Using Convolutional Neural Networks (CNN) and Grad-CAM Explainability. This system, Apple Health Intelligence AI, is a precision agricultural decision-support suite running live on port 5003. Built to aid apple orchardists and agricultural extension agents, our platform provides automated foliage and fruit pathology diagnosis, visual saliency heatmaps, and comprehensive fungicide recommendations."*

### Segment 2: Cedar Apple Rust Leaf Diagnosis (00:20 - 00:45)
> *"We start by selecting a leaf specimen infected with Cedar Apple Rust. With one click, the specimen is preprocessed and passed to our MobileNetV2 transfer learning model. Within 42 milliseconds, the system diagnoses Gymnosporangium juniperi-virginianae with 99.4% confidence and High Severity. Notice the detailed diagnostic card below: it lists typical symptoms, such as bright orange foliar lesions, and prescribes targeted FRAC Group 3 fungicide treatments alongside organic alternatives like liquid lime sulfur."*

### Segment 3: Apple Scab Foliar Lesion Diagnosis (00:45 - 01:10)
> *"Next, we test an apple leaf exhibiting olive-green sooty spots—the Apple Scab pathogen, Venturia inaequalis. Triggering analysis, the CNN accurately identifies foliar scab lesions. The decision-support engine recommends a preventive spray of Captan or Myclobutanil prior to rain infection events and outlines autumn leaf-shredding practices to prevent overwintering fungal ascospore release."*

### Segment 4: Black Rot / Frog-Eye Leaf Diagnosis (01:10 - 01:30)
> *"In our third scenario, we analyze a leaf with circular purple lesions known as frog-eye leaf spot, caused by Botryosphaeria obtusa. The network diagnoses Black Rot with high confidence, advising the grower to prune out dead wood and remove mummified fruit that harbor fungal cankers."*

### Segment 5: Healthy Pathogen-Free Foliage (01:30 - 01:50)
> *"To ensure that benign tissue is not falsely alarmed, we load a healthy apple leaf. The model immediately classifies the leaf as Healthy with 98.6% confidence and zero disease severity, verifying that no chemical sprays or interventions are required."*

### Segment 6: Apple Fruit Condition: Rotten vs Fresh (01:50 - 02:15)
> *"Beyond leaves, our multi-task architecture evaluates post-harvest apple fruit condition. Selecting a decayed apple specimen, the input validator routes the image to our fruit classification model, diagnosing Rotten fruit condition with high confidence and generating post-harvest sanitation guidelines to prevent storage bin contamination."*

### Segment 7: CNN Feature Maps & Grad-CAM Visual Heatmaps (02:15 - 02:30)
> *"Switching to the CNN Feature Maps tab, we inspect the internal representations learned by the network. Here we see layer activations and Grad-CAM visual saliency heatmaps. The glowing warm colors clearly highlight the localized fungal lesions on the leaf surface, proving that the model bases its decisions on genuine pathological evidence rather than background noise."*

### Segment 8: Agronomic Pathology & Treatment Guide (02:30 - 02:45)
> *"Navigating to the Treatment & Pathology Guide, we explore our extensive knowledgebase. Each disease profile details scientific nomenclature, symptoms, registered fungicides with FRAC codes to prevent chemical resistance, OMRI-listed organic remedies, and cultural canopy management practices."*

### Segment 9: Summary & Edge Deployment (02:45 - 03:00)
> *"Returning to the main dashboard, we see that all diagnostic queries have been transactionally logged into our SQLite database. With sub-45 millisecond inference latency on standard CPUs, Apple Health Intelligence AI is fully optimized for real-time edge deployment on mobile phones and orchard drones. This concludes our demonstration of Project 03."*
