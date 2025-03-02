from pydantic import BaseModel
from typing import Optional

class QueryEndPointRequest(BaseModel):
    is_hybrid: bool
    filename: str
    embedding_model: str
    dimension: int
    similarity_metric: str = "dotproduct"
    query: str
    top_k: int
    alpha: Optional[float] = None
    include_metadata: bool
    filter_dict: Optional[dict] = None