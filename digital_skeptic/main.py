from __future__ import annotations
import json, os, sys
from typing import List
import typer
from rich import print as rprint
from rich.panel import Panel
from rich.console import Console
import re

from .config import Config
from .llm_client import LLMClient
from .article_fetcher import fetch_article, read_local_file
from .analysis import extract_core_claims, analyze_tone, detect_red_flags, quick_ner_entities, credibility_score
from .report import build_report

app = typer.Typer(add_completion=False)
console = Console()

def _read_prompt() -> str:
    here = os.path.dirname(__file__)
    return open(os.path.join(here, "prompts", "skeptic.json"), "r", encoding="utf-8").read()

@app.command()
def analyze(
    url: str = typer.Option(None, "--url", "-u", help="URL to the news article"),
    local_file: str = typer.Option(None, "--local-file", "-f", help="Path to local .txt if scraping is blocked"),
    out: str = typer.Option("critical_report.md", "--out", "-o", help="Output Markdown file"),
    max_chars: int = typer.Option(None, help="Hard cap on article text characters for LLM"),
):
    

    """Generate a Critical Analysis Report (Markdown) from a URL or local text file."""
    cfg = Config()
    if not url and not local_file:
        rprint("[red]Error:[/red] Provide a URL or --local-file")
        raise typer.Exit(code=1)

    if local_file:
        article = read_local_file(local_file)
    else:
        article = fetch_article(url)

    text = article.text
    if not text or len(text) < 200:
        rprint("[yellow]Warning:[/yellow] Extracted text seems very short; result quality may be limited.")

    limit = max_chars or cfg.max_input_chars
    text_for_llm = text[:limit]

    # Heuristic analyses
    claims = extract_core_claims(text)
    tone = analyze_tone(text)
    flags = detect_red_flags(text)
    entities = quick_ner_entities(text)
    score, rationale = credibility_score(text, claims, flags)

    # LLM Augmentation
    llm = LLMClient(cfg)
    prompt = _read_prompt()
    user = json.dumps({
        "ARTICLE_TITLE": article.title,
        "ARTICLE_TEXT": text_for_llm,
        "OPTIONAL_URL": article.url or ""
    }, ensure_ascii=False)


    system = prompt
    def extract_json(text: str) -> str:
        """Extract the first JSON object found in a string."""
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return match.group(0)
        raise ValueError("No JSON object found in text")

    try:
        resp = llm.complete(system=system, user=user)
        data = json.loads(extract_json(resp))
        verification_questions: List[str] = data.get("verification_questions", [])[:4] or [
            "Can independent outlets corroborate the key claims?",
            "Are there primary documents or datasets to verify the numbers?"
        ]
        opposing_viewpoint: str = data.get("opposing_viewpoint", "")
    except Exception as e:
        verification_questions = [
            "Can independent outlets corroborate the key claims?",
            "Are there primary documents or datasets to verify the numbers?",
            "Do domain experts offer alternative explanations?"
        ]
        opposing_viewpoint = "An alternative view suggests the article may overemphasize risks while downplaying countervailing evidence and context. Independent datasets and broader expert opinions may present a more nuanced picture."
        rprint(f"[yellow]LLM fallback due to error:[/yellow] {e}")

    md = build_report(
        article_title=article.title or "Untitled",
        article_url=article.url,
        core_claims=claims,
        tone=tone,
        red_flags=flags,
        verification_questions=verification_questions,
        entities_to_investigate=entities,
        opposing_viewpoint=opposing_viewpoint,
        credibility_score=score,
        credibility_rationale=rationale,
    )

    with open(out, "w", encoding="utf-8") as f:
        f.write(md)

    rprint(Panel.fit(f"[green]Report written to[/green] [bold]{out}[/bold]"))
    console.print(md[:1200] + ("\n...\n" if len(md) > 1200 else ""))

if __name__ == "__main__":
    app()
