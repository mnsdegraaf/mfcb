# -*- coding: utf-8 -*-
"""
Created on Fri Apr  2 11:03:09 2021

@author: mgraaf
"""

import email, smtplib, ssl

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class Mail(object):
    def __init__(self):
    
        self.port = 465  # For SSL
        self.smtp_server = "smtp.gmail.com"
        self.sender_email = "email@email.com"  # Enter your address
        #self.receiver_email = "email@email.com"  # Enter receiver address
        self.password = "***********"#input("Type your password and press enter: ")
        self.context = ssl.create_default_context()
    
    def SendMail(self,message,receiver):
        with smtplib.SMTP_SSL(self.smtp_server, self.port, context=self.context) as server:
            server.login(self.sender_email, self.password)
            server.sendmail(self.sender_email, receiver, message)
            
    def AttachSitRep(self,filename):
        subject ="SitRep"
        body = """Updated"""
        message = MIMEMultipart()

        # Add body to email
        message.attach(MIMEText(body, "plain"))
        
        # Open file in binary mode___________________
        with open(filename, "rb") as attachment:
    # Add file as application/octet-stream
    # Email client can usually download this automatically as attachment
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
# Encode file in ASCII characters to send by email    
            encoders.encode_base64(part)

# Add header as key/value pair to attachment part
            part.add_header("Content-Disposition",f"attachment; filename= {filename}",)

    # Add attachment to message and convert message to string
        message.attach(part)
        text = message.as_string()
        return text
