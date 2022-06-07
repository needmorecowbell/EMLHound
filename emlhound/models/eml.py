from typing import Dict, List
import hashlib
import magic

from emlhound.models.eml_attachment import EMLAttachment

class EML():
    """
    Represents an EML file in python code
    """
    def __init__(self, path:str, ip_addresses:list=[], header:Dict={}, body:Dict={},attachments:List[EMLAttachment]=[], assert_filetype:bool=True):

        # Confirm path leads to eml file (can be skipped if filetype is already certain)
        if(assert_filetype):
            with open(path,"rb") as f:
                res = magic.detect_from_content(f.read())
                assert str(res.mime_type) != "message\/rfc822",f"Mimetype not 'message/rfc822' (EML), identified as <{res.mime_type}>"

        self.path = path
        self.ip_addresses= ip_addresses
        self.header = header   
        self.body = body
        self.attachments= attachments
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
            "md5":self.md5,
            "attachments": [attachment.to_dict() for attachment in self.attachments]
        }
      