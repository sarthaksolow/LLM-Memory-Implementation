from database import DatabaseManager
from embeddings import embedding_manager
from memory_extractor import MemoryExtractor
import config

class MemoryManager:
    """Manages the complete memory lifecycle: Create, Store, Search, Retrieve"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.extractor = MemoryExtractor()
        self.exchange_counter = {}  # Track exchanges per session
    
    # ==================
    # CREATE
    # ==================
    
    def should_extract_now(self, session_id: str) -> bool:
        """Determine if we should extract memories now based on exchange count"""
        if session_id not in self.exchange_counter:
            self.exchange_counter[session_id] = 0
        
        self.exchange_counter[session_id] += 1
        
        # Extract every N exchanges
        if self.exchange_counter[session_id] >= config.EXTRACT_EVERY_N_EXCHANGES:
            self.exchange_counter[session_id] = 0
            return True
        
        return False
    
    def create_memory(self, user_id: str, session_id: str, 
                     user_message: str, assistant_response: str) -> bool:
        """
        Extract and store memory from a conversation exchange
        
        Returns True if memory was created, False otherwise
        """
        # Check if we should extract now
        if not self.should_extract_now(session_id):
            return False
        
        print("🧠 Extracting memories...")
        
        # Extract memory using LLM
        extraction = self.extractor.extract_memory(user_message, assistant_response)
        
        if not extraction:
            print("   No significant memories found")
            return False
        
        # Generate embedding for the memory
        embedding = embedding_manager.generate_embedding(extraction['content'])
        
        # Store in LTM
        memory_id = self.db.store_ltm(
            user_id=user_id,
            content=extraction['content'],
            memory_type=extraction['memory_type'],
            importance=extraction['importance'],
            embedding=embedding
        )
        
        print(f"   ✅ Memory created: [{extraction['memory_type']}] {extraction['content'][:50]}...")
        print(f"   Importance: {extraction['importance']}/10")
        
        return True
    
    # ==================
    # SEARCH & RETRIEVE
    # ==================
    
    def retrieve_relevant_memories(self, user_id: str, query: str) -> list:
        """
        Search and retrieve relevant memories for a query
        
        Returns list of memories with relevance scores
        """
        # Generate query embedding
        query_embedding = embedding_manager.generate_embedding(query)
        
        # Semantic search in LTM
        memories = self.db.search_ltm(
            user_id=user_id,
            query_embedding=query_embedding,
            top_k=config.TOP_K_MEMORIES,
            min_similarity=config.MIN_SIMILARITY
        )
        
        if not memories:
            return []
        
        # Calculate relevance scores (combine similarity + importance)
        for memory in memories:
            relevance_score = self._calculate_relevance(
                similarity=memory['similarity'],
                importance=memory['importance']
            )
            memory['relevance_score'] = relevance_score
            
            # Update access tracking
            self.db.update_memory_access(memory['id'])
        
        # Sort by relevance score
        memories.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return memories
    
    def _calculate_relevance(self, similarity: float, importance: int) -> float:
        """
        Calculate relevance score combining similarity and importance
        
        Formula: relevance = (similarity * weight1) + (importance/10 * weight2)
        """
        normalized_importance = importance / 10.0
        
        relevance = (
            similarity * config.SIMILARITY_WEIGHT +
            normalized_importance * config.IMPORTANCE_WEIGHT
        )
        
        return relevance
    
    # ==================
    # MEMORY MANAGEMENT
    # ==================
    
    def get_user_memories(self, user_id: str) -> list:
        """Get all memories for a user"""
        return self.db.get_all_ltm(user_id)
    
    def delete_memory(self, memory_id: int):
        """Delete a specific memory"""
        self.db.delete_ltm(memory_id)
    
    def clear_user_data(self, user_id: str):
        """Clear all data for a user"""
        self.db.clear_user_data(user_id)
        if user_id in self.exchange_counter:
            del self.exchange_counter[user_id]
