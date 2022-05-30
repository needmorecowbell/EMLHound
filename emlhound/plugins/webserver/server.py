from fastapi import FastAPI
from emlhound.vaultman import VaultMan
import redis


class APIServer(FastAPI):
    def __init__(self, eml_pool:redis.Redis, vman:VaultMan, **args):
        super().__init__(**args)
        self.eml_pool = eml_pool
        self.vman= vman