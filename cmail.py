import smtplib
from smtplib import SMTP
from email.message import EmailMessage
def sendmail(to,subject,body):
    server=smtplib.SMTP_SSL('smtp.gmail.com',465)
    server.login('rakeshnandipati5@gmail.com ','ncsl tzhy vqqb fbuu')
    msg=EmailMessage()
    msg['From']='rakeshnandipati5@gmail.com'
    msg['Subject']=subject
    msg['To']=to
    msg.set_content(body)
    server.send_message(msg)
    server.quit()
