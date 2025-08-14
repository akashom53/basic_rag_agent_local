from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from typing import List, Dict, Any
import json
import re
from ..core.config import settings

class OpenRouterLLMProvider:
	def __init__(self, api_key: str = None, model: str = None, base_url: str = None, temperature: float = 0.1):
		api_key = api_key or settings.openrouter_api_key
		model = model or settings.openrouter_model
		base_url = base_url or settings.openrouter_base_url
		self.llm = ChatOpenAI(
			openai_api_key=api_key,
			openai_api_base=base_url,
			model=model,
			temperature=temperature
		)
	
	def generate(self, messages: List, tools: List = None) -> str:
		"""Generate response using OpenRouter"""
		try:
			response = self.llm.invoke(messages)
			return str(response)
		except Exception as e:
			print(f"❌ OpenRouter error: {e}")
			return f"Sorry, I encountered an error: {str(e)}"
	
	def classify_intent(self, messages: List) -> Dict[str, Any]:
		"""Specialized method for intent classification with JSON output validation"""
		try:
			if messages and hasattr(messages[-1], 'content'):
				last_message = messages[-1]
				enhanced_content = f"{last_message.content}\n\nIMPORTANT: Respond with ONLY valid JSON. No additional text, explanations, or formatting."
				enhanced_messages = messages[:-1] + [type(last_message)(content=enhanced_content)]
			else:
				enhanced_messages = messages
			
			response = self.llm.invoke(enhanced_messages)
			response_text = str(response).strip()
			
			json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
			if json_match:
				try:
					result = json.loads(json_match.group())
					return result
				except json.JSONDecodeError:
					print(f"❌ Failed to parse OpenRouter response as JSON: {response_text}")
					return {}
			
			print(f"⚠️ No JSON found in OpenRouter response: {response_text}")
			return {}
			
		except Exception as e:
			print(f"❌ OpenRouter intent classification failed: {e}")
			return {}
	
	def is_available(self) -> bool:
		"""Check if OpenRouter is available"""
		try:
			test_message = [HumanMessage(content="Hello")]
			response = self.llm.invoke(test_message)
			return bool(response and len(str(response)) > 0)
		except Exception as e:
			print(f"❌ OpenRouter availability check failed: {e}")
			return False
