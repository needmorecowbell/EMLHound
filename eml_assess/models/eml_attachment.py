import base64

class EMLAttachment():
    def __init__(self, file_type="", file_name="",file_size=0,file_extension="",mime_type="",mime_type_short="",hashes={},raw=""):
        self.file_type= file_type
        self.file_name= file_name
        self.file_size = file_size
        self.file_extension = file_extension
        self.mime_type = mime_type
        self.mime_type_short = mime_type_short
        self.raw = raw
        self.hashes = hashes
        
    def to_dict(self):
        return {
            "file_type":self.file_type,
            "file_name":self.file_name,
            "file_size":self.file_size,
            "file_extension":self.file_extension,
            "mime_type":self.mime_type,
            "mime_type_short":self.mime_type_short,
            "hashes":self.hashes,
        }
        
    def to_file(self, path:str):
        """Write the attachment to a file
        
        :param path: Path to write the attachment to
        """
        with open(path, "wb") as f:
            f.write(base64.b64decode(self.raw))
        

