import os
import numpy as np
from typing import List
import faiss
from openai import OpenAI
import logging

from common.models_schemas.schemas import EmbeddingList

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def create_text_embeddings(texts: List[str]) -> List[np.ndarray]:
    """
    Generates embeddings for a list of texts using OpenAI's embedding model in a single batch call.
    """
    try:
        response = client.embeddings.create(
            model="text-embedding-ada-002",
            input=texts
        )
        return [np.array(item.embedding, dtype=np.float32) for item in response.data]
    except Exception as e:
        logging.error(f"Error generating batch embeddings: {e}")
        return []

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