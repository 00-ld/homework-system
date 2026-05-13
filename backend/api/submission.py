import os
import shutil
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from ..storage import JsonStore
from ..config import MAX_UPLOAD_SIZE

router = APIRouter(prefix="/api/submit", tags=["submit"])
store = JsonStore()


@router.get("/{link_id}")
def get_submit_page(link_id: str):
    hw = store.get_homework_by_link(link_id)
    if not hw:
        raise HTTPException(status_code=404, detail="链接无效或作业不存在")
    return {
        "homework": {
            "title": hw["title"],
            "description": hw["description"],
            "due_date": hw["due_date"],
            "link_id": hw["link_id"],
            "allow_resubmit": hw.get("allow_resubmit", False)
        }
    }


@router.post("/{link_id}")
async def submit_homework(
    link_id: str,
    student_name: str = Form(...),
    student_id: str = Form(...),
    files: list[UploadFile] = File(...)
):
    hw = store.get_homework_by_link(link_id)
    if not hw:
        raise HTTPException(status_code=404, detail="链接无效或作业不存在")

    check = store.check_submission(link_id, student_name, student_id)
    if check:
        old_dir = store.get_submission_dir(hw, student_name, student_id)
        if old_dir.exists():
            shutil.rmtree(old_dir)

    total_size = 0
    saved_files = []
    student_dir = store.get_submission_dir(hw, student_name, student_id)

    for file in files:
        content = await file.read()
        total_size += len(content)
        if total_size > MAX_UPLOAD_SIZE:
            shutil.rmtree(student_dir, ignore_errors=True)
            raise HTTPException(status_code=413, detail=f"文件总大小超过 {MAX_UPLOAD_SIZE // (1024*1024)}MB 限制")
        file_path = student_dir / file.filename
        with open(file_path, "wb") as f:
            f.write(content)
        saved_files.append(file.filename)

    sub = store.save_submission(link_id, student_name, student_id, saved_files, total_size)
    if sub and "error" in sub:
        shutil.rmtree(student_dir, ignore_errors=True)
        raise HTTPException(status_code=409, detail=sub["message"])

    return {"message": "提交成功", "submission": sub}


@router.get("/{link_id}/check")
def check_submission(link_id: str, student_name: str, student_id: str):
    result = store.check_submission(link_id, student_name, student_id)
    return {"submitted": result is not None, "submission": result}
