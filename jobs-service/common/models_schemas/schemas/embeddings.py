from dataclasses import dataclass
import numpy as np

@dataclass
class EmbeddingTuple:
    content: str
    embedding: np.ndarray

@dataclass
class EmbeddingList:
    embeddings: list[EmbeddingTuple]