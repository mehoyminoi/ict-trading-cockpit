"""Source claims are separate from a run's requested query window."""
from dataclasses import dataclass
from datetime import datetime


def _parse_coverage_datetime(value: str) -> datetime:
    # Python 3.10 requires an explicit UTC offset instead of the ISO 'Z' suffix.
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


@dataclass(frozen=True)
class ContextCoverage:
    start: str = ""
    end: str = ""
    complete: bool = False
    categories: tuple[str, ...] = ()
    event_types: tuple[str, ...] = ()
    impacts: tuple[str, ...] = ()
    affected_markets: tuple[str, ...] = ()
    basis: str = "No source completeness claim recorded."

    def __post_init__(self):
        if type(self.complete) is not bool:
            raise ValueError("Coverage completeness must be an explicit boolean")
        for name in ("categories", "event_types", "impacts", "affected_markets"):
            values = getattr(self, name)
            if isinstance(values, str) or any(not isinstance(x, str) or not x.strip() for x in values):
                raise ValueError("Coverage scopes must be collections of non-empty labels")
            object.__setattr__(self, name, tuple(values))
        if self.start or self.end:
            start = _parse_coverage_datetime(self.start)
            end = _parse_coverage_datetime(self.end)
            if start.utcoffset() is None or end.utcoffset() is None or end < start:
                raise ValueError("Coverage requires ordered aware bounds")
        if self.complete and (not self.start or not self.end or not self.basis.strip()):
            raise ValueError("Complete coverage requires bounds and a source basis")

    def covers(self, condition, start, end):
        if not self.complete or not self.start or not self.end:
            return False
        if _parse_coverage_datetime(self.start) > start or _parse_coverage_datetime(self.end) < end:
            return False
        # '*' is an explicit provider claim of all values in a dimension.
        # An empty scope never means all values.
        requested = (
            ((condition.category.value,) if condition.category else (), self.categories),
            (condition.event_types, self.event_types),
            (tuple(x.value for x in condition.impacts), self.impacts),
            (condition.affected_markets, self.affected_markets),
        )
        return all("*" in scope or (bool(values) and set(values).issubset(scope))
                   for values, scope in requested)

    def to_dict(self):
        return {"start": self.start, "end": self.end, "complete": self.complete,
                "categories": list(self.categories), "event_types": list(self.event_types),
                "impacts": list(self.impacts), "affected_markets": list(self.affected_markets),
                "basis": self.basis}

    @classmethod
    def from_dict(cls, payload=None):
        return cls(**dict(payload or {}))


@dataclass(frozen=True)
class ContextSourceProvenance:
    capture_id: str = ""
    content_sha256: str = ""
    source_reference: str = ""
    imported_at: str = ""
    declared_start: str = ""
    declared_end: str = ""
    timezone_basis: str = ""
    adapter_revision: str = ""
    mapping_revision: str = ""
    knowledge_basis: str = "Not recorded; historical as-of knowledge is unverified."
    limitations: tuple[str, ...] = ()

    def __post_init__(self):
        object.__setattr__(self, "limitations", tuple(self.limitations))

    def to_dict(self):
        return {**self.__dict__, "limitations": list(self.limitations)}

    @classmethod
    def from_dict(cls, payload=None):
        return cls(**dict(payload or {}))
