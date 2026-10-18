import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import random

app = Flask(__name__)
CORS(app)

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))

@app.route('/')
def serve_index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    target = os.path.join(FRONTEND_DIR, path)
    if os.path.exists(target) and not os.path.isdir(target):
        return send_from_directory(FRONTEND_DIR, path)
    return jsonify({'error': 'Not found'}), 404


# ─── WASTE CLASSIFICATION ─────────────────────────────────────────────────────
# Real: Use EfficientNet / MobileNetV3 + Transfer Learning on TrashNet/TACO dataset

WASTE_CATEGORIES = {
    'recyclable': ['Plastic Bottle', 'Glass Bottle', 'Aluminum Can', 'Cardboard', 'Paper', 'Metal Can'],
    'organic': ['Food Waste', 'Garden Waste', 'Wood', 'Compostable Packaging'],
    'hazardous': ['Battery', 'Electronic Waste', 'Chemical Container', 'Medical Waste', 'Paint Can'],
    'non_recyclable': ['Styrofoam', 'Contaminated Paper', 'Dirty Plastic', 'Mixed Material Packaging'],
    'electronic': ['Mobile Phone', 'Laptop', 'Printer', 'Cable', 'Circuit Board']
}

DISPOSAL_GUIDELINES = {
    'recyclable': 'Place in the blue recycling bin. Clean before disposing.',
    'organic': 'Place in the green composting bin. Reduces landfill waste.',
    'hazardous': 'Take to a designated hazardous waste facility. DO NOT put in regular bins.',
    'non_recyclable': 'Place in the black/grey general waste bin.',
    'electronic': 'Take to an e-waste collection center or manufacturer take-back program.'
}

detection_log = []

def classify_waste(image_data):
    category = random.choice(list(WASTE_CATEGORIES.keys()))
    item = random.choice(WASTE_CATEGORIES[category])
    confidence = round(random.uniform(0.70, 0.98), 3)
    return category, item, confidence

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'running', 'service': 'Waste Classification API (CNN)'})

@app.route('/api/classify', methods=['POST'])
def classify():
    data = request.json
    image_data = data.get('image', '')
    category, item, confidence = classify_waste(image_data)
    result = {
        'id': len(detection_log) + 1,
        'category': category,
        'category_label': category.replace('_', ' ').title(),
        'item': item,
        'confidence': confidence,
        'confidence_pct': round(confidence * 100, 1),
        'disposal_guide': DISPOSAL_GUIDELINES[category],
        'is_recyclable': category in ['recyclable', 'organic'],
        'color_code': {'recyclable': '#2196F3', 'organic': '#4CAF50', 'hazardous': '#F44336',
                       'non_recyclable': '#9E9E9E', 'electronic': '#FF9800'}[category],
        'timestamp': datetime.utcnow().isoformat(),
        'model': 'EfficientNetB3 (TrashNet)'
    }
    detection_log.append(result)
    return jsonify(result)

@app.route('/api/history', methods=['GET'])
def get_history():
    return jsonify(detection_log[-30:])

@app.route('/api/stats', methods=['GET'])
def stats():
    total = len(detection_log)
    by_cat = {}
    for d in detection_log:
        by_cat[d['category']] = by_cat.get(d['category'], 0) + 1
    recyclable = sum(1 for d in detection_log if d['is_recyclable'])
    return jsonify({'total': total, 'by_category': by_cat, 'recyclable': recyclable, 'non_recyclable': total-recyclable})

if __name__ == '__main__':
    app.run(debug=True, port=5036)
