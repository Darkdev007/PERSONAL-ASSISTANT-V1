from datetime import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


SCOPES = ["https://www.googleapis.com/auth/calendar"]

def get_calendar_service():
    creds = None
    # token.json stores access & refresh tokens
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)  # Opens browser for login
        # Save the credentials
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    service = build("calendar", "v3", credentials=creds)
    return service



def create_calendar_event( 
    title: str,
    start_time: str,
    end_time: str,
    timezone: str = "Africa/Lagos"
) -> str :
  """
  start_time and end time must be ISO format:
  2025-01-10T14:00:00
  """
  service = get_calendar_service()

  event = {
      "summary" : title,
      "start" : {
        "dateTime" : start_time,
        "timeZone" : timezone,
      },
      "end" : {
          "dateTime" : end_time,
          "timeZone" : timezone
      }
  }
  created_event = service.events().insert(
      calendarId = "primary",
      body=event
      ).execute()

  return {
      "message" :f"Event created: {title} from {start_time} to {end_time}",
      "event_id" : created_event["id"],
      "html_link" : created_event["htmlLink"]
      }

