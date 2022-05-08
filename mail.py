import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import schedule
import time
from app import *
from jinja2 import Template

SMPTP_SERVER_HOST = "localhost"
SMPTP_SERVER_PORT = 1025
SENDER_ADDRESS = "todo@mailhog.com"
SENDER_PASSWORD = "1234"


def send_email(to_address, subject, message):
    msg = MIMEMultipart()
    msg["From"] = SENDER_ADDRESS
    msg["To"] = to_address
    msg["Subject"] = subject

    msg.attach(MIMEText(message,"html"))

    s = smtplib.SMTP(host=SMPTP_SERVER_HOST, port=SMPTP_SERVER_PORT)
    s.login(SENDER_ADDRESS, SENDER_PASSWORD)
    s.send_message(msg)
    s.quit()

    return True

def send():
    users = User.query.all()
    for user in users:
        id = user.userid
        email = user.email
        tasks = Todo.query.filter(Todo.userid==id).all()
        if (tasks!=[]):
            with open("templates/email.html") as file_:
                template = Template(file_.read())
                msg = template.render(tasks=tasks)
            send_email(email,subject="Hello",message=msg)
            
schedule.every().day.at("00:00").do(send)

while True:
    schedule.run_pending()
    time.sleep(1)


