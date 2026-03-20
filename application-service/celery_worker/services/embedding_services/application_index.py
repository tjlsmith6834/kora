import logging
from uuid import UUID
from sqlalchemy.orm import Session

from .faiss_utils import generate_faiss_index
from .application_doc_embeddings import retrieve_application_doc_embeddings, create_and_store_doc_embeddings
from .application_qa_embeddings import retrieve_application_qa_embeddings

from common.models_schemas.schemas import EmbeddingList

async def generate_application_faiss_index(application_id: UUID, db_session: Session):
    """
    Generates a FAISS index for a given application_id by combining document embeddings
    and question-answer embeddings.

    Args:
        application_id (str): The unique identifier for the application.
        db_session (Session): SQLAlchemy session for database transactions.

    Returns:
        tuple: (FAISS index, metadata list) or (None, []) if no embeddings are found.
    """
    logging.info(f"Generating combined FAISS index for application_id: {application_id}")

    # Retrieve document embeddings
    doc_embeddings = await retrieve_application_doc_embeddings(application_id, db_session)
    if not doc_embeddings or len(doc_embeddings.embeddings) == 0:
        doc_embeddings = await create_and_store_doc_embeddings(application_id, db_session)

    # Retrieve QA embeddings
    qa_embeddings = await retrieve_application_qa_embeddings(application_id, db_session)

    # If no embeddings are found, return None
    if (not doc_embeddings or len(doc_embeddings.embeddings) == 0) and (not qa_embeddings or len(qa_embeddings) == 0):
        logging.warning(f"No embeddings found for application_id: {application_id}")
        return None, []

    # Merge document and QA embeddings
    all_embeddings_list = (doc_embeddings.embeddings or []) + (qa_embeddings.embeddings or [])
    all_embeddings = EmbeddingList(
        embeddings=all_embeddings_list
    )

    # Create application index
    faiss_index, metadata = generate_faiss_index(all_embeddings)

    logging.info(f"Successfully created FAISS index with {len(metadata)} combined embeddings.")
    return faiss_index, metadata