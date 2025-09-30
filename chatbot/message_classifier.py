import re
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessageClassifier:
    def __init__(self):
        # Define patterns for different message types
        self.greeting_patterns = [
            r'\b(hello|hi|hey|good morning|good afternoon|good evening)\b',
            r'^[a-z\s]*$'  # Simple lowercase messages (only if no other patterns match)
        ]
        
        self.pricing_patterns = [
            r'\b(price|cost|budget|expensive|cheap|affordable)\b',
            r'\b(how much|pricing|quote|estimate|fee|charge)\b',
            r'\b(payment|money|dollar|rupee|costs)\b',
            r'\b(rate|rates|tariff|tariffs)\b'
        ]
        
        self.support_patterns = [
            r'\b(help|support|issue|problem|error|bug|fix)\b',
            r'\b(not working|broken|down|trouble|difficulty)\b',
            r'\b(how to|how do|tutorial|guide|instructions)\b',
            r'\b(complaint|complaints|dissatisfied|unhappy)\b'
        ]
        
        self.general_patterns = [
            r'\b(thank|thanks|appreciate|grateful)\b',
            r'\b(information|info|details|more)\b',
            r'\b(contact|reach|get in touch)\b'
        ]

    def classify_message(self, message: str) -> Dict[str, Any]:
        """
        Classify incoming message and return appropriate response
        """
        message_lower = message.lower().strip()
        
        # Check for pricing inquiry first (most specific)
        if self._matches_patterns(message_lower, self.pricing_patterns):
            return {
                "type": "pricing",
                "response": "Our pricing starts from $99. Would you like the full details?",
                "confidence": 0.9
            }
        
        # Check for support request
        if self._matches_patterns(message_lower, self.support_patterns):
            return {
                "type": "support",
                "response": "I'm here to help. Could you share more details about the issue?",
                "confidence": 0.8
            }
        
        # Check for general inquiry
        if self._matches_patterns(message_lower, self.general_patterns):
            return {
                "type": "general",
                "response": "Thanks for your message! Our team will respond shortly.",
                "confidence": 0.7
            }
        
        # Check for greeting (more specific patterns only)
        if self._matches_patterns(message_lower, [r'\b(hello|hi|hey|good morning|good afternoon|good evening)\b']):
            return {
                "type": "greeting",
                "response": "Hello 👋 How can I help you today?",
                "confidence": 0.9
            }
        
        # Default response for unrecognized messages
        return {
            "type": "other",
            "response": "Thanks for your message! Our team will respond shortly.",
            "confidence": 0.5
        }

    def _matches_patterns(self, message: str, patterns: list) -> bool:
        """Check if message matches any of the given patterns"""
        for pattern in patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return True
        return False

    def get_enhanced_response(self, message: str, conversation_history: list = None) -> str:
        """
        Get enhanced response using LLaMA for complex messages
        """
        # For simple classified messages, use predefined responses
        classification = self.classify_message(message)
        
        if classification["confidence"] >= 0.8:
            return classification["response"]
        
        # For complex messages, we'll use LLaMA (handled in the main service)
        return None

# Global instance
message_classifier = MessageClassifier()
