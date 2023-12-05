import logging
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://mail.google.com/"]
SCRIPT_DIR = Path(r"")
logging.basicConfig(
    filename=SCRIPT_DIR / "cleanups.log",
    filemode="a",
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
)


def get_creds():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    p = SCRIPT_DIR / "token.json"
    if p.exists():
        logging.info("Token exists")
        creds = Credentials.from_authorized_user_file(p, SCOPES)
        logging.info(f"Creds are {creds}")
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            logging.info("Creds refreshed")
        # Save the credentials for the next run
        with p.open("w") as token:
            token.write(creds.to_json())
            logging.info("Token saved")
    return creds


def clean_mailbox():
    creds = get_creds()
    logging.info("Got creds")
    try:
        service = build("gmail", "v1", credentials=creds)
        messages_reply = (
            service.users()
            .messages()
            .list(userId="me", labelIds="CATEGORY_PROMOTIONS")
            .execute()
        )
        logging.info(f"Receive {len(messages_reply['messages'])} messages.")
        for message in messages_reply["messages"]:
            service.users().messages().trash(userId="me", id=message["id"]).execute()
            logging.info(f"Trash '{message['id']}'.")
    except HttpError as e:
        logging.error(f"HTTP Error occured:\n{e}")
    except Exception as e:
        logging.error(f"Exception occured\n{e}")


if __name__ == "__main__":
    clean_mailbox()
