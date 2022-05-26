import base64

class EMLAttachment():
    def __init__(self):
        self.file_type= ""
        self.file_name= ""
        self.file_size = 0
        self.file_extension = ""
        self.mime_type = ""
        self.mime_type_short = ""
        self.raw = ""
        self.hashes = {}
        self.file_path = ""
        
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

