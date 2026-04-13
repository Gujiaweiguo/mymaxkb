# coding=utf-8

from typing import List, Optional, Protocol, Sequence

from langchain_core.callbacks import Callbacks
from langchain_core.documents import Document


class EmbeddingModel(Protocol):
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        ...

    def embed_query(self, text: str) -> List[float]:
        ...


class DownloadableEmbeddingModel(EmbeddingModel, Protocol):
    def start_down_model_thread(self) -> None:
        ...


class RerankerModel(Protocol):
    def compress_documents(
        self,
        documents: Sequence[Document],
        query: str,
        callbacks: Optional[Callbacks] = None,
    ) -> Sequence[Document]:
        ...
