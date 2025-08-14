import os, json, io
import streamlit as st
from digital_skeptic.config import Config
from digital_skeptic.llm_client import LLMClient
from digital_skeptic.article_fetcher import fetch_article, read_local_file
from digital_skeptic.analysis import extract_core_claims, analyze_tone, detect_red_flags, quick_ner_entities, credibility_score
from digital_skeptic.report import build_report

st.set_page_config(page_title="Digital Skeptic", layout="wide")
st.title("🕵️ Digital Skeptic — Critical News Analyzer")

cfg = Config()
if not cfg.openai_api_key:
    st.warning("OPENAI_API_KEY not set. LLM features will use fallback.")

tab1, tab2 = st.tabs(["Analyze URL", "Analyze Pasted Text"])

with tab1:
    url = st.text_input("Article URL", placeholder="https://example.com/news/story")
    if st.button("Analyze URL") and url:
        article = fetch_article(url)
        text = article.text
        claims = extract_core_claims(text)
        tone = analyze_tone(text)
        flags = detect_red_flags(text)
        entities = quick_ner_entities(text)
        score, rationale = credibility_score(text, claims, flags)

        llm = LLMClient(cfg)
        try:
            system = open(os.path.join(os.path.dirname(__file__), "prompts", "skeptic.json"), "r", encoding="utf-8").read()
            resp = llm.complete(system, json.dumps({"ARTICLE_TITLE": article.title, "ARTICLE_TEXT": text[:cfg.max_input_chars], "OPTIONAL_URL": article.url or ""}))
            data = json.loads(resp)
            verification_questions = data.get("verification_questions", [])
            opposing_viewpoint = data.get("opposing_viewpoint", "")
        except Exception as e:
            verification_questions = [
                "Can independent outlets corroborate the key claims?",
                "Are there primary documents or datasets to verify the numbers?",
                "Do domain experts offer alternative explanations?"
            ]
            opposing_viewpoint = "An alternative view suggests the article may overemphasize risks while downplaying countervailing evidence and context."
            st.warning(f"LLM fallback due to error: {e}")

        md = build_report(article.title, article.url, claims, tone, flags, verification_questions, entities, opposing_viewpoint, score, rationale)
        st.download_button("Download Report", data=md, file_name="critical_report.md", mime="text/markdown")
        st.markdown(md)

with tab2:
    txt = st.text_area("Paste Article Text", height=300)
    title = st.text_input("Optional Title", value="Untitled")
    if st.button("Analyze Text") and txt.strip():
        claims = extract_core_claims(txt)
        tone = analyze_tone(txt)
        flags = detect_red_flags(txt)
        entities = quick_ner_entities(txt)
        score, rationale = credibility_score(txt, claims, flags)

        llm = LLMClient(cfg)
        try:
            system = open(os.path.join(os.path.dirname(__file__), "prompts", "skeptic.json"), "r", encoding="utf-8").read()
            resp = llm.complete(system, json.dumps({"ARTICLE_TITLE": title, "ARTICLE_TEXT": txt[:cfg.max_input_chars], "OPTIONAL_URL": ""}))
            data = json.loads(resp)
            verification_questions = data.get("verification_questions", [])
            opposing_viewpoint = data.get("opposing_viewpoint", "")
        except Exception as e:
            verification_questions = [
                "Can independent outlets corroborate the key claims?",
                "Are there primary documents or datasets to verify the numbers?",
                "Do domain experts offer alternative explanations?"
            ]
            opposing_viewpoint = "An alternative view suggests the article may overemphasize risks while downplaying countervailing evidence and context."
            st.warning(f"LLM fallback due to error: {e}")

        md = build_report(title, None, claims, tone, flags, verification_questions, entities, opposing_viewpoint, score, rationale)
        st.download_button("Download Report", data=md, file_name="critical_report.md", mime="text/markdown")
        st.markdown(md)
