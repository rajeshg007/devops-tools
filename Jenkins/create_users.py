import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import yaml
import secrets
import subprocess
import os
import requests

# Sample creds.yaml
#guser: <User>
#gpass: <App Password>
#jenkins_auth: <user:apiToken>
#jenkins_url: <JenkinsURL>


with open("creds.yaml") as f:
    try:
        config=yaml.safe_load(f)
    except yaml.YAMLError as exc:
        print(exc)

def sendMail(mail_content, receiver_address):
    sender_address = config['guser']
    sender_pass = config['gpass']

    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = 'Your Jenkins Credentials'
    message.attach(MIMEText(mail_content, 'plain'))
    session = smtplib.SMTP('smtp.gmail.com', 587)
    session.starttls()
    session.login(sender_address, sender_pass)
    text = message.as_string()
    print(f"""
    Mail Text:
    {text}
    """)
    yn = input("Should i send the Mail? ")
    if yn == "y":
        session.sendmail(sender_address, receiver_address, text)
    session.quit()
    print('Mail Sent')

def randomPassword():
    password_length = 13
    return(secrets.token_urlsafe(password_length))

def createUser(userName, password):
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    data = f"script=jenkins.model.Jenkins.instance.securityRealm.createAccount('{userName}', '{password}')"
    response = requests.post(f"{config['jenkins_url']}/scriptText", headers=headers, data=data, auth=(config['jenkins_auth'].split(':')[0], config['jenkins_auth'].split(':')[1]))

con=True
while con:
    email=input("Enter a email: ")
    username=email.split('@')[0]
    password=randomPassword()
    createUser(username, password)

    binpaste = f"""
    jenkinsURL: {config['jenkins_url']}
    Username: {username}
    Password: {password}
    """

    print(binpaste)

    binURL=input("Please Enter the Bin URL: ")

    mail_content = f"""
    Hi {username},
    You Jenkins Creadentials are Available at: {binURL}
    Paste will expire in 1 Day, please contact me again in case it has expired.

    Regards,
    Rajesh
    """

    sendMail(mail_content, email)
    con= True if input('create one more? ') == 'y' else False
