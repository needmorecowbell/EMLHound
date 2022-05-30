from emlhound.plugins.plugin import Plugin

from .routes import router
from emlhound.vaultman import VaultMan
import redis
from emlhound.plugins.api_server.server import APIServer
import logging
import uvicorn

class APIServerPlugin(Plugin):
    def __init__(self,eml_pool:redis.Redis, vman:VaultMan, port="4040", host="127.0.0.1"):
        super().__init__()
        self.port = port
        self.host=host
        self.vman= vman
        self.eml_pool=eml_pool

        self.type="api_server"
        
        self.server = APIServer(self.eml_pool,self.vman)
        self.server.include_router(router=router)
    
    def activate(self):
        logging.info(f"Starting API Server on {self.host}:{self.port}")
        uvicorn.run(self.server, port=self.port, host=self.host)