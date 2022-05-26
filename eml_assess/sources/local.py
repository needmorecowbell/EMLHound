from source import Source
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler


class LocalSource(Source):
    def __init__(self,path:str, name="Local Directory Source"):
        super.__init__()
        pass


class EMLHandler (PatternMatchingEventHandler):
    patterns=["*.eml"]
    #rules = config["rules"]
            
    def check(self, event):
       # if(event.src_path not in CACHE):
           # CACHE.append(event.src_path)
        # if event checks out as worth while to check, then send the file over for processing
        pass

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
