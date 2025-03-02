from datetime import datetime
from typing import Any, Dict, List

from bson import ObjectId


class NamespaceDetails:
    def __init__(self, filename: str, embedding_model: str):
        self.filename = filename
        self.embedding_model = embedding_model

    def to_dict(self) -> Dict[str, str]:
        return {
            "filename": self.filename,
            "embedding_model": self.embedding_model,
        }


class Namespace:
    def __init__(self, name: str, filename: str, embedding_model: str):
        self.name = name
        self.details = NamespaceDetails(filename, embedding_model)

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "details": self.details.to_dict()}


class IndexUpsert:
    def __init__(
        self,
        index_name: str,
        index_host: str,
        dimension: int,
        similarity_metric: str,
    ):
        self._id = ObjectId()
        self.index_name = index_name
        self.index_host = index_host
        self.dimension = dimension
        self.similarity_metric = similarity_metric
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.namespaces: List[Namespace] = []

    def add_namespace(self, namespace: Namespace) -> None:
        self.namespaces.append(namespace)
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "_id": str(self._id),
            "index_name": self.index_name,
            "index_host": self.index_host,
            "dimension": self.dimension,
            "similarity_metric": self.similarity_metric,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "namespaces": [
                namespace.to_dict() for namespace in self.namespaces
            ],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IndexUpsert":
        index = cls(
            index_name=data["index_name"],
            index_host=data["index_host"],
            dimension=data["dimension"],
            similarity_metric=data["similarity_metric"],
        )

        # Set ID if it exists
        if "_id" in data:
            if isinstance(data["_id"], str):
                index._id = ObjectId(data["_id"])
            else:
                index._id = data["_id"]

        # Set dates if they exist
        if "created_at" in data:
            if isinstance(data["created_at"], str):
                index.created_at = datetime.fromisoformat(data["created_at"])
            else:
                index.created_at = data["created_at"]

        if "updated_at" in data:
            if isinstance(data["updated_at"], str):
                index.updated_at = datetime.fromisoformat(data["updated_at"])
            else:
                index.updated_at = data["updated_at"]

        # Add namespaces if they exist
        if "namespaces" in data:
            for namespace_data in data["namespaces"]:
                details = namespace_data["details"]
                namespace = Namespace(
                    name=namespace_data["name"],
                    filename=details["filename"],
                    embedding_model=details["embedding_model"],
                )
                index.namespaces.append(namespace)

        return index
