import httpx
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Vertex AI Tech Customer Support System Prompt
SYSTEM_PROMPT = """You are a helpful AI assistant for Vertex AI Tech, a company that builds custom apps, websites, and advanced clones.

Your role:
- Help potential clients understand our services
- Gather information about their project requirements
- Be friendly, professional, and conversational
- Guide them through our service offerings

Our services include:
- App & Website Cloning (Slack, Netflix, TikTok, SoundCloud, E-commerce clones)
- Enhanced Features (real-time chat, AI recommendations, payment gateways, etc.)
- AI & Data Science Solutions
- Web & App Development
- AI Consulting & Training

Keep responses concise (under 200 words) and always be helpful. If they ask about pricing or want to finalize their project, let them know our team will reach out soon."""

async def get_llama_response(conversation_history: list, user_message: str) -> str:
    """Get response from LLaMA model via Groq API"""
    try:
        # Get GROQ API key
        groq_api_key = os.getenv("GROQ_API_KEY")
        groq_api_url = os.getenv("GROQ_API_URL", "https://api.groq.com/openai/v1/chat/completions")
        
        if not groq_api_key:
            logger.error("GROQ_API_KEY not found in environment variables")
            return "I'm sorry, I'm having trouble connecting to my AI service right now. Please try again later."
        
        url = groq_api_url
        headers = {"Authorization": f"Bearer {groq_api_key}"}
        
        # Prepare messages for LLaMA
        messages = []
        
        # Add conversation history
        for msg in conversation_history:
            if msg.get("role") == "client":
                messages.append({"role": "user", "content": msg.get("message", "")})
            elif msg.get("role") == "assistant":
                messages.append({"role": "assistant", "content": msg.get("message", "")})
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # Add system prompt
        formatted_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
        
        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": formatted_messages,
            "stream": False,
            "temperature": 0.7,
            "max_tokens": 200
        }
        
        logger.info(f"Calling LLaMA API with {len(formatted_messages)} messages")
        
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                assistant_reply = data["choices"][0]["message"]["content"]
                logger.info(f"Got LLaMA response: {assistant_reply[:100]}...")
                return assistant_reply
            else:
                logger.error(f"LLaMA API error: {response.status_code} - {response.text}")
                return "I'm sorry, I'm having trouble processing your message right now. Please try again later."
                
    except Exception as e:
        logger.error(f"Error getting LLaMA response: {str(e)}")
        return "I'm sorry, I encountered an error while processing your message. Please try again later."

def check_for_pricing_keywords(message: str) -> bool:
    """Check if message contains pricing-related keywords"""
    pricing_keywords = [
        "price", "cost", "budget", "expensive", "cheap", "affordable",
        "how much", "pricing", "quote", "estimate", "fee", "charge",
        "payment", "money", "dollar", "rupee", "costs"
    ]
    
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in pricing_keywords)

def check_for_completion_keywords(message: str) -> bool:
    """Check if message contains project completion keywords"""
    completion_keywords = [
        "finalize", "complete", "done", "finished", "ready", "proceed",
        "start project", "begin", "go ahead", "confirm", "approve",
        "that's all", "that's it", "nothing else", "perfect", "sounds good"
    ]
    
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in completion_keywords)
