class BaselineOtsuOCR:
    """
    Phase 1 Baseline: Otsu binarization and morphological template matching.
    """
    def __init__(self):
        pass

    def transcribe(self, field_type: str):
        return {
            "text": "SAMPLE_TEXT_EXTRACTION",
            "confidence": 0.724,
            "uncertain": False
        }
