from __future__ import annotations

from datetime import date
from typing import Literal
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ControlledModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=False)


class ObjectProposal(ControlledModel):
    name: str = Field(default="", max_length=240)
    description: str = Field(default="", max_length=4000)


class SourceProposal(ControlledModel):
    title: str = Field(default="", max_length=1000)
    author: str | None = Field(default=None, max_length=1000)
    source_type: Literal["unknown", "primary", "scholarly", "institutional", "other"] = "unknown"
    url: str | None = Field(default=None, max_length=2048)
    bibliographic_reference: str | None = Field(default=None, max_length=4000)
    publication: str | None = Field(default=None, max_length=1000)
    accessed_on: date | None = None
    rights: str = Field(default="unknown", max_length=300)

    @field_validator("url")
    @classmethod
    def safe_url(cls, value: str | None) -> str | None:
        if value is None or not value.strip():
            return None
        parsed = urlsplit(value)
        if (parsed.scheme not in {"http", "https"} or not parsed.hostname
                or parsed.username is not None or parsed.password is not None
                or any(ord(char) < 32 or char.isspace() for char in value)):
            raise ValueError("unsafe_source_url")
        try:
            parsed.port
        except ValueError as exc:
            raise ValueError("unsafe_source_url") from exc
        return value


class ClaimProposal(ControlledModel):
    statement: str = Field(default="", max_length=4000)
    claim_kind: Literal["factual", "observation", "inference", "interpretation", "hypothesis", "counterfactual"] = "factual"
    origin: Literal["user"] = "user"
    confidence: Literal["unknown", "low", "medium", "high"] = "unknown"
    confidence_basis: str | None = Field(default=None, max_length=4000)
    uncertainty: str = Field(default="", max_length=4000)

    @model_validator(mode="after")
    def confidence_has_basis(self):
        if self.confidence != "unknown" and not (self.confidence_basis or "").strip():
            raise ValueError("confidence_basis_required")
        return self


class EvidenceProposal(ControlledModel):
    locator: str = Field(default="", max_length=2000)
    relation_to_claim: Literal["supports", "challenges", "contextualizes"] = "contextualizes"
    evidence_strength: Literal["direct", "indirect", "background"] = "background"
    native_expression: str = Field(default="", max_length=12000)
    native_precision: Literal["unresolved"] = "unresolved"


class CandidateContent(ControlledModel):
    entity: ObjectProposal = Field(default_factory=ObjectProposal)
    source: SourceProposal = Field(default_factory=SourceProposal)
    claim: ClaimProposal = Field(default_factory=ClaimProposal)
    evidence: EvidenceProposal = Field(default_factory=EvidenceProposal)
    human_authored_attestation: bool = False

    def submission_gaps(self) -> list[str]:
        gaps = [path for path, value in [
            ("entity.name", self.entity.name), ("source.title", self.source.title),
            ("claim.statement", self.claim.statement), ("evidence.locator", self.evidence.locator),
            ("evidence.native_expression", self.evidence.native_expression),
        ] if not value.strip()]
        if not (self.source.url or (self.source.bibliographic_reference or "").strip()):
            gaps.append("source.url_or_bibliographic_reference")
        if not self.human_authored_attestation:
            gaps.append("human_authored_attestation")
        return gaps


class DraftCreate(ControlledModel):
    content: CandidateContent = Field(default_factory=CandidateContent)


class VersionRequest(ControlledModel):
    expected_version: int = Field(ge=1, strict=True)


class DraftReplace(VersionRequest):
    content: CandidateContent


class ReviewRequest(VersionRequest):
    submitted_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    expected_predecessor_revision_id: str | None = None
    decision: Literal["accept", "request_changes", "reject"]
    reason: str = Field(min_length=1, max_length=4000)

    @field_validator("reason")
    @classmethod
    def nonblank(cls, value):
        if not value.strip():
            raise ValueError("reason_required")
        return value


class PublishRequest(VersionRequest):
    accepted_revision_id: str
    accepted_revision_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    expected_object_version: int = Field(ge=1, strict=True)
    expected_publication_id: str | None = None


class CorrectionRequest(ControlledModel):
    expected_revision_id: str
    expected_object_version: int = Field(ge=1, strict=True)
    reason: str = Field(min_length=1, max_length=4000)

    @field_validator("reason")
    @classmethod
    def nonblank(cls, value):
        if not value.strip():
            raise ValueError("reason_required")
        return value
