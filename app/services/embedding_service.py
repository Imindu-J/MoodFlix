from sentence_transformers import SentenceTransformer


EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIMENSIONS = 384

class EmbeddingService:
    def __init__(self)->None:
        self.model = SentenceTransformer(EMBEDDING_MODEL_NAME)

        actual_dimensions = (self.model.get_embedding_dimension())
        if actual_dimensions != EMBEDDING_DIMENSIONS:
            raise RuntimeError(
                "Unexpected embedding dimension: "
                f"expected {EMBEDDING_DIMENSIONS}"
                f"received {actual_dimensions}"
            )

    def encode(
            self, 
            texts: list[str],
            *,
            batch_size: int = 32,
            show_progress: bool = True,
    ) -> list[list[float]]:
        if not texts:
            return []
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=show_progress
        )

        return embeddings.tolist()


    def encode_query(self, query: str) -> list[float]:
        cleaned_query = query.strip()
        if not cleaned_query:
            raise ValueError("Query cannot be empty")

        return self.encode([cleaned_query])[0]

    

