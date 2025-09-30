import httpx
import os
import json
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = os.getenv("GROQ_API_URL", "https://api.groq.com/openai/v1/chat/completions")

# Vertex AI Tech Customer Support System Prompt
SYSTEM_PROMPT = """You are a helpful AI assistant for Vertex AI Tech. 

Answer the user's question naturally and helpfully. Be conversational and friendly."""

async def stream_groq_response(messages: list):
    url = GROQ_API_URL
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    
    # Add system prompt to the beginning of messages
    formatted_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": formatted_messages,
        "stream": True,
        "temperature": 0.7,
        "max_tokens": 500
    }

    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream("POST", url, headers=headers, json=payload) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    if line == "data: [DONE]":
                        break
                    yield line[6:]
