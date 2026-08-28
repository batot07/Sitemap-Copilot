from typing import List, Optional, Literal

from pydantic import BaseModel, Field



ArchetypeType = Literal[

    "E-Commerce",

    "B2B SaaS",

    "Mobile App",

    "Content",

    "EdTech",

    "Healthcare",

    "FinTech",

    "Developer Platform"

]



class SitemapNode(BaseModel):

    id: str = Field(..., description="Unique slug, e.g., 'home', 'checkout'")

    label: str = Field(..., description="Display title, e.g., 'Home Page'")

    parent_id: Optional[str] = Field(None, description="Parent node ID. None for root.")

    depth: int = Field(..., description="Tree level (0 for root, 1 for main nav, etc.)")

    description: str = Field(..., description="Key user tasks or purpose of the page")

    rationale: Optional[str] = Field(None, description="Research pain point justification")



class InformationArchitectureDraft(BaseModel):
    site_name: str
    archetype: ArchetypeType
    nodes: List[SitemapNode]

class InformationArchitecture(BaseModel):
    site_name: str
    archetype: ArchetypeType
    nodes: List[SitemapNode]
    mermaid_code: str = Field(..., description="Populated server-side, not by the LLM")

class GenerateIARequest(BaseModel):

    archetype: ArchetypeType

    research_text: Optional[str] = None 

