from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from crud import create_message, get_last_messages, create_lead, create_support_ticket
from schemas import MessageCreate, LeadCreate, SupportTicketCreate, LeadOut, SupportTicketOut
from utils import SYSTEM_PROMPT, GROQ_API_KEY
from whatssms_service import whatssms_service
import json
import logging
import os
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def handle_message_async(phone_number: str, message: str):
    """Handle incoming message asynchronously"""
    try:
        response = await whatssms_service.handle_incoming_message(phone_number, message)
        logger.info(f"Bot response for {phone_number}: {response}")
    except Exception as e:
        logger.error(f"Error in async message handler: {str(e)}")

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
async def chat(user_msg: MessageCreate):
    # 1. Save user message
    await create_message(user_msg)

    # 2. Use only the current user message (no history)
    messages = [{"role": "user", "content": user_msg.content}]
    
    # Debug: Log the messages being sent to AI
    logger.info(f"Sending {len(messages)} messages to AI: {[f'{m['role']}: {m['content'][:30]}...' for m in messages]}")

    # 3. Call Groq API (simple working version)
    try:
        import httpx
        import os
        from dotenv import load_dotenv
        
        # Load environment variables
        load_dotenv()
        groq_api_key = os.getenv("GROQ_API_KEY")
        groq_api_url = os.getenv("GROQ_API_URL", "https://api.groq.com/openai/v1/chat/completions")
        
        if not groq_api_key:
            logger.error("GROQ_API_KEY not found in environment variables")
            return {"error": "API key not configured"}
        
        url = groq_api_url
        headers = {"Authorization": f"Bearer {groq_api_key}"}
        
        # Add system prompt to the beginning of messages
        formatted_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
        
        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": formatted_messages,
            "stream": False,
            "temperature": 0.3,
            "max_tokens": 200
        }

        logger.info(f"Calling GROQ API with {len(formatted_messages)} messages")
        
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, headers=headers, json=payload)
            logger.info(f"GROQ API response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                assistant_reply = data["choices"][0]["message"]["content"]
                logger.info(f"Got response: {assistant_reply[:100]}...")
                
                # Save assistant reply
                await create_message(MessageCreate(role="assistant", content=assistant_reply))
                logger.info(f"Saved assistant reply to database")
                
                return {"response": assistant_reply}
            else:
                logger.error(f"GROQ API error: {response.status_code} - {response.text}")
                return {"error": f"API error: {response.status_code}"}
                
    except Exception as e:
        logger.error(f"Error calling GROQ API: {e}")
        return {"error": f"Server error: {str(e)}"}

@app.post("/leads", response_model=LeadOut)
async def create_lead_endpoint(lead: LeadCreate):
    """Create a new lead for sales follow-up"""
    try:
        # Create the lead in database
        db_lead = await create_lead(lead)
        
        # Send WhatsApp message if phone number is provided
        if lead.phone:
            whatsapp_sent = whatssms_service.send_whatsapp_message(lead.phone, f"Hello {lead.name}! Welcome to Vertex AI Tech. Our team will reach out to you soon.")
            if whatsapp_sent:
                logger.info(f"WhatsApp welcome message sent to {lead.name} at {lead.phone}")
            else:
                logger.warning(f"Failed to send WhatsApp message to {lead.name} at {lead.phone}")
        else:
            logger.info(f"No phone number provided for {lead.name}, skipping WhatsApp message")
        
        return db_lead
        
    except Exception as e:
        logger.error(f"Error creating lead: {str(e)}")
        raise e

@app.post("/support-tickets", response_model=SupportTicketOut)
async def create_support_ticket_endpoint(ticket: SupportTicketCreate):
    """Create a new support ticket"""
    try:
        # Create the support ticket in database
        db_ticket = await create_support_ticket(ticket)
        
        # Send WhatsApp message if phone number is provided
        if ticket.phone:
            whatsapp_sent = whatssms_service.send_whatsapp_message(ticket.phone, f"Hello! Your support ticket has been created. Issue Type: {ticket.issue_type}. Our team will respond within 24 hours.")
            if whatsapp_sent:
                logger.info(f"WhatsApp support confirmation sent to {ticket.email} at {ticket.phone}")
            else:
                logger.warning(f"Failed to send WhatsApp support confirmation to {ticket.phone}")
        else:
            logger.info(f"No phone number provided for support ticket {ticket.email}, skipping WhatsApp message")
        
        return db_ticket
        
    except Exception as e:
        logger.error(f"Error creating support ticket: {str(e)}")
        raise e

@app.get("/")
async def root():
    return {"message": "Vertex AI Tech Customer Support API", "status": "online"}

@app.post("/test-bot")
async def test_bot(request: Request):
    """Test the bot manually"""
    try:
        body = await request.json()
        phone_number = body.get("phone_number", "1234567890")
        message = body.get("message", "Hello")
        
        response = await whatssms_service.handle_incoming_message(phone_number, message)
        
        return {
            "status": "success",
            "phone_number": phone_number,
            "user_message": message,
            "bot_response": "Message processed successfully"
        }
    except Exception as e:
        logger.error(f"Error in test bot: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# WhatsApp Webhook Endpoints
@app.post("/webhook")
async def whatsapp_webhook(request: Request):
    """Handle incoming WhatsApp messages via webhook - Production ready with comprehensive logging"""
    
    # Always return 200 to prevent WhatsSMS.io from retrying
    try:
        # 1. LOG INCOMING HEADERS
        logger.info("=" * 60)
        logger.info("📨 INCOMING WEBHOOK REQUEST")
        logger.info("=" * 60)
        logger.info("📋 Headers:")
        for header_name, header_value in request.headers.items():
            logger.info(f"   {header_name}: {header_value}")
        
        # 2. SAFELY PARSE REQUEST BODY (JSON or Form-encoded)
        try:
            content_type = request.headers.get("content-type", "")
            logger.info(f"📦 Content-Type: {content_type}")
            
            if "application/json" in content_type:
                # Parse JSON data
                body = await request.json()
                logger.info("📦 Request Body (JSON):")
                logger.info(json.dumps(body, indent=2, ensure_ascii=False))
            elif "application/x-www-form-urlencoded" in content_type:
                # Parse form-encoded data
                form_data = await request.form()
                body = dict(form_data)
                logger.info("📦 Request Body (Form-encoded):")
                logger.info(json.dumps(body, indent=2, ensure_ascii=False))
                
                # Try to parse JSON fields if they exist
                if "data" in body and isinstance(body["data"], str):
                    try:
                        body["data"] = json.loads(body["data"])
                    except:
                        pass
            else:
                # Try JSON first, then form
                try:
                    body = await request.json()
                    logger.info("📦 Request Body (JSON - fallback):")
                    logger.info(json.dumps(body, indent=2, ensure_ascii=False))
                except:
                    form_data = await request.form()
                    body = dict(form_data)
                    logger.info("📦 Request Body (Form - fallback):")
                    logger.info(json.dumps(body, indent=2, ensure_ascii=False))
                    
        except Exception as parse_error:
            logger.error(f"❌ Error parsing request body: {str(parse_error)}")
            return JSONResponse(content={"status": "ok", "error": "parse_error"})
        
        # 3. VERIFY WEBHOOK SECRET (check body first, then headers)
        # WhatsSMS.io sends secret in request body, not headers
        incoming_secret = body.get("secret", "") or request.headers.get("x-webhook-secret", "")
        expected_secret = os.getenv("WEBHOOK_SECRET")
        
        if not expected_secret:
            logger.error("WEBHOOK_SECRET not found in environment variables")
            return JSONResponse(content={"status": "ok", "error": "webhook_secret_not_configured"})
        
        if incoming_secret and incoming_secret != expected_secret:
            logger.warning(f"⚠️ Invalid webhook secret: {incoming_secret}")
        elif incoming_secret:
            logger.info("✅ Webhook secret verified")
        else:
            logger.info("ℹ️ No webhook secret provided")
        
        # 4. PROCESS MESSAGES (WHATSAPP AND SMS)
        try:
            # Handle different data structures from WhatsApp
            if "type" in body and "data" in body:
                # JSON format with nested data
                data = body["data"]
                message_type = body["type"]
            elif "type" in body and "phone" in body:
                # Form-encoded format with flat structure
                data = {
                    "phone": body.get("phone", ""),
                    "message": body.get("message", ""),
                    "id": body.get("id", "unknown"),
                    "timestamp": body.get("timestamp", 0)
                }
                message_type = body["type"]
            elif "type" in body and any(key.startswith("data[") for key in body.keys()):
                # Real WhatsApp format with data[field] structure
                data = {}
                for key, value in body.items():
                    if key.startswith("data["):
                        field_name = key[5:-1]  # Remove "data[" and "]"
                        data[field_name] = value
                message_type = body["type"]
                logger.info(f"📱 Real WhatsApp format detected: {data}")
            else:
                logger.warning("⚠️ Invalid message format - missing required fields")
                return JSONResponse(content={"status": "ok", "message": "ignored"})
            
            # Extract message details safely
            message_id = data.get("id", "unknown")
            message = data.get("message", "")
            timestamp = data.get("timestamp", 0)
            
            # Extract sender and normalize to E.164
            raw_sender = data.get("phone", "")
            sender = whatssms_service.normalize_to_e164(raw_sender)
            logger.info(f"   Raw Sender: {raw_sender} -> Normalized Sender: {sender}")
            
            # Extract bot account based on message type
            if message_type == "whatsapp":
                bot_account = data.get("wid", "")  # WhatsApp ID for bot account
                logger.info("📱 WhatsApp Message Details:")
            elif message_type == "sms":
                bot_account = data.get("device", "")  # Device for SMS
                logger.info("📱 SMS Message Details:")
            else:
                bot_account = data.get("account", "")  # Fallback
                logger.info(f"📱 {message_type.upper()} Message Details:")
            
            logger.info(f"   Message ID: {message_id}")
            logger.info(f"   Bot Account: {bot_account}")
            logger.info(f"   Sender: {sender}")
            logger.info(f"   Message: {message}")
            logger.info(f"   Timestamp: {timestamp}")
            
            # Validate that we have a sender
            if not sender:
                logger.error("❌ No sender found in payload, cannot reply!")
                return JSONResponse(content={"status": "ok", "error": "no_sender"})
            
            # 5. HANDLE MESSAGE WITH ERROR HANDLING
            try:
                logger.info(f"🤖 Processing {message_type} message from {sender} to bot {bot_account}...")
                # Process message synchronously to ensure auto-reply is sent
                result = await whatssms_service.handle_incoming_message(sender, message, bot_account, timestamp)
                logger.info(f"✅ {message_type.upper()} message from {sender} processed successfully: {result}")
                return JSONResponse(content={"status": "ok", "message": "processed"})
                
            except Exception as bot_error:
                logger.error(f"❌ Error in bot processing: {str(bot_error)}")
                # Still return 200 to prevent retries
                return JSONResponse(content={"status": "ok", "error": "bot_processing_failed"})
                
        except Exception as processing_error:
            logger.error(f"❌ Error processing message: {str(processing_error)}")
            return JSONResponse(content={"status": "ok", "error": "processing_failed"})
            
    except Exception as general_error:
        # 6. CATCH ALL ERRORS - ALWAYS RETURN 200
        logger.error(f"❌ CRITICAL ERROR in webhook: {str(general_error)}")
        logger.error("=" * 60)
        return JSONResponse(content={"status": "ok", "error": "general_error"})
    
    finally:
        logger.info("=" * 60)
        logger.info("📤 WEBHOOK RESPONSE SENT")
        logger.info("=" * 60)

@app.get("/webhook")
async def whatsapp_webhook_get():
    """Handle WhatsApp webhook verification (GET request)"""
    return {"status": "webhook_ready", "service": "whatssms_bot"}

# Bot Service Endpoints
@app.get("/bot/conversation/{phone_number}")
async def get_bot_conversation(phone_number: str):
    """Get conversation for a specific phone number"""
    try:
        conversation = await whatssms_service.get_or_create_conversation(phone_number)
        return {
            "phone_number": phone_number,
            "client_name": conversation.client_name,
            "status": conversation.status,
            "messages_used": conversation.messages_used,
            "conversation": [
                {
                    "role": msg.role,
                    "message": msg.message,
                    "timestamp": msg.timestamp.isoformat()
                }
                for msg in conversation.conversation
            ],
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting conversation for {phone_number}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/bot/send")
async def send_bot_message(request: Request):
    """Send a WhatsApp message manually via bot service"""
    try:
        body = await request.json()
        phone_number = body.get("phone_number")
        message = body.get("message")
        
        if not phone_number or not message:
            raise HTTPException(status_code=400, detail="phone_number and message are required")
        
        success = whatssms_service.send_whatsapp_message(phone_number, message)
        
        if success:
            return {"status": "sent", "phone_number": phone_number}
        else:
            raise HTTPException(status_code=500, detail="Failed to send message")
            
    except Exception as e:
        logger.error(f"Error sending WhatsApp message: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/bot/notify-team")
async def notify_team_endpoint(request: Request):
    """Send notification to team manually"""
    try:
        body = await request.json()
        message = body.get("message")
        phone_number = body.get("phone_number")
        
        if not message:
            raise HTTPException(status_code=400, detail="message is required")
        
        success = await whatssms_service.notify_team(message, phone_number)
        
        if success:
            return {"status": "sent", "message": "Team notification sent"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send team notification")
            
    except Exception as e:
        logger.error(f"Error sending team notification: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

