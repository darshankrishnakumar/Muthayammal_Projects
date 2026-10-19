# Dataset Corpus & Model Specifications

## 1. Dataset Description

The calibration and benchmark corpus comprises high-contrast digital side-profile egg images:

| Specimen ID | Conformation Profile | Biological Ground Truth | Shape Index (SI) | Typical Breeding Line |
|---|---|---|---|---|
| `F01_standard_female.png` | Standard Oval Hen Egg | Female (Hen) | 80.44% | White Leghorn Layer |
| `F02_spherical_hen_egg.png` | Spherical Round Egg | Female (Hen) | 82.50% | Rhode Island Red |
| `F03_symmetrical_round_egg.png` | Symmetrical Spheroid | Female (Hen) | 84.10% | Australorp Pullet |
| `F04_broad_female_egg.png` | Broad Base Oval | Female (Hen) | 78.40% | Orpington Layer |
| `F05_oval_pullet_egg.png` | Compact Oval Pullet | Female (Hen) | 77.90% | Bovans Brown Pullet |
| `M01_pointed_apex_male.png` | Pointed Acute Apex | Male (Rooster) | 68.50% | Plymouth Rock Male |
| `M02_conical_rooster_egg.png` | Conical Polar Taper | Male (Rooster) | 69.80% | Sussex Cockerel |
| `M03_elongated_male_egg.png` | Elongated Ellipsoid | Male (Rooster) | 66.40% | Brahma Meat Line |
| `M04_asymmetric_tapered_egg.png` | Asymmetric Tapered | Male (Rooster) | 70.10% | Wyandotte Male |
| `M05_sharp_pole_male.png` | Sharp Polar Extrusion | Male (Rooster) | 67.20% | Cornish Cockerel |

## 2. Neural Model Topology

- **Architecture**: Multi-Layer Perceptron (MLP)
- **Input Dimension**: $64 \times 64 = 4,096$ flattened normalized grayscale pixels.
- **Hidden Layer**: 30 neurons with Logistic Sigmoid activation.
- **Output Layer**: 1 neuron with Sigmoid activation ($h_\theta(x) = P(\text{Female})$).
- **Parameters**:
  - $\Theta_1 \in \mathbb{R}^{30 \times 4097}$ (122,910 weights)
  - $\Theta_2 \in \mathbb{R}^{1 \times 31}$ (31 weights)
- **Serialization Format**: `source_code/model_weights.npz` (Compressed NumPy binary).
