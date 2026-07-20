from typing import Any, List, Dict, Tuple, Protocol

class SearchIndex(Protocol):
    def add_document(self, document: Dict[str, Any]) -> None: ...

    # Added the 'add_documents' method to avoid rate limiting errors from VoyageAI
    def add_documents(self, documents: List[Dict[str, Any]]) -> None: ...

    def search(
        self, query: Any, k: int = 1
    ) -> List[Tuple[Dict[str, Any], float]]: ...