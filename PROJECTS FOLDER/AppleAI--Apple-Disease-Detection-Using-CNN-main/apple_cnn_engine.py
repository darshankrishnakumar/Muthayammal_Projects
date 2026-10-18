import os
import io
import math
import json
import base64
from pathlib import Path
import numpy as np
from PIL import Image

import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms as transforms
import torchvision.models as models

# Legacy 5-Class Target Conditions matching the Abstract for backwards compatibility
CLASS_NAMES = [
    'Apple_Scab',
    'Black_Rot',
    'Cedar_Apple_Rust',
    'Healthy_Apple',
    'Apple_Blotch'
]

CLASS_DISPLAY = {
    'Apple_Scab': {
        'name': 'Apple Scab',
        'latin': 'Venturia inaequalis',
        'type': 'Ascomycete Fungal Infection (Foliar & Fruit)',
        'severity': 'Moderate to High Severity',
        'severity_color': '#eab308',
        'severity_level': 3,
        'description': 'Apple Scab is a pervasive fungal disease caused by Venturia inaequalis. It attacks both leaves and fruit, developing velvety olive-green to dark brown corky lesions that cause premature defoliation, stunted fruit, and deep cork cracks.',
        'symptoms': [
            'Olive-green to velvety sooty lesions with feathery margins on upper leaf surfaces',
            'Cork-like scabby patches on fruit epidermis, leading to severe cracking and deformation',
            'Premature chlorosis and extensive summer defoliation weakening tree vigour',
            'Blistered lesions on shoots that may harbor overwintering mycelium'
        ],
        'decision_support': {
            'pesticide_suggestions': [
                {'name': 'Myclobutanil (Rally 40WSP)', 'type': 'DMI / FRAC Group 3', 'rate': '5.0 oz / acre', 'timing': 'Green tip through petal fall, max 4 sprays/season'},
                {'name': 'Captan 80 WDG', 'type': 'Multi-site / FRAC M04', 'rate': '2.5 - 3.75 lb / acre', 'timing': 'Apply prior to primary infection rain events'},
                {'name': 'Fluxapyroxad + Pyraclostrobin (Merivon)', 'type': 'SDHI + QoI (FRAC 7 + 11)', 'rate': '4.0 - 5.5 fl oz / acre', 'timing': 'Pink bud to petal fall for high disease pressure'}
            ],
            'preventive_measures': [
                'Flail-mow or shred dropped leaves in late autumn to speed microbial decomposition of fungal pseudothecia',
                'Apply a 5% agricultural urea solution spray to fallen leaves before winter dormancy to prevent ascospore release',
                'Prune tree canopy annually in open vase or central leader systems to maximize sunlight and airflow',
                'Plant scab-immune or resistant apple cultivars such as Liberty, Enterprise, Freedom, and Pristine'
            ],
            'organic_remedies': [
                {'name': 'Liquid Lime Sulfur (Calcium Polysulfide)', 'usage': '2 gal / 100 gal water at delayed dormant to pink stage'},
                {'name': 'Potassium Bicarbonate (Kaligreen / Armicarb)', 'usage': '2.5 - 3.0 lb / acre applied curatively within 24-36 hrs of rain'},
                {'name': 'Bacillus amyloliquefaciens (Double Nickel 55)', 'usage': '1.0 lb / acre biological biofungicide spray at 7-day intervals'},
                {'name': 'Pure Cold-Pressed Neem Oil (0.7%)', 'usage': 'Foliar application for prophylactic suppression of spore germination'}
            ]
        }
    },
    'Black_Rot': {
        'name': 'Black Rot / Frog-Eye Leaf Spot',
        'latin': 'Botryosphaeria obtusa',
        'type': 'Sphaeropsidales Fungal Pathology',
        'severity': 'Critical Decay & Defoliation',
        'severity_color': '#ef4444',
        'severity_level': 4,
        'description': 'Black Rot is a severe fungal disease of apple trees caused by Botryosphaeria obtusa. On leaves, it manifests as circular "frog-eye" spots with purple halos and tan centers; on fruit, it produces concentric brown rings that rapidly mummify the fruit.',
        'symptoms': [
            'Circular "frog-eye" leaf spots: small purple specks expanding into tan circular lesions with purple borders',
            'Concentric alternating dark and light brown circular decay rings radiating from fruit wounds or calyx',
            'Clusters of tiny black pycnidia (fruiting bodies) peppering the rotting fruit surface',
            'Shriveled, hardened "mummies" that cling to branches over winter, serving as continuous inoculum sources'
        ],
        'decision_support': {
            'pesticide_suggestions': [
                {'name': 'Pyraclostrobin (Cabrio EG)', 'type': 'QoI / FRAC Group 11', 'rate': '9.5 oz / acre', 'timing': 'Bloom through third cover spray'},
                {'name': 'Thiophanate-methyl (Topsin M WSB)', 'type': 'MBC / FRAC Group 1', 'rate': '0.75 - 1.0 lb / acre (tank-mixed with Captan)', 'timing': 'Post-bloom cover sprays'},
                {'name': 'Ziram 76DF', 'type': 'Dithiocarbamate / FRAC M03', 'rate': '6.0 - 8.0 lb / acre', 'timing': 'Late season cover sprays against summer rot'}
            ],
            'preventive_measures': [
                'Vigorously collect and destroy (burn or deep-bury) all mummified apples from trees and orchard floor',
                'Prune out dead wood, fire-blight strikes, and cankers at least 15 cm (6 inches) below visible margins',
                'Paint bark wounds and manage tree borers and cicada damage that create infection courtways',
                'Avoid overhead irrigation that prolongs canopy leaf wetness beyond 9 hours'
            ],
            'organic_remedies': [
                {'name': 'Copper Octanoate (Soap Shield)', 'usage': '1.5 - 2.0 fl oz / gal water as protective dormant and pre-bloom spray'},
                {'name': 'Bio-antagonist Aureobasidium pullulans (Botry-Zen)', 'usage': 'Competitive exclusion treatment on fresh fruit wounds'},
                {'name': 'Aerated Compost Tea + Equisetum arvense (Horsetail)', 'usage': 'Biostimulant foliar wash to strengthen epidermal silica barriers'},
                {'name': 'Sulfur 80 WDG (OMRI Listed)', 'usage': '6 - 10 lb / acre protective dusting during warm humid periods'}
            ]
        }
    },
    'Cedar_Apple_Rust': {
        'name': 'Cedar Apple Rust',
        'latin': 'Gymnosporangium juniperi-virginianae',
        'type': 'Heteroecious Rust Fungus (Foliar Target)',
        'severity': 'Moderate Foliar Disease',
        'severity_color': '#f97316',
        'severity_level': 2,
        'description': 'Cedar Apple Rust is a heteroecious fungus requiring two alternating hosts: Eastern Red Cedar / Juniper (Juniperus virginiana) and Apple (Malus). In spring, spores from cedar galls blow onto apple foliage, creating unmistakable brilliant yellow-orange spots.',
        'symptoms': [
            'Brilliant bright yellow-orange circular spots on upper apple leaf surfaces with reddish outer halos',
            'Tiny dark fungal pycnia (black pimples) clustered in the centers of orange leaf spots',
            'Fringed, tube-like aecia structures forming on the underside of leaves and fruit calyx in mid-summer',
            'Severe leaf distortion and premature leaf loss under heavy alternating host spore showers'
        ],
        'decision_support': {
            'pesticide_suggestions': [
                {'name': 'Trifloxystrobin (Flint Extra)', 'type': 'Strobilurin / FRAC 11', 'rate': '2.5 - 2.9 fl oz / acre', 'timing': 'Tight cluster through second cover'},
                {'name': 'Myclobutanil (Immunox / Rally)', 'type': 'Sterol Inhibitor / FRAC 3', 'rate': '5.0 oz / acre', 'timing': 'Pink bud to petal fall (highly specific against rusts)'},
                {'name': 'Mancozeb (Dithane F-45 / Manzate)', 'type': 'Multi-site / FRAC M03', 'rate': '3.2 qt / acre', 'timing': 'Protective barrier spray before cedar gall gelatinization'}
            ],
            'preventive_measures': [
                'Eradicate Eastern red cedars and decorative junipers within 1 to 2 miles of commercial apple orchard perimeter',
                'Physically inspect and cut out brown gelatinous cedar galls from adjacent ornamental junipers in late winter',
                'Select rust-immune or resistant varieties: RedFree, Liberty, Freedom, Enterprise, Dayton, Priscilla',
                'Avoid highly susceptible cultivars like Rome Beauty, Golden Delicious, Jonathan, and Gala near wooded perimeters'
            ],
            'organic_remedies': [
                {'name': 'Micronized Wettable Sulfur (90%)', 'usage': '10 - 15 lb / acre applied every 7-10 days throughout rust spore release'},
                {'name': 'Bacillus subtilis strain QST 713 (Serenade ASO)', 'usage': '2 - 4 qt / acre applied preventatively to suppress basidiospore penetration'},
                {'name': 'Garlic Barrier + Horticultural Mineral Oil', 'usage': 'Physical spore impediment spray applied prior to warm spring rains'},
                {'name': 'Potassium Silicate (Sil-Matrix)', 'usage': '1 - 2 qt / acre to reinforce epidermal leaf cuticles against fungal haustoria'}
            ]
        }
    },
    'Healthy_Apple': {
        'name': 'Healthy Apple Specimen',
        'latin': 'Malus domestica (Pathogen-Free)',
        'type': 'Physiologically Normal & Vigorous',
        'severity': 'Optimal Health',
        'severity_color': '#10b981',
        'severity_level': 0,
        'description': 'The apple specimen displays optimal physiological vigor with intact epidermal cells, dense chloroplast distribution, and zero necrotic, chlorotic, or fungal symptoms.',
        'symptoms': [
            'Vibrant, deep green leaf blades with fully intact cuticle and well-defined venation',
            'Zero necrotic spots, chlorotic rings, scabs, rust galls, or pycnidial fruiting bodies',
            'Smooth fruit epidermis with natural wax bloom and uniform cell expansion',
            'High photosynthetic output and healthy balance of vegetative and generative bud development'
        ],
        'decision_support': {
            'pesticide_suggestions': [
                {'name': 'No Therapeutic Pesticide Needed', 'type': 'Not Applicable', 'rate': '0', 'timing': 'Maintenance phase; conserve beneficial arthropods and native orchard biome'}
            ],
            'preventive_measures': [
                'Perform weekly systematic orchard scouting following an integrated pest management (IPM) monitoring grid',
                'Maintain balanced fertigation: avoid excessive nitrogen that generates succulent, disease-prone shoots',
                'Ensure drip or under-canopy micro-sprinklers are calibrated to prevent unnecessary leaf wetting',
                'Maintain grass mulch alleyways to minimize dust and spore splashing from bare orchard soil'
            ],
            'organic_remedies': [
                {'name': 'Prophylactic Kelp Meal & Seaweed Extract', 'usage': 'Foliar spray (2 qt / acre) to stimulate natural systemic acquired resistance (SAR)'},
                {'name': 'Mycorrhizal Fungi Inoculant (Glomus intraradices)', 'usage': 'Root zone drench to bolster phosphorus uptake and root resilience'},
                {'name': 'Beneficial Insectary Hedgerows', 'usage': 'Plant sweet alyssum and dill borders to shelter predatory mites and lacewings'},
                {'name': 'Regular Horticultural Oil Flush (Dormant)', 'usage': '1.5% dormant oil spray to suffocate overwintering scale and mite eggs'}
            ]
        }
    },
    'Apple_Blotch': {
        'name': 'Apple Blotch',
        'latin': 'Phyllosticta solitaria',
        'type': 'Fungal Cortical & Epicuticular Infection',
        'severity': 'High Severity',
        'severity_color': '#d97706',
        'severity_level': 3,
        'description': 'Apple Blotch is caused by Phyllosticta solitaria. It produces dark, irregular star-shaped crusty blotches with fringed margins on fruit, and raised pinhead lesions on petioles that cause cracking and severe yield reduction.',
        'symptoms': [
            'Dark olive to black crusty blotches with fringed irregular margins on expanding fruit',
            'Deep superficial cracks radiating across fruit surfaces as tissue expands',
            'Small, raised, light-colored pinhead lesions on leaf petioles and midribs',
            'Swollen, rough cankers on twigs that serve as perennial overwintering fungal reservoirs'
        ],
        'decision_support': {
            'pesticide_suggestions': [
                {'name': 'Captan 80 WDG + Ziram', 'type': 'Multi-site / FRAC M04 + M03', 'rate': '2.5 lb + 4 lb / acre', 'timing': 'Petal fall through 4th cover spray'},
                {'name': 'Boscalid + Pyraclostrobin (Pristine)', 'type': 'SDHI + QoI (FRAC 7 + 11)', 'rate': '14.5 - 18.5 oz / acre', 'timing': 'At 2nd and 4th cover sprays for blotch control'},
                {'name': 'Copper Hydroxide (Kocide 3000)', 'type': 'Inorganic / FRAC M01', 'rate': '3.5 - 7.0 lb / acre', 'timing': 'Delayed dormant stage only to prevent phytotoxicity'}
            ],
            'preventive_measures': [
                'Prune out dead wood, cankered twigs, and water sprouts during winter dormancy',
                'Disinfect pruning shears in 70% isopropyl alcohol or 10% sodium hypochlorite between cuts',
                'Ensure adequate canopy airflow through annual thinning and proper tree training',
                'Choose resistant apple varieties where feasible and avoid planting near infected wild crabapples'
            ],
            'organic_remedies': [
                {'name': 'Bacillus subtilis (Serenade MAX)', 'usage': '1 - 3 lb / acre applied at petal fall through cover sprays'},
                {'name': 'Liquid Sulfur + Spreader Sticker', 'usage': '6 - 8 lb / 100 gal as preventative cover spray'},
                {'name': 'Trichoderma harzianum (RootShield PLUS)', 'usage': 'Soil biological amendment to suppress pathogen inoculum'},
                {'name': 'Neem Cake Soil Application', 'usage': '100 kg / acre incorporated into root zone for natural bio-nematicidal benefits'}
            ]
        }
    },
    'Fresh': {
        'name': 'Fresh Healthy Apple (Fruit)',
        'latin': 'Malus domestica (Sound Post-Harvest Fruit)',
        'type': 'Intact Commercial Grade Pomological Fruit',
        'severity': 'Fresh & Sound (Grade A)',
        'severity_color': '#10b981',
        'severity_level': 0,
        'description': 'The apple fruit is structurally sound, displaying crisp cellular turgor, intact waxy cuticle, and zero signs of soft rot decay, fungal mycelium, or brown mold breakdown.',
        'symptoms': [
            'Firm, uniform skin texture without water-soaked softening',
            'Zero brown concentric rot lesions or sunken decay pockets',
            'Intact natural epicuticular wax layer protecting internal flesh',
            'Natural calyx and stem basin integrity'
        ],
        'decision_support': {
            'pesticide_suggestions': [
                {'name': 'No Fungicidal Treatment Required', 'type': 'Not Applicable', 'rate': '0', 'timing': 'Maintain cold chain storage (0°C to 2°C, 90-95% RH)'}
            ],
            'preventive_measures': [
                'Store apples under Controlled Atmosphere (CA) storage (1.5% O2, 1.0% CO2 at 1°C) to retard senescence',
                'Handle harvest bins gently to avoid fruit micro-bruises that serve as infection courts',
                'Sanitize hydro-cooling and post-harvest washing water with peracetic acid or chlorine dioxide'
            ],
            'organic_remedies': [
                {'name': 'Chitosan Biopolymer Fruit Coating', 'usage': '1.0% food-grade foliar dip to preserve freshness and reduce weight loss'},
                {'name': 'Carnauba Wax Food-Grade Polish', 'usage': 'Post-harvest protective coating against moisture evaporation'}
            ]
        }
    },
    'Rotten': {
        'name': 'Rotten / Decayed Apple (Fruit)',
        'latin': 'Fruit Decay Complex (Botryosphaeria / Colletotrichum / Penicillium)',
        'type': 'Post-Harvest Soft Rot / Brown Rot Decay',
        'severity': 'Critical Fruit Decay (Unfit for Consumption)',
        'severity_color': '#ef4444',
        'severity_level': 4,
        'description': 'The apple exhibits severe fruit decay characterized by tissue necrosis, epidermal softening, brown discoloration, and active fungal spore breakdown. Unfit for fresh consumption or commercial distribution.',
        'symptoms': [
            'Water-soaked softening of the fruit flesh rapidly advancing into brown rot',
            'Concentric decay rings or sunken necrotic craters radiating from wounds',
            'Tufts of white, grey, or blue-green fungal spore masses erupting through epidermis',
            'Off-odors and fermentation byproducts from pectinolytic enzymes'
        ],
        'decision_support': {
            'pesticide_suggestions': [
                {'name': 'Fludioxonil (Scholar SC)', 'type': 'Phenylpyrrole / FRAC 12', 'rate': '16.0 - 32.0 fl oz / 100 gal', 'timing': 'Post-harvest drench/dip within 24 hours of harvest'},
                {'name': 'Pyrimethanil (Penbotec 400 SC)', 'type': 'Anilinopyrimidine / FRAC 9', 'rate': '16.0 fl oz / 100 gal', 'timing': 'Post-harvest fungicide drench before cold storage'}
            ],
            'preventive_measures': [
                'Immediately isolate and discard decayed fruit to prevent contact transmission in storage bins',
                'Disinfect packing line sorting rollers and storage crates with quaternary ammonium or ozone wash',
                'Ensure harvest workers trim fingernails and harvest with canvas bags to prevent skin punctures',
                'Avoid packing fruit harvested after prolonged rain periods when latent spore load is peak'
            ],
            'organic_remedies': [
                {'name': 'Pseudomonas syringae strain ESC-10 (Bio-Save 10 LP)', 'usage': 'Competitive antagonist post-harvest bio-wash against decay fungi'},
                {'name': 'Aqueous Ozone Sanitizing Rinse', 'usage': '1.5 - 2.5 ppm dissolved ozone wash for surface spore deactivation'},
                {'name': 'Hot Water Dips (Thermocure)', 'usage': 'Immerse fruit in 48°C water for 2-3 minutes to eliminate surface spore viability'}
            ]
        }
    },
    'Healthy': {
        'name': 'Healthy Apple Leaf',
        'latin': 'Malus domestica (Pathogen-Free Foliage)',
        'type': 'Physiologically Normal Foliage',
        'severity': 'Optimal Health',
        'severity_color': '#10b981',
        'severity_level': 0,
        'description': 'The apple leaf is healthy and vigorous with deep green chlorophyll pigment, intact cuticular membrane, and absence of necrotic spotting or powdery rust spores.',
        'symptoms': [
            'Intact, rich green leaf surface with crisp margins',
            'Zero olive-green scabs, orange rust spots, or frog-eye purple halos',
            'Uniform solar absorption and photosynthetic efficiency'
        ],
        'decision_support': {
            'pesticide_suggestions': [
                {'name': 'No Therapeutic Spray Required', 'type': 'Maintenance Phase', 'rate': '0', 'timing': 'Continue regular scouting'}
            ],
            'preventive_measures': [
                'Maintain annual canopy pruning for optimal light and airflow',
                'Scout orchard weekly during primary ascospore discharge periods (April - June)'
            ],
            'organic_remedies': [
                {'name': 'Prophylactic Seaweed / Kelp Foliar Spray', 'usage': '2 qt / acre for general foliar vigor'}
            ]
        }
    }
}


class AppleCustomCNN(nn.Module):
    """
    CNN Architecture from the project's original Jupyter Notebook:
    - Conv2D(128, (3,3), relu, input_shape=(224, 224, 3)) -> MaxPool(2,2)
    - Conv2D(128, (3,3), relu) -> MaxPool(2,2)
    - Conv2D(64, (3,3), relu) -> MaxPool(2,2)
    - Conv2D(64, (3,3), relu) -> MaxPool(2,2)
    - Flatten -> Dropout(0.5) -> Dense(512, relu) -> Dense(5, softmax)
    """
    def __init__(self, num_classes=5):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 128, kernel_size=3, padding=0)
        self.pool1 = nn.MaxPool2d(2, 2)
        
        self.conv2 = nn.Conv2d(128, 128, kernel_size=3, padding=0)
        self.pool2 = nn.MaxPool2d(2, 2)
        
        self.conv3 = nn.Conv2d(128, 64, kernel_size=3, padding=0)
        self.pool3 = nn.MaxPool2d(2, 2)
        
        self.conv4 = nn.Conv2d(64, 64, kernel_size=3, padding=0)
        self.pool4 = nn.MaxPool2d(2, 2)
        
        self.flatten = nn.Flatten()
        self.dropout = nn.Dropout(0.5)
        self.fc1 = nn.Linear(64 * 12 * 12, 512)
        self.fc2 = nn.Linear(512, num_classes)
        
        self.gradients = None
        self.activations = None

    def activations_hook(self, grad):
        self.gradients = grad

    def forward(self, x, retain_grad=False):
        x1 = F.relu(self.conv1(x))
        p1 = self.pool1(x1)
        
        x2 = F.relu(self.conv2(p1))
        p2 = self.pool2(x2)
        
        x3 = F.relu(self.conv3(p2))
        p3 = self.pool3(x3)
        
        x4 = F.relu(self.conv4(p3))
        if retain_grad:
            self.activations = x4
            x4.register_hook(self.activations_hook)
        p4 = self.pool4(x4)
        
        flat = self.flatten(p4)
        drop = self.dropout(flat)
        f1 = F.relu(self.fc1(drop))
        out = self.fc2(f1)
        return out

    def get_intermediate_features(self, x):
        x1 = F.relu(self.conv1(x))
        p1 = self.pool1(x1)
        x2 = F.relu(self.conv2(p1))
        p2 = self.pool2(x2)
        x3 = F.relu(self.conv3(p2))
        p3 = self.pool3(x3)
        x4 = F.relu(self.conv4(p3))
        return {
            'conv1': x1,
            'conv2': x2,
            'conv3': x3,
            'conv4': x4
        }


class TaskClassifier(nn.Module):
    """Modern MobileNetV2 backbone for separate task models (Fruit, Leaf, Validator)."""
    def __init__(self, num_classes: int, dropout: float = 0.3):
        super().__init__()
        base = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)
        self.features = base.features
        in_features = base.last_channel
        
        self.classifier = nn.Sequential(
            nn.Dropout(p=dropout),
            nn.Linear(in_features, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(p=dropout),
            nn.Linear(256, num_classes)
        )
        self.gradients = None
        self.activations = None

    def activations_hook(self, grad):
        self.gradients = grad

    def forward(self, x, retain_grad: bool = False):
        feat = self.features(x)
        if retain_grad:
            self.activations = feat
            feat.register_hook(self.activations_hook)
        pooled = F.adaptive_avg_pool2d(feat, (1, 1)).reshape(feat.shape[0], -1)
        out = self.classifier(pooled)
        return out


class AppleDiagnosisEngine:
    """
    Unified Multi-Model Apple Health Intelligence Engine:
    - Model A: Apple Fruit Condition Classifier (Fresh vs Rotten)
    - Model B: Apple Leaf Disease Classifier (Healthy, Scab, Black Rot, Cedar Rust)
    - Model C: Input Type Validator (apple_fruit, apple_leaf, unsupported)
    - Legacy Custom CNN & Rollback Support
    """
    def __init__(self, models_dir: str = "models", legacy_weights: str = "apple_cnn_model_v2.pth"):
        self.device = torch.device("cpu")
        self.models_dir = Path(models_dir)
        self.legacy_weights = legacy_weights

        # Preprocessing transforms
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
        ])
        
        self.norm_transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

        # Feature map extractor
        self.custom_model = AppleCustomCNN(num_classes=5).to(self.device)

        # Multi-task models
        self.fruit_model = None
        self.fruit_classes = ['Fresh', 'Rotten']

        self.leaf_model = None
        self.leaf_classes = ['Apple_Scab', 'Black_Rot', 'Cedar_Apple_Rust', 'Healthy']

        self.validator_model = None
        self.validator_classes = ['apple_fruit', 'apple_leaf', 'unsupported']

        self.legacy_transfer_model = None

        self._load_all_models()

    def _load_all_models(self):
        """Loads trained versioned checkpoints with graceful fallback and rollback options."""
        # 1. Load Fruit Condition Model
        fruit_ckpt = self.models_dir / "apple_fruit_condition_v1.pth"
        if fruit_ckpt.exists():
            try:
                ckpt = torch.load(fruit_ckpt, map_location=self.device)
                self.fruit_classes = ckpt.get("classes", ['Fresh', 'Rotten'])
                self.fruit_model = TaskClassifier(num_classes=len(self.fruit_classes)).to(self.device)
                self.fruit_model.load_state_dict(ckpt["model_state_dict"])
                self.fruit_model.eval()
                print(f"[Engine] Successfully loaded Fruit Condition Model from {fruit_ckpt}")
            except Exception as e:
                print(f"[Engine] Error loading fruit condition model: {e}")

        # 2. Load Leaf Disease Model
        leaf_ckpt = self.models_dir / "apple_leaf_disease_v1.pth"
        if leaf_ckpt.exists():
            try:
                ckpt = torch.load(leaf_ckpt, map_location=self.device)
                self.leaf_classes = ckpt.get("classes", ['Apple_Scab', 'Black_Rot', 'Cedar_Apple_Rust', 'Healthy'])
                self.leaf_model = TaskClassifier(num_classes=len(self.leaf_classes)).to(self.device)
                self.leaf_model.load_state_dict(ckpt["model_state_dict"])
                self.leaf_model.eval()
                print(f"[Engine] Successfully loaded Leaf Disease Model from {leaf_ckpt}")
            except Exception as e:
                print(f"[Engine] Error loading leaf disease model: {e}")

        # 3. Load Input Validator Model
        val_ckpt = self.models_dir / "apple_input_validator_v1.pth"
        if val_ckpt.exists():
            try:
                ckpt = torch.load(val_ckpt, map_location=self.device)
                self.validator_classes = ckpt.get("classes", ['apple_fruit', 'apple_leaf', 'unsupported'])
                self.validator_model = TaskClassifier(num_classes=len(self.validator_classes)).to(self.device)
                self.validator_model.load_state_dict(ckpt["model_state_dict"])
                self.validator_model.eval()
                print(f"[Engine] Successfully loaded Input Validator Model from {val_ckpt}")
            except Exception as e:
                print(f"[Engine] Error loading validator model: {e}")

        # 4. Load Legacy Checkpoint for Custom CNN & Rollback Support
        if os.path.exists(self.legacy_weights):
            try:
                state = torch.load(self.legacy_weights, map_location=self.device)
                if 'custom_model' in state:
                    self.custom_model.load_state_dict(state['custom_model'])
                    self.custom_model.eval()
                print(f"[Engine] Loaded legacy custom CNN from {self.legacy_weights}")
            except Exception as e:
                print(f"[Engine] Notice on legacy weights: {e}")

    def validate_input(self, pil_image: Image.Image) -> tuple[str, float, dict]:
        """
        Runs input validation to distinguish:
        - apple_fruit
        - apple_leaf
        - unsupported
        """
        if self.validator_model is None:
            # Fallback heuristic: check color variance (leaf tends to have high green index)
            arr = np.array(pil_image.resize((64, 64)), dtype=np.float32)
            g_ratio = arr[:, :, 1].mean() / (arr[:, :, 0].mean() + arr[:, :, 2].mean() + 1e-5)
            specimen = 'apple_leaf' if g_ratio > 0.65 else 'apple_fruit'
            return specimen, 75.0, {specimen: 75.0}

        self.validator_model.eval()
        t = self.norm_transform(pil_image).unsqueeze(0).to(self.device)
        with torch.no_grad():
            logits = self.validator_model(t)
            probs = F.softmax(logits, dim=1).squeeze().cpu().numpy()

        pred_idx = int(np.argmax(probs))
        specimen_type = self.validator_classes[pred_idx]
        confidence = float(probs[pred_idx] * 100.0)
        probs_dict = {self.validator_classes[i]: round(float(probs[i] * 100.0), 2) for i in range(len(self.validator_classes))}
        return specimen_type, confidence, probs_dict

    def generate_gradcam(self, model, input_tensor, target_class):
        """Generates gradient-weighted class activation map targeting the last conv features."""
        model.eval()
        input_tensor.requires_grad_(True)
        
        output = model(input_tensor, retain_grad=True)
        score = output[0, target_class]
        
        model.zero_grad()
        score.backward(retain_graph=True)
        
        gradients = model.gradients
        activations = model.activations
        
        if gradients is None or activations is None:
            return np.zeros((224, 224), dtype=np.float32)
            
        pooled_gradients = torch.mean(gradients, dim=[0, 2, 3])
        
        for i in range(activations.size(1)):
            activations[:, i, :, :] *= pooled_gradients[i]
            
        heatmap = torch.mean(activations, dim=1).squeeze()
        heatmap = F.relu(heatmap)
        heatmap = heatmap.detach().cpu().numpy()
        
        if np.max(heatmap) > 0:
            heatmap = heatmap / np.max(heatmap)
        else:
            heatmap = np.zeros_like(heatmap)
            
        return heatmap

    def overlay_heatmap_on_image(self, pil_image: Image.Image, heatmap: np.ndarray, alpha=0.55):
        orig_resized = pil_image.resize((224, 224)).convert('RGB')
        orig_arr = np.array(orig_resized, dtype=np.float32) / 255.0
        
        hm_img = Image.fromarray((heatmap * 255).astype(np.uint8)).resize((224, 224), Image.Resampling.BILINEAR)
        hm_arr = np.array(hm_img, dtype=np.float32) / 255.0
        
        # Colorize (Jet colormap)
        r = np.clip(1.5 - np.abs(4.0 * hm_arr - 3.0), 0, 1)
        g = np.clip(1.5 - np.abs(4.0 * hm_arr - 2.0), 0, 1)
        b = np.clip(1.5 - np.abs(4.0 * hm_arr - 1.0), 0, 1)
        color_hm = np.stack([r, g, b], axis=-1)
        
        blend_mask = (hm_arr[:, :, np.newaxis] > 0.08).astype(np.float32) * alpha
        blended = (1.0 - blend_mask) * orig_arr + blend_mask * color_hm
        blended = np.clip(blended * 255.0, 0, 255).astype(np.uint8)
        
        return Image.fromarray(blended)

    def extract_layer_activations(self, input_tensor):
        self.custom_model.eval()
        with torch.no_grad():
            features = self.custom_model.get_intermediate_features(input_tensor)
            
        results = {}
        for layer_name, feat in features.items():
            feat_sq = feat.squeeze(0).cpu().numpy()
            num_channels = feat_sq.shape[0]
            channel_imgs = []
            for ch in range(min(4, num_channels)):
                ch_map = feat_sq[ch]
                ch_min, ch_max = ch_map.min(), ch_map.max()
                if ch_max > ch_min:
                    norm_map = (ch_map - ch_min) / (ch_max - ch_min)
                else:
                    norm_map = np.zeros_like(ch_map)
                
                pil_feat = Image.fromarray((norm_map * 255).astype(np.uint8)).resize((80, 80), Image.Resampling.NEAREST)
                buf = io.BytesIO()
                pil_feat.save(buf, format="PNG")
                b64 = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode('utf-8')
                channel_imgs.append(b64)
                
            results[layer_name] = {
                'channels': num_channels,
                'dim': f"{feat_sq.shape[1]}x{feat_sq.shape[2]}",
                'thumbnails': channel_imgs
            }
        return results

    def predict(self, pil_image: Image.Image, model_type: str = 'transfer', specimen_override: str = None) -> dict:
        """
        Executes diagnostic prediction:
        - Validates input type (fruit vs leaf vs unsupported)
        - Routes to dedicated task model
        - Handles uncertainty rejection
        - Computes Grad-CAM & layer activation maps
        """
        # 1. Input Validation Stage
        specimen_type, val_conf, val_probs = self.validate_input(pil_image)
        if specimen_override in ['fruit', 'apple_fruit']:
            specimen_type = 'apple_fruit'
        elif specimen_override in ['leaf', 'apple_leaf']:
            specimen_type = 'apple_leaf'

        is_uncertain = False
        uncertainty_reason = None

        if specimen_type == 'unsupported' or val_conf < 40.0:
            is_uncertain = True
            uncertainty_reason = "Uploaded image does not appear to be an apple fruit or foliage specimen. Diagnostic confidence is reduced."

        # 2. Select appropriate model
        if model_type == 'custom_cnn':
            # Legacy 4-Conv Custom CNN
            active_model = self.custom_model
            class_labels = CLASS_NAMES
            norm_tensor = self.transform(pil_image).unsqueeze(0).to(self.device)
            task_type = 'legacy_custom_cnn'
        elif specimen_type == 'apple_fruit' and self.fruit_model is not None:
            # Task A: Apple Fruit Condition Classifier (Fresh vs Rotten)
            active_model = self.fruit_model
            class_labels = self.fruit_classes
            norm_tensor = self.norm_transform(pil_image).unsqueeze(0).to(self.device)
            task_type = 'fruit_condition'
        elif specimen_type == 'apple_leaf' and self.leaf_model is not None:
            # Task B: Apple Leaf Disease Classifier (Healthy, Scab, Black Rot, Rust)
            active_model = self.leaf_model
            class_labels = self.leaf_classes
            norm_tensor = self.norm_transform(pil_image).unsqueeze(0).to(self.device)
            task_type = 'leaf_disease'
        else:
            # Fallback to Fruit or Leaf Model if available
            active_model = self.fruit_model or self.leaf_model or self.custom_model
            class_labels = self.fruit_classes if self.fruit_model else CLASS_NAMES
            norm_tensor = self.norm_transform(pil_image).unsqueeze(0).to(self.device)
            task_type = 'fallback_general'

        active_model.eval()
        with torch.no_grad():
            logits = active_model(norm_tensor)
            probs = F.softmax(logits, dim=1).squeeze().cpu().numpy()

        pred_idx = int(np.argmax(probs))
        pred_class = class_labels[pred_idx]
        confidence = float(probs[pred_idx] * 100.0)

        # Confidence Safety Threshold check
        REJECTION_THRESHOLD = 60.0
        if confidence < REJECTION_THRESHOLD and not is_uncertain:
            is_uncertain = True
            uncertainty_reason = f"Prediction confidence ({confidence:.1f}%) is below the reliable safety threshold ({REJECTION_THRESHOLD:.0f}%). Please verify with a clear, direct photograph."

        # Grad-CAM heatmap
        tensor_for_grad = norm_tensor.clone().detach()
        heatmap = self.generate_gradcam(active_model, tensor_for_grad, pred_idx)
        cam_image = self.overlay_heatmap_on_image(pil_image, heatmap)

        cam_buf = io.BytesIO()
        cam_image.save(cam_buf, format="JPEG", quality=90)
        cam_b64 = "data:image/jpeg;base64," + base64.b64encode(cam_buf.getvalue()).decode('utf-8')

        prob_dict = {
            class_labels[i]: round(float(probs[i] * 100.0), 2)
            for i in range(len(class_labels))
        }

        # Intermediate feature maps
        raw_tensor = self.transform(pil_image).unsqueeze(0).to(self.device)
        activations = self.extract_layer_activations(raw_tensor)

        # Meta mapping
        meta = CLASS_DISPLAY.get(pred_class)
        if not meta:
            # Fuzzy fallback
            if 'Rot' in pred_class:
                meta = CLASS_DISPLAY.get('Rotten') or CLASS_DISPLAY.get('Black_Rot')
            elif 'Fresh' in pred_class or 'Healthy' in pred_class:
                meta = CLASS_DISPLAY.get('Fresh') or CLASS_DISPLAY.get('Healthy_Apple')
            else:
                meta = CLASS_DISPLAY.get('Apple_Scab')

        meta = meta or {}

        model_name_display = (
            f"MobileNetV2 Fine-Tuned ({task_type.replace('_', ' ').title()})"
            if model_type != 'custom_cnn'
            else "AppleCustomCNN (Paper 4-Conv Architecture)"
        )

        return {
            'predicted_class': pred_class,
            'confidence': round(confidence, 2),
            'display_name': meta.get('name', pred_class),
            'scientific_name': meta.get('latin', ''),
            'type': meta.get('type', ''),
            'severity': meta.get('severity', ''),
            'severity_color': meta.get('severity_color', '#10b981'),
            'severity_level': meta.get('severity_level', 0),
            'description': meta.get('description', ''),
            'symptoms': meta.get('symptoms', []),
            'decision_support': meta.get('decision_support', {}),
            'all_probabilities': prob_dict,
            'gradcam_image': cam_b64,
            'activations': activations,
            'model_used': model_name_display,
            'task_type': task_type,
            'specimen_type': specimen_type,
            'is_uncertain': is_uncertain,
            'uncertainty_reason': uncertainty_reason,
            'validation_scores': val_probs
        }


_engine = None

def get_engine():
    global _engine
    if _engine is None:
        _engine = AppleDiagnosisEngine()
    return _engine


if __name__ == '__main__':
    print("Testing upgraded multi-model AppleDiagnosisEngine...")
    engine = get_engine()
    samples = ['rot_apple_sample.jpg', 'normal_apple_sample.jpg', 'scab_leaf_sample.jpg', 'healthy_leaf_sample.jpg']
    for s_name in samples:
        p = os.path.join("sample_images", s_name)
        if os.path.exists(p):
            res = engine.predict(Image.open(p), 'transfer')
            print(f"{s_name:<25} -> Specimen: {res['specimen_type']:<12} | Pred: {res['predicted_class']:<15} ({res['confidence']}%) | Task: {res['task_type']}")
