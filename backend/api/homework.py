from fastapi import APIRouter, HTTPException, Header, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from ..models.schemas import LoginRequest, CreateHomeworkRequest
from ..storage import JsonStore
from ..notify.email_sender import send_homework_reminder


# 改进4: 授权码字段
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
    auth_code: str = ""


class ClassCreateRequest(BaseModel):
    name: str


class UpdateStudentRequest(BaseModel):
    student_name: str = ""
    student_id_new: str = ""
    phone: str = ""
    class_name: str = ""


class ManualSubmissionRequest(BaseModel):
    student_name: str
    student_id: str


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


# 改进4: 授权码注册管理员
@router.post("/register")
def register_admin(req: AdminRegisterRequest):
    if not req.username.strip() or not req.password.strip() or not req.class_name.strip():
        raise HTTPException(status_code=400, detail="用户名、密码和班级不能为空")
    # 超级管理员（admin 用户）注册时不需要授权码
    if req.username.strip() != "admin" and req.auth_code != "work":
        raise HTTPException(status_code=403, detail="授权码错误，请输入正确的授权码")
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


# 大文件优化: 使用 StreamingResponse 流式返回 ZIP，避免大文件加载到内存
@router.get("/homeworks/{hw_id}/download-all")
def download_all(hw_id: str, flat: bool = False, authorization: str = Header(None)):
    get_current_admin(authorization)
    hw = store.get_homework(hw_id)
    if not hw:
        raise HTTPException(status_code=404, detail="作业不存在")
    if not hw.get("submissions"):
        raise HTTPException(status_code=404, detail="暂无提交")
    suffix = "_flat" if flat else ""
    generator = store.iter_submission_zip_chunks(hw_id, flat=flat)
    return StreamingResponse(
        generator,
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
def list_students(keyword: str = "", authorization: str = Header(None)):
    admin = get_current_admin(authorization)
    if keyword:
        students = store.search_students(keyword, admin["class_name"])
    else:
        students = store.list_students_by_class(admin["class_name"])
    return {"students": students}


@router.put("/students/{student_id}")
def update_student(student_id: str, req: UpdateStudentRequest, authorization: str = Header(None)):
    """修改学生信息（姓名、学号、手机号、班级）"""
    admin = get_current_admin(authorization)
    student = store.get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    if admin["class_name"] != student.get("class_name", "") and admin["username"] != "admin":
        raise HTTPException(status_code=403, detail="无权操作该学生")
    data = {k: v for k, v in req.model_dump().items() if v}
    updated = store.update_student_info(student_id, data)
    if not updated:
        raise HTTPException(status_code=500, detail="更新失败")
    return {"message": "学生信息已更新", "student": updated}


@router.post("/homeworks/{hw_id}/students")
def add_manual_submission(hw_id: str, req: ManualSubmissionRequest, authorization: str = Header(None)):
    """手动添加提交记录（补交）"""
    admin = get_current_admin(authorization)
    hw = store.get_homework(hw_id)
    if not hw:
        raise HTTPException(status_code=404, detail="作业不存在")
    if hw.get("class_name") != admin["class_name"]:
        raise HTTPException(status_code=403, detail="无权操作该作业")
    # 确保学生存在，不存在则注册
    student = store.get_student_by_id(req.student_id)
    if not student:
        student = store.register_student(req.student_name, req.student_id, class_name=admin["class_name"])
    sub = store.add_manual_submission(hw_id, req.student_name, req.student_id)
    if not sub:
        raise HTTPException(status_code=500, detail="添加失败")
    return {"message": f"已为 {req.student_name}（{req.student_id}）添加补交记录", "submission": sub}


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


# ─── 改进6: 班级人员管理 ───

@router.get("/classes/{class_name}/students")
def get_class_students(class_name: str, authorization: str = Header(None)):
    """查看班级所有学生（包括非活跃的）"""
    admin = get_current_admin(authorization)
    if admin["class_name"] != class_name and admin["username"] != "admin":
        raise HTTPException(status_code=403, detail="无权访问该班级")
    students = store.list_students_by_class(class_name, active_only=False)
    return {"students": students}


@router.get("/classes/{class_name}/stats")
def get_class_stats(class_name: str, authorization: str = Header(None)):
    """班级统计（总人数、活跃人数）"""
    admin = get_current_admin(authorization)
    if admin["class_name"] != class_name and admin["username"] != "admin":
        raise HTTPException(status_code=403, detail="无权访问该班级")
    all_students = store.list_students_by_class(class_name, active_only=False)
    active_students = store.list_students_by_class(class_name, active_only=True)
    return {
        "class_name": class_name,
        "total_students": len(all_students),
        "active_students": len(active_students),
        "inactive_students": len(all_students) - len(active_students)
    }


@router.delete("/students/{student_id}")
def remove_student(student_id: str, authorization: str = Header(None)):
    """移除学生（标记为非活跃）"""
    admin = get_current_admin(authorization)
    student = store.get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    if admin["class_name"] != student.get("class_name", "") and admin["username"] != "admin":
        raise HTTPException(status_code=403, detail="无权操作该学生")
    if store.deactivate_student(student_id):
        return {"message": f"已移除学生 {student.get('student_name')}（{student_id}）"}
    raise HTTPException(status_code=500, detail="操作失败")


@router.get("/homeworks/{hw_id}/status")
def get_homework_status(hw_id: str, authorization: str = Header(None)):
    """查看作业谁提交了谁没提交"""
    admin = get_current_admin(authorization)
    hw = store.get_homework(hw_id)
    if not hw:
        raise HTTPException(status_code=404, detail="作业不存在")
    if hw.get("class_name") != admin["class_name"]:
        raise HTTPException(status_code=403, detail="无权访问该作业")
    # 获取作业对应班级的所有活跃学生
    class_name = hw.get("class_name", admin["class_name"])
    students = store.list_students_by_class(class_name, active_only=True)
    # 获取已提交的学生 ID 集合
    submitted_ids = {s["student_id"] for s in hw.get("submissions", [])}
    result = []
    for s in students:
        result.append({
            "student_name": s["student_name"],
            "student_id": s["student_id"],
            "submitted": s["student_id"] in submitted_ids
        })
    return {"homework_title": hw["title"], "students": result}


# ─── 改进7: 超管权限 ───

@router.get("/system/stats")
def get_system_stats(authorization: str = Header(None)):
    """系统统计 — 仅超管可访问"""
    admin = get_current_admin(authorization)
    if admin["username"] != "admin":
        raise HTTPException(status_code=403, detail="仅超级管理员可操作")
    admins = store.list_all_admins()
    classes = store.list_classes()
    students = store.list_all_students()
    homeworks = store.list_homeworks()
    total_submissions = sum(len(hw.get("submissions", [])) for hw in homeworks)
    return {
        "total_admins": len(admins),
        "total_classes": len(classes),
        "total_students": len(students),
        "total_homeworks": len(homeworks),
        "total_submissions": total_submissions
    }


@router.get("/system/recent-activities")
def get_recent_activities(limit: int = 20, authorization: str = Header(None)):
    """最近活动日志 — 仅超管可访问"""
    admin = get_current_admin(authorization)
    if admin["username"] != "admin":
        raise HTTPException(status_code=403, detail="仅超级管理员可操作")
    homeworks = store.list_homeworks()
    activities = []
    for hw in homeworks:
        activities.append({
            "type": "homework_created",
            "title": hw["title"],
            "class_name": hw.get("class_name", ""),
            "time": hw["created_at"]
        })
        for sub in hw.get("submissions", []):
            activities.append({
                "type": "submission",
                "homework_title": hw["title"],
                "student_name": sub["student_name"],
                "student_id": sub["student_id"],
                "time": sub["submitted_at"]
            })
    # 按时间降序排列
    activities.sort(key=lambda a: a.get("time", ""), reverse=True)
    return {"activities": activities[:limit]}
