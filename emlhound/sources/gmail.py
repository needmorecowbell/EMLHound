import base64
from emlhound.sources.source import Source
from emlhound.models.eml import EML
import logging
import redis
import time
import imaplib
import os
import json
import hashlib
from emlhound.vaultman import VaultMan
from pprint import pprint

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class GMailSource(Source):
    def __init__(self,key_file:str,token_file:str, eml_pool:redis.Redis, vman:VaultMan, folder:str="inbox", name="GMail Source", period:int=5):
        super().__init__(eml_pool, name=name)
        self.key_file= key_file
        self.folder = folder
        self.type="gmail"
        self.scopes = ['https://www.googleapis.com/auth/gmail.readonly']
        self.vman = vman
        self.token_file = token_file
        self.period=period # in minutes
    
    def activate(self):
        logging.log(msg=f"Activating {self.name}", level=logging.INFO)

        while True:
            logging.log(msg=f"Source {self.name} started scan on folder '{self.folder}'", level=logging.INFO)

            creds = None
                # The file token.json stores the user's access and refresh tokens, and is
                # created automatically when the authorization flow completes for the first
                # time.
            if os.path.exists(self.token_file):
                    creds = Credentials.from_authorized_user_file(self.token_file, self.scopes)
            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.key_file, self.scopes)
                    creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open(self.token_file, 'w') as token:
                    token.write(creds.to_json())

            try:
                # Call the Gmail API
                service = build('gmail', 'v1', credentials=creds)
                results = service.users().messages().list(userId='me',labelIds=self.folder).execute()
                messages = results.get('messages', [])

                
                for message in messages:
                    mail = service.users().messages().get(userId='me', id=message['id'], format="raw").execute()
                    raw= base64.urlsafe_b64decode(mail['raw'])
                    md5 = hashlib.md5(raw).hexdigest()
                    path =f"/tmp/{md5}.eml"
                    if not os.path.exists(path) and md5 not in self.vman.get_eml_hashes():
                        with open(path, "wb") as f:
                            f.write(raw)
                        logging.log(msg=f"Source {self.name} added EML to redis pool: {path}", level=logging.INFO)
                        self.eml_pool.lpush("eml_queue", json.dumps({"path":path, "delete_after_scan":True}))

            except HttpError as error:
                logging.warn(f'An error occurred while Using the GMail API: {error}')

        
            time.sleep(self.period*60)

