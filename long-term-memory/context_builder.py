from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import config

class ContextBuilder:
    """Build context window combining LTM, STM, and current query"""
    
    def build_context(self, ltm_memories: list, stm_messages: list, 
                     system_prompt: str = None) -> list:
        """
        Assemble the complete context for LLM
        
        Args:
            ltm_memories: Retrieved long-term memories
            stm_messages: Recent short-term messages
            system_prompt: Optional custom system prompt
            
        Returns:
            List of messages ready for LLM
        """
        context = []
        
        # 1. System prompt
        if not system_prompt:
            system_prompt = "You are a helpful AI assistant with long-term memory of the user. Use the provided memories to personalize your responses."
        
        context.append(SystemMessage(content=system_prompt))
        
        # 2. Long-term memories (if any)
        if ltm_memories:
            ltm_context = self._format_ltm_context(ltm_memories)
            context.append(SystemMessage(content=ltm_context))
        
        # 3. Short-term messages
        for msg in stm_messages:
            if msg.role == "user":
                context.append(HumanMessage(content=msg.content))
            else:
                context.append(AIMessage(content=msg.content))
        
        return context
    
    def _format_ltm_context(self, memories: list) -> str:
        """
        Format LTM memories with relevance-based emphasis
        
        Memories are weighted by relevance score to guide LLM attention
        """
        ltm_text = "=== Relevant Information About the User ===\n\n"
        
        for memory in memories:
            relevance = memory['relevance_score']
            content = memory['content']
            memory_type = memory['memory_type']
            
            # Determine emphasis level
            emphasis = self._get_emphasis_level(relevance)
            
            # Format with emphasis
            if emphasis == "high":
                ltm_text += f"🔴 IMPORTANT [{memory_type}]: {content}\n"
            elif emphasis == "medium":
                ltm_text += f"🟡 Note [{memory_type}]: {content}\n"
            else:
                ltm_text += f"⚪ [{memory_type}]: {content}\n"
        
        ltm_text += "\n=== Use this information to personalize your response ===\n"
        
        return ltm_text
    
    def _get_emphasis_level(self, relevance_score: float) -> str:
        """Determine emphasis level based on relevance score"""
        if relevance_score >= config.HIGH_RELEVANCE_THRESHOLD:
            return "high"
        elif relevance_score >= config.MEDIUM_RELEVANCE_THRESHOLD:
            return "medium"
        else:
            return "low"
    
    def get_context_stats(self, context: list) -> dict:
        """Get statistics about the assembled context"""
        total_messages = len(context)
        system_messages = sum(1 for msg in context if isinstance(msg, SystemMessage))
        user_messages = sum(1 for msg in context if isinstance(msg, HumanMessage))
        assistant_messages = sum(1 for msg in context if isinstance(msg, AIMessage))
        
        # Estimate token count (rough approximation: 1 token ≈ 4 characters)
        total_chars = sum(len(msg.content) for msg in context)
        estimated_tokens = total_chars // 4
        
        return {
            'total_messages': total_messages,
            'system_messages': system_messages,
            'user_messages': user_messages,
            'assistant_messages': assistant_messages,
            'estimated_tokens': estimated_tokens
        }
