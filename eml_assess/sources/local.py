from eml_assess.sources.source import Source
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from eml_assess.models.eml import EML
import logging
import os

from eml_assess.vaultman import VaultMan 
import redis


class LocalSource(Source):
    def __init__(self,path:str, recursive:bool, eml_pool:redis.Redis, name="Local Directory Source"):
        super().__init__(eml_pool, name=name)
        self.path = path
        self.watchdog_observer = Observer()
        self.watchdog_observer.schedule(EMLHandler(eml_pool=eml_pool),self.path, recursive=recursive)
    
    def activate(self):
        logging.log(msg=f"Activating "+self.name+" watchdog observer...", level=logging.INFO)
        self.watchdog_observer.start()
        try:
            while self.watchdog_observer.is_alive():
                self.watchdog_observer.join(1)
        except KeyboardInterrupt:
            logging.log(msg="Keyboard interrupt detected, stopping watchdog observer...", level=logging.INFO)
        finally:
            self.watchdog_observer.stop()
            self.watchdog_observer.join()
            logging.log(msg="Watchdog Observer stopped", level=logging.INFO)


class EMLHandler (PatternMatchingEventHandler):
    patterns=["*.eml"]

    def __init__(self, eml_pool:redis.Redis, patterns=None, ignore_patterns=None, ignore_directories=False, case_sensitive=False):
        super().__init__(patterns, ignore_patterns, ignore_directories, case_sensitive)
        self.eml_pool = eml_pool
            
    def check(self, event):
        logging.log(msg="Local Source EML Detected: "+event.src_path, level=logging.INFO)

        self.eml_pool.lpush("eml_queue",event.src_path)

        logging.log(msg="Eml path added to redis pool", level=logging.INFO)


    def on_modified(self, event):
        # self.check(event)
        pass

    def on_moved(self, event):
        pass


    def on_created(self, event):
        self.check(event)
