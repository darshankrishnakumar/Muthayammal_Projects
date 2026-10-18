class BaselineTFIDFMatcher:
    """
    Phase 1 Baseline: TF-IDF Bag of Words & Jaccard skill keyword overlap.
    """
    def __init__(self):
        pass

    def match(self, resume_skills: list, job_skills: list):
        r_set = set([s.strip().lower() for s in resume_skills])
        j_set = set([s.strip().lower() for s in job_skills])
        overlap = r_set.intersection(j_set)
        jaccard = len(overlap) / max(1, len(j_set))
        return {
            "keyword_overlap_score": round(jaccard * 100.0, 1),
            "matched_count": len(overlap),
            "missing_count": len(j_set - r_set)
        }
