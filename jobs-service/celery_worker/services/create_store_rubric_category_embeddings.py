import numpy as np
from sqlalchemy import delete
from sqlalchemy.orm import Session
from typing import List, Tuple
from uuid import UUID
import logging

from .faiss_utils import create_text_embedding

from common.models_schemas.schemas import RubricOut, RubricCategoryOut, RubricCategoryEmbeddingsOut
from common.models_schemas.models import RubricCategoryEmbeddings, Rubric

def create_store_rubric_category_embeddings(rubric: RubricOut, db: Session) -> List[RubricCategoryEmbeddingsOut]:

    try:
        logging.info(f"Running create_store_rubric_category_embeddings")
        embedding_entries: List[RubricCategoryEmbeddings] = []

        # Generate embeddings for the rubric
        for category in rubric.categories:
            focus_embedding, criteria_embedding = generate_rubric_category_embeddings(category)
            embedding_model = store_rubric_category_embeddings(category.category_id, focus_embedding, criteria_embedding, db)
            embedding_entries.append(embedding_model)

        rubric_db = db.query(Rubric).filter(Rubric.rubric_id == rubric.rubric_id).one_or_none()
        rubric_db.status="analyzed"

        db.commit()

        embeddings_out = [RubricCategoryEmbeddingsOut(
            embedding_id = r.embedding_id,
            category_id = r.category_id,
            focus_embedding = r.focus_embedding,
            criteria_embedding = r.criteria_embedding) for r in embedding_entries]

        return embeddings_out

    except Exception as e:
        db.rollback()
        logging.error(f"❌ Error in build_and_store_rubric_category_embeddings_from_rubric: {e}")
        raise RuntimeError(f"Error storing rubric category embeddings: {e}")

### EMBEDDING CREATION FUNCTION ###
def generate_rubric_category_embeddings(rubric_category: RubricCategoryOut) -> Tuple[np.ndarray, np.ndarray]:

    combined_criteria: str = ", ".join(criterion for criterion in rubric_category.criteria)

    focus_embedding = create_text_embedding(rubric_category.focus)
    focus_embedding_array = np.array(focus_embedding, dtype=np.float32)

    criteria_embedding = create_text_embedding(combined_criteria)
    criteria_embedding_array = np.array(criteria_embedding, dtype=np.float32)

    return focus_embedding_array, criteria_embedding_array

### EMBEDDING STORAGE FUNCTION ###
def store_rubric_category_embeddings(category_id: UUID, focus_embedding: np.array, criteria_embedding: np.array, db_session: Session) -> RubricCategoryEmbeddings:

    logging.info(f"Storing embeddings for category_id: {category_id}")

    try:
        db_session.execute(
            delete(RubricCategoryEmbeddings)
            .where(RubricCategoryEmbeddings.category_id == category_id)
        )

        embedding_entry = RubricCategoryEmbeddings(
            category_id=category_id,
            focus_embedding=focus_embedding.tolist(),  # Convert NumPy array to list
            criteria_embedding=criteria_embedding.tolist(),
        )
        db_session.add(embedding_entry)

        logging.info(f"Added embeddings for category_id: {category_id}")
        return embedding_entry

    except Exception as e:
        db_session.rollback()
        logging.error(f"Error storing embeddings: {e}")
        raise