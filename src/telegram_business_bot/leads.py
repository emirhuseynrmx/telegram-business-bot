from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel, ConfigDict, EmailStr, Field, ValidationError


class Lead(BaseModel):
    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    name: str = Field(min_length=2)
    email: EmailStr
    message: str = Field(min_length=3, max_length=1000)
    created_at: datetime

    def to_row(self) -> dict[str, str]:
        return {
            "name": self.name,
            "email": self.email,
            "message": self.message,
            "created_at": self.created_at.isoformat(),
        }


class LeadExportSummary(BaseModel):
    model_config = ConfigDict(frozen=True)

    rows: int
    path: Path
    latest_created_at: str | None


class LeadStore:
    def __init__(self, path: Path) -> None:
        self.path = path

    def append(self, lead: Lead) -> Path:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        exists = self.path.exists()
        with self.path.open("a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=["name", "email", "message", "created_at"])
            if not exists:
                writer.writeheader()
            writer.writerow(lead.to_row())
        return self.path

    def read_all(self) -> list[dict[str, str]]:
        if not self.path.exists():
            return []
        with self.path.open(newline="", encoding="utf-8") as file:
            return list(csv.DictReader(file))

    def summary(self) -> LeadExportSummary:
        rows = self.read_all()
        latest = rows[-1]["created_at"] if rows else None
        return LeadExportSummary(rows=len(rows), path=self.path, latest_created_at=latest)


def parse_lead_command(text: str) -> Lead:
    raw = text.removeprefix("/lead").strip()
    parts = [part.strip() for part in raw.split("|")]
    if len(parts) != 3:
        raise ValueError("Use: /lead name | email | message")
    try:
        return Lead(
            name=parts[0],
            email=parts[1],
            message=parts[2],
            created_at=datetime.now(timezone.utc),
        )
    except ValidationError as exc:
        raise ValueError("Lead is invalid. Check name, email, and message.") from exc
