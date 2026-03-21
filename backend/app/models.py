from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, CheckConstraint
from sqlalchemy.orm import relationship

from app.database import Base


def _utcnow():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    credits = Column(Integer, default=100)
    created_at = Column(DateTime, default=_utcnow)

    transactions = relationship("CreditTransaction", back_populates="user")
    courses = relationship("Course", back_populates="user")


class CreditTransaction(Base):
    __tablename__ = "credit_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Integer, nullable=False)  # positive = add, negative = deduct
    balance_after = Column(Integer, nullable=False)
    type = Column(String, nullable=False)  # "registration_bonus", "chat_deduction", "admin_topup"
    description = Column(String, default="")
    created_at = Column(DateTime, default=_utcnow)

    user = relationship("User", back_populates="transactions")


class Course(Base):
    __tablename__ = "courses"
    __table_args__ = (
        CheckConstraint("status IN ('learning', 'completed')", name="ck_course_status"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    status = Column(String, default="learning")
    created_at = Column(DateTime, default=_utcnow)

    user = relationship("User", back_populates="courses")
    syllabus = relationship("Syllabus", back_populates="course", uselist=False, cascade="all, delete-orphan")
    lessons = relationship("Lesson", back_populates="course", order_by="Lesson.number", cascade="all, delete-orphan")


class Syllabus(Base):
    __tablename__ = "syllabi"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), unique=True, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=_utcnow)

    course = relationship("Course", back_populates="syllabus")


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    number = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    is_evaluation = Column(Boolean, default=False)
    created_at = Column(DateTime, default=_utcnow)

    course = relationship("Course", back_populates="lessons")
    annotations = relationship("Annotation", back_populates="lesson", cascade="all, delete-orphan")
    feedback = relationship("Feedback", back_populates="lesson", uselist=False, cascade="all, delete-orphan")


class Annotation(Base):
    __tablename__ = "annotations"
    __table_args__ = (
        CheckConstraint("position_end >= position_start", name="ck_annotation_positions"),
    )

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    position_start = Column(Integer, nullable=False)
    position_end = Column(Integer, nullable=False)
    original_text = Column(Text, nullable=False)
    comment = Column(Text, nullable=False)
    created_at = Column(DateTime, default=_utcnow)

    lesson = relationship("Lesson", back_populates="annotations")
    user = relationship("User")


class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, default="")
    thought_answers = Column(Text, default="")  # JSON string
    created_at = Column(DateTime, default=_utcnow)

    lesson = relationship("Lesson", back_populates="feedback")
    user = relationship("User")
