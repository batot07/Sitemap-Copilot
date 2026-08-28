import os
import glob
from typing import List, Optional
from dotenv import load_dotenv

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document

from app.schemas import InformationArchitecture, ArchetypeType, InformationArchitectureDraft

load_dotenv()

# Global vector store instance for caching
_VECTOR_STORE = None


def get_or_create_vector_store() -> Optional[FAISS]:
    """Indexes all .txt research documents in data/ into FAISS."""
    global _VECTOR_STORE
    if _VECTOR_STORE is not None:
        return _VECTOR_STORE

    docs = []
    # Search for all text files inside the data/ folder
    for file_path in glob.glob("data/*.txt"):
        try:
            loader = TextLoader(file_path, encoding="utf-8")
            loaded = loader.load()
            for doc in loaded:
                doc.metadata["source"] = file_path
            docs.extend(loaded)
        except Exception as e:
            print(f"[Warning] Failed to load {file_path}: {e}")

    if not docs:
        print("[Warning] No research files found in data/. Ensure mock .txt files exist.")
        return None

    # Split documents into retrievable chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=50)
    splits = text_splitter.split_documents(docs)

    # Initialize local lightweight embeddings (all-MiniLM-L6-v2)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    _VECTOR_STORE = FAISS.from_documents(splits, embeddings)
    return _VECTOR_STORE


def retrieve_research(question: str = "", archetype: str = "", k: int = 3) -> List[Document]:
    """Retrieves the raw matching document chunks from FAISS."""
    vector_store = get_or_create_vector_store()
    if not vector_store:
        return []

    search_query = f"{archetype} user interviews navigation pain points {question}".strip()
    return vector_store.similarity_search(search_query, k=k)


def _build_ia_chain(temperature: float = 0.2):
    """Builds the Groq prompt + structured LLM chain."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set in the .env file.")

    llm = ChatGroq(
        model_name="openai/gpt-oss-120b",
        temperature=temperature,
        groq_api_key=api_key
    )
    structured_llm = llm.with_structured_output(InformationArchitectureDraft)    

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", """You are an expert UX Information Architect and Product Strategist.
Your mission is to generate a comprehensive, highly logical Information Architecture (IA) and sitemap based on qualitative user research.

CRITICAL FORMATTING CONSTRAINT: Never include quotation marks of any kind (' or ") inside any text field (rationale, description, label, site_name). If you want to reference something the user said, paraphrase it in plain prose instead of quoting it directly. Do not use possessive apostrophes either (write "Mens" or "Men section" instead of "Men's"). Quotation marks or apostrophes inside field values will break the response format.

CRITICAL: Output only the JSON tool call arguments. Never include comments (no // or /* */), trailing commas, or any explanatory text inside the arguments object.

Rules:
1. Max tree depth: 3 levels (0 = Home/Root, 1 = Primary Navigation, 2 = Subsections, 3 = Detail Pages).
2. Navigation Breadth: Include 4–7 top-level navigation hubs (Miller's Law).
3. Reference real user pain points from the research in the `rationale` field, but paraphrase them fully in your own words — no quotation marks or quoted phrases from the source text.
4. Ensure `site_name` and `archetype` are populated.

Archetype-specific Guidelines:
- E-Commerce: Clear catalog hierarchy (Category -> Subcategory -> Product Detail), simplified checkout.
- B2B SaaS: Workspace separation (Projects, Tasks) from administration/settings/billing.
- Mobile App: Flat hierarchy suitable for a 3–5 bottom-navigation tab layout.
- Content: Topic clusters, searchable archives, author hubs, and newsletters.
- EdTech: Clean division between student learning dashboard, catalog discovery, and instructor management.
- Developer Platform: Clear separation between Documentation, API Reference, SDKs/Tools, Sandbox/Console, and Community Hub.
"""),
        ("human", """Generate the Information Architecture for the following product:

Archetype: {archetype}

Retrieved Research Insights:
{retrieved_data}

Custom User Input / Specific Constraints:
{custom_research}
""")
    ])

    return prompt_template | structured_llm


def generate_information_architecture(
    archetype: str,
    research_text: str = ""
) -> InformationArchitecture:
    """Synchronous pipeline entrypoint (used for CLI test scripts)."""
    docs = retrieve_research(question=research_text, archetype=archetype, k=3)
    retrieved_data = "\n\n".join([doc.page_content for doc in docs]) if docs else "No specific research indexed."

    
    last_error = None
    for attempt in range(5):
        chain = _build_ia_chain(temperature=0.2 + (attempt * 0.15))  # 0.2, 0.35, 0.5
        try:
            return chain.invoke({
                "archetype": archetype,
                "retrieved_data": retrieved_data,
                "custom_research": research_text if research_text else "None provided"
            })
        except Exception as e:
            last_error = e
            print(f"[Retry] Attempt {attempt + 1} failed: {e}")
    raise last_error


async def agenerate_information_architecture(
    archetype: str,
    research_text: str = ""
) -> InformationArchitecture:
    """Asynchronous pipeline entrypoint (used for FastAPI endpoints)."""
    docs = retrieve_research(question=research_text, archetype=archetype, k=3)
    retrieved_data = "\n\n".join([doc.page_content for doc in docs]) if docs else "No specific research indexed."

    last_error = None
    for attempt in range(5):
        chain = _build_ia_chain(temperature=0.2 + (attempt * 0.15))  # 0.2, 0.35, 0.5
        try:
            return await chain.ainvoke({...})
        except Exception as e:
            last_error = e
            print(f"[Retry] Attempt {attempt + 1} failed: {e}")
    raise last_error