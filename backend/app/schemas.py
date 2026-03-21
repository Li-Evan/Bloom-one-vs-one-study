from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


# Auth
class RegisterRequest(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=6, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    credits: int
    created_at: datetime

    model_config = {"from_attributes": True}


# Credits
class CreditBalanceResponse(BaseModel):
    credits: int


class CreditTransactionResponse(BaseModel):
    id: int
    amount: int
    balance_after: int
    type: str
    description: str
    created_at: datetime

    model_config = {"from_attributes": True}


# Course
class CreateCourseRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)


class CourseResponse(BaseModel):
    id: int
    name: str
    created_at: datetime
    message_count: int = 0

    model_config = {"from_attributes": True}


# Chat
class ChatRequest(BaseModel):
    course_id: int
    message: str = Field(..., min_length=1, max_length=10000)


class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}
