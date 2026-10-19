import os
import json
import torch
import torch.nn as nn
import numpy as np

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))

class NIDSAutoencoder(nn.Module):
    def __init__(self, input_dim=12, latent_dim=4):
        super(NIDSAutoencoder, self).__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 24),
            nn.BatchNorm1d(24),
            nn.LeakyReLU(0.2),
            nn.Linear(24, 12),
            nn.BatchNorm1d(12),
            nn.LeakyReLU(0.2),
            nn.Linear(12, latent_dim)
        )
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 12),
            nn.BatchNorm1d(12),
            nn.LeakyReLU(0.2),
            nn.Linear(12, 24),
            nn.BatchNorm1d(24),
            nn.LeakyReLU(0.2),
            nn.Linear(24, input_dim)
        )

    def forward(self, x):
        latent = self.encoder(x)
        reconstruction = self.decoder(latent)
        return latent, reconstruction

class NIDSEnsembleClassifier(nn.Module):
    def __init__(self, input_dim=17, num_classes=7):
        super(NIDSEnsembleClassifier, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(32, num_classes)
        )

    def forward(self, x):
        return self.net(x)

class NIDSInferenceEngine:
    def __init__(self):
        meta_path = os.path.join(BACKEND_DIR, "nids_model_metadata.json")
        ae_weights_path = os.path.join(BACKEND_DIR, "nids_autoencoder_weights.pt")
        clf_weights_path = os.path.join(BACKEND_DIR, "nids_classifier_weights.pt")

        if not os.path.exists(meta_path):
            raise FileNotFoundError(f"Metadata not found at {meta_path}")

        with open(meta_path, "r") as f:
            self.metadata = json.load(f)

        self.features = self.metadata["features"]
        self.classes = self.metadata["classes"]
        self.taxonomy = self.metadata["taxonomy"]
        self.mean = np.array(self.metadata["feature_mean"], dtype=np.float32)
        self.std = np.array(self.metadata["feature_std"], dtype=np.float32)
        self.threshold = float(self.metadata["anomaly_reconstruction_threshold"])

        # Initialize and load Autoencoder
        self.autoencoder = NIDSAutoencoder(input_dim=12, latent_dim=4)
        if os.path.exists(ae_weights_path):
            self.autoencoder.load_state_dict(torch.load(ae_weights_path, map_location="cpu"))
        self.autoencoder.eval()

        # Initialize and load Classifier
        self.classifier = NIDSEnsembleClassifier(input_dim=17, num_classes=len(self.classes))
        if os.path.exists(clf_weights_path):
            self.classifier.load_state_dict(torch.load(clf_weights_path, map_location="cpu"))
        self.classifier.eval()

    def extract_vector(self, flow):
        vec = []
        for feat in self.features:
            val = flow.get(feat, 0.0)
            try:
                vec.append(float(val))
            except (ValueError, TypeError):
                vec.append(0.0)
        return np.array(vec, dtype=np.float32)

    def evaluate(self, flow):
        raw_vec = self.extract_vector(flow)
        norm_vec = (raw_vec - self.mean) / self.std
        tensor_x = torch.tensor(norm_vec).unsqueeze(0) # [1, 12]

        with torch.no_grad():
            latent, recon = self.autoencoder(tensor_x)
            recon_error = torch.mean((tensor_x - recon) ** 2, dim=1, keepdim=True)
            recon_val = float(recon_error.item())

            enriched = torch.cat([tensor_x, latent, recon_error], dim=1) # [1, 17]
            logits = self.classifier(enriched)
            probs = torch.softmax(logits, dim=1).numpy()[0]

        pred_idx = int(np.argmax(probs))
        pred_class = self.classes[pred_idx]
        confidence = round(float(probs[pred_idx]) * 100, 1)

        # Unsupervised Zero-Day Anomaly Detection
        # If autoencoder reconstruction error is abnormally high but classifier called it Normal, trigger ZeroDay
        threshold_exceeded = recon_val > self.threshold
        if threshold_exceeded and pred_class == "Normal":
            pred_class = "ZeroDay_Anomaly"
            confidence = round(min(99.4, 75.0 + (recon_val / self.threshold) * 8.0), 1)

        meta = self.taxonomy.get(pred_class, {
            "category": "Unknown Anomaly",
            "severity": "HIGH",
            "action": "SANDBOX_ISOLATE"
        })

        is_attack = (pred_class != "Normal")
        firewall_action = "BLOCK / DROP" if is_attack else "ACCEPT / ROUTE"

        proto = flow.get("protocol", "TCP")
        srv = flow.get("service", "HTTP")
        flag = flow.get("flag", "SF")
        s_bytes = float(flow.get("src_bytes", 0))
        d_bytes = float(flow.get("dst_bytes", 0))

        # Class probabilities map
        prob_distribution = {
            cls_name: round(float(probs[idx]) * 100, 2)
            for idx, cls_name in enumerate(self.classes)
        }

        return {
            "attack_name": pred_class.replace("_", " "),
            "attack_type": pred_class,
            "category": meta["category"],
            "severity": meta["severity"],
            "confidence": confidence,
            "is_attack": is_attack,
            "reconstruction_error": round(recon_val, 5),
            "threshold": round(self.threshold, 5),
            "threshold_exceeded": threshold_exceeded,
            "firewall_action": firewall_action,
            "flow_summary": f"{proto} {srv} [{flag}] • {s_bytes:.0f}b in / {d_bytes:.0f}b out",
            "class_probabilities": prob_distribution,
            "latent_representation": [round(float(x), 4) for x in latent.squeeze(0).numpy()]
        }

# Global singleton
_engine_instance = None
def get_nids_engine():
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = NIDSInferenceEngine()
    return _engine_instance
