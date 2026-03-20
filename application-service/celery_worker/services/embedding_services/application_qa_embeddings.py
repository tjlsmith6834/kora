from sqlalchemy.orm import Session
import numpy as np
import asyncio
import logging
from uuid import UUID

from .faiss_utils import create_text_embeddings

from common.models_schemas.models import ApplicationQuestionsAnswers
from common.models_schemas.schemas import EmbeddingList, EmbeddingTuple, QAResponse

### MAIN FUNCTIONS ###
def generate_all_qa_embeddings(db_session: Session):
    logging.info("Fetching question-answer pairs from the database.")

    # Retrieve all records without embeddings
    qa_entries = db_session.query(ApplicationQuestionsAnswers).filter(
        (ApplicationQuestionsAnswers.embeddings == None) &
        (ApplicationQuestionsAnswers.answer_text.isnot(None))
    ).all()

    if not qa_entries:
        logging.info("No new question-answer pairs found for embedding.")
        return

    combined_texts = [
        f"Q: {entry.question_text} A: {entry.answer_text}"
        for entry in qa_entries
    ]

    embeddings = create_text_embeddings(combined_texts)  # Batch call

    for entry, embedding in zip(qa_entries, embeddings):
        entry.embeddings = embedding.tolist()
        entry.embedding_content = f"Q: {entry.question_text} A: {entry.answer_text}"
        db_session.add(entry)

    db_session.commit()
    logging.info("Successfully stored embeddings in the database.")


async def generate_qa_embedding_for_entry(qa_id: UUID, db_session: Session):
    """
    Generates and stores an embedding for a specific question-answer entry in the database.

    Args:
        db_session (Session): SQLAlchemy session for database transactions.
        qa_id (UUID): The ID of the question-answer entry to process.
    """
    logging.info(f"Fetching QA entry with qa_id: {qa_id}")

    async def fetch_qa_entry(qa_id: UUID, db_session: Session):
        # Define a function for the blocking operation.
        def query_entry():
            return db_session.query(ApplicationQuestionsAnswers).filter(
                ApplicationQuestionsAnswers.qa_id == qa_id
            ).one_or_none()

        # Run the blocking query in a thread and await its result.
        entry = await asyncio.to_thread(query_entry)
        return entry

    entry = await fetch_qa_entry(qa_id, db_session)
    if not entry:
        logging.info(f"No valid entry found for qa_id: {qa_id}.")
        return None

    qa = QAResponse(
        question=entry.question_text,
        answer = entry.answer_text
    )

    logging.info(f"Generating embedding for qa: {qa}")

    # Generate embedding
    embedding_tuple = await create_qa_embedding(qa)
    embedding_record = await store_qa_embedding(
        qa_id= qa_id,
        embedding_tuple= embedding_tuple,
        db_session= db_session)
    return embedding_record

async def retrieve_application_qa_embeddings(application_id: UUID, db_session: Session) -> EmbeddingList:
    """
    Retrieves stored embeddings for a given application ID.
    """
    logging.info(f"Retrieving embeddings for application_id: {application_id}")

    embeddings = db_session.query(ApplicationQuestionsAnswers).filter_by(application_id=application_id).all()

    if embeddings is None or len(embeddings) == 0:
        logging.warning(f"No QA embeddings found for application_id: {application_id}")
        return EmbeddingList(embeddings=[])

    embedding_tuples = []
    for entry in embeddings:
        embedding_array = np.array(entry.embeddings, dtype=np.float32)
        embedding_content = f"Question: {entry.question_text} Answer: {entry.answer_text}"
        embedding_tuples.append(
            EmbeddingTuple(
                content=embedding_content,
                embedding=embedding_array
            )
        )

    result = EmbeddingList(embeddings=embedding_tuples)

    return result

async def create_qa_embedding(qa: QAResponse) -> EmbeddingTuple:
    logging.info(f"Running create_qa_embedding for qa {qa}")

    embedding_content = f"Question: {qa.question} Answer: {qa.answer}"

    # Use batch API even for single item (returns a list of embeddings)
    embeddings = await asyncio.to_thread(create_text_embeddings, [embedding_content])
    if not embeddings or len(embeddings) != 1:
        raise ValueError("Failed to create embedding")

    embedding_array = embeddings[0]  # Already a np.array from your batch function
    return EmbeddingTuple(content=embedding_content, embedding=embedding_array)

async def store_qa_embedding(qa_id: UUID, embedding_tuple: EmbeddingTuple, db_session: Session):
    """
        Updates the ApplicationQuestionsAnswers record with the provided qa_id by setting
        its embeddings and embedding_content fields using the data from new_embedding.

        Args:
            qa_id (UUID): The UUID of the question-answer record to update.
            embedding_tuple (EmbeddingTuple): The new embedding tuple containing content and embedding vector.
            db_session (Session): SQLAlchemy database session.

        Returns:
            ApplicationQuestionsAnswers: The updated record.
        """
    # Retrieve the record to update
    qa_record = db_session.query(ApplicationQuestionsAnswers).filter_by(qa_id=qa_id).first()
    if not qa_record:
        raise ValueError(f"No ApplicationQuestionsAnswers record found with qa_id: {qa_id}")

    # Update fields
    qa_record.embeddings = embedding_tuple.embedding.tolist()
    qa_record.embedding_content = embedding_tuple.content

    # Commit the changes to the database
    db_session.commit()
    db_session.refresh(qa_record)

    return qa_record.qa_id
