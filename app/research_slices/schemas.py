from __future__ import annotations

from datetime import datetime
from math import isfinite
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

RESEARCH_SLICE_SCHEMA_VERSION = "2.0"
EpistemicType = Literal["fact", "interpretation", "hypothesis"]
EvidenceState = Literal["supported", "missing"]
ConclusionStatus = Literal["concluded", "unresolved"]


class FeatureRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    feature_id: str = Field(min_length=1, max_length=255)

    @field_validator("feature_id")
    @classmethod
    def validate_feature_id(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("feature_id must not be empty")
        return normalized


class EvidenceRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: Literal["source", "relation"]
    ref_id: str = Field(min_length=1, max_length=255)
    supports_finding_ids: list[str] = Field(default_factory=list, max_length=100)

    @field_validator("ref_id")
    @classmethod
    def validate_ref_id(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("evidence ref_id must not be empty")
        return normalized

    @field_validator("supports_finding_ids")
    @classmethod
    def normalize_supports_finding_ids(cls, value: list[str]) -> list[str]:
        normalized = [str(item).strip() for item in value]
        if any(not item for item in normalized):
            raise ValueError("supports_finding_ids must not contain empty ids")
        if len(normalized) != len(set(normalized)):
            raise ValueError("supports_finding_ids must be unique")
        return normalized


class TimeRange(BaseModel):
    model_config = ConfigDict(extra="forbid")

    start: int
    end: int
    mode: Literal["point", "range"] = "range"

    @model_validator(mode="after")
    def validate_order(self) -> "TimeRange":
        if self.start > self.end:
            raise ValueError("time_range.start must be <= time_range.end")
        return self


class ViewState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    center: list[float]
    zoom: float
    enabled_layer_ids: list[str] = Field(default_factory=list)
    active_quick_layer_ids: list[str] = Field(default_factory=list)
    selected_feature_id: str | None = None

    @field_validator("center")
    @classmethod
    def validate_center(cls, value: list[float]) -> list[float]:
        if len(value) != 2:
            raise ValueError("view_state.center must contain exactly 2 numbers")
        lon = float(value[0])
        lat = float(value[1])
        if not (isfinite(lon) and isfinite(lat)):
            raise ValueError("view_state.center must contain finite numbers")
        return [lon, lat]

    @field_validator("zoom")
    @classmethod
    def validate_zoom(cls, value: float) -> float:
        zoom = float(value)
        if not isfinite(zoom):
            raise ValueError("view_state.zoom must be a finite number")
        return zoom

    @field_validator("selected_feature_id")
    @classmethod
    def normalize_selected_feature_id(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class SavedView(BaseModel):
    model_config = ConfigDict(extra="forbid")

    time_range: TimeRange
    view_state: ViewState
    filter_state: dict[str, str | int | float | bool | list[str] | None] = Field(default_factory=dict)
    comparison_feature_ids: list[str] = Field(default_factory=list, max_length=20)

    @field_validator("comparison_feature_ids")
    @classmethod
    def normalize_comparison_feature_ids(cls, value: list[str]) -> list[str]:
        normalized = [str(item).strip() for item in value]
        if any(not item for item in normalized):
            raise ValueError("comparison_feature_ids must not contain empty ids")
        if len(normalized) != len(set(normalized)):
            raise ValueError("comparison_feature_ids must be unique")
        return normalized


class SliceFinding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1, max_length=255)
    type: EpistemicType
    text: str = Field(min_length=1, max_length=4000)
    feature_id: str | None = None

    @field_validator("id", "text")
    @classmethod
    def validate_required_trimmed(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("finding fields must not be empty")
        return normalized

    @field_validator("feature_id")
    @classmethod
    def normalize_feature_id(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


# Compatibility name retained for code and clients that still say "annotation".
SliceAnnotation = SliceFinding


class ResearchSliceBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=180)
    description: str = Field(default="", max_length=4000)
    research_question: str | None = Field(default=None, max_length=1000)
    selection_rationale: str | None = Field(default=None, max_length=4000)
    feature_refs: list[FeatureRef]
    evidence_state: EvidenceState | None = None
    evidence_refs: list[EvidenceRef] = Field(default_factory=list, max_length=200)
    findings: list[SliceFinding] | None = None
    conclusion_status: ConclusionStatus = "unresolved"
    conclusion: str = Field(default="", max_length=4000)
    uncertainty_notes: str = Field(default="", max_length=4000)
    saved_view: SavedView | None = None
    schema_version: Literal["2.0"] = RESEARCH_SLICE_SCHEMA_VERSION
    content_version: int = Field(default=1, ge=1)

    # Legacy compatibility fields. They mirror saved_view/findings in every response.
    time_range: TimeRange | None = None
    view_state: ViewState | None = None
    annotations: list[SliceFinding] | None = None
    visibility: Literal["private"] = "private"

    @model_validator(mode="before")
    @classmethod
    def hydrate_v2_from_legacy_shape(cls, value):
        if not isinstance(value, dict):
            return value
        data = dict(value)

        saved_view = data.get("saved_view")
        if isinstance(saved_view, dict):
            data.setdefault("time_range", saved_view.get("time_range"))
            data.setdefault("view_state", saved_view.get("view_state"))
        elif data.get("time_range") is not None and data.get("view_state") is not None:
            data["saved_view"] = {
                "time_range": data["time_range"],
                "view_state": data["view_state"],
                "filter_state": {},
                "comparison_feature_ids": [
                    str(entry.get("feature_id", "")).strip()
                    for entry in data.get("feature_refs", [])
                    if isinstance(entry, dict) and str(entry.get("feature_id", "")).strip()
                ],
            }

        if data.get("findings") is None:
            data["findings"] = list(data.get("annotations") or [])
        if data.get("annotations") is None:
            data["annotations"] = list(data.get("findings") or [])

        title = str(data.get("title") or "").strip()
        description = str(data.get("description") or "").strip()
        if not str(data.get("research_question") or "").strip():
            data["research_question"] = title
        if not str(data.get("selection_rationale") or "").strip():
            data["selection_rationale"] = description or "Selection rationale was not captured in the legacy slice."
        if data.get("evidence_state") is None:
            data["evidence_state"] = "supported" if data.get("evidence_refs") else "missing"
        return data

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("title must not be empty")
        return normalized

    @field_validator(
        "description",
        "research_question",
        "selection_rationale",
        "conclusion",
        "uncertainty_notes",
    )
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip()

    @field_validator("feature_refs")
    @classmethod
    def validate_feature_refs_non_empty(cls, value: list[FeatureRef]) -> list[FeatureRef]:
        if not value:
            raise ValueError("feature_refs must not be empty")
        ids = [entry.feature_id for entry in value]
        if len(ids) != len(set(ids)):
            raise ValueError("feature_refs must be unique")
        return value

    @model_validator(mode="after")
    def validate_v2_semantics(self) -> "ResearchSliceBase":
        if not self.research_question:
            raise ValueError("research_question must not be empty")
        if not self.selection_rationale:
            raise ValueError("selection_rationale must not be empty")
        if self.saved_view is None or self.time_range is None or self.view_state is None:
            raise ValueError("saved_view or legacy time_range/view_state is required")

        if self.saved_view.time_range != self.time_range or self.saved_view.view_state != self.view_state:
            raise ValueError("saved_view must match legacy time_range/view_state compatibility fields")

        feature_ids = {entry.feature_id for entry in self.feature_refs}
        selected = self.saved_view.view_state.selected_feature_id
        if selected is not None and selected not in feature_ids:
            raise ValueError("view_state.selected_feature_id must reference feature_refs")
        if any(item not in feature_ids for item in self.saved_view.comparison_feature_ids):
            raise ValueError("saved_view.comparison_feature_ids must reference feature_refs")

        findings = self.findings or []
        annotations = self.annotations or []
        if findings != annotations:
            raise ValueError("findings must match legacy annotations compatibility field")
        finding_ids = [entry.id for entry in findings]
        if len(finding_ids) != len(set(finding_ids)):
            raise ValueError("finding ids must be unique")
        if any(entry.feature_id and entry.feature_id not in feature_ids for entry in findings):
            raise ValueError("finding.feature_id must reference feature_refs")

        if self.evidence_state == "supported" and not self.evidence_refs:
            raise ValueError("supported evidence_state requires evidence_refs")
        if self.evidence_state == "missing" and self.evidence_refs:
            raise ValueError("missing evidence_state must not include evidence_refs")
        finding_id_set = set(finding_ids)
        if any(
            finding_id not in finding_id_set
            for evidence in self.evidence_refs
            for finding_id in evidence.supports_finding_ids
        ):
            raise ValueError("evidence supports_finding_ids must reference findings")

        if self.conclusion_status == "concluded" and not self.conclusion:
            raise ValueError("concluded status requires conclusion")
        return self


class ResearchSliceCreate(ResearchSliceBase):
    pass


class ResearchSliceUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=180)
    description: str | None = Field(default=None, max_length=4000)
    research_question: str | None = Field(default=None, min_length=1, max_length=1000)
    selection_rationale: str | None = Field(default=None, min_length=1, max_length=4000)
    feature_refs: list[FeatureRef] | None = None
    evidence_state: EvidenceState | None = None
    evidence_refs: list[EvidenceRef] | None = None
    findings: list[SliceFinding] | None = None
    conclusion_status: ConclusionStatus | None = None
    conclusion: str | None = Field(default=None, max_length=4000)
    uncertainty_notes: str | None = Field(default=None, max_length=4000)
    saved_view: SavedView | None = None
    schema_version: Literal["2.0"] | None = None
    content_version: int | None = Field(default=None, ge=1)
    time_range: TimeRange | None = None
    view_state: ViewState | None = None
    annotations: list[SliceFinding] | None = None
    visibility: Literal["private"] | None = None

    @model_validator(mode="before")
    @classmethod
    def normalize_compatibility_fields(cls, value):
        if not isinstance(value, dict):
            return value
        data = dict(value)
        saved_view = data.get("saved_view")
        if isinstance(saved_view, dict):
            data.setdefault("time_range", saved_view.get("time_range"))
            data.setdefault("view_state", saved_view.get("view_state"))
        if data.get("findings") is not None and data.get("annotations") is None:
            data["annotations"] = list(data["findings"])
        if data.get("annotations") is not None and data.get("findings") is None:
            data["findings"] = list(data["annotations"])
        return data

    @field_validator(
        "title",
        "description",
        "research_question",
        "selection_rationale",
        "conclusion",
        "uncertainty_notes",
    )
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized

    @field_validator("feature_refs")
    @classmethod
    def validate_feature_refs(cls, value: list[FeatureRef] | None) -> list[FeatureRef] | None:
        if value is None:
            return None
        if not value:
            raise ValueError("feature_refs must not be empty")
        ids = [entry.feature_id for entry in value]
        if len(ids) != len(set(ids)):
            raise ValueError("feature_refs must be unique")
        return value

    @model_validator(mode="after")
    def validate_supplied_pairs(self) -> "ResearchSliceUpdate":
        if self.saved_view is not None:
            if self.time_range is not None and self.saved_view.time_range != self.time_range:
                raise ValueError("saved_view must match time_range")
            if self.view_state is not None and self.saved_view.view_state != self.view_state:
                raise ValueError("saved_view must match view_state")
        if self.findings is not None and self.annotations is not None and self.findings != self.annotations:
            raise ValueError("findings must match annotations")
        if self.evidence_state == "supported" and self.evidence_refs == []:
            raise ValueError("supported evidence_state requires evidence_refs")
        if self.evidence_state == "missing" and self.evidence_refs:
            raise ValueError("missing evidence_state must not include evidence_refs")
        if self.conclusion_status == "concluded" and self.conclusion is not None and not self.conclusion:
            raise ValueError("concluded status requires conclusion")
        return self


class ResearchSliceResponse(ResearchSliceBase):
    id: str
    owner_id: str
    content_status: Literal["complete", "incomplete"]
    created_at: datetime
    updated_at: datetime


class ResearchSliceListItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    visibility: Literal["private"]
    is_shared: bool = False
    feature_count: int
    finding_count: int
    annotation_count: int
    evidence_state: EvidenceState
    conclusion_status: ConclusionStatus
    content_status: Literal["complete", "incomplete"]
    content_version: int
    created_at: datetime
    updated_at: datetime


class ResearchSliceShareResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    share_token: str
    share_fragment: str
    shared_at: datetime


class PublicResearchSliceResponse(ResearchSliceBase):
    id: str
    content_status: Literal["complete", "incomplete"]
    visibility: Literal["shared_read_only"] = "shared_read_only"
    shared_at: datetime
    updated_at: datetime
