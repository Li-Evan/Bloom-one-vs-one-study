import logging
import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from openai import OpenAI

from app.config import settings
from app.database import get_db
from app.models import User, Course, Syllabus, Lesson, Annotation, Feedback
from app.auth import get_current_user
from app.credits import deduct_credits, refund_credits
from app.schemas import (
    CreateCourseRequest, CourseResponse, CourseDetailResponse,
    SyllabusResponse, SyllabusUpdateRequest,
    LessonListItem, LessonResponse,
    CreateAnnotationRequest, AnnotationResponse,
    CreateFeedbackRequest, FeedbackResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["courses"])

# ---------------------------------------------------------------------------
# AI System Prompts
# ---------------------------------------------------------------------------

SYLLABUS_PROMPT = """你是一个课程大纲设计专家。根据用户给出的课题名称，生成一份结构化的课程大纲。

## 输出格式（严格遵守，不要加额外说明）

```markdown
# [课题名] · 课程大纲

> 这份大纲定义了完成本课题后你将掌握的所有能力。
> 文档数量因人而异，但掌握内容不打折扣。

## 核心掌握项

完成本课题后，你将能够：

### [模块一名称]
- [ ] [具体能力描述，用"能够……"句式，可验证]
- [ ] [具体能力描述]

### [模块二名称]
- [ ] [具体能力描述]
- [ ] [具体能力描述]

## 不在本课题范围内

- [明确列出哪些相关主题本课不涵盖]

## 学习进度

| 文档 | 覆盖掌握项 | 生成日期 |
|------|-----------|---------|
```

## 规则
1. 所有掌握项必须是**可验证的行为**（能解释、能推导、能应用、能判断），禁止写"了解 X""熟悉 Y"
2. 按知识的内在逻辑分 2-5 个模块
3. 总条目数控制在 8-15 条
4. "不在本课题范围内"必须填写
5. 只输出 markdown 内容，不要加任何前缀说明或后缀解释
"""

FIRST_LESSON_PROMPT = """你是一个基于 Bloom 2-Sigma 理论的一对一苏格拉底式导师。

根据以下课程大纲，生成第一篇课文（01）。

## 课程大纲
{syllabus}

## 输出格式（严格遵守）

```markdown
# [章节标题]

> 前置知识：[列出阅读本文需要的前置知识]
> 难度：[入门 / 进阶 / 高级]
> 预计阅读时间：[X 分钟]

## 正文内容

[清晰、有深度、有举例的知识阐述]
[关键概念用 **加粗** 标注]
[重要定义或公式用引用块]

## 思考题

[2-3 个引导用户深入思考的问题，不给答案]

## 你的反馈

> 在这里写下你的问题、感悟、不理解的地方，或者你希望下一篇深入探讨的方向。
```

## 规则
1. 内容要有实质性的知识增量，不要太水
2. 关键概念加粗，重要定义用引用块
3. 思考题要有深度，引导用户思考而不是简单记忆
4. 只输出 markdown 内容
"""

NEXT_LESSON_PROMPT = """你是一个基于 Bloom 2-Sigma 理论的一对一苏格拉底式导师。

根据学生的反馈和批注，生成下一篇课文。

## 课程大纲
{syllabus}

## 已完成的课文
{previous_lessons}

## 上一篇课文的学生反馈
{feedback}

## 上一篇课文中的学生批注（??? 标注）
{annotations}

## 当前课文编号：{lesson_number}

## 输出格式（严格遵守）

```markdown
# [章节标题]

> 前置知识：[列出阅读本文需要的前置知识]
> 难度：[入门 / 进阶 / 高级]
> 预计阅读时间：[X 分钟]

---

## 上一篇思考题复盘

> 📝 本模块评估你对上一篇思考题的回答，并给出正确答案。

### 你的回答评估

[逐题评估用户回答：✅对/❌错/⚠️部分正确，简要说明理由]
[如果用户没有作答，注明"未作答"，直接给出正确答案]

### 正确答案

**第1题：** [题目简述]
> [完整的正确答案和必要的解析]

**第2题：** [题目简述]
> [完整的正确答案和必要的解析]

---

## ??? 解答

> 💬 本模块解答你在上一篇中用 ??? 标注的所有困惑。

[若无 ??? 标注，写"上一篇中没有 ??? 标注，直接进入新内容。"]

---

## 正文内容

[清晰、有深度、有举例的知识阐述]

## 思考题

[2-3 个引导用户深入思考的问题，不给答案]

## 你的反馈

> 在这里写下你的问题、感悟、不理解的地方，或者你希望下一篇深入探讨的方向。
```

## 规则
1. 必须严格按照"思考题复盘 → ??? 解答 → 正文新内容"的顺序
2. 基于学生反馈和批注调整内容深度和方向
3. 每篇文档应覆盖大纲中至少一条掌握项
4. 只输出 markdown 内容
"""

EVAL_LESSON_PROMPT = """你是一个基于 Bloom 2-Sigma 理论的一对一苏格拉底式导师。

大纲中所有掌握项已经全部覆盖完毕。现在生成评估篇，只需要回答最后一篇的思考题和 ??? 困惑，不包含任何新内容。

## 课程大纲
{syllabus}

## 上一篇课文
{last_lesson}

## 上一篇课文的学生反馈
{feedback}

## 上一篇课文中的学生批注
{annotations}

## 输出格式（严格遵守，第一行必须是 <!-- eval-article -->）

```markdown
<!-- eval-article -->

# [课题名] · 最终评估

> 本篇为课程评估篇，不含新内容。
> 作用：解答最后一篇的思考题与 ??? 困惑，确认你已完全掌握。

---

## 上一篇思考题复盘

> 📝 本模块评估你对上一篇思考题的回答，并给出正确答案。

### 你的回答评估

[逐题评估，标注 ✅ / ❌ / ⚠️，并简要说明理由]

### 正确答案

**第1题：** [题目简述]
> [完整答案和解析]

---

## ??? 解答

> 💬 本模块解答你在上一篇中用 ??? 标注的所有困惑。

[若无标注，写"上一篇中没有 ??? 标注。"]

---

## 你的反馈

> 写下你对这门课的最终感想、仍有疑问的地方，或希望延伸的方向。
> 当你读完本篇后，告诉我"我读完了"，系统将自动为你生成完整的总结。
```
"""

SUMMARY_PROMPT = """你是一个课程总结专家。根据课程的完整学习过程，生成一份结构化的学习总结。

## 课程大纲
{syllabus}

## 所有课文内容
{all_lessons}

## 输出格式

```markdown
# [课题名] · 学习总结

## 知识图谱

[核心概念及其关系，用层级列表表达]

## 大纲复盘

[逐条回顾每条掌握项的达成情况]

## 关键洞察

[学习过程中最重要的发现和理解]

## 延伸方向

[值得继续探索的方向]
```

只输出 markdown 内容。
"""


# ---------------------------------------------------------------------------
# LLM Helpers
# ---------------------------------------------------------------------------

def get_openai_client() -> OpenAI:
    return OpenAI(api_key=settings.DASHSCOPE_API_KEY, base_url=settings.DASHSCOPE_BASE_URL)


import re

_FENCE_RE = re.compile(r'^```(?:markdown|md)?\s*\n?', re.IGNORECASE)
_FENCE_END_RE = re.compile(r'\n?```\s*$')


def _strip_markdown_fences(text: str) -> str:
    """Strip wrapping ```markdown ... ``` fences that LLMs often add."""
    text = text.strip()
    if _FENCE_RE.match(text):
        text = _FENCE_RE.sub('', text, count=1)
        text = _FENCE_END_RE.sub('', text)
    return text.strip()


def _stream_llm(system_prompt: str, user_message: str):
    """Generator that yields SSE chunks from LLM streaming."""
    client = get_openai_client()
    stream = client.chat.completions.create(
        model=settings.DASHSCOPE_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        stream=True,
    )
    full_response = ""
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            full_response += content
            yield content, False
    yield full_response, True  # final yield with complete text


def _call_llm(system_prompt: str, user_message: str) -> str:
    """Non-streaming LLM call, returns full response."""
    client = get_openai_client()
    response = client.chat.completions.create(
        model=settings.DASHSCOPE_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
    )
    return response.choices[0].message.content


def _check_all_mastery_items_done(syllabus_content: str) -> bool:
    """Check if all checkbox items in syllabus are checked."""
    lines = syllabus_content.split("\n")
    has_unchecked = False
    has_any_checkbox = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- [ ]"):
            has_unchecked = True
            has_any_checkbox = True
        elif stripped.startswith("- [x]") or stripped.startswith("- [X]"):
            has_any_checkbox = True
    return has_any_checkbox and not has_unchecked


# ---------------------------------------------------------------------------
# API Routes
# ---------------------------------------------------------------------------

@router.post("/courses", response_model=CourseDetailResponse)
def create_course(
    req: CreateCourseRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create course + AI generates syllabus + first lesson (blocking)."""
    if not deduct_credits(db, user.id, settings.CREDITS_PER_REQUEST, f"创建课程「{req.name}」"):
        raise HTTPException(status_code=402, detail="积分不足")

    course = Course(user_id=user.id, name=req.name, status="learning")
    db.add(course)
    db.flush()

    try:
        # Generate syllabus
        syllabus_content = _strip_markdown_fences(_call_llm(SYLLABUS_PROMPT, f"课题：{req.name}"))
        syllabus = Syllabus(course_id=course.id, content=syllabus_content)
        db.add(syllabus)
        db.flush()

        # Generate first lesson
        prompt = FIRST_LESSON_PROMPT.format(syllabus=syllabus_content)
        lesson_content = _strip_markdown_fences(_call_llm(prompt, f"请为课题「{req.name}」生成第一篇课文"))
        lesson = Lesson(course_id=course.id, number=1, content=lesson_content)
        db.add(lesson)

        db.commit()
        db.refresh(course)

        return CourseDetailResponse(
            id=course.id, name=course.name, status=course.status,
            created_at=course.created_at, lesson_count=1,
            syllabus_content=syllabus_content,
        )

    except Exception as e:
        logger.exception("Course creation error")
        db.rollback()
        refund_credits(db, user.id, settings.CREDITS_PER_REQUEST, "退款：课程创建失败")
        db.commit()
        raise HTTPException(status_code=500, detail="课程创建失败，请稍后重试")


@router.get("/courses", response_model=list[CourseResponse])
def list_courses(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    courses = db.query(Course).filter(Course.user_id == user.id).order_by(Course.created_at.desc()).all()
    return [
        CourseResponse(
            id=c.id, name=c.name, status=c.status,
            created_at=c.created_at, lesson_count=len(c.lessons),
        )
        for c in courses
    ]


@router.get("/courses/{course_id}", response_model=CourseDetailResponse)
def get_course(course_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id, Course.user_id == user.id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    return CourseDetailResponse(
        id=course.id, name=course.name, status=course.status,
        created_at=course.created_at, lesson_count=len(course.lessons),
        syllabus_content=course.syllabus.content if course.syllabus else None,
    )


@router.get("/courses/{course_id}/syllabus", response_model=SyllabusResponse)
def get_syllabus(course_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id, Course.user_id == user.id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    if not course.syllabus:
        raise HTTPException(status_code=404, detail="大纲尚未生成")
    return course.syllabus


@router.put("/courses/{course_id}/syllabus", response_model=SyllabusResponse)
def update_syllabus(
    course_id: int,
    req: SyllabusUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    course = db.query(Course).filter(Course.id == course_id, Course.user_id == user.id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    if not course.syllabus:
        raise HTTPException(status_code=404, detail="大纲尚未生成")
    course.syllabus.content = req.content
    db.commit()
    db.refresh(course.syllabus)
    return course.syllabus


@router.get("/courses/{course_id}/lessons", response_model=list[LessonListItem])
def list_lessons(course_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id, Course.user_id == user.id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    return [
        LessonListItem(id=l.id, number=l.number, is_evaluation=l.is_evaluation, created_at=l.created_at)
        for l in course.lessons
    ]


@router.get("/courses/{course_id}/lessons/{lesson_num}", response_model=LessonResponse)
def get_lesson(course_id: int, lesson_num: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id, Course.user_id == user.id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    lesson = db.query(Lesson).filter(Lesson.course_id == course_id, Lesson.number == lesson_num).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="课文不存在")
    return lesson


@router.post("/courses/{course_id}/lessons/{lesson_num}/annotations", response_model=AnnotationResponse)
def create_annotation(
    course_id: int,
    lesson_num: int,
    req: CreateAnnotationRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    course = db.query(Course).filter(Course.id == course_id, Course.user_id == user.id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    lesson = db.query(Lesson).filter(Lesson.course_id == course_id, Lesson.number == lesson_num).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="课文不存在")

    annotation = Annotation(
        lesson_id=lesson.id,
        user_id=user.id,
        position_start=req.position_start,
        position_end=req.position_end,
        original_text=req.original_text,
        comment=req.comment,
    )
    db.add(annotation)
    db.commit()
    db.refresh(annotation)
    return annotation


@router.get("/courses/{course_id}/lessons/{lesson_num}/annotations", response_model=list[AnnotationResponse])
def get_annotations(
    course_id: int,
    lesson_num: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    course = db.query(Course).filter(Course.id == course_id, Course.user_id == user.id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    lesson = db.query(Lesson).filter(Lesson.course_id == course_id, Lesson.number == lesson_num).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="课文不存在")
    return db.query(Annotation).filter(Annotation.lesson_id == lesson.id).order_by(Annotation.created_at).all()


@router.post("/courses/{course_id}/lessons/{lesson_num}/feedback", response_model=FeedbackResponse)
def create_feedback(
    course_id: int,
    lesson_num: int,
    req: CreateFeedbackRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    course = db.query(Course).filter(Course.id == course_id, Course.user_id == user.id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    lesson = db.query(Lesson).filter(Lesson.course_id == course_id, Lesson.number == lesson_num).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="课文不存在")

    # Check if feedback already exists, update if so
    existing = db.query(Feedback).filter(Feedback.lesson_id == lesson.id, Feedback.user_id == user.id).first()
    if existing:
        existing.content = req.content
        existing.thought_answers = req.thought_answers
        db.commit()
        db.refresh(existing)
        return existing

    feedback = Feedback(
        lesson_id=lesson.id,
        user_id=user.id,
        content=req.content,
        thought_answers=req.thought_answers,
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


@router.post("/courses/{course_id}/next")
def generate_next_lesson(
    course_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """'我读完了' → AI generates next lesson (SSE streaming)."""
    course = db.query(Course).filter(Course.id == course_id, Course.user_id == user.id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    if course.status == "completed":
        raise HTTPException(status_code=400, detail="课程已完结")
    if not course.syllabus:
        raise HTTPException(status_code=400, detail="课程大纲尚未生成")

    if not deduct_credits(db, user.id, settings.CREDITS_PER_REQUEST, f"课程「{course.name}」生成课文"):
        raise HTTPException(status_code=402, detail="积分不足")
    db.commit()

    lessons = course.lessons
    if not lessons:
        raise HTTPException(status_code=400, detail="尚无课文")

    last_lesson = lessons[-1]

    # Check if last lesson is an evaluation article — if so, generate summary
    if last_lesson.is_evaluation:
        return _generate_summary_response(course, user.id, db)

    syllabus_content = course.syllabus.content
    all_mastery_done = _check_all_mastery_items_done(syllabus_content)

    # Collect feedback and annotations from last lesson
    last_feedback = db.query(Feedback).filter(
        Feedback.lesson_id == last_lesson.id, Feedback.user_id == user.id
    ).first()
    last_annotations = db.query(Annotation).filter(
        Annotation.lesson_id == last_lesson.id
    ).order_by(Annotation.created_at).all()

    feedback_text = ""
    if last_feedback:
        feedback_text = f"反馈内容：{last_feedback.content}\n思考题回答：{last_feedback.thought_answers}"
    else:
        feedback_text = "学生没有提交反馈。"

    annotations_text = ""
    if last_annotations:
        annotations_text = "\n".join(
            f"- 原文「{a.original_text}」→ 批注：{a.comment}" for a in last_annotations
        )
    else:
        annotations_text = "无批注。"

    next_number = last_lesson.number + 1

    if all_mastery_done:
        prompt = EVAL_LESSON_PROMPT.format(
            syllabus=syllabus_content,
            last_lesson=last_lesson.content,
            feedback=feedback_text,
            annotations=annotations_text,
        )
        user_msg = "生成评估篇"
    else:
        recent = lessons[-3:] if len(lessons) > 3 else lessons
        prev_text = "\n\n---\n\n".join(
            f"### 第{l.number}篇\n{l.content[:2000]}" for l in recent
        )
        prompt = NEXT_LESSON_PROMPT.format(
            syllabus=syllabus_content,
            previous_lessons=prev_text,
            feedback=feedback_text,
            annotations=annotations_text,
            lesson_number=next_number,
        )
        user_msg = f"生成第{next_number}篇课文"

    cid = course.id
    uid = user.id

    def generate():
        try:
            lesson_content = ""
            for content, is_final in _stream_llm(prompt, user_msg):
                if is_final:
                    lesson_content = content
                else:
                    yield f"data: {json.dumps({'content': content}, ensure_ascii=False)}\n\n"

            lesson_content = _strip_markdown_fences(lesson_content)
            is_eval = lesson_content.strip().startswith("<!-- eval-article -->")

            # Use request db session (alive during streaming)
            new_lesson = Lesson(
                course_id=cid, number=next_number,
                content=lesson_content, is_evaluation=is_eval,
            )
            db.add(new_lesson)
            db.commit()

            yield f"data: {json.dumps({'done': True, 'lesson_number': next_number, 'is_evaluation': is_eval}, ensure_ascii=False)}\n\n"

        except Exception as e:
            logger.exception("Next lesson generation error")
            db.rollback()
            try:
                refund_credits(db, uid, settings.CREDITS_PER_REQUEST, "退款：课文生成失败")
                db.commit()
            except Exception:
                logger.exception("Failed to refund credits")
            yield f"data: {json.dumps({'error': '服务暂时不可用，请稍后重试'}, ensure_ascii=False)}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


def _generate_summary_response(course: Course, user_id: int, db: Session):
    """Generate summary after evaluation article is read."""
    syllabus_content = course.syllabus.content
    all_lessons_text = "\n\n---\n\n".join(
        f"### 第{l.number}篇\n{l.content}" for l in course.lessons
    )

    cid = course.id

    def generate():
        try:
            prompt = SUMMARY_PROMPT.format(
                syllabus=syllabus_content,
                all_lessons=all_lessons_text,
            )
            summary_content = ""
            for content, is_final in _stream_llm(prompt, "生成课程总结"):
                if is_final:
                    summary_content = content
                else:
                    yield f"data: {json.dumps({'phase': 'summary', 'content': content}, ensure_ascii=False)}\n\n"

            summary_content = _strip_markdown_fences(summary_content)
            # Save summary as lesson number=0 and mark course completed
            course_obj = db.query(Course).filter(Course.id == cid).first()
            course_obj.status = "completed"
            summary_lesson = Lesson(
                course_id=cid, number=0, content=summary_content, is_evaluation=False,
            )
            db.add(summary_lesson)
            db.commit()

            yield f"data: {json.dumps({'done': True, 'completed': True}, ensure_ascii=False)}\n\n"

        except Exception as e:
            logger.exception("Summary generation error")
            db.rollback()
            yield f"data: {json.dumps({'error': '总结生成失败，请重试'}, ensure_ascii=False)}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.get("/courses/{course_id}/summary")
def get_summary(course_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id, Course.user_id == user.id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    # Summary is stored as lesson number 0
    summary = db.query(Lesson).filter(Lesson.course_id == course_id, Lesson.number == 0).first()
    if not summary:
        raise HTTPException(status_code=404, detail="总结尚未生成")
    return {"content": summary.content}
