from db import get_database
from models import Message, Lead, SupportTicket
from schemas import MessageCreate, LeadCreate, SupportTicketCreate
from typing import List

async def create_message(msg: MessageCreate):
    db = await get_database()
    message_dict = {
        "role": msg.role,
        "content": msg.content
    }
    result = await db.messages.insert_one(message_dict)
    message_dict["_id"] = result.inserted_id
    message_obj = Message(**message_dict)
    # Convert ObjectId to string for API response
    message_obj.id = str(message_obj.id)
    return message_obj

async def get_last_messages(limit: int = 10) -> List[Message]:
    db = await get_database()
    cursor = db.messages.find().sort("timestamp", -1).limit(limit)
    messages = []
    async for doc in cursor:
        message_obj = Message(**doc)
        # Convert ObjectId to string
        message_obj.id = str(message_obj.id)
        messages.append(message_obj)
    return messages[::-1]  # Reverse to get chronological order

async def create_lead(lead: LeadCreate):
    db = await get_database()
    lead_dict = {
        "name": lead.name,
        "email": lead.email,
        "phone": lead.phone,
        "request_type": lead.request_type,
        "message": lead.message
    }
    result = await db.leads.insert_one(lead_dict)
    lead_dict["_id"] = result.inserted_id
    lead_obj = Lead(**lead_dict)
    # Convert ObjectId to string for API response
    lead_obj.id = str(lead_obj.id)
    return lead_obj

async def create_support_ticket(ticket: SupportTicketCreate):
    db = await get_database()
    ticket_dict = {
        "email": ticket.email,
        "issue_type": ticket.issue_type,
        "description": ticket.description,
        "phone": ticket.phone,
        "status": "open"
    }
    result = await db.support_tickets.insert_one(ticket_dict)
    ticket_dict["_id"] = result.inserted_id
    ticket_obj = SupportTicket(**ticket_dict)
    # Convert ObjectId to string for API response
    ticket_obj.id = str(ticket_obj.id)
    return ticket_obj
