# modules/engineering_intelligence.py
import re
from typing import Dict, List, Any

class EngineeringIntelligence:
    def __init__(self, blackboard: Any):
        self.blackboard = blackboard
        self.priorities_cache: List[Dict[str, Any]] = []

    def compile_insights(self) -> Dict[str, Any]:
        """Consumes raw reports from the blackboard and synthesizes metrics."""
        # Fallback to defaults if components haven't run yet in this session
        review_report = getattr(self.blackboard, "last_review_report", {})
        dep_graph = getattr(self.blackboard, "last_dependency_graph", {})
        workspace = getattr(self.blackboard, "last_workspace_report", {})

        # 1. Harvest active, non-suppressed violations from code review
        violations = []
        if isinstance(review_report, dict):
            for key in ["violations", "active_violations", "report", "flags"]:
                if key in review_report and isinstance(review_report[key], list):
                    violations = review_report[key]
                    break
            if not violations and "meta" in review_report:
                # Fallback check if it's nested or stored as a flat list elsewhere
                for val in review_report.values():
                    if isinstance(val, list):
                        violations = val
                        break
        elif isinstance(review_report, list):
            violations = review_report
        
        crit_count = sum(1 for v in violations if v.get("category") .upper().strip() in ["CRIT", "CRITICAL"])
        sec_count = sum(1 for v in violations if v.get("category") .upper().strip() in ["SEC", "SECURITY"])
        opt_count = sum(1 for v in violations if v.get("category") .upper().strip() in ["OPT", "OPTIMIZATION"])
        style_count = sum(1 for v in violations if v.get("category") .upper().strip() in ["STYL", "STYLE"])

        # 2. Compute Health Scores (0 to 10 Scales)
        security_score = max(0, 10 - (crit_count * 3 + sec_count * 2))
        maintainability_score = max(0, 10 - (opt_count * 0.5 + min(5, style_count * 0.1)))
        
        # Architecture score factors in coupling from the dependency graph if available
        circular_deps = dep_graph.get("circular_dependencies", 0)
        architecture_score = max(0, 10 - (circular_deps * 2))
        
        performance_score = 9.0  # Derived from structural performance profiling in future scopes

        # Calculate weighted overall score (out of 100)
        overall = int(((security_score * 0.4) + (architecture_score * 0.3) + 
                       (maintainability_score * 0.2) + (performance_score * 0.1)) * 10)

        return {
            "metrics": {
                "Security": f"{security_score:.1f}/10",
                "Architecture": f"{architecture_score:.1f}/10",
                "Maintainability": f"{maintainability_score:.1f}/10",
                "Performance": f"{performance_score:.1f}/10",
                "Overall": f"{overall}/100"
            },
            "raw_counts": {"crit": crit_count, "sec": sec_count, "opt": opt_count, "style": style_count}
        }

    def generate_priorities(self) -> List[Dict[str, Any]]:
        """Synthesizes granular violations into deduplicated strategic tasks."""
        review_report = getattr(self.blackboard, "last_review_report", {})
        violations = []
        if isinstance(review_report, dict):
            for key in ["violations", "active_violations", "report", "flags"]:
                if key in review_report and isinstance(review_report[key], list):
                    violations = review_report[key]
                    break
            if not violations:
                for val in review_report.values():
                    if isinstance(val, list):
                        violations = val
                        break
        elif isinstance(review_report, list):
            violations = review_report
        
        priorities = []
        
        # Track grouped items to avoid duplicates
        bare_except_files = []
        style_violation_counts = {}

        for v in violations:
            desc = str(v.get("detail", "")).lower()
            file = v.get("file", "unknown_file")
            cat = str(v.get("category", "")).upper().strip()
            
            # Grouping Logic 1: Bare except clauses
            if "except:" in desc or "catch-all" in desc or "bare" in desc or cat in ["OPT", "OPTIMIZATION"]:
                if file not in bare_except_files:
                    bare_except_files.append(file)
                continue
                
            # Grouping Logic 2: Mass PEP8 style issues
            if "pep 8" in desc or "width" in desc or "limit" in desc or "exceeds" in desc or cat in ["STYL", "STYLE"]:
                style_violation_counts[file] = style_violation_counts.get(file, 0) + 1
                continue

            # Critical/Security unique issues handle instantly as standalone items
            if cat in ["CRIT", "CRITICAL", "SEC", "SECURITY"]:
                priorities.append({
                    "title": v.get("detail", "Critical System Correction Required"),
                    "impact": "★★★★★",
                    "reason": f"High-risk {v.get('category')} flaw exposed in operational sub-module.",
                    "effort": "10 minutes",
                    "files": [file],
                    "benefit": "Eliminates potential runtime exploitation vectors or critical crashes.",
                    "complexity": "Low (Requires local replacement with safe alternate routines)"
                })

        # Inject consolidated Bare Except Tasks if found
        if bare_except_files:
            priorities.append({
                "title": "Replace bare except statements with specific exception handlers",
                "impact": "★★★★☆",
                "reason": "Prevents silent failures and allows precise stack handling during unexpected system errors.",
                "effort": f"{len(bare_except_files) * 5} minutes",
                "files": bare_except_files,
                "benefit": "Stabilizes app runtime debugging state and stops catch-all swallows.",
                "complexity": "Medium (Requires reviewing method boundaries to identify predictable exceptions)"
            })

        # Inject consolidated Style Cleanup Tasks if found
        if style_violation_counts:
            most_debt_file = max(style_violation_counts, key=style_violation_counts.get)
            priorities.append({
                "title": f"Refactor line-width formatting constraints inside {most_debt_file}",
                "impact": "★★★☆☆",
                "reason": f"High accumulation of stylistic formatting debt ({style_violation_counts[most_debt_file]} violations).",
                "effort": "30 minutes",
                "files": [most_debt_file],
                "benefit": "Improves code readability and alignment with standard clean-code specs.",
                "complexity": "Low (Purely typographical breaks or minor block extractions)"
            })

        self.priorities_cache = priorities
        return priorities