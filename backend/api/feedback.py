# 改进11: 意见与Bug反馈系统
from fastapi import APIRouter, HTTPException, Header, Query
from pydantic import BaseModel
from ..storage import JsonStore

router = APIRouter(prefix="/api", tags=["feedback"])
store = JsonStore()


class FeedbackCreateRequest(BaseModel):
    name: str
    contact: str = ""
    content: str
    type: str = "suggestion"  # "bug" or "suggestion"


def get_current_admin(authorization: str = Header(None)) -> dict:
    if not authorization:
        raise HTTPException(status_code=401, detail="未登录")
    token = authorization.replace("Bearer ", "")
    admin = store.get_admin_by_token(token)
    if not admin:
        raise HTTPException(status_code=401, detail="无效的登录凭证")
    return admin


@router.post("/feedback")
def submit_feedback(req: FeedbackCreateRequest):
    """提交反馈（不需要认证）"""
    if not req.name.strip() or not req.content.strip():
        raise HTTPException(status_code=400, detail="姓名和反馈内容不能为空")
    if req.type not in ("bug", "suggestion"):
        raise HTTPException(status_code=400, detail="反馈类型必须为 bug 或 suggestion")
    fb = store.save_feedback(req.name.strip(), req.contact.strip(), req.content.strip(), req.type)
    return {"message": "反馈提交成功，感谢您的意见！", "feedback": fb}


@router.get("/admin/feedback")
def list_feedbacks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    authorization: str = Header(None)
):
    """管理员查看所有反馈（需认证，支持分页）"""
    get_current_admin(authorization)
    result = store.list_feedbacks(page=page, page_size=page_size)
    return result


@router.get("/admin/feedback/stats")
def feedback_stats(authorization: str = Header(None)):
    """反馈统计（总条数、按类型分组）"""
    get_current_admin(authorization)
    return store.get_feedback_stats()


@router.delete("/admin/feedback/{fb_id}")
def delete_feedback(fb_id: str, authorization: str = Header(None)):
    """删除反馈"""
    get_current_admin(authorization)
    if store.delete_feedback(fb_id):
        return {"message": "反馈已删除"}
    raise HTTPException(status_code=404, detail="反馈不存在")
