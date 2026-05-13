import smtplib
from email.mime.text import MIMEText
from email.header import Header


def send_email(config: dict, to_addr: str, subject: str, body: str) -> dict:
    if not config.get("enabled") or not config.get("smtp_server") or not config.get("smtp_user"):
        return {"Code": "SKIP", "Message": "邮件未配置"}

    try:
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = Header(subject, "utf-8")
        msg["From"] = config["smtp_user"]
        msg["To"] = to_addr

        server = smtplib.SMTP(config["smtp_server"], int(config.get("smtp_port", 465)))
        server.starttls()
        server.login(config["smtp_user"], config.get("smtp_password", ""))
        server.sendmail(config["smtp_user"], [to_addr], msg.as_string())
        server.quit()
        return {"Code": "OK", "Message": "发送成功"}
    except Exception as e:
        return {"Code": "FAIL", "Message": str(e)}


def send_homework_reminder(config: dict, to_addr: str, student_name: str, homework_title: str, due_date: str) -> dict:
    subject = f"作业提醒：{homework_title}"
    body = f"{student_name} 同学，您好！\n\n作业「{homework_title}」即将截止，截止时间为 {due_date}，请尽快提交。\n\n—— 班级作业提交系统"
    return send_email(config, to_addr, subject, body)
