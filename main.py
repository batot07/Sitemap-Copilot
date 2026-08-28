from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

from app.schemas import GenerateIARequest, InformationArchitecture
from app.agent import generate_information_architecture
from app.tools import validate_information_architecture, export_markdown_spec, build_mermaid_from_nodes

app = FastAPI(
    title="AI UX Architect API",
    description="Agentic IA Synthesizer with Deterministic Validation & RAG",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

latest_ia: InformationArchitecture = None


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "UX Architect API is active and running"}


from app.schemas import InformationArchitecture
from app.tools import validate_information_architecture, export_markdown_spec, build_mermaid_from_nodes

@app.post("/generate-ia", response_model=InformationArchitecture)
def generate_ia(payload: GenerateIARequest):
    global latest_ia
    try:
        ia_draft = generate_information_architecture(
            archetype=payload.archetype,
            research_text=payload.research_text or ""
        )

        validation_report = validate_information_architecture(ia_draft)
        if not validation_report["valid"]:
            print(f"[Validation Warning] Flagged rules: {validation_report['errors']}")

        ia_result = InformationArchitecture(
            site_name=ia_draft.site_name,
            archetype=ia_draft.archetype,
            nodes=ia_draft.nodes,
            mermaid_code=build_mermaid_from_nodes(ia_draft)
        )

        latest_ia = ia_result
        return ia_result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/export-spec", response_class=PlainTextResponse)
def export_spec():
    global latest_ia
    if latest_ia is None:
        raise HTTPException(
            status_code=404,
            detail="No generated Information Architecture available."
        )
    return export_markdown_spec(latest_ia)