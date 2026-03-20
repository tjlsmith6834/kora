from pydantic import BaseModel, Field, conlist, field_validator

from typing import List, Optional
from uuid import UUID

class RubricCategoryOut(BaseModel):
    """Represents a rubric category with multiple criteria."""
    category_id: UUID = Field(..., description="Unique identifier for the category.")
    category: str = Field(..., description="Category name.")
    criteria: List[str] = Field(..., description="List of criteria descriptions.")
    weight: int = Field(..., description="Weight of the category in rubric scoring.")
    focus: str = Field(..., description="Description of what the category evaluates.")

    @field_validator('weight', mode='before')
    @classmethod
    def round_weight(cls, v):
        return round(v)

class RubricOut(BaseModel):
    """Response model for the retrieved rubric."""
    rubric_id: UUID = Field(..., description="Unique identifier for the rubric.")
    categories: List[RubricCategoryOut] = Field(..., description="List of rubric categories.")
    analysis_task_id: Optional[UUID] = Field(None, description="Unique identifier for the analysis task.")

class RubricCategoryIn(BaseModel):
    """Represents a rubric category with multiple criteria."""
    category: str = Field(..., description="Category name.")
    criteria: List[str] = Field(..., description="List of criteria descriptions.")
    weight: int = Field(..., description="Weight of the category in rubric scoring.")
    focus: str = Field(..., description="Description of what the category evaluates.")

class RubricIn(BaseModel):
    categories: List[RubricCategoryIn] = Field(..., description="List of rubric categories.")

class RubricCategoryEmbeddingsOut(BaseModel):
    embedding_id: UUID = Field(..., description="Primary key UUID for this embedding row")
    category_id: UUID = Field(..., description="Foreign key to rubric_categories.category_id")
    focus_embedding: conlist(float) = Field(..., description="1536-dimensional embedding vector for the category focus")
    criteria_embedding: conlist(float) = Field(..., description="1536-dimensional embedding vector for the criteria")


