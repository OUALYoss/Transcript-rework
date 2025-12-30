from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Change:
    """Une modification."""

    step: str
    message_index: int
    before: str
    after: str


@dataclass
class TransformationReport:
    """Rapport des transformations."""

    transcript_id: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    changes: list[Change] = field(default_factory=list)

    def add(self, step: str, index: int, before: str, after: str):
        if before != after:
            self.changes.append(Change(step, index, before, after))

    def summary(self) -> dict:
        by_step = {}
        for c in self.changes:
            by_step[c.step] = by_step.get(c.step, 0) + 1  # compteur de steps
        return {
            "transcript_id": self.transcript_id,
            "total_changes": len(self.changes),
            "by_step": by_step,
        }

    def to_dict(self) -> dict:
        return {
            "transcript_id": self.transcript_id,
            "timestamp": self.timestamp,
            "total_changes": len(self.changes),
            "changes": [
                {
                    "step": c.step,
                    "message_index": c.message_index,
                    "before": c.before,
                    "after": c.after,
                }
                for c in self.changes
            ],
        }
