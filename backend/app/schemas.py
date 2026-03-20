from pydantic import BaseModel, EmailStr
from datetime import datetime


# Auth
class RegisterRequest(BaseModel):
    email: str
    username: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    credits: float
    created_at: datetime

    model_config = {"from_attributes": True}


# Credits
class CreditBalanceResponse(BaseModel):
    credits: float


class CreditTransactionResponse(BaseModel):
    id: int
    amount: float
    balance_after: float
    type: str
    description: str
    created_at: datetime

    model_config = {"from_attributes": True}


# Course
class CreateCourseRequest(BaseModel):
    name: str


class CourseResponse(BaseModel):
    id: int
    name: str
    created_at: datetime
    message_count: int = 0

    model_config = {"from_attributes": True}


# Chat
class ChatRequest(BaseModel):
    course_id: int
    message: str


class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}
