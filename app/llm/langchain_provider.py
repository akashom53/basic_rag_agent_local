from langchain_ollama import OllamaLLM
from langchain_core.messages import HumanMessage, SystemMessage
from typing import List, Dict, Any
import json
import re

class LangChainLLMProvider:
    def __init__(self, model_name: str = "qwen2.5:3b-instruct", num_gpu: int = None):
        # Extract the actual model name if it starts with 'ollama:'
        if model_name.startswith('ollama:'):
            model_name = model_name.replace('ollama:', '')
        
        self.model_name = model_name
        
        # Configure OllamaLLM with explicit host and GPU layer settings
        llm_kwargs = {
            "model": model_name,
            "base_url": "http://ollama:11434"  # Explicitly set container host
        }
        if num_gpu is not None:
            llm_kwargs["options"] = {"num_gpu": num_gpu}
        
        self.llm = OllamaLLM(**llm_kwargs)
    
    def generate(self, messages: List, tools: List = None) -> str:
        """Generate response using LangChain Ollama integration"""
        try:
            if tools:
                # If tools are provided, use structured output
                response = self.llm.invoke(messages)
            else:
                # Simple text generation
                response = self.llm.invoke(messages)
            
            return response
        except Exception as e:
            print(f"❌ LLM error: {e}")
            return f"Sorry, I encountered an error: {str(e)}"
    
    def classify_intent(self, messages: List) -> Dict[str, Any]:
        """Specialized method for intent classification with JSON output validation"""
        try:
            # Add JSON formatting instruction to the last message
            if messages and hasattr(messages[-1], 'content'):
                last_message = messages[-1]
                enhanced_content = f"{last_message.content}\n\nIMPORTANT: Respond with ONLY valid JSON. No additional text, explanations, or formatting."
                enhanced_messages = messages[:-1] + [type(last_message)(content=enhanced_content)]
            else:
                enhanced_messages = messages
            
            # Get LLM response
            response = self.llm.invoke(enhanced_messages)
            response_text = str(response).strip()
            
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    result = json.loads(json_match.group())
                    return result
                except json.JSONDecodeError:
                    print(f"❌ Failed to parse LLM response as JSON: {response_text}")
                    return {}
            
            # If no JSON found, return empty dict
            print(f"⚠️ No JSON found in LLM response: {response_text}")
            return {}
            
        except Exception as e:
            print(f"❌ LLM intent classification failed: {e}")
            return {}
    
    def is_available(self) -> bool:
        """Check if Ollama is available"""
        try:
            # Simple connectivity test to ollama container
            import requests
            response = requests.get("http://ollama:11434/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Ollama availability check failed: {e}")
            return False