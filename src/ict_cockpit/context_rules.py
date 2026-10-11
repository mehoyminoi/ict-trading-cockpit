"""Immutable, provider-neutral Trade Plan context policy definitions."""
from dataclasses import dataclass, field
from datetime import time
from enum import Enum

from ict_cockpit.analysis.market_context_event import MarketContextEventCategory, MarketContextImpact


class ContextEffect(str, Enum):
    INFORMATIONAL = "Informational"
    WARNING = "Warning"
    BLOCK_NEW_ENTRY = "Block New Entry"
    STAND_DOWN_DAY = "Stand Down Day"


class ContextConditionKind(str, Enum):
    MARKET_CLOCK = "Market Clock"
    EVENT_PRESENT = "Event Present"
    EVENT_ABSENT = "Event Absent"


class ContextEventWindow(str, Enum):
    FUTURES_DAY = "Futures Day"
    CALENDAR_WEEK = "Calendar Week"


@dataclass(frozen=True)
class ContextConditionDefinition:
    """Conjunctive rule term. Weekdays use Python's Monday=0 convention.

    Clock terms use America/New_York civil time. Calendar event weekdays use
    Monday=0 in an explicitly offset calendar week (0 means the reference's
    week). Event terms use normalized facts, never title/native text matching.
    """
    kind: ContextConditionKind
    weekdays: tuple[int, ...] = field(default_factory=tuple)
    after_time: str = ""
    event_window: ContextEventWindow = ContextEventWindow.FUTURES_DAY
    category: MarketContextEventCategory | None = None
    event_types: tuple[str, ...] = field(default_factory=tuple)
    impacts: tuple[MarketContextImpact, ...] = field(default_factory=tuple)
    affected_markets: tuple[str, ...] = field(default_factory=tuple)
    event_weekdays: tuple[int, ...] = field(default_factory=tuple)
    calendar_week_offset: int = 0

    def __post_init__(self):
        object.__setattr__(self, "kind", ContextConditionKind(self.kind))
        object.__setattr__(self, "event_window", ContextEventWindow(self.event_window))
        object.__setattr__(self, "weekdays", tuple(self.weekdays))
        object.__setattr__(self, "event_weekdays", tuple(self.event_weekdays))
        object.__setattr__(self, "event_types", tuple(self.event_types))
        object.__setattr__(self, "affected_markets", tuple(self.affected_markets))
        object.__setattr__(self, "impacts", tuple(MarketContextImpact(x) for x in self.impacts))
        if self.category is not None:
            object.__setattr__(self, "category", MarketContextEventCategory(self.category))
        if any(type(x) is not int or x not in range(7) for x in (*self.weekdays, *self.event_weekdays)):
            raise ValueError("weekdays must be integers from 0 to 6")
        if type(self.calendar_week_offset) is not int:
            raise ValueError("calendar_week_offset must be an integer")
        if (self.event_weekdays or self.calendar_week_offset) and self.event_window is not ContextEventWindow.CALENDAR_WEEK:
            raise ValueError("event weekdays and week offsets require Calendar Week")
        for values in (self.weekdays, self.event_weekdays, self.event_types, self.impacts, self.affected_markets):
            if len(values) != len(set(values)):
                raise ValueError("condition selectors must be unique")
        if any(not x.strip() or x != x.strip() for x in (*self.event_types, *self.affected_markets)):
            raise ValueError("event selectors must be non-empty normalized strings")
        if MarketContextImpact.UNKNOWN in self.impacts:
            raise ValueError("Unknown impact cannot be a positive selector")
        if self.kind is ContextConditionKind.MARKET_CLOCK:
            if not self.weekdays and not self.after_time:
                raise ValueError("clock condition requires weekdays or after_time")
            if self.category or self.event_types or self.impacts or self.affected_markets or self.event_window is not ContextEventWindow.FUTURES_DAY:
                raise ValueError("clock condition cannot contain event selectors")
            if self.after_time:
                if len(self.after_time) != 5 or time.fromisoformat(self.after_time).isoformat(timespec="minutes") != self.after_time:
                    raise ValueError("after_time must be HH:MM")
        elif self.weekdays or self.after_time:
            raise ValueError("event condition cannot contain clock selectors")
        elif not (self.category or self.event_types or self.impacts or self.affected_markets):
            raise ValueError("event condition requires an explicit selector")

    def to_dict(self):
        return dict(kind=self.kind.value, weekdays=list(self.weekdays), after_time=self.after_time,
                    event_window=self.event_window.value, category=self.category.value if self.category else None,
                    event_types=list(self.event_types), impacts=[x.value for x in self.impacts],
                    affected_markets=list(self.affected_markets), event_weekdays=list(self.event_weekdays),
                    calendar_week_offset=self.calendar_week_offset)

    @classmethod
    def from_dict(cls, payload):
        return cls(**payload)


@dataclass(frozen=True)
class ContextRuleDefinition:
    id: str
    name: str
    conditions: tuple[ContextConditionDefinition, ...]
    environments: tuple[str, ...]
    effect: ContextEffect
    unknown_effect: ContextEffect
    rationale: str
    playbook_ids: tuple[str, ...] = field(default_factory=tuple)
    not_matched_effect: ContextEffect | None = None

    def __post_init__(self):
        for key in ("id", "name", "rationale"):
            object.__setattr__(self, key, getattr(self, key).strip())
            if not getattr(self, key):
                raise ValueError(f"context rule {key} cannot be empty")
        object.__setattr__(self, "effect", ContextEffect(self.effect))
        object.__setattr__(self, "unknown_effect", ContextEffect(self.unknown_effect))
        if self.not_matched_effect is not None:
            object.__setattr__(self, "not_matched_effect", ContextEffect(self.not_matched_effect))
        if isinstance(self.playbook_ids, str):
            raise ValueError("playbook_ids must be a collection of normalized ids")
        object.__setattr__(self, "playbook_ids", tuple(self.playbook_ids))
        if any(not isinstance(x, str) or not x.strip() or x != x.strip() for x in self.playbook_ids):
            raise ValueError("playbook ids must be non-empty normalized strings")
        if len(self.playbook_ids) != len(set(self.playbook_ids)):
            raise ValueError("playbook ids must be unique")
        if self.playbook_ids and ContextEffect.STAND_DOWN_DAY in (self.effect, self.unknown_effect, self.not_matched_effect):
            raise ValueError("Stand Down Day requires a run-wide rule, not playbook scope")
        object.__setattr__(self, "environments", tuple(self.environments))
        object.__setattr__(self, "conditions", tuple(self.conditions))
        if not self.conditions or not all(isinstance(x, ContextConditionDefinition) for x in self.conditions):
            raise ValueError("context rule requires typed conditions")
        if len(self.conditions) != len(set(self.conditions)):
            raise ValueError("context rule conditions must be unique")
        if not self.environments or set(self.environments) - {"Live", "Replay", "Historical Backtest", "Forward Test"}:
            raise ValueError("context rule requires explicit known environments")
        if len(self.environments) != len(set(self.environments)):
            raise ValueError("context rule environments must be unique")

    def to_dict(self):
        return dict(id=self.id, name=self.name, conditions=[x.to_dict() for x in self.conditions],
                    environments=list(self.environments), effect=self.effect.value,
                    unknown_effect=self.unknown_effect.value, rationale=self.rationale,
                    playbook_ids=list(self.playbook_ids),
                    not_matched_effect=self.not_matched_effect.value if self.not_matched_effect else None)

    @classmethod
    def from_dict(cls, payload):
        return cls(**{**payload, "conditions": tuple(ContextConditionDefinition.from_dict(x) for x in payload["conditions"])})


def normalize_context_rules(payload):
    rules = tuple(x if isinstance(x, ContextRuleDefinition) else ContextRuleDefinition.from_dict(x) for x in payload)
    if len({x.id for x in rules}) != len(rules):
        raise ValueError("context rule ids must be unique")
    return rules
