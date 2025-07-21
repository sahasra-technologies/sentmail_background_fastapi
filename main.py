from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
import ssl
import uvicorn

load_dotenv()

app = FastAPI()


# Pydantic model for request validation
class UserData(BaseModel):
    firstName: str
    lastName: str
    email: EmailStr
    phone: str


# Convert JSON data to an HTML table
def generate_html_table(data: dict) -> str:
    rows = "".join(
        f"<tr><td><strong>{key}</strong></td><td>{value}</td></tr>"
        for key, value in data.items()
    )
    return f"""
    <html>
        <body>
            <h3>User Submitted Data on Sahasra Landing Page</h3>
            <table border="1" cellpadding="5" cellspacing="0">
                {rows}
            </table>
        </body>
    </html>
    """


# Background task for sending email
def send_email_background(data: dict):
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT"))
    email_from = os.getenv("EMAIL_FROM")
    email_password = os.getenv("EMAIL_PASSWORD")
    email_to = os.getenv("EMAIL_TO")  # Sending to self or can be changed

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "User Submitted Data"
    msg["From"] = email_from
    msg["To"] = email_to

    html_body = generate_html_table(data)
    msg.attach(MIMEText(html_body, "html"))
    context = ssl.create_default_context()

    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
            # server.starttls()
            server.login(email_from, email_password)
            server.sendmail(email_from, email_to, msg.as_string())
            server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print("Failed to send email:", e)


# Endpoint
@app.post("/send-json-mail")
async def send_json_mail(data: UserData, background_tasks: BackgroundTasks):
    background_tasks.add_task(send_email_background, data.dict())
    return JSONResponse(content={"message": "Email will be sent in background."})

if __name__ == "__main__":
    uvicorn.run("main:app", host='127.0.0.1', port=8100, reload=True, workers=3)