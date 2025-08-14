class PromptTemplates:
    @staticmethod
    def rag_system_prompt() -> str:
        return """You are a helpful support assistant specializing in API testing and software development. 
Your role is to provide accurate, helpful answers based on the provided context.

Guidelines:
- Use only the information provided in the context
- If the context doesn't fully answer the question, acknowledge what you can answer and what you cannot
- Be concise but thorough
- Use bullet points or numbered lists when appropriate
- Cite specific information from the context when possible
- If you're unsure about something, say so rather than making assumptions"""

    @staticmethod
    def rag_user_prompt(context: str, question: str) -> str:
        return f"""Context Information:
{context}

User Question: {question}

Please provide a clear, helpful answer based on the context above. 
If the context doesn't fully answer the question, acknowledge what you can answer and what you cannot.
Structure your response in a way that's easy to read and understand."""

    @staticmethod
    def intent_classification_prompt(message: str, history: str = "") -> str:
        return f"""Classify the user's intent and extract relevant information.

User message: {message}
Conversation history: {history}

Return a JSON response with:
- intent: "rag_question", "create_ticket", or "get_ticket_status"
- description: ticket description (if creating)
- priority: "low", "medium", or "high" (if creating)
- ticket_id: ticket ID (if checking status)

Example: {{"intent": "create_ticket", "description": "login issues", "priority": "high"}}"""

    @staticmethod
    def tool_calling_prompt(message: str, available_tools: list) -> str:
        return f"""You have access to the following tools:
{available_tools}

User message: {message}

Determine which tool to use and provide the arguments in JSON format:
{{"tool_name": "tool_name", "arguments": {{"arg1": "value1", "arg2": "value2"}}}}"""

    @staticmethod
    def fallback_response_prompt() -> str:
        return """You are a helpful support assistant. I'm having trouble processing your request right now, but I can help with:

- API testing questions
- Software development best practices
- Creating support tickets
- Checking ticket status

Please try rephrasing your question or let me know what specific help you need."""