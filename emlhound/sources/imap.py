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


class IMAPSource(Source):
    def __init__(self,username:str, password:str,eml_pool:redis.Redis, vman:VaultMan, folder:str="inbox", server:str="imap.gmail.com", name="IMAP Source", period:int=5):
        super().__init__(eml_pool, name=name)
        self.username= username
        self.password = password
        self.server = server
        self.folder = folder
        self.type="imap"
        self.vman = vman
        self.period=period # in minutes
    
    def activate(self):
        logging.log(msg=f"Activating {self.name} for {self.username} on folder {self.folder}", level=logging.INFO)

        while True:
            logging.log(msg=f"Source {self.name} started scan for {self.username} on folder '{self.folder}'", level=logging.INFO)

            mail = imaplib.IMAP4_SSL(self.server)
            mail.login(self.username, self.password)
            mail.select(self.folder)
            status, data = mail.search(None, 'ALL')
            mail_ids = data[0].split()

            logging.info("Found %d emails in %s" % (len(mail_ids), self.folder))
            for mail_id in mail_ids:
                status, data = mail.fetch(mail_id, '(RFC822)')
                md5 = hashlib.md5(data[0][1]).hexdigest()

                path =f"/tmp/{md5}.eml"

                if not os.path.exists(path) and md5 not in self.vman.get_eml_hashes(): # don't add if it's about to be scanned or is already scanned
                    hashlib.md5(data[0][1])
                    with open(path, "wb") as f:
                        logging.info(f"Writing EML to {path}")
                        f.write(data[0][1])

                    job={"path":path, "delete_after_scan":True}

                    self.eml_pool.rpush("eml_queue", json.dumps(job))
        
            logging.info(f"Source {self.name} scan on {self.username} completed, waiting {str(self.period)} minutes before next scan")
            time.sleep(self.period*60)

