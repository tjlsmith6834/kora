from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import date

from common.models_schemas.models.profile import RecentRole as RecentRoleORM
from common.models_schemas.schemas.profiles import RecentRole as RecentRoleSchema


def get_recent_roles_block(application_id: UUID, db: Session) -> str:
    """
    Fetch all recent roles for a given application_id, convert to Pydantic models,
    and return a formatted career path block for prompting.
    """
    # Retrieve roles ordered by recency ascending (0 = most recent)
    roles: List[RecentRoleORM] = (
        db.query(RecentRoleORM)
        .filter(RecentRoleORM.application_id == application_id)
        .order_by(RecentRoleORM.recency.asc())
        .all()
    )

    # Convert ORM objects → Pydantic models
    role_schemas: List[RecentRoleSchema] = [
        RecentRoleSchema(
            id=r.id,
            application_id=r.application_id,
            title=r.title,
            organization=r.organization,
            recency=r.recency,
            start_date=r.start_date,
            end_date=r.end_date,
        )
        for r in roles
    ]

    # Return formatted block (safe for prompt insertion)
    return format_career_path(role_schemas)

def _months_between(d1: date, d2: date) -> int:
    """Whole-month difference from d1 -> d2 (assumes d2 >= d1)."""
    months = (d2.year - d1.year) * 12 + (d2.month - d1.month)
    # keep it simple/deterministic; ignore day-level rounding
    return max(0, months)

def _fmt_tenure(months: int) -> str:
    y, m = divmod(months, 12)
    if y and m: return f"{y}y {m}m"
    if y:        return f"{y}y"
    return f"{m}m"


# ---- main: build a deterministic, quotable block ----
def format_career_path(roles: List[RecentRoleSchema]) -> str:
    """
    Returns lines like:
    - Senior PM @ Acme | 2022-01-01 – present (3y 4m) [gap 5m]
    """
    if not roles:
        return "(no roles found)"

    today = date.today()

    # Most recent first: by (end_date or today), then start_date
    def sort_key(r: RecentRoleSchema):
        end = r.end_date or today
        return (end, r.start_date)

    roles_sorted = sorted(roles, key=sort_key, reverse=True)

    # Precompute tenures
    def tenure_months(r: RecentRoleSchema) -> int:
        end = r.end_date or today
        return _months_between(r.start_date, end)

    lines = []
    for i, r in enumerate(roles_sorted):
        end_label = "present" if r.end_date is None else r.end_date.isoformat()
        tenure = _fmt_tenure(tenure_months(r))

        # Gap vs. the immediately-more-recent role (i-1)
        gap_tag = ""
        if i > 0:
            newer = roles_sorted[i - 1]  # more recent role above
            if r.end_date is not None:
                # gap exists only if this (older) role ended BEFORE the newer role started
                if r.end_date < newer.start_date:
                    gap_m = _months_between(r.end_date, newer.start_date)
                    if gap_m >= 3:  # tweak threshold if you like
                        gap_tag = f" [gap {gap_m}m]"

        line = (
            f"- {r.title} @ {r.organization} | "
            f"{r.start_date.isoformat()} – {end_label} "
            f"({tenure}){gap_tag}"
        )
        lines.append(line)

    return "\n".join(lines)