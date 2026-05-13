from pydantic import BaseModel
from typing import Optional


class SubmissionInfo(BaseModel):
    student_name: str
    student_id: str
    files: list[str] = []
    submitted_at: Optional[str] = None
    file_size: int = 0


class Homework(BaseModel):
    id: str
    title: str
    description: str
    due_date: str
    created_at: str
    link_id: str
    allow_resubmit: bool = False
    submissions: list[SubmissionInfo] = []


class LoginRequest(BaseModel):
    username: str
    password: str


class CreateHomeworkRequest(BaseModel):
    title: str
    description: str
    due_date: str
    allow_resubmit: bool = False


class SubmitRequest(BaseModel):
    student_name: str
    student_id: str
