from typing import Optional

from pydantic import BaseModel


class QueryEndPointRequest(BaseModel):
    is_hybrid: bool
    file_name: str
    embedding_model: str
    dimension: int
    similarity_metric: str = "dotproduct"
    query: str
    top_k: int
    alpha: Optional[float] = None
    include_metadata: bool = False
    filter_dict: Optional[dict] = None
