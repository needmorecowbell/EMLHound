from eml_assess.vaultman import VaultMan
import redis 

import logging
class Source():
    """Source
    
    Base EML File Source Class
    """
    
    def __init__(self,eml_pool:redis.Redis, name="Unnamed Source"):
        self.name = name
        self.eml_pool = eml_pool
        
        self.period_types = ["cron","dynamic","seconds"]
        self.cronschedule = "* * * * *"

    def activate(self):
        """
            Activate a source to start retrieving EMLs
        """
        pass
    
    def check(self):
        """
            Sources should check each new EML and vet them before including them for reports
        """
        pass