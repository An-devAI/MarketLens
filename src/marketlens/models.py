from typing import Literal
from urllib.parse import urlsplit

from pydantic import BaseModel, Field, field_validator, model_validator

AXES = ["product", "pricing", "customers", "integrations", "positioning"]


class Company(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    website: str

    @field_validator("website")
    @classmethod
    def website_valid(cls, value):
        parsed = urlsplit(value)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username:
            raise ValueError("Provide a public HTTPS company website")
        return value


class ResearchRequest(BaseModel):
    companies: list[Company] = Field(min_length=2, max_length=3)
    brief: str = Field(default="Compare these companies using public evidence", max_length=2000)

    @model_validator(mode="after")
    def unique_names(self):
        if len({c.name.casefold() for c in self.companies}) != len(self.companies):
            raise ValueError("Company names must be unique")
        return self


class Evidence(BaseModel):
    id: str
    company: str
    url: str
    title: str
    text: str
    fetched_at: str
    content_hash: str
    published_at: str | None = None


class Claim(BaseModel):
    company: str
    criterion: Literal["product", "pricing", "customers", "integrations", "positioning"]
    text: str = Field(min_length=1)
    evidence_ids: list[str] = Field(default_factory=list)
    quote: str = ""
    kind: Literal["fact", "inference", "unknown"] = "fact"


class ClaimBatch(BaseModel):
    claims: list[Claim]


class ResearchPlan(BaseModel):
    queries: list[str] = Field(min_length=1, max_length=3)


class Settings(BaseModel):
    max_searches: int = Field(default=30, ge=1, le=30)
    max_documents: int = Field(default=30, ge=1, le=30)
    rounds: int = Field(default=2, ge=0, le=2)
    retrieval: Literal["bm25", "dense", "hybrid"] = "hybrid"
    model: str = "Qwen/Qwen3-4B-Instruct-2507"
    embedding: str = "intfloat/multilingual-e5-small"


class ReportBundle(BaseModel):
    schema_version: int = 1
    request: ResearchRequest
    claims: list[Claim]
    evidence: list[Evidence]
    warnings: list[str]
    manifest: dict
    status: Literal["complete", "partial"]
