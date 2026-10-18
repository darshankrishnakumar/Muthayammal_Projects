class BaselineSkillOverlapMatcher:
    """
    Phase 1 Baseline: Simple set difference skill-gap counter.
    """
    def __init__(self):
        pass

    def evaluate(self, current_skills: list, target_skills: list):
        c_set = set([s.strip().lower() for s in current_skills])
        t_set = set([s.strip().lower() for s in target_skills])
        overlap = c_set.intersection(t_set)
        gap = t_set - c_set
        match_pct = (len(overlap) / max(1, len(t_set))) * 100.0
        return {
            "readiness_pct": round(match_pct, 1),
            "missing_skills_count": len(gap)
        }
