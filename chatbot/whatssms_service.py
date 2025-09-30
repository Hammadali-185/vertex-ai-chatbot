import requests
import logging
import json
import httpx
import asyncio
import re
from typing import Optional, Dict, Any
from datetime import datetime
from db import get_database
from models import WhatsAppConversation, ConversationMessage
from llama_helper import get_llama_response, check_for_pricing_keywords, check_for_completion_keywords
from message_classifier import message_classifier
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def format_phone_number(phone_number: str) -> str:
    """
    Format phone number to WhatsSMS.io compatible format
    Handles various input formats and converts to 92XXXXXXXXXX format
    """
    if not phone_number:
        return phone_number
    
    # Remove all non-digit characters
    cleaned = re.sub(r'\D', '', phone_number)
    
    # Handle different formats
    if cleaned.startswith('92'):
        # Already has country code
        return cleaned
    elif cleaned.startswith('0'):
        # Remove leading 0 and add country code
        return '92' + cleaned[1:]
    elif len(cleaned) == 10:
        # 10 digit number, add country code
        return '92' + cleaned
    elif len(cleaned) == 11 and cleaned.startswith('3'):
        # 11 digit number starting with 3, add country code
        return '92' + cleaned
    else:
        # Return as is if we can't determine format
        logger.warning(f"Could not format phone number: {phone_number} -> {cleaned}")
        return cleaned

class WhatsSMSService:
    def __init__(self):
        # WhatsSMS API credentials
        self.api_url = os.getenv("WHATSAPP_API_URL", "https://app.whatssms.io/api")
        self.secret = os.getenv("ACCESS_TOKEN")
        self.account_id = os.getenv("WHATSAPP_ACCOUNT_ID")
        self.bot_phone = os.getenv("BOT_PHONE_NUMBER")
        self.team_number = os.getenv("TEAM_NUMBER")
        
        # Validate required environment variables
        if not all([self.secret, self.account_id, self.bot_phone, self.team_number]):
            raise ValueError("Missing required environment variables: ACCESS_TOKEN, WHATSAPP_ACCOUNT_ID, BOT_PHONE_NUMBER, TEAM_NUMBER")
        
        # WhatsSMS API endpoints
        self.send_message_url = f"{self.api_url}/send/whatsapp"
        
        logger.info("WhatsSMS service initialized successfully")

    def normalize_to_e164(self, phone_number: str) -> str:
        """
        Normalize phone number to E.164 format (+923001112233)
        
        Examples:
        - +923001112233 → +923001112233 (keep as is)
        - 923001112233 → +923001112233 (add +)
        - 03001112233 → +923001112233 (convert to +92)
        - 3001112233 → +923001112233 (convert to +92)
        - Any other case → strip non-digits, prepend +
        """
        if not phone_number:
            return phone_number
            
        # Remove all non-digit characters
        digits = ''.join(filter(str.isdigit, phone_number))
        
        # Handle different cases based on digits only
        if digits.startswith('92') and len(digits) >= 12:
            # Has country code, add +
            return f"+{digits}"
        elif digits.startswith('0') and len(digits) == 11:
            # Pakistani number with leading 0, convert to +92
            return f"+92{digits[1:]}"
        elif len(digits) == 10:
            # 10 digit number, assume Pakistani and add +92
            return f"+92{digits}"
        else:
            # Any other case, strip non-digits and prepend +
            return f"+{digits}"

    def format_phone_number(self, phone_number: str) -> str:
        """Format phone number for WhatsApp (legacy function - use normalize_to_e164 instead)"""
        # Remove all non-digit characters
        digits = ''.join(filter(str.isdigit, phone_number))
        
        # Add country code if not present
        if not phone_number.startswith('+'):
            # Assume Pakistan country code if not specified
            if len(digits) == 10:
                digits = '92' + digits
            elif len(digits) == 11 and digits.startswith('0'):
                digits = '92' + digits[1:]
        
        return digits

    def send_whatsapp_message(self, client_phone: str, message: str) -> bool:
        """Send WhatsApp message via WhatsSMS API"""
        try:
            # Normalize recipient to E.164 format
            recipient = self.normalize_to_e164(client_phone)
            
            # WhatsSMS API payload
            data = {
                "secret": self.secret,
                "account": self.account_id,
                "recipient": recipient,
                "type": "text",
                "message": message
            }
            
            # Log before sending
            logger.info(f"📤 Sending WhatsApp message:")
            logger.info(f"   Bot Account ID: {self.account_id}")
            logger.info(f"   Recipient: {recipient}")
            logger.info(f"   Message: {message}")
            logger.info(f"   Full Payload:")
            logger.info(json.dumps(data, indent=2))
            
            # Send request
            response = requests.post(
                self.send_message_url,
                data=data,  # multipart/form-data
                timeout=30
            )
            
            # Log after sending
            logger.info(f"📥 Response Status Code: {response.status_code}")
            logger.info(f"📥 Full Response Text: {response.text}")
            
            # Error handling
            if response.status_code == 200:
                try:
                    response_json = response.json()
                    if response_json.get("status") == 200:
                        logger.info(f"✅ WhatsApp message sent successfully to {recipient}")
                        return True
                    else:
                        logger.error(f"❌ WhatsSMS rejected request for {recipient}")
                        logger.error(f"❌ Payload was: {json.dumps(data, indent=2)}")
                        logger.error(f"❌ Response: {response.text}")
                        return False
                except (ValueError, KeyError):
                    logger.error(f"❌ Invalid JSON response for {recipient}")
                    logger.error(f"❌ Payload was: {json.dumps(data, indent=2)}")
                    logger.error(f"❌ Response: {response.text}")
                    return False
            else:
                logger.error(f"❌ HTTP error for {recipient}")
                logger.error(f"❌ Payload was: {json.dumps(data, indent=2)}")
                logger.error(f"❌ Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Unexpected error sending to {client_phone}: {str(e)}")
            return False

    async def get_or_create_conversation(self, phone_number: str) -> WhatsAppConversation:
        """Get existing conversation or create new one"""
        try:
            db = await get_database()
            conversations_collection = db["whatsapp_conversations"]
            
            # Normalize before lookup
            normalized_phone = self.normalize_to_e164(phone_number)
            conversation_doc = await conversations_collection.find_one({"_id": normalized_phone})
            
            if conversation_doc:
                # Convert to WhatsAppConversation model
                conversation = WhatsAppConversation(
                    id=conversation_doc["_id"],
                    client_name=conversation_doc.get("client_name"),
                    phone_number=conversation_doc["phone_number"],
                    conversation=[ConversationMessage(**msg) for msg in conversation_doc.get("conversation", [])],
                    status=conversation_doc.get("status", "pending"),
                    messages_used=conversation_doc.get("messages_used", 0),
                    created_at=conversation_doc.get("created_at", datetime.utcnow()),
                    updated_at=conversation_doc.get("updated_at", datetime.utcnow())
                )
                return conversation
            else:
                # Create new conversation
                new_conversation = WhatsAppConversation(
                    phone_number=normalized_phone,
                    conversation=[],
                    status="pending",
                    messages_used=0
                )
                
                # Save to database
                conversation_dict = new_conversation.dict(by_alias=True)
                conversation_dict["_id"] = normalized_phone  # Always save normalized
                await conversations_collection.insert_one(conversation_dict)
                
                logger.info(f"Created new conversation for {normalized_phone}")
                return new_conversation
                
        except Exception as e:
            logger.error(f"Error getting/creating conversation: {str(e)}")
            raise e

    async def save_conversation(self, conversation: WhatsAppConversation):
        """Save conversation to MongoDB"""
        try:
            db = await get_database()
            conversations_collection = db["whatsapp_conversations"]
            
            # Update conversation
            conversation.updated_at = datetime.utcnow()
            conversation_dict = conversation.dict(by_alias=True)
            conversation_dict["_id"] = conversation.phone_number
            
            await conversations_collection.replace_one(
                {"_id": conversation.phone_number},
                conversation_dict,
                upsert=True
            )
            
            logger.info(f"Saved conversation for {conversation.phone_number}")
            
        except Exception as e:
            logger.error(f"Error saving conversation: {str(e)}")
            raise e

    async def notify_team(self, message: str, phone_number: str = None, client_name: str = None, project_details: str = None):
        """Send notification to team WhatsApp number with detailed client information"""
        try:
            team_message = f"🚨 TEAM ALERT 🚨\n\n{message}"
            
            if client_name:
                team_message += f"\n👤 Client Name: {client_name}"
            
            if phone_number:
                team_message += f"\n📱 Client Phone: {phone_number}"
            
            if project_details:
                team_message += f"\n💼 Project Details: {project_details}"
            
            team_message += f"\n\n🤖 Bot Response: Please reach out to this client for further discussion about their project requirements."
            
            success = self.send_whatsapp_message(self.team_number, team_message)
            
            if success:
                logger.info(f"Team notification sent successfully to {self.team_number}")
            else:
                logger.error(f"Failed to send team notification to {self.team_number}")
                
            return success
            
        except Exception as e:
            logger.error(f"Error sending team notification: {str(e)}")
            return False

    async def handle_incoming_message(self, phone_number: str, message_content: str, account: str = None, timestamp: int = None) -> bool:
        """Handle incoming WhatsApp message with full workflow"""
        try:
            logger.info(f"Processing message from {phone_number}: {message_content}")
            
            # Get or create conversation
            conversation = await self.get_or_create_conversation(phone_number)
            
            # Add client message to conversation
            client_message = ConversationMessage(
                role="client",
                message=message_content
            )
            conversation.conversation.append(client_message)
            conversation.messages_used += 1
            
            # Determine response based on workflow
            response_message = ""
            
            # Use message classifier for quick responses
            classification = message_classifier.classify_message(message_content)
            
            # Check if this is the first message and no name is set
            if not conversation.client_name and conversation.messages_used == 1:
                response_message = "Hello! What is your name, sir?"
                conversation.client_name = "Unknown"  # Will be updated when they provide name
                
            # Check if they provided their name (second message)
            elif not conversation.client_name or conversation.client_name == "Unknown":
                conversation.client_name = message_content.strip()
                response_message = f"Nice to meet you, {conversation.client_name}! I'm here to help you with your project requirements. What type of app or website are you looking to build?"
                
            # Use classified response for high confidence classifications
            elif classification["confidence"] >= 0.8:
                response_message = classification["response"]
                
                # Notify team for pricing inquiries
                if classification["type"] == "pricing":
                    await self.notify_team(
                        f"💰 PRICING INQUIRY\n\nMessage: {message_content}",
                        phone_number,
                        conversation.client_name,
                        "Client is asking about pricing for our services"
                    )
                
            # Check if client wants team to reach out
            elif any(keyword in message_content.lower() for keyword in [
                "team reach out", "contact me", "call me", "reach out", "team contact", 
                "speak with team", "talk to team", "team call", "contact team", "team reach"
            ]):
                response_message = "Perfect! I'll have our team reach out to you shortly to discuss your project requirements in detail."
                
                # Notify team that client wants to be contacted
                await self.notify_team(
                    f"📞 CLIENT WANTS TEAM CONTACT\n\nMessage: {message_content}",
                    phone_number,
                    conversation.client_name,
                    "Client specifically requested team to reach out for project discussion"
                )
                
            # Check for completion keywords
            elif check_for_completion_keywords(message_content):
                conversation.status = "finalized"
                response_message = "Great! Your project description has been saved. Our team will reach out to you soon."
                
                # Notify team with full conversation
                conversation_summary = self.format_conversation_summary(conversation)
                await self.notify_team(
                    f"✅ PROJECT FINALIZED\n\n{conversation_summary}",
                    phone_number,
                    conversation.client_name,
                    "Client has finalized their project requirements"
                )
                
            # Check message limit
            elif conversation.messages_used >= 20:
                response_message = "You've reached the message limit. Our team will contact you shortly."
                await self.notify_team(
                    f"⚠️ MESSAGE LIMIT REACHED\n\nMessages used: {conversation.messages_used}",
                    phone_number,
                    conversation.client_name,
                    "Client has reached the message limit and needs team follow-up"
                )
                
            else:
                # Get LLaMA response for complex conversations
                conversation_history = [
                    {"role": msg.role, "message": msg.message} 
                    for msg in conversation.conversation[:-1]  # Exclude the current message
                ]
                response_message = await get_llama_response(conversation_history, message_content)
            
            # Add assistant response to conversation
            assistant_message = ConversationMessage(
                role="assistant",
                message=response_message
            )
            conversation.conversation.append(assistant_message)
            
            # Save conversation
            await self.save_conversation(conversation)
            
            # Send response via WhatsApp
            success = self.send_whatsapp_message(phone_number, response_message)
            
            if success:
                logger.info(f"Successfully handled message from {phone_number}")
            else:
                logger.error(f"Failed to send response to {phone_number}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error handling incoming message: {str(e)}")
            return False

    def format_conversation_summary(self, conversation: WhatsAppConversation) -> str:
        """Format conversation for team notification"""
        summary = f"Client: {conversation.client_name}\n"
        summary += f"Phone: {conversation.phone_number}\n"
        summary += f"Messages: {conversation.messages_used}\n"
        summary += f"Status: {conversation.status}\n\n"
        summary += "Conversation:\n"
        
        for msg in conversation.conversation:
            role_emoji = "👤" if msg.role == "client" else "🤖"
            summary += f"{role_emoji} {msg.role.title()}: {msg.message}\n"
        
        return summary

# Global instance
whatssms_service = WhatsSMSService()
