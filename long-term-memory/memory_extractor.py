from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import json
import config

class MemoryExtractor:
    """Extract important information worth remembering using LLM"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=config.MODEL_NAME,
            openai_api_key=config.OPENROUTER_API_KEY,
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=0.3,  # Lower temperature for more consistent extraction
        )
        
        self.extraction_prompt = """You are a memory extraction system. Analyze the conversation and determine if it contains information worth remembering long-term.

Extract ONLY if the conversation contains:
- Personal information (name, age, location, occupation, etc.)
- User preferences or likes/dislikes
- Important facts the user shared
- Goals, plans, or decisions
- Significant context that would be useful in future conversations

DO NOT extract:
- Generic greetings or small talk
- Temporary/transient information
- Questions without answers
- Common knowledge or facts not specific to the user

Conversation:
User: {user_message}
Assistant: {assistant_response}

Respond ONLY with valid JSON in this exact format:
{{
    "should_remember": true/false,
    "memory_type": "personal_info/preference/fact/decision/goal",
    "content": "concise memory description (one sentence)",
    "importance": 1-10 (integer)
}}

If nothing is worth remembering, respond with:
{{"should_remember": false}}
"""
    
    def extract_memory(self, user_message: str, assistant_response: str) -> dict:
        """
        Extract memory from a conversation exchange
        
        Args:
            user_message: User's message
            assistant_response: Assistant's response
            
        Returns:
            dict with extraction results or None if nothing to remember
        """
        try:
            # Format prompt
            prompt = self.extraction_prompt.format(
                user_message=user_message,
                assistant_response=assistant_response
            )
            
            # Get extraction from LLM
            response = self.llm.invoke([HumanMessage(content=prompt)])
            
            # Parse JSON response
            result = self._parse_json_response(response.content)
            
            # Validate extraction
            if result and result.get('should_remember', False):
                # Ensure all required fields
                if all(k in result for k in ['memory_type', 'content', 'importance']):
                    # Clamp importance to 1-10
                    result['importance'] = max(1, min(10, result['importance']))
                    return result
            
            return None
            
        except Exception as e:
            print(f"⚠️  Memory extraction error: {e}")
            return None
    
    def _parse_json_response(self, response: str) -> dict:
        """Parse JSON from LLM response, handling various formats"""
        try:
            # Try direct parsing
            return json.loads(response)
        except:
            # Try to extract JSON from markdown code blocks
            if '```json' in response:
                json_str = response.split('```json')[1].split('```')[0].strip()
                return json.loads(json_str)
            elif '```' in response:
                json_str = response.split('```')[1].split('```')[0].strip()
                return json.loads(json_str)
            else:
                # Try to find JSON object in text
                start = response.find('{')
                end = response.rfind('}') + 1
                if start != -1 and end > start:
                    return json.loads(response[start:end])
        
        return None
    
    def batch_extract(self, exchanges: list) -> list:
        """
        Extract memories from multiple exchanges
        
        Args:
            exchanges: List of (user_msg, assistant_msg) tuples
            
        Returns:
            List of extracted memories
        """
        memories = []
        for user_msg, assistant_msg in exchanges:
            memory = self.extract_memory(user_msg, assistant_msg)
            if memory:
                memories.append(memory)
        
        return memories
