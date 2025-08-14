# 🕵️‍♂️ Digital Skeptic — AI-Powered News Reality Check

> _"Don’t just read the news. Question it."_

---

## 📌 About This Project
Digital Skeptic is your **AI-powered truth buddy** — it won’t tell you what’s “true” or “false,” but it will help you **spot red flags, ask better questions, and see another side of the story**.

Built for the **Hackathon Mission 2: Digital Skeptic**, this tool blends **NLP magic + Generative AI** to transform any article into a **Critical Analysis Report**.

---

## ✨ What It Does
✅ Finds the **core factual claims**  
✅ Detects **bias, tone, and emotional language**  
✅ Spots **potential red flags** in reporting  
✅ Suggests **questions to verify** the story  
✅ Generates an **opposing viewpoint** for balance  
✅ Gives a **credibility score** (heuristic-based)  
✅ Outputs everything in **beautiful Markdown**  

---

## 📂 Project at a Glance
```
digital_skeptic/
├── main.py            # The brain – runs the whole analysis
├── article_fetcher.py # Gets and cleans article text
├── analysis.py        # Finds claims, bias, red flags
├── llm_client.py      # Talks to Gemini AI
├── report.py          # Builds the final report
├── streamlit_app.py   # Optional GUI for live demos
├── prompts/           # AI prompts live here
└── tests/sample.txt   # Example article
```

---

## ⚙️ How to Run It

### 1️⃣ Get the Code
```bash
git clone https://github.com/yourusername/digital-skeptic.git
cd digital-skeptic
```

### 2️⃣ Set Up Your Environment
```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

### 3️⃣ Add Your Gemini API Key
```bash
export GEMINI_API_KEY="your_api_key_here"  # macOS/Linux
setx GEMINI_API_KEY "your_api_key_here"    # Windows
```

---

## 🚀 Usage Examples

### Analyze an Online Article
```bash
python -m digital_skeptic.main --url "https://www.bbc.com/news/technology-68104636" -o report.md
```

### Analyze a Local File
```bash
python -m digital_skeptic.main --local-file digital_skeptic/tests/sample.txt -o report.md
```

### View the Report
```bash
cat report.md
```

---

## 🧠 How It Works
1. **Input**: URL or local text file  
2. **Heuristics**: Detects claims, tone, red flags, credibility score  
3. **Gemini AI**: Writes verification questions & opposing viewpoint  
4. **Report**: Markdown file you can read or share  

---

## 🏆 Hackathon Highlights
- **Functionality**: Handles URLs & local files, outputs structured Markdown
- **Creativity**: Opposing viewpoint simulation, entity hints, Streamlit UI
- **Engineering**: Modular, documented, easy to extend
- **Impact**: Helps fight misinformation by empowering the reader

---

## 💡 Pro Tip for Hackathon Judges
Want a quick test?  
```bash
python -m digital_skeptic.main --local-file digital_skeptic/tests/sample.txt -o quick_demo.md
cat quick_demo.md
```
In **10 seconds** you’ll see exactly what it does.

---

## 📜 License
MIT License — use it, remix it, share it.
