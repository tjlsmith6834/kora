from typing import List
from uuid import UUID
from pydantic import BaseModel, Field, conlist

class RubricCategory(BaseModel):
    """Represents a rubric category with multiple criteria."""
    category_id: UUID = Field(..., description="Unique identifier for the category.")
    category: str = Field(..., description="Category name.")
    criteria: List[str] = Field(..., description="List of criteria descriptions.")
    weight: float = Field(..., description="Weight of the category in rubric scoring.")
    focus: str = Field(..., description="Description of what the category evaluates.")

class Rubric(BaseModel):
    """Response model for the retrieved rubric."""
    categories: List[RubricCategory] = Field(..., description="List of rubric categories.")

class RubricCategoryEmbeddings(BaseModel):
    embedding_id: UUID = Field(..., description="Primary key UUID for this embedding row")
    category_id: UUID = Field(..., description="Foreign key to rubric_categories.category_id")
    focus_embedding: conlist(float) = Field(..., description="1536-dimensional embedding vector for the category focus")
    criteria_embedding: conlist(float) = Field(..., description="1536-dimensional embedding vector for the criteria")