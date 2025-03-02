from typing import Any, Dict, List, Union

from pydantic import BaseModel, model_validator


class Document(BaseModel):
    id: str
    text: str

    model_config = {
        "extra": "ignore"  # Ignores any extra fields in the document
    }


class RerankingRequest(BaseModel):
    model_name: str
    query: str
    documents: Union[
        List[Dict], Dict[str, Any]
    ]  # Can accept either the nested structure or direct list
    top_n: int

    @model_validator(mode="before")
    @classmethod
    def extract_relevant_docs(cls, values):
        docs = values.get("documents")

        # If documents is a dict with the nested structure, extract relevant_docs
        if isinstance(docs, dict):
            # Try to extract from the nested structure
            if (
                "data" in docs
                and isinstance(docs["data"], dict)
                and "relevant_docs" in docs["data"]
            ):
                values["documents"] = docs["data"]["relevant_docs"]

        return values


class RerankingResult(BaseModel):
    document: Dict
    score: float


class RerankingResponse(BaseModel):
    results: List[RerankingResult]
