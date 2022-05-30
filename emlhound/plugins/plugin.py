import redis
from emlhound.vaultman import VaultMan

class Plugin():
    """Plugin
    
    Base Plugin Class for EMLHound
    """

    def __init__(self,):
        pass

    
    def __init__(self,eml_pool:redis.Redis=None, vman:VaultMan=None, name="Unnamed Source", description=""):
        self.name = name
        self.eml_pool = eml_pool
        self.vman = vman
        self.description=description


    def load(self):
        """
            Load a Plugin to start interacting with EMLAssess
        """
        pass
    
    def activate(self):
        """
            Sources should check each new EML and vet them before including them for reports
        """
        pass