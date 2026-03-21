from pydantic import BaseModel, Field, field_validator
from datetime import datetime


# Course
class CreateCourseRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    reference: str = Field("", max_length=50000)  # optional reference material


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
    content: str
    thought_answers: str
    created_at: datetime

    model_config = {"from_attributes": True}
