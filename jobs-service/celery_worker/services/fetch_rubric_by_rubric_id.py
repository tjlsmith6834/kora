from uuid import UUID
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from common.models_schemas.models import Rubric, RubricCategory, RubricCriteria
from common.models_schemas.schemas import RubricOut, RubricCategoryOut

def fetch_rubric_by_rubric_id(
    rubric_id: UUID,
    db: Session
) -> RubricOut:
    # 1) Fetch the rubric itself
    rubric = db.query(Rubric).filter(Rubric.rubric_id == rubric_id).one_or_none()
    if rubric is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rubric {rubric_id} not found"
        )

    # 2) Fetch all categories for that rubric
    categories: List[RubricCategory] = (
        db.query(RubricCategory)
          .filter(RubricCategory.rubric_id == rubric_id)
          .all()
    )

    # 3) Batch‐fetch all criteria in one go
    category_ids = [c.category_id for c in categories]
    all_criteria: List[RubricCriteria] = []
    if category_ids:
        all_criteria = (
            db.query(RubricCriteria)
              .filter(RubricCriteria.category_id.in_(category_ids))
              .all()
        )

    # 4) Group criteria texts by category_id
    crit_map: dict[UUID, List[str]] = {cid: [] for cid in category_ids}
    for crit in all_criteria:
        crit_map[crit.category_id].append(crit.criterion)

    # 5) Build your output categories
    out_categories: List[RubricCategoryOut] = []
    for cat in categories:
        out_categories.append(
            RubricCategoryOut(
                category_id=cat.category_id,
                category=cat.category,
                weight=cat.weight,
                focus=cat.focus,
                criteria=crit_map.get(cat.category_id, [])
            )
        )

    # 6) Return the full RubricOut
    return RubricOut(
        rubric_id=rubric.rubric_id,
        analysis_task_id=rubric.analysis_task_id,
        categories=out_categories
    )