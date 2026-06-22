import os
import smtplib
from email.mime.text import MIMEText
from app.tools.registry import registry

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.qq.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")

def send_email(to: str, subject: str, body: str) -> str:
    """发送邮件（需要配置 SMTP 环境变量）。"""
    if not SMTP_USER or not SMTP_PASS:
        return "错误：邮件服务未配置 SMTP_USER / SMTP_PASS"
    try:
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = SMTP_USER
        msg["To"] = to

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, [to], msg.as_string())
        return f"邮件已发送至 {to}"
    except Exception as e:
        return f"邮件发送失败：{str(e)}"

registry.register("send_email", send_email)
