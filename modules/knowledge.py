import os
import json
from datetime import datetime
from modules.logger import log_info, log_error

GRAPH_PATH = os.path.join("data", "knowledge_graph.json")

def initialize_knowledge_graph():
    """Ensures the knowledge database registry exists on disk."""
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists(GRAPH_PATH):
        default_graph = {
            "documents": {},  # Raw file logs / verbatim text captures
            "entities": {}    # Core facts and structural research linkages
        }
        try:
            with open(GRAPH_PATH, "w") as f:
                json.dump(default_graph, f, indent=4)
            log_info("KnowledgeEngine", "Seeded empty Unified Knowledge Graph database.")
        except Exception as e:
            log_error("KnowledgeEngine", f"Failed seeding graph: {e}")

def load_graph() -> dict:
    """Loads the active unified knowledge matrix from storage."""
    initialize_knowledge_graph()
    try:
        with open(GRAPH_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        log_error("KnowledgeEngine", f"Error loading graph layout: {e}")
        return {"documents": {}, "entities": {}}

def save_graph(graph_data: dict):
    """Commits changes securely back to the knowledge graph ledger."""
    try:
        with open(GRAPH_PATH, "w") as f:
            json.dump(graph_data, f, indent=4)
    except Exception as e:
        log_error("KnowledgeEngine", f"Error saving graph state: {e}")

def ingest_document_verbatim(doc_title: str, raw_content: str) -> str:
    """
    Ingests source documents under a strict preservation rule: 
    Stores and reads text exactly as provided without altering or modifying content.
    """
    log_info("KnowledgeEngine", f"Verbatim ingestion routine triggered for document: '{doc_title}'")
    graph = load_graph()
    
    # Store text exactly as provided, preserving every character and space
    graph["documents"][doc_title.strip()] = {
        "content": raw_content,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "character_count": len(raw_content)
    }
    
    save_graph(graph)
    return f"Document '{doc_title}' safely indexed verbatim into Knowledge Engine. Structure preserved."

def query_knowledge_engine(search_term: str) -> str:
    """
    Simultaneously crawls both documents and entities to retrieve 
    unified context from a single search query.
    """
    graph = load_graph()
    term_lower = search_term.lower().strip()
    
    document_matches = []
    entity_matches = []
    
    # Scan raw document records
    for title, doc_data in graph["documents"].items():
        if term_lower in title.lower() or term_lower in doc_data["content"].lower():
            document_matches.append(title)
            
    # Scan structured memory attributes
    for entity, entity_val in graph["entities"].items():
        if term_lower in entity.lower() or term_lower in str(entity_val).lower():
            entity_matches.append(f"{entity} -> {entity_val}")
            
    if not document_matches and not entity_matches:
        return f"No records matching '{search_term}' found across the knowledge graph."
        
    output = f"\n=== KNOWLEDGE GRAPH SEARCH RESULTS FOR: '{search_term}' ===\n"
    if document_matches:
        output += "\n[MATCHED VERBATIM DOCUMENTS]\n"
        for doc in document_matches:
            output += f"  - {doc}\n"
    if entity_matches:
        output += "\n[MATCHED KEY-VALUE ENTITIES]\n"
        for ent in entity_matches:
            output += f"  - {ent}\n"
    output += "="*55+"\n"
    return output