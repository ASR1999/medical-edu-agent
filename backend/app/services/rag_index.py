"""
RAG (Retrieval-Augmented Generation) Index System for EHR Data

This module provides vector-based semantic search over patient EHR data using:
- ChromaDB for local vector storage (privacy-preserving, no external API calls)
- Sentence-Transformers for embedding generation
- Recursive chunking to handle nested JSON structures
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from chromadb import Client, Settings
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer

from app.config import RAG_DIR, EMBEDDING_MODEL, RAG_CHUNK_SIZE, RAG_CHUNK_OVERLAP

logger = logging.getLogger(__name__)


class EmbeddingFunction:
    """Wrapper for sentence-transformers to work with ChromaDB"""
    
    def __init__(self, model_name: str = EMBEDDING_MODEL):
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        logger.info(f"Embedding model loaded. Dimension: {self.model.get_sentence_embedding_dimension()}")
    
    def __call__(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of texts"""
        embeddings = self.model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return embeddings.tolist()


class RAGIndex:
    """
    RAG Index for patient EHR data.
    
    Features:
    - Per-patient collections for data isolation
    - Hierarchical JSON flattening with path tracking
    - Semantic search with relevance scoring
    - Metadata tagging for provenance
    """
    
    def __init__(self, persist_dir: str = RAG_DIR, model_name: str = EMBEDDING_MODEL):
        """Initialize the RAG index with ChromaDB and embedding model"""
        os.makedirs(persist_dir, exist_ok=True)
        self.persist_dir = persist_dir
        self.embedding_function = EmbeddingFunction(model_name)
        
        # Initialize ChromaDB client with persistence
        self.client = Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=persist_dir,
            anonymized_telemetry=False
        ))
        
        logger.info(f"RAG Index initialized with persist_dir: {persist_dir}")
    
    def _flatten_json_to_chunks(
        self, 
        data: Any, 
        path: str = "", 
        parent_context: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Recursively flatten nested JSON into searchable text chunks with metadata.
        
        Args:
            data: The data structure to flatten
            path: Current path in the JSON hierarchy (e.g., "conditions[0].name")
            parent_context: Context from parent nodes for better semantic meaning
            
        Returns:
            List of dicts with 'text', 'path', and 'type' keys
        """
        chunks = []
        
        if isinstance(data, dict):
            # For dictionaries, recurse into each key
            for key, value in data.items():
                new_path = f"{path}.{key}" if path else key
                # Build context from current level
                context = f"{parent_context} {key}" if parent_context else key
                chunks.extend(self._flatten_json_to_chunks(value, new_path, context))
                
        elif isinstance(data, list):
            # For lists, index each element
            for i, item in enumerate(data):
                new_path = f"{path}[{i}]"
                chunks.extend(self._flatten_json_to_chunks(item, new_path, parent_context))
                
        else:
            # Leaf node: create a searchable chunk
            if data is not None and str(data).strip():
                # Create rich text representation
                text = f"{parent_context}: {data}" if parent_context else str(data)
                
                # Determine data type for metadata
                data_type = "unknown"
                if "condition" in path.lower():
                    data_type = "condition"
                elif "medication" in path.lower():
                    data_type = "medication"
                elif "lab" in path.lower() or "test" in path.lower():
                    data_type = "lab_result"
                elif "note" in path.lower():
                    data_type = "clinical_note"
                elif "personal" in path.lower():
                    data_type = "demographics"
                
                chunks.append({
                    "text": text,
                    "path": path,
                    "type": data_type,
                    "value": str(data)
                })
        
        return chunks
    
    def _get_collection_name(self, patient_id: str) -> str:
        """Generate a safe collection name for a patient"""
        # ChromaDB collection names must be alphanumeric + underscore/hyphen
        safe_id = patient_id.replace(" ", "_").replace("@", "_at_")
        return f"ehr_patient_{safe_id}"
    
    def index_patient(self, patient_id: str, ehr_data: Dict[str, Any]) -> None:
        """
        Index a patient's EHR data into the vector store.
        
        Args:
            patient_id: Unique patient identifier
            ehr_data: Complete EHR data dictionary
        """
        try:
            collection_name = self._get_collection_name(patient_id)
            
            # Delete existing collection if present (for re-indexing)
            try:
                self.client.delete_collection(collection_name)
                logger.info(f"Deleted existing collection: {collection_name}")
            except:
                pass
            
            # Create new collection
            collection = self.client.create_collection(
                name=collection_name,
                embedding_function=self.embedding_function,
                metadata={"patient_id": patient_id, "indexed_at": datetime.utcnow().isoformat()}
            )
            
            # Flatten EHR data into chunks
            chunks = self._flatten_json_to_chunks(ehr_data)
            
            if not chunks:
                logger.warning(f"No chunks generated for patient {patient_id}")
                return
            
            # Prepare data for ChromaDB
            documents = [chunk["text"] for chunk in chunks]
            metadatas = [
                {
                    "patient_id": patient_id,
                    "path": chunk["path"],
                    "type": chunk["type"],
                    "value": chunk["value"][:500]  # Limit metadata size
                }
                for chunk in chunks
            ]
            ids = [f"{patient_id}_{i}" for i in range(len(chunks))]
            
            # Add to collection in batches to avoid memory issues
            batch_size = 100
            for i in range(0, len(documents), batch_size):
                collection.add(
                    documents=documents[i:i+batch_size],
                    metadatas=metadatas[i:i+batch_size],
                    ids=ids[i:i+batch_size]
                )
            
            logger.info(f"Indexed {len(chunks)} chunks for patient {patient_id}")
            
        except Exception as e:
            logger.error(f"Error indexing patient {patient_id}: {e}")
            raise
    
    def search(
        self, 
        patient_id: str, 
        query: str, 
        k: int = 5,
        filter_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Semantic search over a patient's EHR data.
        
        Args:
            patient_id: Patient to search
            query: Natural language query
            k: Number of results to return
            filter_type: Optional filter by data type (condition, medication, lab_result, etc.)
            
        Returns:
            List of dicts with 'text', 'metadata', 'score', and 'distance' keys
        """
        try:
            collection_name = self._get_collection_name(patient_id)
            
            # Get collection
            try:
                collection = self.client.get_collection(
                    name=collection_name,
                    embedding_function=self.embedding_function
                )
            except:
                logger.warning(f"Collection not found for patient {patient_id}. Indexing may be needed.")
                return []
            
            # Build filter if specified
            where_filter = None
            if filter_type:
                where_filter = {"type": filter_type}
            
            # Perform search
            results = collection.query(
                query_texts=[query],
                n_results=k,
                where=where_filter
            )
            
            # Format results
            formatted_results = []
            if results and results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    formatted_results.append({
                        "text": doc,
                        "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                        "distance": results['distances'][0][i] if results['distances'] else 0.0,
                        "score": 1.0 - results['distances'][0][i] if results['distances'] else 1.0,  # Convert distance to similarity
                        "id": results['ids'][0][i] if results['ids'] else ""
                    })
            
            logger.info(f"Search for patient {patient_id} returned {len(formatted_results)} results")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching for patient {patient_id}: {e}")
            return []
    
    def delete_patient_index(self, patient_id: str) -> bool:
        """Delete a patient's entire index"""
        try:
            collection_name = self._get_collection_name(patient_id)
            self.client.delete_collection(collection_name)
            logger.info(f"Deleted index for patient {patient_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting index for patient {patient_id}: {e}")
            return False
    
    def list_indexed_patients(self) -> List[str]:
        """List all patients with indexed data"""
        try:
            collections = self.client.list_collections()
            patients = []
            for col in collections:
                if col.name.startswith("ehr_patient_"):
                    patient_id = col.name.replace("ehr_patient_", "").replace("_", " ")
                    patients.append(patient_id)
            return patients
        except Exception as e:
            logger.error(f"Error listing indexed patients: {e}")
            return []


# Singleton instance
_rag_instance = None

def get_rag_index() -> RAGIndex:
    """Get or create the singleton RAG index instance"""
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = RAGIndex()
    return _rag_instance

