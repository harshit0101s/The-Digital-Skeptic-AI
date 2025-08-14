from __future__ import annotations
from typing import List
from dataclasses import dataclass
from .analysis import CoreClaim, RedFlag

def build_report(
    article_title: str,
    article_url: str | None,
    core_claims: List[CoreClaim],
    tone: str,
    red_flags: List[RedFlag],
    verification_questions: List[str],
    entities_to_investigate: List[str],
    opposing_viewpoint: str,
    credibility_score: int,
    credibility_rationale: str,
) -> str:
    url_line = f" for: [{article_title}]({article_url})" if article_url else f" for: {article_title}"
    lines: List[str] = []
    lines.append(f"# Critical Analysis Report{url_line}\n")
    lines.append("## Summary")
    lines.append(f"- **Credibility (heuristic):** {credibility_score}/10")
    lines.append(f"- **Rationale:** {credibility_rationale}\n")
    lines.append("## Core Claims")
    if core_claims:
        for c in core_claims:
            lines.append(f"- {c.sentence}")
    else:
        lines.append("- No clear factual core claims detected; the article may be highly opinionated or anecdotal.")
    lines.append("\n## Language & Tone Analysis")
    lines.append(tone + "\n")
    lines.append("## Potential Red Flags")
    if red_flags:
        for f in red_flags:
            lines.append(f"- {f.description}")
    else:
        lines.append("- No obvious red flags detected by heuristics; a deeper read is still recommended.")
    lines.append("\n## Verification Questions")
    for q in verification_questions:
        lines.append(f"1. {q}")
    lines.append("\n## Entities to Investigate")
    if entities_to_investigate:
        for e in entities_to_investigate:
            lines.append(f"- {e}")
    else:
        lines.append("- (None detected)")
    lines.append("\n## Opposing Viewpoint (Simulated)")
    lines.append(opposing_viewpoint or "_Not available._")
    lines.append("\n---\n_This report is an assistive analysis and not a truth verdict. Cross-check with reputable sources._\n")
    return "\n".join(lines)
