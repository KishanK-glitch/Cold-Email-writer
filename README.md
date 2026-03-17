# Autonomous Cold Outreach System 🚀

A multi-agent AI system that automates lead research and hyper-personalized cold email generation. Built with **LangGraph**, **FastAPI**, and **Llama 3.3 (Groq)**.

## 🏗️ Architecture
The system utilizes a state-driven multi-agent workflow:
- **Researcher Agent:** Scrapes target URLs via Firecrawl to extract Company DNA.
- **Strategist Agent:** Analyzes pain points and maps them to service offerings.
- **Copywriter Agent:** Generates high-conversion, peer-to-peer cold emails (3-4 sentences).

## 🛠️ Tech Stack
- **Orchestration:** LangGraph
- **LLM:** Llama-3.3-70b-versatile (via Groq)
- **Scraping:** Firecrawl (Markdown optimized)
- **API:** FastAPI
- **UI:** Streamlit

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd cold-email-writer
