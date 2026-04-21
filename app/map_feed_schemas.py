from pydantic import BaseModel, ConfigDict, StrictInt


class MapFeedItem(BaseModel):
    """
    Internal runtime feed item (non-canonical adapter model).

    This schema is intentionally separate from the canonical public GeoJSON contract
    and must not be treated as a public map-source schema.
    """

    model_config = ConfigDict(extra="forbid")

    id: str
    entity_type: str
    name: str | None = None
    layer_id: str | None = None
    geometry_type: str | None = None
    longitude: float | None = None
    latitude: float | None = None
    date_start: str | None = None
    date_end: str | None = None


class MapFeedResponse(BaseModel):
    """
    Internal runtime feed response envelope.

    Boundary: this response model is for `/api/map/feed` runtime support only
    and is not a public replacement for `/data/features.geojson`.
    """

    model_config = ConfigDict(extra="forbid")

    items: list[MapFeedItem]
    total: StrictInt
    bbox_applied: bool
