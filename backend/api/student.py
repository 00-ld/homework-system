from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..storage import JsonStore

router = APIRouter(prefix="/api/student", tags=["student"])
store = JsonStore()


class RegisterRequest(BaseModel):
    student_name: str
    student_id: str
    phone: str = ""
    email: str = ""
    class_name: str = ""


class LoginRequest(BaseModel):
    student_name: str
    student_id: str


class UpdatePhoneRequest(BaseModel):
    student_id: str
    phone: str


# 改进5: 支持信息更新（学号已存在时更新信息而非拒绝）
@router.post("/register")
def register(req: RegisterRequest):
    if not req.student_name.strip() or not req.student_id.strip():
        raise HTTPException(status_code=400, detail="姓名和学号不能为空")
    result = store.register_student(req.student_name.strip(), req.student_id.strip(), req.phone.strip(), req.class_name.strip(), req.email.strip())
    if "error" in result:
        raise HTTPException(status_code=409, detail=result["message"])
    if result.get("updated"):
        return {"message": "信息已更新", "student": result["student"]}
    return {"message": "注册成功", "student": result}


@router.post("/update-phone")
def update_phone(req: UpdatePhoneRequest):
    student = store.update_student_phone(req.student_id.strip(), req.phone.strip())
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    return {"message": "手机号已更新", "student": student}


@router.get("/homeworks")
def list_homeworks(class_name: str = ""):
    all_hw = store.list_homeworks()
    result = []
    for hw in all_hw:
        if class_name and hw.get("class_name") != class_name:
            continue
        result.append({
            "title": hw["title"],
            "description": hw["description"],
            "due_date": hw["due_date"],
            "link_id": hw["link_id"],
            "created_at": hw["created_at"],
            "class_name": hw.get("class_name", "")
        })
    return {"homeworks": result}


@router.get("/homeworks/{link_id}")
def get_homework(link_id: str):
    hw = store.get_homework_by_link(link_id)
    if not hw:
        raise HTTPException(status_code=404, detail="作业不存在")
    return {"homework": {"title": hw["title"], "description": hw["description"], "due_date": hw["due_date"], "class_name": hw.get("class_name", "")}}


@router.post("/login")
def login(req: LoginRequest):
    student = store.verify_student(req.student_id.strip(), req.student_name.strip())
    if not student:
        raise HTTPException(status_code=404, detail="未找到该学生，请先注册")
    return {"message": "验证成功", "student": student}


@router.get("/classes")
def list_classes():
    return {"classes": store.list_classes()}
