from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
import re


# Auth
class RegisterRequest(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=6, max_length=128)

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z0-9_\u4e00-\u9fff]+$', v):
            raise ValueError("用户名只能包含字母、数字、下划线或中文")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., max_length=128)


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
    status: str
    created_at: datetime
    lesson_count: int = 0

    model_config = {"from_attributes": True}


class CourseDetailResponse(BaseModel):
    id: int
    name: str
    status: str
    created_at: datetime
    lesson_count: int = 0
    syllabus_content: str | None = None

    model_config = {"from_attributes": True}


# Syllabus
class SyllabusResponse(BaseModel):
    id: int
    course_id: int
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class SyllabusUpdateRequest(BaseModel):
    content: str = Field(..., min_length=1)


# Lesson
class LessonListItem(BaseModel):
    id: int
    number: int
    is_evaluation: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class LessonResponse(BaseModel):
    id: int
    course_id: int
    number: int
    content: str
    is_evaluation: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# Annotation
class CreateAnnotationRequest(BaseModel):
    position_start: int = Field(..., ge=0)
    position_end: int = Field(..., ge=0)
    original_text: str = Field(..., min_length=1, max_length=5000)
    comment: str = Field(..., min_length=1, max_length=5000)

    @field_validator("position_end")
    @classmethod
    def end_gte_start(cls, v: int, info) -> int:
        if "position_start" in info.data and v < info.data["position_start"]:
            raise ValueError("position_end must be >= position_start")
        return v


class AnnotationResponse(BaseModel):
    id: int
    lesson_id: int
    user_id: int
    position_start: int
    position_end: int
    original_text: str
    comment: str
    created_at: datetime

    model_config = {"from_attributes": True}


# Feedback
class CreateFeedbackRequest(BaseModel):
    content: str = Field("", max_length=10000)
    thought_answers: str | None = Field(None, max_length=10000)


class FeedbackResponse(BaseModel):
    id: int
    lesson_id: int
    user_id: int
    content: str
    thought_answers: str
    created_at: datetime

    model_config = {"from_attributes": True}
