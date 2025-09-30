from pydantic import BaseModel, Field, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from typing import Optional, Any, List, Dict
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type: Any, _handler: Any) -> Any:
        from pydantic_core import core_schema
        return core_schema.no_info_plain_validator_function(cls.validate)

    @classmethod
    def __get_pydantic_json_schema__(cls, _core_schema: Any, handler: GetJsonSchemaHandler) -> JsonSchemaValue:
        return {"type": "string"}

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

class ConversationMessage(BaseModel):
    role: str  # "client" or "assistant"
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class WhatsAppConversation(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")  # Use string for phone number
    client_name: Optional[str] = None
    phone_number: str  # This will be the _id (phone number)
    conversation: List[ConversationMessage] = []
    status: str = "pending"  # "pending" or "finalized"
    messages_used: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# Keep existing models for backward compatibility
class Message(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class Lead(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str
    email: str
    phone: Optional[str] = None
    request_type: str  # "pricing", "demo", "services"
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class SupportTicket(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    email: str
    issue_type: str  # "login", "technical", "billing", "general"
    description: str
    status: str = "open"  # "open", "in_progress", "resolved"
    phone: Optional[str] = None  # Optional phone number for WhatsApp notifications
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
