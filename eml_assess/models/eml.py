from typing import List
import hashlib

class EML():
    """
    Represents an EML file in python code
    """
    def __init__(self, path:str):
        self.path = path
        self.ip_addresses=[]
        self.header = {}
        self.body = {}
        self.attachments= []
        self.md5 = hashlib.md5(open(self.path,"rb").read()).hexdigest()


    def append_attachment(self, EMLAttachment) -> None:
        self.attachments.append(EMLAttachment)


    def get_ip_addresses(self) -> List[str]:
        """
        Returns a list of IP addresses in the EML file
        
        :return: List of IP addresses"""

        return self.ip_addresses


    def get_path(self) -> str:
        """
        Returns the path to the EML file
        """
        return self.path
    
    def get_header(self) -> dict:
        """
        Returns the headers in the EML file
        """
        return self.header
    
    def get_body(self) -> dict:
        """
        Returns the body of the EML file
        """
        return self.body

    def to_dict(self):
        return {
            "path":self.path,
            "ip_addresses":self.ip_addresses,
            "header":self.header,
            "body":self.body,
            "attachments": [attachment.to_dict() for attachment in self.attachments]
        }
      