from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FindingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    rule_id: str
    severity: str
    file_path: str
    line: int | None
    message: str
    explanation: str | None


class ScanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    repo_full_name: str
    pr_number: int
    head_sha: str
    status: str
    created_at: datetime
    findings: list[FindingOut] = []
