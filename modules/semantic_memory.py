import os
import json
import math
import re
from modules.logger import log_info, log_error

# Local Semantic Mapping Matrix
CONCEPT_ANCHORS = {
    # Staff / Labor Concepts
    "employee": "concept_staff",
    "personnel": "concept_staff",
    "staff": "concept_staff",
    "worker": "concept_staff",
    "workers": "concept_staff",
    
    # Morale / Drive Concepts
    "morale": "concept_motivation",
    "satisfaction": "concept_motivation",
    "motivation": "concept_motivation",
    "happiness": "concept_motivation",
    
    # Leadership / Command Concepts
    "leadership": "concept_management",
    "management": "concept_management",
    "transformational": "concept_management",
    
    # Assessment Concepts
    "analyzing": "concept_evaluation",
    "measuring": "concept_evaluation",
    "evaluating": "concept_evaluation",
    "research": "concept_evaluation"
}

class SemanticMemoryEngine:
    """Manages lightweight, local vector space embeddings and similarity ranking."""
    def __init__(self, storage_path="data/semantic_store.json"):
        self.storage_path = storage_path
        self.memories = []
        self._load_store()

    def _load_store(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r") as f:
                    self.memories = json.load(f)
            except Exception as e:
                log_error("SemanticMemory", f"Failed to load memory store: {e}")
                self.memories = []
        else:
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            self.memories = []

    def _save_store(self):
        try:
            with open(self.storage_path, "w") as f:
                json.dump(self.memories, f, indent=4)
        except Exception as e:
            log_error("SemanticMemory", f"Failed to persist memory store: {e}")

    def _tokenize_and_vectorize(self, text: str) -> dict:
        """Creates a normalized term vector, mapping synonyms to unified concepts."""
        clean_text = re.sub(r"[^\w\s]", "", text.lower())
        raw_tokens = [w for w in clean_text.split() if len(w) > 2]
        
        vector = {}
        if not raw_tokens:
            return vector
            
        # Translate raw tokens to unified concept anchors where applicable
        for token in raw_tokens:
            resolved_token = CONCEPT_ANCHORS.get(token, token)
            vector[resolved_token] = vector.get(resolved_token, 0) + 1
            
        # Normalize the vector to unit length
        magnitude = math.sqrt(sum(val ** 2 for val in vector.values()))
        if magnitude > 0:
            for token in vector:
                vector[token] /= magnitude
                
        return vector

    def add_memory(self, content_id: str, text: str, metadata: dict = None):
        vector = self._tokenize_and_vectorize(text)
        if not vector:
            return
            
        memory_node = {
            "id": content_id,
            "raw_text": text,
            "vector": vector,
            "metadata": metadata or {}
        }
        
        self.memories = [m for m in self.memories if m["id"] != content_id]
        self.memories.append(memory_node)
        self._save_store()
        log_info("SemanticMemory", f"Ingested semantic node: '{content_id}'")

    def query_semantic_closeness(self, query: str, limit: int = 3) -> list:
        query_vector = self._tokenize_and_vectorize(query)
        if not query_vector or not self.memories:
            return []
            
        results = []
        for node in self.memories:
            similarity = 0.0
            node_vector = node["vector"]
            
            for token, weight in query_vector.items():
                if token in node_vector:
                    similarity += weight * node_vector[token]
            
            if similarity > 0.05:
                results.append((similarity, node))
                
        results.sort(key=lambda x: x[0], reverse=True)
        return results[:limit]

# Global instance of local Semantic Database
semantic_db = SemanticMemoryEngine()