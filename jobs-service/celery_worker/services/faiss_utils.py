import os
import numpy as np
import faiss
from openai import OpenAI
import logging

from common.models_schemas.schemas import EmbeddingList

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def create_text_embedding(text):
    """
    Generates an embedding for the given text using OpenAI's model.
    """
    try:
        response = client.embeddings.create(
            model="text-embedding-ada-002",  # Use the latest embedding model
            input=text
        )
        return response.data[0].embedding  # Extract embedding vector
    except Exception as e:
        logging.error(f"Error generating embedding: {e}")
        return None

def generate_faiss_index(embedding_list: EmbeddingList, index_type="IndexFlatL2"):
    """
    Creates a FAISS index from multiple embeddings in an EmbeddingList dataclass.

    Args:
        embedding_list (EmbeddingList):
            A dataclass containing a list of embeddings, where each embedding has:
            - content (str)
            - embedding (np.ndarray)
        index_type (str):
            The FAISS index type to use. Defaults to "IndexFlatL2".
            Supported: "IndexFlatL2", "IndexFlatIP"

    Returns:
        tuple: (faiss.Index, List[str])
            A tuple containing the FAISS index and a list of metadata (content strings).
    """
    logging.info(f"Running generate_faiss_index using {index_type}.")

    if not embedding_list.embeddings:
        raise ValueError("No embeddings to build the FAISS index.")

    # Extract vectors (as np.ndarray) and metadata from the EmbeddingList
    vectors = np.array([emb.embedding for emb in embedding_list.embeddings], dtype=np.float32)
    metadata = [emb.content for emb in embedding_list.embeddings]

    if vectors.ndim != 2:
        raise ValueError("Embeddings must be a 2D array (num_embeddings, vector_size).")

    dimension = vectors.shape[1]

    # Select the FAISS index type
    if index_type == "IndexFlatL2":
        index = faiss.IndexFlatL2(dimension)
    elif index_type == "IndexFlatIP":
        index = faiss.IndexFlatIP(dimension)  # for cosine or inner product
    else:
        raise ValueError(f"Unsupported FAISS index type: {index_type}")

    # Add embeddings to the FAISS index
    index.add(vectors)

    logging.info(f"FAISS index created with {len(vectors)} embeddings.")
    return index, metadata