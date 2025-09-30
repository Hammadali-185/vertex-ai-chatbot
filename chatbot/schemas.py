from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from bson import ObjectId

class MessageCreate(BaseModel):
    role: str
    content: str

class MessageOut(BaseModel):
    id: str
    role: str
    content: str
    timestamp: datetime

    class Config:
        populate_by_name = True

class LeadCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    request_type: str
    message: Optional[str] = None

class LeadOut(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str]
    request_type: str
    message: Optional[str]
    timestamp: datetime

    class Config:
        populate_by_name = True

class SupportTicketCreate(BaseModel):
    email: str
    issue_type: str
    description: str
    phone: Optional[str] = None

class SupportTicketOut(BaseModel):
    id: str
    email: str
    issue_type: str
    description: str
    status: str
    timestamp: datetime
    phone: Optional[str] = None

    class Config:
        populate_by_name = True
