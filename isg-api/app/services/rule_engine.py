from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional, Tuple

from app.models.safety_rule import SafetyRule, SafetyRuleType


@dataclass
class RuleEvaluationResult:
    triggered: bool
    occurred_at: datetime
    rule_type: SafetyRuleType


class RuleEngine:
    """
    In-memory rule evaluator that applies min_duration and cooldown per
    (camera_id, track_id, rule_type) tuple.
    """

    def __init__(self) -> None:
        self._state: Dict[Tuple[int, Optional[int], SafetyRuleType], Dict[str, Optional[datetime]]] = {}

    def reset(self, camera_id: int, track_id: Optional[int], rule_type: SafetyRuleType) -> None:
        key = (camera_id, track_id, rule_type)
        if key in self._state:
            self._state.pop(key, None)

    def update(
        self,
        *,
        camera_id: int,
        rule: SafetyRule,
        is_missing: bool,
        track_id: Optional[int] = None,
        now: Optional[datetime] = None,
    ) -> Optional[RuleEvaluationResult]:
        now = now or datetime.utcnow()
        key = (camera_id, track_id, rule.rule_type)
        state = self._state.setdefault(
            key,
            {
                "missing_since": None,
                "last_triggered": None,
            },
        )

        if not rule.enabled:
            self.reset(camera_id, track_id, rule.rule_type)
            return None

        if not is_missing:
            state["missing_since"] = None
            return None

        if state["missing_since"] is None:
            state["missing_since"] = now
            return None

        # Enforce min_duration
        elapsed = (now - state["missing_since"]).total_seconds()
        if elapsed < (rule.min_duration_sec or 0):
            return None

        # Cooldown
        last_triggered = state.get("last_triggered")
        if last_triggered:
            cooldown_elapsed = (now - last_triggered).total_seconds()
            if cooldown_elapsed < (rule.cooldown_sec or 0):
                return None

        state["last_triggered"] = now
        return RuleEvaluationResult(triggered=True, occurred_at=now, rule_type=rule.rule_type)
