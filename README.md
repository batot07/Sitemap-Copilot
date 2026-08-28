# 🧭 Sitemap Copilot (AI UX Architect)

> **Autonomous User Research Synthesizer & Deterministic Information Architecture Engine**

Sitemap Copilot is an AI UX assistant that converts raw qualitative user studies, interview transcripts, and usability notes into structured, mathematically validated Information Architectures (IA) and interactive sitemaps.

By coupling an **Agentic Retrieval-Augmented Generation (RAG)** pipeline with **deterministic graph heuristics**, the system extracts key user journeys and enforces cognitive load principles (such as Miller's Law and archetype-specific depth caps) to ensure LLM outputs are structurally sound and developer-ready.

---

## 👥 Team: AI Geeks

* **Fatma Abdalla** – Team Leader, Idea Owner, Schemas, Presentation, UI/UX Design System & Frontend Development
* * **Mohanad** – Backend & AI RAG Pipeline
* **Omar** – Backend & Graph Validation
* **Omar** – Vector Retrieval & Architecture

---

## 🚀 Key Features

* **Semantic RAG Ingestion:** Indexes qualitative research transcripts in an in-memory FAISS vector store using local `all-MiniLM-L6-v2` embeddings to retrieve the top-3 domain pain points.
* **Agentic Reasoning Core:** Employs Groq hardware acceleration (`llama-3.3-70b-versatile` / `openai/gpt-oss-120b`) via LangChain to produce strict, structured Pydantic schemas.
* **Deterministic Graph Validation:** Pure-Python heuristics layer in `tools.py` that verifies single-root integrity, eliminates orphan nodes, prevents duplicate routes, and enforces tree depth and breadth bounds.
* **Archetype-Specific Heuristics:** Tailors structural limits dynamically across 8 digital domains (e.g., Mobile App depth $\le 2$, E-Commerce depth $\le 4$, B2B SaaS workspace isolation).
* **Visual Rendering & PRD Export:** Renders the validated hierarchy into interactive Mermaid.js flowcharts and exports complete Markdown UX specifications with one click.

---

## 🛠️ Tech Stack

| Layer | Technologies Used |
| :--- | :--- |
| **AI Core & RAG** | LangChain, Groq API, FAISS Vector Store, HuggingFace Embeddings (`all-MiniLM-L6-v2`) |
| **Backend & Validation** | FastAPI, Pydantic v2, Uvicorn, Python Graph Algorithms |
| **Frontend & UI** | Vanilla JavaScript (ES6+ fetch), HTML5, CSS3, Mermaid.js CDN |

---

## 📐 System Architecture

```text
User Archetype + Qualitative Research (.txt)
                   │
                   ▼
     [FAISS Vector Store Retrieval] ──► Extracts Top-3 Domain Pain Points
                   │
                   ▼
     [Groq LLM + Structured Output] ──► Generates Pydantic IA Blueprint
                   │
                   ▼
   [Deterministic Graph Validator]  ──► Enforces Miller's Law & Depth Caps
                   │
                   ▼
   [Interactive Mermaid Flowchart]  ──► Browser Viewport + Markdown PRD Export
```
