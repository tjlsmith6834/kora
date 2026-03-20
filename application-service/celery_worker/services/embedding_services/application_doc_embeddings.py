import asyncio
import numpy as np
import logging
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session

from .faiss_utils import create_text_embeddings
from ...utils.text_from_file_utils import extract_text_from_file

from common.models_schemas.schemas import EmbeddingList, EmbeddingTuple
from common.models_schemas.models import ApplicationEmbedding
from common.storage_retrieval_services import retrieve_application_docs

# Initialize logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

### MAIN FUNCTIONS ###
async def create_and_store_doc_embeddings(application_id: UUID, db_session: Session) -> EmbeddingList:
    """
    Wrapper function to store document embeddings and generate a FAISS index.
    """
    try:
        resume_list = await retrieve_application_docs(application_id, db_session)
        resume = resume_list[0]
        embeddings_list = await create_doc_embeddings(resume)
        await store_doc_embeddings(embeddings_list, application_id, db_session)

        logging.info(f"FAISS index generated with {len(embeddings_list.embeddings)} items.")
        return embeddings_list

    except Exception as e:
        logging.error(f"Error in create_and_store_doc_embeddings: {e}")
        raise RuntimeError(f"An error occurred: {e}")

async def retrieve_application_doc_embeddings(application_id: UUID, db_session: Session) -> EmbeddingList:
    """
    Retrieves stored document embeddings for a given application ID from the PostgreSQL database
    and returns them in a Pydantic EmbeddingList format.

    Args:
        application_id (UUID): The application ID for which to fetch embeddings.
        db_session (Session): SQLAlchemy session for database transactions.

    Returns:
        EmbeddingList: A dataclass containing a list of EmbeddingTuple items.
    """
    logging.info(f"Fetching stored document embeddings for application_id: {application_id}")

    embeddings = db_session.query(ApplicationEmbedding).filter_by(application_id=application_id).all()

    if not embeddings or len(embeddings) == 0:
        logging.warning(f"No document embeddings found for application_id: {application_id}")
        # Return an empty EmbeddingList
        return EmbeddingList(embeddings=[])

    # Convert database objects to a EmbeddingTuple list
    embedding_tuples = []
    for embedding in embeddings:
        embedding_array = np.array(embedding.embedding, dtype=np.float32)
        embedding_tuples.append(
            EmbeddingTuple(
                content=embedding.content,
                embedding=embedding_array
            )
        )

    result = EmbeddingList(embeddings=embedding_tuples)
    logging.info(f"Retrieved {len(result.embeddings)} document embeddings for application_id: {application_id}")

    return result


async def create_doc_embeddings(file) -> EmbeddingList:
    logging.info(f"Running create_doc_embeddings for {file.name}")

    try:
        text_chunks = await extract_and_split_file_text(file)

        # Batch embed all chunks at once
        embeddings = await asyncio.to_thread(create_text_embeddings, text_chunks)

        embedding_tuples = [
            EmbeddingTuple(content=chunk, embedding=embedding)
            for chunk, embedding in zip(text_chunks, embeddings)
        ]

    except Exception as e:
        logging.error(f"Error processing file: {e}")
        raise

    logging.info(f"Generated {len(embedding_tuples)} embeddings.")
    return EmbeddingList(embeddings=embedding_tuples)

async def store_doc_embeddings(embeddings_list: EmbeddingList, application_id: UUID, db_session: Session):
    """
    Stores generated document embeddings in PostgreSQL using SQLAlchemy ORM.

    Args:
        embeddings_list: Dataclass containing list of embedding tuples (content, embedding_vector).
        application_id (str): The associated application ID.
        db_session (Session): SQLAlchemy session for database transactions.

    Returns:
        int: The number of stored embeddings.
    """
    embeddings = embeddings_list.embeddings
    logging.info(f"Running store_doc_embeddings.\nStoring {len(embeddings)} embeddings for application_id: {application_id}")

    for emb in embeddings:
        try:
            # Store embedding in the database
            embedding_vector = emb.embedding.tolist()
            embedding_content = emb.content
            embedding_entry = ApplicationEmbedding(
                application_id=application_id,
                embedding=embedding_vector,
                content=embedding_content,
            )
            db_session.add(embedding_entry)

        except Exception as e:
            logging.error(f"Error storing embedding: {e}")
            raise

    db_session.commit()
    logging.info(f"Successfully stored {len(embeddings)} embeddings in the database.")
    return len(embeddings)

# Helper Functions
async def extract_and_split_file_text(file) -> List[str]:
    """
    Extracts content from a file, either from a file path or a file object.

    Args:
        file (file-like): File-like object.

    Returns:
        str: The extracted file content.
    """
    content = extract_text_from_file(file.file)

    logging.info(f"File content length: {len(content)} characters")
    text_chunks = split_text(content)
    return text_chunks


def split_text(file_content: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[str]:
    """
    Splits extracted text into chunks of fixed size with overlap.

    Args:
        file_content (str): The full text to split.
        chunk_size (int): Maximum number of characters per chunk.
        chunk_overlap (int): Number of overlapping characters between chunks.

    Returns:
        List[str]: A list of text chunks.
    """
    text_length = len(file_content)
    if chunk_size <= chunk_overlap:
        raise ValueError("chunk_size must be greater than chunk_overlap")

    text_chunks = []
    start = 0
    # Calculate the step for each chunk (non-overlapping portion)
    step = chunk_size - chunk_overlap

    # Use a sliding window to extract chunks until we reach the end.
    while start < text_length:
        end = start + chunk_size
        chunk = file_content[start:end]
        text_chunks.append(chunk)
        # Move the window forward by the step length
        start += step

    logging.info(f"Extracted {len(text_chunks)} chunks from document.")
    return text_chunks


