from pydantic import BaseModel


class IndexUpsertRequest(BaseModel):
    file_name: str
    embed_model: str
    similarity_metric: str
    dimension: int
