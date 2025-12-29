
import base64
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from email.message import EmailMessage
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText


#Scope for sending emails
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

#Authenticate and build gmail service
def get_gmail_service():
    creds = None
    #token_gmail stores your access and refresh tokens
    if os.path.exists("token_gmail.json"):
        creds = Credentials.from_authorized_user_file("token_gmail.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        with open("token_gmail.json", "w") as token:
            token.write(creds.to_json())

    service = build("gmail", "v1", credentials=creds)
    return service


#Send and email

def send_email(to: str, subject:str, body_text: str):
    service = get_gmail_service()

    #Create MIMEText message
    message = MIMEText(body_text)
    message["to"] = to
    message["subject"] = subject
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    #send email
    sent_message = service.users().messages().send(
        userId = "me",
        body = {"raw": raw_message}
    ).execute()

    return f"Email sent to {to}! Message ID: {sent_message['id']}"

