import numpy as np

class PavementSeverityEvaluator:
    @staticmethod
    def calculate_metrics(mask: np.ndarray, mm_per_pixel: float = 0.5):
        crack_pixels = np.sum(mask > 0.5)
        total_pixels = mask.size
        density_pct = float(crack_pixels / total_pixels * 100.0)

        # Width and length estimations
        if crack_pixels == 0:
            return {
                "crack_type": "NONE",
                "severity_level": "NONE",
                "mean_width_mm": 0.0,
                "total_length_cm": 0.0,
                "density_percentage": 0.0,
                "pci_score": 100.0,
                "recommendation": "ROUTINE_MONITOR"
            }

        mean_width_mm = float(np.clip(density_pct * 0.45 * mm_per_pixel * 10.0, 0.5, 12.0))
        total_length_cm = float(np.clip(crack_pixels * 0.15, 5.0, 350.0))

        # PCI calculation (ASTM D6433 empirical approximation)
        deduct_value = min(100.0, density_pct * 3.5 + mean_width_mm * 4.0)
        pci = float(np.clip(100.0 - deduct_value, 15.0, 98.0))

        if mean_width_mm > 5.0 or pci < 45.0:
            severity = "HIGH"
            crack_type = "ALLIGATOR" if density_pct > 12.0 else "TRANSVERSE"
            rec = "MILL_AND_FILL"
        elif mean_width_mm > 2.0 or pci < 70.0:
            severity = "MEDIUM"
            crack_type = "LONGITUDINAL"
            rec = "SEALING"
        else:
            severity = "LOW"
            crack_type = "HAIRLINE"
            rec = "ROUTINE_MONITOR"

        return {
            "crack_type": crack_type,
            "severity_level": severity,
            "mean_width_mm": round(mean_width_mm, 2),
            "total_length_cm": round(total_length_cm, 1),
            "density_percentage": round(density_pct, 2),
            "pci_score": round(pci, 1),
            "recommendation": rec
        }
