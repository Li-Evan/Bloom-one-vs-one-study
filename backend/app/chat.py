from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from openai import OpenAI
import json

from app.config import settings
from app.database import get_db
from app.models import User, Course, Message
from app.auth import get_current_user
from app.credits import deduct_credits
from app.schemas import ChatRequest, CourseResponse, CreateCourseRequest, MessageResponse

router = APIRouter(prefix="/api", tags=["chat"])

SYSTEM_PROMPT = """你是一个基于 Bloom 2-Sigma 理论的一对一苏格拉底式导师。

## 你的教学原则

1. **不直接给答案** — 用提问引导学生自己推导出答案
2. **自适应调整** — 根据学生的反馈实时调整内容深度和方向
3. **掌握学习法** — 确保每个知识点都被真正掌握后再推进
4. **耐心鼓励，但不手软** — 理解错误时温和纠正，不放过任何知识盲点

## 交互方式

- 当学生提出要学习的课题时，先用 2-3 个问题了解学生的现有知识水平
- 然后根据学生水平，从合适的起点开始讲解
- 每次讲解后，提出 1-2 个思考题检验理解
- 根据学生的回答，决定是深入当前知识点还是推进到下一个

## 语言要求

- 始终使用中文交流
- 解释要清晰、有深度、有例子
- 关键概念加粗标注
"""


def get_openai_client() -> OpenAI:
    return OpenAI(api_key=settings.DASHSCOPE_API_KEY, base_url=settings.DASHSCOPE_BASE_URL)


@router.post("/courses", response_model=CourseResponse)
def create_course(req: CreateCourseRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    course = Course(user_id=user.id, name=req.name)
    db.add(course)
    db.commit()
    db.refresh(course)
    return CourseResponse(id=course.id, name=course.name, created_at=course.created_at, message_count=0)


@router.get("/courses", response_model=list[CourseResponse])
def list_courses(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    courses = db.query(Course).filter(Course.user_id == user.id).order_by(Course.created_at.desc()).all()
    result = []
    for c in courses:
        result.append(
            CourseResponse(id=c.id, name=c.name, created_at=c.created_at, message_count=len(c.messages))
        )
    return result


@router.get("/courses/{course_id}/messages", response_model=list[MessageResponse])
def get_messages(course_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id, Course.user_id == user.id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    return [MessageResponse(id=m.id, role=m.role, content=m.content, created_at=m.created_at) for m in course.messages]


@router.post("/chat/send")
def send_message(req: ChatRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == req.course_id, Course.user_id == user.id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")

    # Check credits before calling API
    if user.credits < settings.CREDITS_PER_REQUEST:
        raise HTTPException(status_code=402, detail=f"积分不足，当前余额 {user.credits}")

    # Save user message
    user_msg = Message(course_id=course.id, role="user", content=req.message)
    db.add(user_msg)
    db.commit()

    # Build conversation history
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in course.messages:
        if m.role != "system":
            messages.append({"role": m.role, "content": m.content})

    # Call DashScope API with streaming
    client = get_openai_client()

    def generate():
        full_response = ""
        try:
            stream = client.chat.completions.create(
                model=settings.DASHSCOPE_MODEL,
                messages=messages,
                stream=True,
            )
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield f"data: {json.dumps({'content': content})}\n\n"

            # Save assistant message and deduct credits
            assistant_msg = Message(course_id=course.id, role="assistant", content=full_response)
            db.add(assistant_msg)
            deduct_credits(db, user, settings.CREDITS_PER_REQUEST, f"课程「{course.name}」对话")
            db.commit()

            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
