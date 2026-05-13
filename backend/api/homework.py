from fastapi import APIRouter, HTTPException, Header, Response
from pydantic import BaseModel
from ..models.schemas import LoginRequest, CreateHomeworkRequest
from ..storage import JsonStore
from ..notify.email_sender import send_homework_reminder


class EmailConfigRequest(BaseModel):
    smtp_server: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    enabled: bool = False


class AdminRegisterRequest(BaseModel):
    username: str
    password: str
    class_name: str


class ClassCreateRequest(BaseModel):
    name: str


router = APIRouter(prefix="/api/admin", tags=["admin"])
store = JsonStore()


def get_current_admin(authorization: str = Header(None)) -> dict:
    if not authorization:
        raise HTTPException(status_code=401, detail="未登录")
    token = authorization.replace("Bearer ", "")
    admin = store.get_admin_by_token(token)
    if not admin:
        raise HTTPException(status_code=401, detail="无效的登录凭证")
    return admin


@router.post("/register")
def register_admin(req: AdminRegisterRequest):
    if not req.username.strip() or not req.password.strip() or not req.class_name.strip():
        raise HTTPException(status_code=400, detail="用户名、密码和班级不能为空")
    result = store.register_admin(req.username.strip(), req.password.strip(), req.class_name.strip())
    if "error" in result:
        raise HTTPException(status_code=409, detail=result["message"])
    return {"message": "注册成功", "admin": {"username": result["username"], "class_name": result["class_name"]}}


@router.post("/login")
def login(req: LoginRequest):
    admin = store.verify_admin(req.username, req.password)
    if admin:
        token = store.create_token(admin["username"])
        return {"token": token, "message": "登录成功", "admin": {"username": admin["username"], "class_name": admin["class_name"]}}
    raise HTTPException(status_code=401, detail="用户名或密码错误")


@router.post("/homeworks")
def create_homework(req: CreateHomeworkRequest, authorization: str = Header(None)):
    admin = get_current_admin(authorization)
    hw = store.create_homework(
        title=req.title,
        description=req.description,
        due_date=req.due_date,
        allow_resubmit=req.allow_resubmit,
        class_name=admin["class_name"]
    )
    return {"message": "创建成功", "homework": hw}


@router.get("/homeworks")
def list_homeworks(authorization: str = Header(None)):
    admin = get_current_admin(authorization)
    all_hw = store.list_homeworks()
    my_hw = [h for h in all_hw if h.get("class_name") == admin["class_name"]]
    return {"homeworks": my_hw}


@router.get("/homeworks/{hw_id}")
def get_homework(hw_id: str, authorization: str = Header(None)):
    admin = get_current_admin(authorization)
    hw = store.get_homework(hw_id)
    if not hw:
        raise HTTPException(status_code=404, detail="作业不存在")
    if hw.get("class_name") != admin["class_name"]:
        raise HTTPException(status_code=403, detail="无权访问该作业")
    return {"homework": hw}


@router.delete("/homeworks/{hw_id}")
def delete_homework(hw_id: str, authorization: str = Header(None)):
    get_current_admin(authorization)
    if store.delete_homework(hw_id):
        return {"message": "删除成功"}
    raise HTTPException(status_code=404, detail="作业不存在")


@router.get("/homeworks/{hw_id}/export-csv")
def export_csv(hw_id: str, authorization: str = Header(None)):
    get_current_admin(authorization)
    csv_data = store.export_csv(hw_id)
    if csv_data is None:
        raise HTTPException(status_code=404, detail="作业不存在")
    return Response(
        content=csv_data,
        media_type="text/csv; charset=utf-8-sig",
        headers={"Content-Disposition": f"attachment; filename=submissions_{hw_id}.csv"}
    )


@router.get("/homeworks/{hw_id}/download-all")
def download_all(hw_id: str, flat: bool = False, authorization: str = Header(None)):
    get_current_admin(authorization)
    zip_data = store.create_submission_zip(hw_id, flat=flat)
    if zip_data is None:
        raise HTTPException(status_code=404, detail="作业不存在或暂无提交")
    suffix = "_flat" if flat else ""
    return Response(
        content=zip_data,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=all_submissions{suffix}_{hw_id}.zip"}
    )


@router.get("/email-config")
def get_email_config(authorization: str = Header(None)):
    get_current_admin(authorization)
    cfg = store.get_email_config()
    safe = {k: v for k, v in cfg.items() if k != "smtp_password"}
    if "smtp_password" in cfg:
        safe["smtp_password"] = "****" if cfg["smtp_password"] else ""
    return safe


@router.post("/email-config")
def set_email_config(req: EmailConfigRequest, authorization: str = Header(None)):
    get_current_admin(authorization)
    old = store.get_email_config()
    pwd = req.smtp_password if req.smtp_password and req.smtp_password != "****" else old.get("smtp_password", "")
    config = {
        "smtp_server": req.smtp_server,
        "smtp_port": req.smtp_port,
        "smtp_user": req.smtp_user,
        "smtp_password": pwd,
        "enabled": req.enabled,
    }
    store.save_email_config(config)
    return {"message": "邮件配置已保存"}


@router.post("/homeworks/{hw_id}/send-reminder")
def send_reminder(hw_id: str, authorization: str = Header(None)):
    get_current_admin(authorization)
    hw = store.get_homework(hw_id)
    if not hw:
        raise HTTPException(status_code=404, detail="作业不存在")
    config = store.get_email_config()
    if not config.get("enabled"):
        raise HTTPException(status_code=400, detail="邮件提醒未开启，请先在系统设置中配置SMTP")
    students = store.find_all_phones_by_homework(hw_id)
    if not students:
        raise HTTPException(status_code=400, detail="没有找到已填写邮箱的已提交学生")
    results = []
    for s in students:
        email = s.get("email") or s.get("phone", "")
        if not email:
            continue
        result = send_homework_reminder(config, email, s["student_name"], hw["title"], hw["due_date"])
        results.append({"student": s["student_name"], "to": email, "code": result.get("Code", "ERROR")})
    sent = [r for r in results if r["code"] == "OK"]
    return {"message": f"成功发送 {len(sent)} 人，共 {len(results)} 人", "results": results}


# --- Class management ---

@router.get("/classes")
def list_classes():
    return {"classes": store.list_classes()}


@router.post("/classes")
def create_class(req: ClassCreateRequest):
    if not req.name.strip():
        raise HTTPException(status_code=400, detail="班级名称不能为空")
    result = store.add_class(req.name.strip())
    if "error" in result:
        raise HTTPException(status_code=409, detail=result["message"])
    return {"message": "班级创建成功", "class": result}


# --- Student management ---

@router.get("/students")
def list_students(authorization: str = Header(None)):
    admin = get_current_admin(authorization)
    students = store.list_students_by_class(admin["class_name"])
    return {"students": students}


# --- Super admin: admin management ---

@router.get("/all-admins")
def list_all_admins(authorization: str = Header(None)):
    admin = get_current_admin(authorization)
    if admin["username"] != "admin":
        raise HTTPException(status_code=403, detail="仅超级管理员可操作")
    admins = store.list_all_admins()
    safe = [{"username": a["username"], "class_name": a["class_name"], "created_at": a.get("created_at", "")} for a in admins]
    return {"admins": safe}


@router.delete("/admins/{username}")
def delete_admin(username: str, authorization: str = Header(None)):
    admin = get_current_admin(authorization)
    if admin["username"] != "admin":
        raise HTTPException(status_code=403, detail="仅超级管理员可操作")
    if username == "admin":
        raise HTTPException(status_code=400, detail="不能删除超级管理员")
    if store.delete_admin(username):
        return {"message": f"已踢出管理员 {username}"}
    raise HTTPException(status_code=404, detail="管理员不存在")
