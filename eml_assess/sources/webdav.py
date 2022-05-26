from source import Source

class WebDavSource(Source):
    def __init__(self, webdav_url:str, name:str="Unidentified WebDav Source"):
        super.__init__(name=name)
        
        self.period_type=""
        
        self.webdav_url=webdav_url
