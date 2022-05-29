from eml_assess.sources.source import Source
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from eml_assess.models.eml import EML
import logging 

class LocalSource(Source):
    def __init__(self,path:str, name="Local Directory Source"):
        super().__init__()
        self.path = path
        self.watchdog_observer = EMLWatchdog(self.path)

class EMLHandler (PatternMatchingEventHandler):
    patterns=["*.eml"]
    #rules = config["rules"]
            
    def check(self, event):
        logging.log(msg="File created: "+event.src_path, level=logging.INFO)
        # scan new file
        eml = EML(event.src_path)

       # if(event.src_path not in CACHE):
           # CACHE.append(event.src_path)
        # if event checks out as worth while to check, then send the file over for processing

    def on_modified(self, event):
        # self.check(event)
        pass

    def on_moved(self, event):
        pass


    def on_created(self, event):
        self.check(event)


class EMLWatchdog(Observer):
    def __init__(self, path):
        super().__init__()
        self.schedule(EMLHandler(), path=path, recursive=True)
        self.start()
